#!/usr/bin/env python3
"""Experimental, bounded Jev planner for progressive BSB page reading.

This module is deliberately a planner rather than a reader.  It builds a small,
question-focused excerpt for every local candidate, asks Jev for an advisory
classification for every explicit need, and returns descriptors for the caller
to read in full.  The complete candidate catalog remains in every plan so a
caller can continue reading after the initial recommendation.

The planner never writes to the brain.  It reuses the lexical candidate
generator, credential handling, and strict response validation in
``scripts.bsb_jev``.  Jev sees redacted excerpts without local paths; path and
hash validation happens locally.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
import time
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

try:  # Running as ``python scripts/bsb_jev_focus.py``.
    from . import bsb_jev
except ImportError:  # pragma: no cover - exercised by the CLI invocation.
    import bsb_jev  # type: ignore


MAX_NEEDS = 6
MAX_QUERY_CHARS = 4096
MAX_NEED_CHARS = 1024
MAX_CANDIDATES = 16
MAX_BATCH_DOCS = 16
MAX_API_CALLS = 8
MAX_DOC_EXCERPT_BYTES = 2048
MAX_TOTAL_SUPPLIED_CANDIDATES = MAX_BATCH_DOCS * MAX_API_CALLS
CHOICES = ("direct", "partial", "contrary", "none", "unknown")
_ID_RE = re.compile(r"^[A-Za-z0-9_.:-]{1,80}$")
_HASH_RE = re.compile(r"^[0-9a-f]{64}$")
_STOPWORDS = set(
    "the and for are was were this that with from have has had what when where which who how why "
    "does did its his her their them they will would should could can than then into about also "
    "according specific in on at of to is as an by or be not der die das den dem ein eine einer "
    "eines und oder mit von zur zum im am ist sind war wie was welche welcher welches warum aus "
    "auf bei sich auch fuer für nach vor werden wird eine einem einem einer eines"
    .split()
)


def _validate_query(query_text: Any) -> str:
    if not isinstance(query_text, str) or not query_text.strip() or len(query_text) > MAX_QUERY_CHARS:
        raise ValueError("Query must contain 1..4096 characters")
    if "\x00" in query_text or bsb_jev.SECRET_CONTENT_REGEX.search(query_text):
        raise ValueError("Query contains refused secret-looking content")
    return query_text


def _validate_needs(needs: Any) -> List[str]:
    if not isinstance(needs, (list, tuple)) or not 1 <= len(needs) <= MAX_NEEDS:
        raise ValueError("Needs must contain 1..6 explicit subquestions")
    out: List[str] = []
    for item in needs:
        if not isinstance(item, str) or not item.strip() or len(item) > MAX_NEED_CHARS:
            raise ValueError("Each need must contain 1..1024 characters")
        if "\x00" in item or bsb_jev.SECRET_CONTENT_REGEX.search(item):
            raise ValueError("Need contains refused secret-looking content")
        out.append(item.strip())
    return out


def _validate_candidate_limit(candidate_limit: Any) -> int:
    if type(candidate_limit) is not int or not 1 <= candidate_limit <= MAX_CANDIDATES:
        raise ValueError("Candidate limit must be an integer in 1..16")
    return candidate_limit


def _validate_bool(value: Any, name: str) -> bool:
    if type(value) is not bool:
        raise ValueError(f"{name} must be boolean")
    return value


def _tokens(text: str) -> List[str]:
    return [token for token in re.findall(r"\w+", text.casefold()) if token not in _STOPWORDS]


def _terms(text: str) -> set[str]:
    values = set(_tokens(text))
    return values or set(re.findall(r"\w+", text.casefold()))


def _scrub_transport_text(text: str, secret: Optional[str] = None) -> str:
    """Redact credentials and local/link paths before putting text in a packet."""

    scrubbed = bsb_jev.sanitize_text(str(text), secret=secret)
    if bsb_jev.SECRET_CONTENT_REGEX.search(scrubbed):
        return "[REDACTED]"
    # Wikilinks and Markdown links can expose the local graph even when the
    # surrounding sentence is harmless.  Keep a marker so Jev sees a gap.
    scrubbed = re.sub(r"\[\[[^\]\n]{0,1024}\]\]", "[linked path redacted]", scrubbed)
    scrubbed = re.sub(r"\[[^\]\n]{0,512}\]\([^\)\n]{0,1024}\)", "[linked path redacted]", scrubbed)
    # Redact common absolute and relative local path spellings.  This is only
    # applied to the transport copy; local descriptors retain their paths.
    scrubbed = re.sub(r"(?<![\w])(?:[A-Za-z]:[\\/]|\\\\)[^\s<>\]\)]+", "[local path redacted]", scrubbed)
    scrubbed = re.sub(
        r"(?<![\w])(?:wiki|raw|journal|brain|docs|scripts)/[A-Za-z0-9_./-]+",
        "[local path redacted]",
        scrubbed,
        flags=re.IGNORECASE,
    )
    return scrubbed


def _safe_local_path(root: Path, relative: Any) -> Path:
    if not isinstance(relative, str):
        raise ValueError("Candidate path must be a relative string")
    return bsb_jev._safe_path(root, relative)


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _clip_utf8(text: str, limit: int) -> Tuple[str, bool]:
    data = text.encode("utf-8")
    if len(data) <= limit:
        return text, False
    # Decode after clipping so a multi-byte character cannot break the packet.
    clipped = data[:limit].decode("utf-8", errors="ignore")
    return clipped, True


def _candidate_descriptor(
    candidate: Mapping[str, Any], root: Path, rank: int, *, require_hash: bool = False
) -> Dict[str, Any]:
    if not isinstance(candidate, Mapping):
        raise ValueError("Candidate descriptor must be an object")
    candidate_id = candidate.get("id") or f"c{rank}"
    if not isinstance(candidate_id, str) or not _ID_RE.fullmatch(candidate_id):
        raise ValueError("Invalid candidate identifier")
    path_name = candidate.get("path")
    path = _safe_local_path(root, path_name)
    if not path.is_file():
        raise ValueError("Candidate path is unavailable")
    raw = path.read_bytes()
    actual_hash = _sha256_bytes(raw)
    supplied_hash = candidate.get("file_sha256", candidate.get("sha256", candidate.get("hash")))
    if supplied_hash is not None:
        if not isinstance(supplied_hash, str) or not _HASH_RE.fullmatch(supplied_hash):
            raise ValueError("Invalid candidate hash")
        if supplied_hash != actual_hash:
            raise ValueError("Candidate changed since it was cataloged")
    elif require_hash:
        raise ValueError("Candidate hash is required")
    title = candidate.get("title") or path.stem
    if not isinstance(title, str) or not title.strip():
        title = path.stem
    if len(title) > 512:
        title = title[:512]
    return {
        "id": candidate_id,
        "path": path.relative_to(root).as_posix(),
        "title": title.strip(),
        "hash": actual_hash,
        "rank": rank,
    }


def _line_score(line: str, query_terms: set[str], need_terms: set[str]) -> float:
    words = set(re.findall(r"\w+", line.casefold()))
    if not words:
        return 0.0
    score = float(len(words & query_terms))
    score += 2.0 * len(words & need_terms)
    if line.lstrip().startswith("#"):
        score += 0.5
    return score


def _excerpt_windows(
    lines: Sequence[str], query_text: str, needs: Sequence[str], candidate: Mapping[str, Any]
) -> List[Dict[str, Any]]:
    """Choose several local line windows while preserving exact provenance."""

    if not lines:
        return []
    query_terms = _terms(query_text)
    need_terms = [_terms(need) for need in needs]
    scores: List[float] = []
    for line in lines:
        line_score = _line_score(line, query_terms, set().union(*need_terms))
        scores.append(line_score)

    anchors: List[Tuple[float, int]] = []
    # Keep up to two good sections per need.  This is intentionally small; a
    # caller must read the full page before relying on any answer.
    for terms in need_terms:
        need_scores = [_line_score(line, query_terms, terms) for line in lines]
        for idx in sorted(range(len(lines)), key=lambda i: (-need_scores[i], i))[:2]:
            if need_scores[idx] > 0:
                anchors.append((need_scores[idx] + 0.25, idx))
    for idx in sorted(range(len(lines)), key=lambda i: (-scores[i], i))[:4]:
        if scores[idx] > 0:
            anchors.append((scores[idx], idx))

    if not anchors:
        try:
            fallback_start = max(1, int(candidate.get("line_start", 1)))
            fallback_end = min(len(lines), int(candidate.get("line_end", fallback_start)))
        except (TypeError, ValueError):
            fallback_start, fallback_end = 1, min(len(lines), 3)
        anchors = [(1.0, max(0, fallback_start - 1))]
        fallback_end = max(fallback_start, fallback_end)

    # Expand around anchors, merge overlaps, and remember the best score for
    # each section.  Non-overlapping sections stay separate in the final plan.
    raw_sections: List[Tuple[float, int, int]] = []
    for score, idx in sorted(anchors, key=lambda item: (-item[0], item[1])):
        start = max(0, idx - 1)
        end = min(len(lines), idx + 2)
        raw_sections.append((score, start, end))
    raw_sections.sort(key=lambda item: (item[1], item[2]))
    merged: List[Tuple[float, int, int]] = []
    for score, start, end in raw_sections:
        if merged and start <= merged[-1][2]:
            old_score, old_start, old_end = merged[-1]
            merged[-1] = (max(old_score, score), old_start, max(old_end, end))
        else:
            merged.append((score, start, end))
    merged.sort(key=lambda item: (-item[0], item[1]))

    windows: List[Dict[str, Any]] = []
    used_bytes = 0
    for score, start, end in merged:
        section_text = "\n".join(lines[start:end])
        remaining = MAX_DOC_EXCERPT_BYTES - used_bytes
        if remaining <= 0:
            break
        section_text, clipped = _clip_utf8(section_text, remaining)
        if not section_text:
            continue
        windows.append(
            {
                "start_line": start + 1,
                "end_line": min(len(lines), end),
                "text": section_text,
                "score": round(float(score), 4),
                "truncated": clipped,
            }
        )
        used_bytes += len(section_text.encode("utf-8"))
        if clipped:
            break
    windows.sort(key=lambda item: (item["start_line"], item["end_line"]))
    return windows


def build_focus_excerpts(
    candidates: Sequence[Mapping[str, Any]],
    query_text: str,
    needs: Sequence[str],
    repo_root: Optional[Path | str] = None,
) -> List[Dict[str, Any]]:
    """Build bounded, multi-window excerpts from locally validated candidates.

    The returned ``text`` values are excerpts only.  Every item carries the
    source hash and line ranges, plus an explicit note that unseen lines may
    contain relevant evidence.
    """

    query = _validate_query(query_text)
    validated_needs = _validate_needs(list(needs))
    root = bsb_jev.resolve_repo_root(repo_root)
    if not isinstance(candidates, Sequence) or isinstance(candidates, (str, bytes)):
        raise ValueError("Candidates must be a sequence")
    if not 1 <= len(candidates) <= MAX_TOTAL_SUPPLIED_CANDIDATES:
        raise ValueError(f"Candidates must contain 1..{MAX_TOTAL_SUPPLIED_CANDIDATES} items")
    out: List[Dict[str, Any]] = []
    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    for rank, candidate in enumerate(candidates, start=1):
        descriptor = _candidate_descriptor(candidate, root, rank)
        if descriptor["id"] in seen_ids or descriptor["path"] in seen_paths:
            raise ValueError("Candidate identifiers and paths must be unique")
        seen_ids.add(descriptor["id"])
        seen_paths.add(descriptor["path"])
        path = root / descriptor["path"]
        raw = path.read_bytes()
        if len(raw) > 262144:
            raise ValueError("Candidate page exceeds the lexical reader bound")
        # The descriptor check above is intentionally repeated immediately
        # before reading: a concurrent edit must never be silently classified.
        if _sha256_bytes(raw) != descriptor["hash"]:
            raise ValueError("Candidate changed while excerpts were being built")
        content = raw.decode("utf-8-sig")
        if "\x00" in content or bsb_jev.SECRET_CONTENT_REGEX.search(content):
            raise ValueError("Candidate contains refused secret-looking content")
        lines = content.splitlines()
        windows = _excerpt_windows(lines, query, validated_needs, candidate)
        excerpt_bytes = sum(len(window["text"].encode("utf-8")) for window in windows)
        if excerpt_bytes > MAX_DOC_EXCERPT_BYTES:
            raise ValueError("Excerpt exceeds per-document bound")
        out.append(
            {
                **descriptor,
                "windows": windows,
                "excerpt_bytes": excerpt_bytes,
                "unseen_text_may_contain_relevant_evidence": True,
                "coverage_note": (
                    "Only the listed line windows were supplied to Jev; read the whole page before "
                    "using it as evidence."
                ),
            }
        )
    return out


def _descriptor_for_plan(item: Mapping[str, Any]) -> Dict[str, Any]:
    return {
        "id": item["id"],
        "path": item["path"],
        "title": item.get("title", Path(item["path"]).stem),
        "hash": item["hash"],
        "file_sha256": item["hash"],
        "rank": item.get("rank", 0),
    }


def _make_payload(
    query_text: str,
    needs: Sequence[str],
    excerpts: Sequence[Mapping[str, Any]],
    secret: Optional[str],
    model: str = bsb_jev.DEFAULT_MODEL,
) -> Dict[str, Any]:
    state_documents: Dict[str, Any] = {}
    for item in excerpts:
        windows = []
        for window in item["windows"]:
            windows.append(
                {
                    "start_line": window["start_line"],
                    "end_line": window["end_line"],
                    "text": _scrub_transport_text(window["text"], secret),
                }
            )
        state_documents[item["id"]] = {
            "title": _scrub_transport_text(item.get("title", ""), secret),
            "hash": item["hash"],
            "windows": windows,
            "text": _scrub_transport_text("\n\n".join(w["text"] for w in windows), secret),
        }
    state_needs = {
        f"n{index}": {"text": _scrub_transport_text(need, secret)}
        for index, need in enumerate(needs, start=1)
    }
    questions: Dict[str, Any] = {}
    for item in excerpts:
        for index, _need in enumerate(needs, start=1):
            need_id = f"n{index}"
            question_id = f"{item['id']}:{need_id}"
            questions[question_id] = {
                "type": "choice",
                "instructions": (
                    bsb_jev.UNTRUSTED_DATA_NOTICE
                    + f" Classify document id {item['id']} against explicit need id {need_id}. "
                    + f"The need text is: {state_needs[need_id]['text']} "
                    + f"Use only the bounded excerpt in state.documents[{item['id']!r}]. "
                    + "Use unknown when the listed windows do not establish a classification. "
                    + "Contrary evidence must be retained. This is advisory, never proof of "
                    + "sufficiency or absence."
                ),
                "criteria": {
                    "direct": "The supplied excerpt directly answers or supports this need.",
                    "partial": "The excerpt supports part of this need but leaves material gaps.",
                    "contrary": "The excerpt contains evidence that conflicts with the need or an apparent answer.",
                    "none": "The supplied excerpt does not address this need.",
                    "unknown": "The bounded excerpt is insufficient to classify this need.",
                },
            }
    return {
        "model": model,
        "state": {
            "operation": "focus",
            "query": _scrub_transport_text(query_text, secret),
            "needs": state_needs,
            # IDs, hashes and line spans are safe provenance; local paths are
            # deliberately absent from the network packet.
            "documents": state_documents,
        },
        "questions": questions,
    }


def _packet_bytes(payload: Mapping[str, Any]) -> int:
    return len(json.dumps(payload, sort_keys=True, ensure_ascii=False, allow_nan=False).encode("utf-8"))


def _build_batches(
    query_text: str,
    needs: Sequence[str],
    excerpts: Sequence[Mapping[str, Any]],
    secret: Optional[str],
    model: str = bsb_jev.DEFAULT_MODEL,
) -> List[List[Mapping[str, Any]]]:
    batches: List[List[Mapping[str, Any]]] = []
    current: List[Mapping[str, Any]] = []
    for item in excerpts:
        if len(current) >= MAX_BATCH_DOCS:
            batches.append(current)
            current = []
        proposed = current + [item]
        payload = _make_payload(query_text, needs, proposed, secret, model)
        if _packet_bytes(payload) <= bsb_jev.MAX_PAYLOAD_SIZE_BYTES:
            current = proposed
            continue
        if current:
            batches.append(current)
            current = []
            single = _make_payload(query_text, needs, [item], secret, model)
            if _packet_bytes(single) > bsb_jev.MAX_PAYLOAD_SIZE_BYTES:
                raise ValueError("Single focus document cannot fit Jev packet limit")
            current = [item]
        else:
            raise ValueError("Single focus document cannot fit Jev packet limit")
    if current:
        batches.append(current)
    if len(batches) > MAX_API_CALLS:
        raise ValueError("Focus review requires more than eight bounded API calls")
    return batches


def _fallback_coverage(needs: Sequence[str], descriptors: Sequence[Mapping[str, Any]]) -> Dict[str, Any]:
    coverage: Dict[str, Any] = {}
    for index, need in enumerate(needs, start=1):
        coverage[f"n{index}"] = {
            "need": need,
            "direct": [],
            "partial": [],
            "contrary": [],
            "none": [],
            "unknown": [],
            "initial": [item["id"] for item in descriptors],
            "status": "gap",
            "advisory": True,
        }
    return coverage


def _selection_and_coverage(
    descriptors: Sequence[Mapping[str, Any]], needs: Sequence[str], judgments: Sequence[Mapping[str, Any]]
) -> Tuple[set[str], Dict[str, Any], List[str], List[str]]:
    by_need: Dict[str, Dict[str, List[str]]] = {
        f"n{index}": {choice: [] for choice in CHOICES} for index, _need in enumerate(needs, start=1)
    }
    by_doc_need: Dict[Tuple[str, str], str] = {}
    for judgment in judgments:
        doc_id = judgment.get("document_id")
        if not doc_id:
            raw_id = judgment.get("id")
            doc_id = raw_id.split(":", 1)[0] if isinstance(raw_id, str) else raw_id
        need_id = judgment.get("need_id")
        choice = judgment.get("choice")
        if doc_id in {item["id"] for item in descriptors} and need_id in by_need and choice in CHOICES:
            by_need[need_id][choice].append(doc_id)
            by_doc_need[(doc_id, need_id)] = choice
    ranks = {item["id"]: item.get("rank", 0) for item in descriptors}
    selected: set[str] = set()
    # Every contrary judgment is selected, even when it loses the greedy gain
    # comparison.  A contrary page is evidence that must stay visible.
    for values in by_need.values():
        selected.update(values["contrary"])

    unresolved = {f"n{index}" for index in range(1, len(needs) + 1)}
    # A contrary page can still directly cover another need. Preserve the
    # conflict while allowing that same descriptor to close the other gap.
    for need_id in list(unresolved):
        if any(by_doc_need.get((doc_id, need_id)) == "direct" for doc_id in selected):
            unresolved.remove(need_id)
    while unresolved:
        best_id: Optional[str] = None
        best_gain: Tuple[Any, ...] = (0, 0, "")
        for item in descriptors:
            doc_id = item["id"]
            if doc_id in selected:
                continue
            direct_gain = sum(by_doc_need.get((doc_id, need_id)) == "direct" for need_id in unresolved)
            partial_gain = sum(by_doc_need.get((doc_id, need_id)) == "partial" for need_id in unresolved)
            gain = int(direct_gain) * 4 + int(partial_gain) * 2
            if gain <= 0:
                continue
            # Larger evidence gain wins; lower lexical rank then ID breaks ties.
            key = (gain, -int(item.get("rank", 0)), doc_id)
            if best_id is None or key > best_gain:
                best_id, best_gain = doc_id, key
        if best_id is None:
            break
        selected.add(best_id)
        for need_id in list(unresolved):
            if by_doc_need.get((best_id, need_id)) in {"direct", "partial"}:
                unresolved.remove(need_id)

    # Keep a deterministic foothold when Jev has no positive classification.
    # This is still only a reading suggestion: the caller must inspect the
    # whole page, and the need remains outstanding below.
    if not selected and descriptors:
        selected.add(min(descriptors, key=lambda item: (item.get("rank", 0), item["id"]))["id"])

    coverage: Dict[str, Any] = {}
    outstanding: List[str] = []
    outstanding_ids: List[str] = []
    for index, need in enumerate(needs, start=1):
        need_id = f"n{index}"
        values = by_need[need_id]
        direct = sorted(set(values["direct"]), key=lambda doc: (ranks.get(doc, 0), doc))
        partial = sorted(set(values["partial"]), key=lambda doc: (ranks.get(doc, 0), doc))
        contrary = sorted(set(values["contrary"]), key=lambda doc: (ranks.get(doc, 0), doc))
        none = sorted(set(values["none"]), key=lambda doc: (ranks.get(doc, 0), doc))
        unknown = sorted(set(values["unknown"]), key=lambda doc: (ranks.get(doc, 0), doc))
        selected_direct = [doc for doc in direct if doc in selected]
        selected_partial = [doc for doc in partial if doc in selected]
        if contrary and any(doc in selected for doc in contrary):
            status = "conflict"
            outstanding.append(need)
            outstanding_ids.append(need_id)
        elif selected_direct:
            status = "covered_provisionally"
        elif selected_partial:
            status = "partial_gap"
            outstanding.append(need)
            outstanding_ids.append(need_id)
        else:
            status = "gap"
            outstanding.append(need)
            outstanding_ids.append(need_id)
        coverage[need_id] = {
            "need": need,
            "direct": direct,
            "partial": partial,
            "contrary": contrary,
            "none": none,
            "unknown": unknown,
            "initial": sorted(selected, key=lambda doc: (ranks.get(doc, 0), doc)),
            "status": status,
            "advisory": True,
        }
    return selected, coverage, outstanding, outstanding_ids


def _make_base_plan(
    *,
    status: str,
    reason: Optional[str],
    root: Path,
    query_text: str,
    needs: Sequence[str],
    excerpts: Sequence[Mapping[str, Any]],
    api_calls: int = 0,
    api_usage: Optional[Sequence[Any]] = None,
    api_latency_ms: Optional[Sequence[float]] = None,
    judgments: Optional[Sequence[Mapping[str, Any]]] = None,
    model: str = bsb_jev.DEFAULT_MODEL,
) -> Dict[str, Any]:
    descriptors = [_descriptor_for_plan(item) for item in excerpts]
    all_ids = {item["id"] for item in descriptors}
    judgment_list = list(judgments or [])
    if status in {"disabled", "dry_run", "fallback"}:
        initial_ids = all_ids
        coverage = _fallback_coverage(needs, descriptors)
        outstanding = list(needs)
        outstanding_ids = [f"n{index}" for index in range(1, len(needs) + 1)]
    else:
        initial_ids, coverage, outstanding, outstanding_ids = _selection_and_coverage(
            descriptors, needs, judgment_list
        )
    initial = sorted((item for item in descriptors if item["id"] in initial_ids), key=lambda item: (item["rank"], item["id"]))
    deferred = sorted((item for item in descriptors if item["id"] not in initial_ids), key=lambda item: (item["rank"], item["id"]))
    usage = list(api_usage or [])
    call_latency = [round(float(value), 2) for value in (api_latency_ms or [])]
    total_latency = round(sum(call_latency), 2)
    return {
        "status": status,
        "reason": reason,
        "repo_root": str(root),
        "query": query_text,
        "needs": [{"id": f"n{index}", "text": need} for index, need in enumerate(needs, start=1)],
        "initial": initial,
        "deferred": deferred,
        "candidate_catalog": descriptors,
        "excerpts": [
            {
                "id": item["id"],
                "path": item["path"],
                "title": item["title"],
                "hash": item["hash"],
                "windows": item["windows"],
                "excerpt_bytes": item["excerpt_bytes"],
                "unseen_text_may_contain_relevant_evidence": True,
                "coverage_note": item["coverage_note"],
            }
            for item in excerpts
        ],
        "provisional_coverage": coverage,
        "outstanding_needs": outstanding,
        "outstanding_need_ids": outstanding_ids,
        "judgments": judgment_list,
        "api_usage": usage,
        "usage": usage,
        "api_calls": api_calls,
        "api_latency_ms": call_latency,
        "api_latency_ms_total": total_latency,
        "latency_ms": total_latency,
        "model": model,
        "review_advisory": True,
        "full_page_read_required": True,
        "global_absence_proven": False,
        "pruning": False,
    }


def _catalog_from_candidates(
    query_text: str,
    needs: Sequence[str],
    root: Path,
    candidate_limit: int,
    candidates: Optional[Sequence[Any]],
) -> List[Mapping[str, Any]]:
    if candidates is None:
        generated = bsb_jev.extract_lexical_candidates(query_text, root, None, candidate_limit)
        if not isinstance(generated, list):
            raise ValueError("Lexical candidate generator returned an invalid pool")
        return generated
    if not isinstance(candidates, Sequence) or isinstance(candidates, (str, bytes)):
        raise ValueError("Candidates must be a sequence")
    if not 1 <= len(candidates) <= MAX_CANDIDATES:
        raise ValueError("Supplied candidates must contain 1..16 descriptors")
    # Text supplied by a caller is intentionally ignored.  Local files and
    # hashes are re-read by build_focus_excerpts.  A path-only list is useful
    # to the navigator when it discovers a graph neighbor after the first
    # plan; IDs are deterministic in the supplied order.
    normalized: List[Mapping[str, Any]] = []
    for index, candidate in enumerate(candidates, start=1):
        if isinstance(candidate, str):
            normalized.append({"id": f"c{index}", "path": candidate})
        elif isinstance(candidate, Mapping):
            normalized.append(candidate)
        else:
            raise ValueError("Supplied candidates must be descriptors or relative paths")
    return normalized


def focus(
    query_text: str,
    needs: Sequence[str],
    repo_root: Optional[Path | str] = None,
    candidate_limit: int = 12,
    dry_run: bool = False,
    transport: Optional[Callable[..., Dict[str, Any]]] = None,
    api_key: Optional[str] = None,
    candidates: Optional[Sequence[Any]] = None,
) -> Dict[str, Any]:
    """Plan progressive reading for explicit needs.

    Jev classification is advisory.  A successful plan recommends an initial
    set, while ``candidate_catalog`` and ``deferred`` preserve every candidate
    for deterministic follow-up.  Disabled, dry-run, credential, packet, and
    service failures return all candidates conservatively.
    """

    started = time.perf_counter()
    query = _validate_query(query_text)
    validated_needs = _validate_needs(needs)
    limit = _validate_candidate_limit(candidate_limit)
    dry = _validate_bool(dry_run, "dry_run")
    if api_key is not None and not isinstance(api_key, str):
        raise ValueError("api_key must be a string or None")
    if transport is not None and not callable(transport):
        raise ValueError("transport must be callable")
    root = bsb_jev.resolve_repo_root(repo_root)
    cfg = bsb_jev.get_config(root)
    model_name = str(cfg.get("model", bsb_jev.DEFAULT_MODEL))
    pool = _catalog_from_candidates(query, validated_needs, root, limit, candidates)
    if len(pool) > MAX_TOTAL_SUPPLIED_CANDIDATES:
        raise ValueError("Candidate pool exceeds bounded follow-up capacity")
    # Validate and rebuild from local bytes.  This also ensures supplied graph
    # descriptors cannot smuggle text or a path outside the brain.  A single
    # deleted, linked, binary, or secret-looking page must not crash the whole
    # retrieval operation: classify none of the pool and retain every usable
    # descriptor for caller-controlled follow-up.
    blocked_candidates: List[Dict[str, Any]] = []
    excerpts: List[Dict[str, Any]] = []
    for candidate in pool:
        try:
            excerpts.extend(build_focus_excerpts([candidate], query, validated_needs, root))
        except (ValueError, OSError, UnicodeError) as exc:
            path_value = candidate.get("path") if isinstance(candidate, Mapping) else candidate
            try:
                lexical_name = str(path_value).replace("\\", "/")
                lexical = Path(lexical_name)
                if lexical.is_absolute() or ":" in lexical_name or ".." in lexical.parts or lexical_name.startswith("."):
                    raise ValueError("unsafe candidate label")
                safe_path = lexical.as_posix()
            except Exception:
                safe_path = "[unavailable candidate]"
            blocked_candidates.append({"path": safe_path, "reason": "local_candidate_unavailable"})
    if blocked_candidates:
        plan = _make_base_plan(
            status="fallback",
            reason="local_candidate_unavailable",
            root=root,
            query_text=query,
            needs=validated_needs,
            excerpts=excerpts,
            model=model_name,
        )
        plan["blocked_candidates"] = blocked_candidates
        plan["latency_ms"] = round((time.perf_counter() - started) * 1000, 2)
        return plan
    if not excerpts:
        status = "disabled" if cfg.get("enabled") is not True else "no_candidates"
        plan = _make_base_plan(
            status=status,
            reason="gateway_disabled" if status == "disabled" else "no_candidates",
            root=root,
            query_text=query,
            needs=validated_needs,
            excerpts=excerpts,
            model=model_name,
        )
        plan["latency_ms"] = round((time.perf_counter() - started) * 1000, 2)
        return plan
    if cfg.get("enabled") is not True:
        plan = _make_base_plan(
            status="disabled",
            reason="gateway_disabled",
            root=root,
            query_text=query,
            needs=validated_needs,
            excerpts=excerpts,
            model=model_name,
        )
        plan["latency_ms"] = round((time.perf_counter() - started) * 1000, 2)
        return plan
    if dry:
        plan = _make_base_plan(
            status="dry_run",
            reason="dry_run_no_review",
            root=root,
            query_text=query,
            needs=validated_needs,
            excerpts=excerpts,
            model=model_name,
        )
        plan["latency_ms"] = round((time.perf_counter() - started) * 1000, 2)
        return plan

    secret = api_key if api_key else None
    try:
        batches = _build_batches(
            query,
            validated_needs,
            excerpts,
            secret,
            model_name,
        )
    except ValueError as exc:
        plan = _make_base_plan(
            status="fallback",
            reason="packet_or_batch_bound_exceeded",
            root=root,
            query_text=query,
            needs=validated_needs,
            excerpts=excerpts,
            model=model_name,
        )
        plan["error_detail"] = bsb_jev.sanitize_text(str(exc))
        plan["latency_ms"] = round((time.perf_counter() - started) * 1000, 2)
        return plan

    judgments: List[Dict[str, Any]] = []
    usages: List[Any] = []
    call_latencies: List[float] = []
    calls = 0
    try:
        for batch in batches:
            payload = _make_payload(
                query,
                validated_needs,
                batch,
                secret,
                model_name,
            )
            if _packet_bytes(payload) > bsb_jev.MAX_PAYLOAD_SIZE_BYTES:
                raise ValueError("Jev packet exceeds limit")
            call_started = time.perf_counter()
            calls += 1
            try:
                reviewed = bsb_jev._review(payload, cfg, transport=transport, api_key=api_key)
            finally:
                call_latencies.append((time.perf_counter() - call_started) * 1000)
            usages.append(reviewed.get("usage"))
            answers = reviewed.get("answers")
            if not isinstance(answers, Mapping) or set(answers) != set(payload["questions"]):
                raise ValueError("Jev returned incomplete focus judgments")
            by_question = {qid: question for qid, question in payload["questions"].items()}
            for question_id in payload["questions"]:
                answer = answers[question_id]
                question = by_question[question_id]
                try:
                    document_id, need_id = question_id.rsplit(":", 1)
                except ValueError:
                    raise ValueError("Jev returned an invalid focus question identifier") from None
                if not _ID_RE.fullmatch(document_id) or not re.fullmatch(r"n[1-9][0-9]*", need_id):
                    raise ValueError("Jev returned an invalid focus question identifier")
                if not isinstance(answer, Mapping) or answer.get("choice") not in CHOICES:
                    raise ValueError("Jev returned an invalid focus choice")
                judgments.append(
                    {
                        "id": question_id,
                        "document_id": document_id,
                        "need_id": need_id,
                        "need": validated_needs[int(need_id[1:]) - 1],
                        "choice": answer["choice"],
                        "confidence": answer["confidence"],
                        "probabilities": dict(answer["probabilities"]),
                    }
                )
    except Exception:
        # Any missing/invalid batch invalidates all partial classifications.
        # The complete local pool remains available and is selected so no page
        # disappears merely because a later review call failed.
        plan = _make_base_plan(
            status="fallback",
            reason="credential_or_service_unavailable_or_invalid",
            root=root,
            query_text=query,
            needs=validated_needs,
            excerpts=excerpts,
            api_calls=calls,
            api_usage=usages,
            api_latency_ms=call_latencies,
            model=model_name,
        )
        plan["latency_ms"] = round((time.perf_counter() - started) * 1000, 2)
        return plan

    plan = _make_base_plan(
        status="recommended",
        reason=None,
        root=root,
        query_text=query,
        needs=validated_needs,
        excerpts=excerpts,
        api_calls=calls,
        api_usage=usages,
        api_latency_ms=call_latencies,
        judgments=judgments,
        model=model_name,
    )
    plan["latency_ms"] = round((time.perf_counter() - started) * 1000, 2)
    return plan


def _validate_plan_catalog(plan: Mapping[str, Any]) -> Tuple[Path, List[Dict[str, Any]]]:
    if not isinstance(plan, Mapping):
        raise ValueError("Plan must be an object")
    root_value = plan.get("repo_root")
    if not isinstance(root_value, str) or not root_value:
        raise ValueError("Plan is missing repo root")
    root = Path(root_value).resolve()
    if not root.is_dir():
        raise ValueError("Plan repo root is unavailable")
    catalog = plan.get("candidate_catalog")
    if not isinstance(catalog, list) or len(catalog) > MAX_TOTAL_SUPPLIED_CANDIDATES:
        raise ValueError("Plan candidate catalog is invalid")
    descriptors: List[Dict[str, Any]] = []
    ids: set[str] = set()
    paths: set[str] = set()
    for item in catalog:
        if not isinstance(item, Mapping):
            raise ValueError("Plan candidate descriptor is invalid")
        descriptor = _candidate_descriptor(item, root, int(item.get("rank", len(descriptors) + 1)), require_hash=True)
        if descriptor["id"] in ids or descriptor["path"] in paths:
            raise ValueError("Plan candidate catalog contains duplicates")
        ids.add(descriptor["id"])
        paths.add(descriptor["path"])
        descriptors.append(descriptor)
    initial = plan.get("initial", [])
    deferred = plan.get("deferred", [])
    if not isinstance(initial, list) or not isinstance(deferred, list):
        raise ValueError("Plan page lists are invalid")
    listed = [item.get("id") for item in initial + deferred if isinstance(item, Mapping)]
    if set(listed) != ids or len(listed) != len(ids):
        raise ValueError("Plan does not retain the complete candidate catalog")
    return root, descriptors


def next_read(
    plan: Mapping[str, Any], read_ids: Sequence[str], missing_needs: Optional[Sequence[str]] = None
) -> List[Dict[str, Any]]:
    """Return unread relevant descriptors, then all other unread descriptors.

    Paths and hashes are checked against the current local files on every call.
    The function only returns catalogued descriptors; it never fabricates a
    path or treats an empty result as proof that no evidence exists.
    """

    root, descriptors = _validate_plan_catalog(plan)
    if not isinstance(read_ids, (list, tuple, set)):
        raise ValueError("read_ids must be a sequence of candidate IDs")
    read_list = list(read_ids)
    if any(not isinstance(item, str) for item in read_list) or len(set(read_list)) != len(read_list):
        raise ValueError("read_ids must contain unique strings")
    known_ids = {item["id"] for item in descriptors}
    if not set(read_list).issubset(known_ids):
        raise ValueError("read_ids contains an unknown candidate")
    needs_items = plan.get("needs")
    if not isinstance(needs_items, list) or not needs_items:
        raise ValueError("Plan needs are invalid")
    need_by_text: Dict[str, str] = {}
    need_ids: set[str] = set()
    for item in needs_items:
        if not isinstance(item, Mapping) or not isinstance(item.get("id"), str) or not isinstance(item.get("text"), str):
            raise ValueError("Plan need is invalid")
        need_by_text[item["text"]] = item["id"]
        need_ids.add(item["id"])
    if missing_needs is None:
        requested = plan.get("outstanding_needs", [])
    else:
        if not isinstance(missing_needs, (list, tuple, set)):
            raise ValueError("missing_needs must be a sequence")
        requested = list(missing_needs)
    unresolved: set[str] = set()
    for value in requested:
        if value in need_ids:
            unresolved.add(value)
        elif value in need_by_text:
            unresolved.add(need_by_text[value])
        else:
            raise ValueError("missing_needs contains an unknown need")

    judgment_rows = plan.get("judgments", [])
    if not isinstance(judgment_rows, list):
        raise ValueError("Plan judgments are invalid")
    doc_need_choice: Dict[Tuple[str, str], str] = {}
    for row in judgment_rows:
        if not isinstance(row, Mapping):
            raise ValueError("Plan judgment is invalid")
        doc_id, need_id, choice = row.get("document_id"), row.get("need_id"), row.get("choice")
        if doc_id not in known_ids or need_id not in need_ids or choice not in CHOICES:
            raise ValueError("Plan judgment references unknown data")
        doc_need_choice[(doc_id, need_id)] = choice

    unread = [item for item in descriptors if item["id"] not in set(read_list)]
    rank = {item["id"]: item.get("rank", index) for index, item in enumerate(descriptors, start=1)}
    priority = {"direct": 5, "partial": 4, "contrary": 3, "unknown": 2, "none": 0}
    relevant: List[Tuple[int, Dict[str, Any]]] = []
    remaining: List[Dict[str, Any]] = []
    for item in unread:
        scores = [
            priority[doc_need_choice[(item["id"], need_id)]]
            for need_id in unresolved
            if (item["id"], need_id) in doc_need_choice
        ]
        best = max(scores, default=0)
        if best > 0:
            relevant.append((best, item))
        else:
            remaining.append(item)
    relevant.sort(key=lambda pair: (-pair[0], rank[pair[1]["id"]], pair[1]["id"]))
    remaining.sort(key=lambda item: (rank[item["id"]], item["id"]))
    return [_descriptor_for_plan(item) for _score, item in relevant] + [
        _descriptor_for_plan(item) for item in remaining
    ]


def _read_request(path_name: Optional[str]) -> Dict[str, Any]:
    if not path_name or path_name == "-":
        data = sys.stdin.buffer.read(65537)
    else:
        path = Path(path_name)
        data = path.read_bytes()
        if len(data) > 65536:
            raise ValueError("Request JSON exceeds 64 KiB")
    if len(data) > 65536:
        raise ValueError("Request JSON exceeds 64 KiB")
    try:
        parsed = json.loads(data.decode("utf-8-sig"))
    except (UnicodeError, json.JSONDecodeError):
        raise ValueError("Request must be valid UTF-8 JSON") from None
    if not isinstance(parsed, dict):
        raise ValueError("Request JSON must be an object")
    return parsed


def build_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="bsb_jev_focus", description="Bounded experimental Jev focus planner")
    parser.add_argument("request", nargs="?", help="Request JSON file, or - for stdin")
    parser.add_argument("--root", help="Brain root")
    parser.add_argument("--dry-run", action="store_true", help="Build a no-network plan")
    parser.add_argument("--out", help="Write JSON output to this file")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_cli_parser()
    args = parser.parse_args(argv)
    try:
        request = _read_request(args.request)
        query = request.get("query_text", request.get("query"))
        needs = request.get("needs")
        if query is None or needs is None:
            raise ValueError("Request JSON requires query and needs")
        candidate_limit = request.get("candidate_limit", 12)
        result = focus(
            query,
            needs,
            repo_root=args.root,
            candidate_limit=candidate_limit,
            dry_run=bool(args.dry_run),
        )
        output = json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True)
        if args.out:
            root = bsb_jev.resolve_repo_root(args.root)
            target = Path(args.out)
            if target.is_absolute():
                target = target.relative_to(root)
            if len(target.parts) != 1 or not re.fullmatch(r"(?:jev-focus|focus-result)[A-Za-z0-9_-]*\.json", target.name):
                raise ValueError("--out must be a root-level jev-focus*.json or focus-result*.json file")
            bsb_jev._atomic(root / target, (output + "\n").encode("utf-8"))
        print(output)
        return 0
    except Exception:
        # Do not echo request data, paths, or credential-looking exception
        # text to a terminal or output file.
        print(json.dumps({"status": "error", "error": "invalid focus request or unavailable local evidence"}))
        return 1


__all__ = ["build_focus_excerpts", "focus", "next_read", "build_cli_parser", "main"]


if __name__ == "__main__":
    raise SystemExit(main())
