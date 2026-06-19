#!/usr/bin/env python3
"""Token-efficiency report for a BSB benchmark example.

Measures — deterministically and reproducibly — whether a BSB (research-gated)
wiki is more token-efficient than (a) a vanilla Karpathy wiki and (b) reading the
raw corpus, in the TWO regimes the question is usually asked about:

  READ  / "understand" cost  - tokens you must LOAD to answer one query.
  FILL  / "interconnection" cost - tokens of the produced wiki ARTIFACT plus its
                                   cross-link (interconnection) density.

The core trade the LLM-wiki pattern makes: the wiki costs tokens once at FILL
time (and a bit more if you also wire interconnections), but saves tokens on
every READ. So this tool also reports the BREAK-EVEN: after how many queries the
one-time fill cost is repaid by per-query read savings.

Token estimate: uses ``tiktoken`` (cl100k_base) when importable, else a
~len/4 chars-per-token heuristic. The SAME estimator is applied to every arm, so
the ratios below are valid regardless of which one ran (the absolute numbers are
approximate; the comparisons are not).

Layout expected (as produced by the bsb-benchmark workflow)::

    <example>/
      raw/                 the shared source corpus
      arm-vanilla/wiki/    the vanilla Karpathy wiki
      arm-bsb/wiki/        the BSB (research-gated) wiki
      questions.json       (optional) the gold question set, for n_queries

Usage::

    python scripts/token_report.py benchmark/small
    python scripts/token_report.py benchmark/small --json benchmark/small/tokens.json
    python scripts/token_report.py benchmark/small --rag-k 3 --md
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from pathlib import Path

WIKILINK_RE = re.compile(r"\[\[([^\]]+?)\]\]")
NAV_NAME_RE = re.compile(r"\b(index|overview|readme|moc|map|start)\b", re.I)


def make_tokenizer():
    """Return (count_fn, name). Prefer tiktoken; fall back to chars/4."""
    try:
        import tiktoken  # type: ignore
        enc = tiktoken.get_encoding("cl100k_base")
        return (lambda s: len(enc.encode(s))), "tiktoken/cl100k_base"
    except Exception:
        return (lambda s: max(1, round(len(s) / 4))), "approx(len/4)"


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def md_files(root: Path) -> list[Path]:
    if not root.is_dir():
        return []
    return sorted(p for p in root.rglob("*.md") if p.is_file())


def measure_corpus(raw_dir: Path, count) -> dict:
    files = [p for p in raw_dir.rglob("*") if p.is_file()] if raw_dir.is_dir() else []
    text_files = [p for p in files if p.suffix.lower() in (".md", ".txt", ".rst", "")]
    tokens = [count(read_text(p)) for p in text_files]
    return {
        "n_sources": len(text_files),
        "total_tokens": sum(tokens),
        "per_source_avg": round(statistics.mean(tokens)) if tokens else 0,
    }


def measure_arm(arm_wiki: Path, count) -> dict | None:
    files = md_files(arm_wiki)
    if not files:
        return None
    page_tokens: list[int] = []
    total_links = 0
    nav_candidates: list[tuple[int, str]] = []  # (tokens, rel)
    for p in files:
        text = read_text(p)
        t = count(text)
        page_tokens.append(t)
        total_links += len(WIKILINK_RE.findall(text))
        if NAV_NAME_RE.search(p.stem):
            nav_candidates.append((t, p.name))
    total = sum(page_tokens)
    median_page = round(statistics.median(page_tokens)) if page_tokens else 0
    # Navigation footprint: the smallest index/overview/MOC page if one exists,
    # otherwise the median page acts as the "locate" read.
    nav_tokens = min(c[0] for c in nav_candidates) if nav_candidates else median_page
    return {
        "n_pages": len(files),
        "total_tokens": total,            # FILL artifact size
        "median_page_tokens": median_page,
        "nav_tokens": nav_tokens,
        "n_wikilinks": total_links,        # interconnections
        "links_per_page": round(total_links / len(files), 2),
        "links_per_1k_tokens": round(total_links / (total / 1000), 2) if total else 0,
        # READ cost to answer one query = locate via nav + read one page.
        "read_per_query": nav_tokens + median_page,
    }


def break_even(fill_tokens: int, savings_per_query: float) -> float | None:
    if savings_per_query is None or savings_per_query <= 0:
        return None
    return round(fill_tokens / savings_per_query, 1)


def build_report(example_dir: Path, rag_k: int) -> dict:
    count, tok_name = make_tokenizer()
    raw = measure_corpus(example_dir / "raw", count)

    arms: dict[str, dict] = {}
    for arm in ("vanilla", "bsb"):
        m = measure_arm(example_dir / f"arm-{arm}" / "wiki", count)
        if m is not None:
            arms[arm] = m

    qpath = example_dir / "questions.json"
    n_queries = None
    if qpath.is_file():
        try:
            n_queries = len(json.loads(read_text(qpath)).get("questions", []))
        except Exception:
            n_queries = None

    # Read-cost baselines from the raw corpus.
    raw_total = raw["total_tokens"]
    rag_read = (
        round(raw["per_source_avg"] * min(rag_k, raw["n_sources"]))
        if raw["n_sources"] else 0
    )
    read_baselines = {
        "raw_read_all_per_query": raw_total,                 # no map: scan everything
        f"raw_rag_top{rag_k}_per_query": rag_read,           # naive RAG: k source-chunks
    }

    # Derive comparisons per arm.
    comparisons = {}
    for arm, m in arms.items():
        rq = m["read_per_query"]
        save_vs_all = raw_total - rq
        save_vs_rag = rag_read - rq
        comparisons[arm] = {
            "read_per_query": rq,
            "fill_artifact_tokens": m["total_tokens"],
            "compression_vs_raw_all": round(raw_total / rq, 1) if rq else None,
            "compression_vs_rag": round(rag_read / rq, 1) if rq else None,
            "read_savings_vs_raw_all_per_query": save_vs_all,
            "break_even_queries_vs_raw_all": break_even(m["total_tokens"], save_vs_all),
            "break_even_queries_vs_rag": break_even(m["total_tokens"], save_vs_rag),
        }

    return {
        "example": example_dir.name,
        "tokenizer": tok_name,
        "n_queries": n_queries,
        "rag_k": rag_k,
        "corpus": raw,
        "read_baselines": read_baselines,
        "arms": arms,
        "comparisons": comparisons,
    }


def print_human(rep: dict) -> None:
    print(f"# Token-efficiency report — example '{rep['example']}'  (tokenizer: {rep['tokenizer']})")
    c = rep["corpus"]
    print(f"\nCorpus (raw): {c['n_sources']} sources, {c['total_tokens']:,} tokens "
          f"(~{c['per_source_avg']:,}/source). Questions: {rep['n_queries']}")
    rb = rep["read_baselines"]
    print("\nRead baselines (no wiki):")
    for k, v in rb.items():
        print(f"  {k:<32} {v:>10,} tokens/query")

    print("\nFILL (build the wiki + interconnections):")
    hdr = f"  {'arm':<9}{'pages':>7}{'tokens':>11}{'links':>8}{'links/pg':>10}{'links/1k':>10}"
    print(hdr)
    for arm, m in rep["arms"].items():
        print(f"  {arm:<9}{m['n_pages']:>7}{m['total_tokens']:>11,}{m['n_wikilinks']:>8}"
              f"{m['links_per_page']:>10}{m['links_per_1k_tokens']:>10}")

    print("\nREAD (tokens to answer one query) + amortization:")
    hdr2 = (f"  {'arm':<9}{'read/q':>9}{'vs raw-all':>12}{'vs rag':>9}"
            f"{'breakeven(all)':>16}{'breakeven(rag)':>16}")
    print(hdr2)
    for arm, cmp in rep["comparisons"].items():
        be_all = cmp["break_even_queries_vs_raw_all"]
        be_rag = cmp["break_even_queries_vs_rag"]
        print(f"  {arm:<9}{cmp['read_per_query']:>9,}"
              f"{('%.1fx' % cmp['compression_vs_raw_all']) if cmp['compression_vs_raw_all'] else '-':>12}"
              f"{('%.1fx' % cmp['compression_vs_rag']) if cmp['compression_vs_rag'] else '-':>9}"
              f"{(str(be_all)) if be_all is not None else 'never':>16}"
              f"{(str(be_rag)) if be_rag is not None else 'never':>16}")
    print("\n(read/q = nav/index + one page. compression = raw-read / wiki-read. "
          "breakeven = queries until fill cost is repaid by per-query read savings.)")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Token-efficiency report for a BSB benchmark example.")
    ap.add_argument("example_dir", help="Path to a benchmark example dir (contains raw/, arm-*/wiki/).")
    ap.add_argument("--rag-k", type=int, default=3, help="Chunks a naive RAG baseline would retrieve (default 3).")
    ap.add_argument("--json", metavar="PATH", help="Also write the full report as JSON to PATH.")
    ap.add_argument("--md", action="store_true", help="Print as a markdown-friendly block (same content).")
    args = ap.parse_args(argv)

    example_dir = Path(args.example_dir).resolve()
    if not example_dir.is_dir():
        print(f"error: {example_dir} is not a directory", file=sys.stderr)
        return 2

    rep = build_report(example_dir, args.rag_k)
    print_human(rep)
    if args.json:
        Path(args.json).write_text(json.dumps(rep, indent=2), encoding="utf-8")
        print(f"\nWrote JSON: {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
