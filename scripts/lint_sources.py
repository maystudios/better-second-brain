#!/usr/bin/env python3
"""Source-grade quality lint for the BSB (Second Brain) wiki.

This tool enforces the RESEARCH-DISCIPLINE GATE (CLAUDE.md s1.5): every page
should be grounded in REAL, citable sources, and "lint-clean != trustworthy".
It scans ``wiki/**/*.md``, parses the YAML frontmatter and body of each page,
and assigns a source-grade tier.

TIERS
-----
  Tier A : >= 3 sources AND >= 3 of them resolve to an existing
           ``wiki/sources/<slug>.md`` page (fully paired).
  Tier B : >= 3 sources with >= 1 paired source page.
  Tier C : >= 3 sources but URL-only (no paired source pages).
  Tier D : < 3 sources (stub).

STUB-SOURCE DETECTOR
--------------------
A page under ``wiki/sources/`` is flagged as a *stub source* if its body has
fewer than 12 non-empty lines OR contains any fetch-failure marker
(case-insensitive): "fetch failed", "cloudflare", "403 forbidden",
"general guidance stub", "could not fetch". Stub sources are flagged even when
they are otherwise lint-clean, because a lint-clean page is not the same thing
as a trustworthy one.

WHAT GETS GRADED / GATED
------------------------
Only ``cheatsheet`` and ``synthesis`` pages are *graded and gated*: these are
the reference-grade outputs the gate protects. ``concept``, ``entity``,
``source`` and ``moc`` pages are reported for visibility but are NOT gated by
``--strict``.

The page "type" is taken from the frontmatter ``type:`` key when present,
otherwise inferred from the containing ``wiki/<folder>/`` directory
(cheatsheets -> cheatsheet, syntheses -> synthesis, sources -> source,
concepts -> concept, entities -> entity, moc -> moc).

FLAGS
-----
  --summary                 Per-folder tier breakdown plus totals.
  --strict                  Exit non-zero if any gated page is below the min
                            tier. Used by the pre-commit hook and CI.
  --strict-min-tier {A,B,C} Minimum acceptable tier for gated pages
                            (default B). A is strictest.
  --tsv PATH                Write a full per-page TSV with columns:
                            rel_path, type, tier, source_count, paired_count,
                            is_stub.

With no flags, prints a readable per-page report.

Python 3.10+, standard library only. Run from the repository root::

    python scripts/lint_sources.py .
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass, field

# Tiers ordered from strongest (A) to weakest (D).
TIER_ORDER = ["A", "B", "C", "D"]
TIER_RANK = {t: i for i, t in enumerate(TIER_ORDER)}

# Page types that the source-grade gate actually protects.
GATED_TYPES = {"cheatsheet", "synthesis"}

# Markers (lowercased) that indicate a source page failed to fetch / is filler.
STUB_MARKERS = [
    "fetch failed",
    "cloudflare",
    "403 forbidden",
    "general guidance stub",
    "could not fetch",
]

# Map of wiki subfolder -> canonical page type.
FOLDER_TYPE = {
    "cheatsheets": "cheatsheet",
    "syntheses": "synthesis",
    "sources": "source",
    "concepts": "concept",
    "entities": "entity",
    "moc": "moc",
}

# Recognised frontmatter keys that hold the source list.
SOURCE_KEYS = ("sources", "sources-cited", "sources_cited")

# Matches a wiki/sources/<slug> reference, with or without [[ ]] and folder
# prefix, and tolerates an optional .md extension and alias pipe.
_SOURCE_SLUG_RE = re.compile(
    r"(?:wiki/)?sources/([A-Za-z0-9][A-Za-z0-9._-]*?)(?:\.md)?(?:\||\]|$|\s)",
)


@dataclass
class Page:
    rel_path: str
    abs_path: str
    folder: str
    ptype: str
    frontmatter: dict
    body: str
    source_count: int = 0
    paired_count: int = 0
    tier: str = "D"
    is_stub: bool = False
    notes: list[str] = field(default_factory=list)


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Split a markdown file into (frontmatter dict, body).

    Minimal hand parser: reads between the first two ``---`` lines. Handles
    simple ``key: value`` scalars, block lists (``- item``) and inline flow
    lists (``[a, b, c]``). Returns ({}, text) when there is no frontmatter.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text

    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return {}, text

    fm_lines = lines[1:end]
    body = "\n".join(lines[end + 1:])

    data: dict = {}
    current_key: str | None = None
    for raw in fm_lines:
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue

        stripped = line.lstrip()
        # Block-list item belonging to the current key.
        if stripped.startswith("- ") or stripped == "-":
            if current_key is not None:
                val = stripped[1:].strip()
                val = _strip_scalar(val)
                if val != "":
                    data.setdefault(current_key, [])
                    if isinstance(data[current_key], list):
                        data[current_key].append(val)
            continue

        # key: value
        m = re.match(r"^([A-Za-z0-9_.\-]+)\s*:\s*(.*)$", line)
        if not m:
            continue
        key = m.group(1).strip()
        value = m.group(2).strip()
        current_key = key

        if value == "":
            # Likely a block list / mapping follows on subsequent lines.
            data[key] = []
        elif value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            items = [
                _strip_scalar(p.strip())
                for p in _split_flow_list(inner)
                if p.strip() != ""
            ]
            data[key] = items
        else:
            data[key] = _strip_scalar(value)

    return data, body


def _split_flow_list(inner: str) -> list[str]:
    """Split a flow-style list body on commas not inside quotes."""
    items: list[str] = []
    buf = []
    quote = None
    for ch in inner:
        if quote:
            buf.append(ch)
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
            buf.append(ch)
        elif ch == ",":
            items.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    if "".join(buf).strip():
        items.append("".join(buf))
    return items


def _strip_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def collect_sources(frontmatter: dict, body: str) -> list[str]:
    """Gather source entries from frontmatter list keys and the ## Sources body.

    Returns a flat list of source strings (URLs, wikilinks, or free text).
    """
    sources: list[str] = []
    for key in SOURCE_KEYS:
        if key in frontmatter:
            val = frontmatter[key]
            if isinstance(val, list):
                sources.extend(str(v) for v in val if str(v).strip())
            elif isinstance(val, str) and val.strip():
                sources.append(val.strip())

    # If frontmatter carried no usable sources, fall back to the body
    # "## Sources" section: count list items / non-empty content lines there.
    if not sources:
        sources.extend(_sources_from_body(body))
    return sources


def _sources_from_body(body: str) -> list[str]:
    found: list[str] = []
    in_sources = False
    for raw in body.splitlines():
        line = raw.strip()
        if re.match(r"^#{1,6}\s", line):
            in_sources = re.match(r"^#{1,6}\s+sources\b", line, re.I) is not None
            continue
        if in_sources and line:
            # Treat list items or any non-empty line as one source entry.
            found.append(re.sub(r"^[-*+]\s*", "", line))
    return found


def count_paired(sources: list[str], existing_source_slugs: set[str]) -> int:
    """Count how many source entries resolve to an existing source page."""
    paired = 0
    for s in sources:
        for m in _SOURCE_SLUG_RE.finditer(s + " "):
            slug = m.group(1)
            if slug in existing_source_slugs:
                paired += 1
                break
    return paired


def distinct_paired_slugs(text: str, existing_source_slugs: set[str]) -> set[str]:
    """Distinct existing source-page slugs referenced ANYWHERE in the page.

    BSB cites sources in three layers (frontmatter, the body ``## Sources``
    block, and inline ``([[wiki/sources/slug]])`` claim-level cites). Pairing is
    measured across all of them, so a page that cites via the body or inline is
    not undercounted just because its frontmatter used ``name:``/``url:`` maps
    instead of wikilink scalars.
    """
    found: set[str] = set()
    for m in _SOURCE_SLUG_RE.finditer(text + " "):
        slug = m.group(1)
        if slug in existing_source_slugs:
            found.add(slug)
    return found


def frontmatter_sources(frontmatter: dict) -> list[str]:
    """Source entries declared in frontmatter list/scalar keys only."""
    out: list[str] = []
    for key in SOURCE_KEYS:
        if key in frontmatter:
            val = frontmatter[key]
            if isinstance(val, list):
                out.extend(str(v) for v in val if str(v).strip())
            elif isinstance(val, str) and val.strip():
                out.append(val.strip())
    return out


def classify_tier(source_count: int, paired_count: int) -> str:
    if source_count >= 3 and paired_count >= 3:
        return "A"
    if source_count >= 3 and paired_count >= 1:
        return "B"
    if source_count >= 3:
        return "C"
    return "D"


def detect_stub_source(ptype: str, body: str) -> tuple[bool, list[str]]:
    """Return (is_stub, reasons) for a source page; ('', []) otherwise."""
    if ptype != "source":
        return False, []
    reasons: list[str] = []
    low = body.lower()
    for marker in STUB_MARKERS:
        if marker in low:
            reasons.append(f"fetch-failure marker: {marker!r}")
    non_empty = [ln for ln in body.splitlines() if ln.strip()]
    if len(non_empty) < 12:
        reasons.append(f"thin body ({len(non_empty)} non-empty lines < 12)")
    return (len(reasons) > 0), reasons


def find_wiki_root(repo_root: str) -> str | None:
    candidate = os.path.join(repo_root, "wiki")
    return candidate if os.path.isdir(candidate) else None


def infer_folder(rel_path: str) -> str:
    parts = rel_path.replace("\\", "/").split("/")
    # parts like ["wiki", "<folder>", "..."]
    if len(parts) >= 2 and parts[0] == "wiki":
        return parts[1]
    return parts[1] if len(parts) >= 2 else ""


def infer_type(frontmatter: dict, folder: str) -> str:
    t = str(frontmatter.get("type", "")).strip().lower()
    if t:
        return t
    return FOLDER_TYPE.get(folder, folder or "unknown")


def scan(repo_root: str) -> list[Page]:
    wiki_root = find_wiki_root(repo_root)
    if wiki_root is None:
        return []

    md_files: list[str] = []
    for dirpath, _dirs, files in os.walk(wiki_root):
        for fn in files:
            if fn.lower().endswith(".md"):
                md_files.append(os.path.join(dirpath, fn))
    md_files.sort()

    # First pass: discover existing source slugs.
    existing_source_slugs: set[str] = set()
    for abs_path in md_files:
        rel = os.path.relpath(abs_path, repo_root).replace("\\", "/")
        parts = rel.split("/")
        if len(parts) >= 3 and parts[0] == "wiki" and parts[1] == "sources":
            slug = os.path.splitext(parts[-1])[0]
            existing_source_slugs.add(slug)

    pages: list[Page] = []
    for abs_path in md_files:
        rel = os.path.relpath(abs_path, repo_root).replace("\\", "/")
        try:
            with open(abs_path, "r", encoding="utf-8") as fh:
                text = fh.read()
        except (OSError, UnicodeDecodeError) as exc:
            page = Page(
                rel_path=rel, abs_path=abs_path, folder=infer_folder(rel),
                ptype="unknown", frontmatter={}, body="",
            )
            page.notes.append(f"unreadable: {exc}")
            pages.append(page)
            continue

        fm, body = parse_frontmatter(text)
        folder = infer_folder(rel)
        ptype = infer_type(fm, folder)

        # Source count = the most generous honest reading across the three
        # citation layers; pairing = distinct existing source pages referenced
        # anywhere on the page (frontmatter + body ## Sources + inline cites).
        fm_sources = frontmatter_sources(fm)
        body_sources = _sources_from_body(body)
        paired_slugs = distinct_paired_slugs(text, existing_source_slugs)
        paired_count = len(paired_slugs)
        source_count = max(len(fm_sources), len(body_sources), paired_count)
        tier = classify_tier(source_count, paired_count)
        is_stub, reasons = detect_stub_source(ptype, body)

        page = Page(
            rel_path=rel, abs_path=abs_path, folder=folder, ptype=ptype,
            frontmatter=fm, body=body, source_count=source_count,
            paired_count=paired_count, tier=tier, is_stub=is_stub,
        )
        page.notes.extend(reasons)
        pages.append(page)

    return pages


def write_tsv(pages: list[Page], path: str) -> None:
    rows = ["\t".join(
        ["rel_path", "type", "tier", "source_count", "paired_count", "is_stub"]
    )]
    for p in pages:
        rows.append("\t".join([
            p.rel_path, p.ptype, p.tier, str(p.source_count),
            str(p.paired_count), "1" if p.is_stub else "0",
        ]))
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(rows) + "\n")


def print_report(pages: list[Page]) -> None:
    if not pages:
        print("No wiki/**/*.md pages found.")
        return
    print("Source-grade lint report")
    print("=" * 60)
    for p in pages:
        gated = " [GATED]" if p.ptype in GATED_TYPES else ""
        stub = " STUB-SOURCE" if p.is_stub else ""
        print(
            f"{p.tier}  {p.rel_path}  "
            f"(type={p.ptype}, sources={p.source_count}, "
            f"paired={p.paired_count}){gated}{stub}"
        )
        for note in p.notes:
            print(f"      - {note}")


def print_summary(pages: list[Page]) -> None:
    by_folder: dict[str, dict[str, int]] = {}
    totals: dict[str, int] = {t: 0 for t in TIER_ORDER}
    stub_count = 0
    for p in pages:
        folder = p.folder or "(root)"
        slot = by_folder.setdefault(folder, {t: 0 for t in TIER_ORDER})
        slot[p.tier] += 1
        totals[p.tier] += 1
        if p.is_stub:
            stub_count += 1

    print("Per-folder tier breakdown")
    print("=" * 60)
    header = f"{'folder':<16} " + " ".join(f"{t:>4}" for t in TIER_ORDER) + "  total"
    print(header)
    print("-" * len(header))
    for folder in sorted(by_folder):
        slot = by_folder[folder]
        total = sum(slot.values())
        cells = " ".join(f"{slot[t]:>4}" for t in TIER_ORDER)
        print(f"{folder:<16} {cells}  {total:>5}")
    print("-" * len(header))
    grand = sum(totals.values())
    cells = " ".join(f"{totals[t]:>4}" for t in TIER_ORDER)
    print(f"{'TOTAL':<16} {cells}  {grand:>5}")
    print()
    print(f"Stub sources flagged: {stub_count}")


def evaluate_strict(pages: list[Page], min_tier: str) -> list[Page]:
    """Return gated pages that fall below min_tier (worse rank)."""
    threshold = TIER_RANK[min_tier]
    failing = []
    for p in pages:
        if p.ptype in GATED_TYPES and TIER_RANK[p.tier] > threshold:
            failing.append(p)
    return failing


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lint_sources.py",
        description=(
            "Source-grade quality lint for the BSB wiki. Grades cheatsheet "
            "and synthesis pages (Tier A-D); reports concept/entity/source/moc "
            "without gating. Enforces CLAUDE.md s1.5 research discipline."
        ),
    )
    parser.add_argument(
        "root", nargs="?", default=".",
        help="Repository root containing the wiki/ directory (default: .).",
    )
    parser.add_argument(
        "--summary", action="store_true",
        help="Print per-folder tier breakdown plus totals.",
    )
    parser.add_argument(
        "--strict", action="store_true",
        help="Exit non-zero if any gated page is below --strict-min-tier.",
    )
    parser.add_argument(
        "--strict-min-tier", choices=["A", "B", "C"], default="B",
        help="Minimum acceptable tier for gated pages (default: B).",
    )
    parser.add_argument(
        "--tsv", metavar="PATH",
        help="Write a full per-page TSV to PATH.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    repo_root = os.path.abspath(args.root)

    pages = scan(repo_root)

    if args.tsv:
        write_tsv(pages, args.tsv)
        print(f"Wrote TSV: {args.tsv} ({len(pages)} rows)")

    if args.summary:
        print_summary(pages)
    elif not args.tsv:
        print_report(pages)

    # Always surface stub sources prominently (lint-clean != trustworthy).
    stubs = [p for p in pages if p.is_stub]
    if stubs:
        print()
        print("STUB SOURCES (lint-clean != trustworthy):")
        for p in stubs:
            print(f"  - {p.rel_path}: {'; '.join(p.notes) or 'flagged'}")

    if args.strict:
        failing = evaluate_strict(pages, args.strict_min_tier)
        if failing:
            print()
            print(
                f"STRICT FAILURE: {len(failing)} gated page(s) below "
                f"Tier {args.strict_min_tier}:"
            )
            for p in failing:
                print(f"  - [{p.tier}] {p.rel_path} (type={p.ptype})")
            print()
            print(
                "Research-discipline gate (CLAUDE.md s1.5/s3.3): ground every "
                "page in >= 3 real, cited sources and pair them to "
                "wiki/sources/<slug>.md pages."
            )
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
