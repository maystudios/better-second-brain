#!/usr/bin/env python3
"""Deterministic method-mutation levers + measurement for the BSB RSI loop.

The RSI loop (docs/rsi-loop.md) mutates the *method* and re-measures. To run forward
experiments REPRODUCIBLY - without an LLM hand-editing pages non-deterministically -
this script applies named, deterministic **levers** to a copy of a wiki, then measures
the result. It is the "build a candidate `train.py` and run the 5-minute experiment"
step, made repeatable.

A lever approximates "what the corpus would look like if it had been written under a
changed fill/format policy". It is a proxy (the real change is to CLAUDE.md), but a
deterministic, inspectable one.

Levers (apply to a wiki dir; operate on the lean-arm structure):
  drop-links              - strip the trailing "## Links" footer from every page (redundant
                            with inline citations). Small token cut, citations preserved.
  strip-frontmatter       - reduce frontmatter to type/title/url only. Minor token cut.
  merge-sources           - delete wiki/sources/* and remove [[sources/...]] citations from
                            concepts. Big token cut, but the cited source URLs vanish ->
                            citation coverage drops. The "bold, worse-now" candidate.
  merge-sources-keep-urls - like merge-sources, but first inline each source's url into the
                            citing concept, so coverage survives. The stepping-stone payoff.

Quality proxy (deterministic, Goodhart-resistant - anchored to external facts, not an LLM
self-score): citation_coverage = fraction of the gold questions whose `source` URL still
appears anywhere in the candidate wiki. Token cost via token_report.measure_arm.

Usage:
  python scripts/rsi_transforms.py build --lever merge-sources \\
      --base benchmark/large/arm-bsb-lean/wiki --out /tmp/cand/wiki
  python scripts/rsi_transforms.py measure --wiki /tmp/cand/wiki \\
      --questions benchmark/large/questions.json [--json out.json]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import stat
import sys
from pathlib import Path


def _robust_rmtree(path: Path) -> None:
    """Remove a tree, tolerating Windows read-only attrs / transient handle locks."""
    if not path.exists():
        return

    def onexc(func, p, exc):
        try:
            os.chmod(p, stat.S_IWRITE)
            func(p)
        except OSError:
            pass

    for _ in range(10):
        try:
            shutil.rmtree(path, onexc=onexc)        # Python 3.12+
        except TypeError:
            shutil.rmtree(path, onerror=lambda f, p, e: onexc(f, p, e))  # older
        except OSError:
            pass
        if not path.exists():
            return
    raise SystemExit(f"error: could not remove {path} (Windows lock); delete it manually and retry.")

SCRIPT_DIR = Path(__file__).resolve().parent
SRC_LINK_RE = re.compile(r"\[\[sources/([^\]\|]+?)(?:\|[^\]]*)?\]\]")
LINKS_FOOTER_RE = re.compile(r"\n##\s+Links\b.*?(?=\n##\s|\Z)", re.S)
FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)
URL_FM_RE = re.compile(r"^url:\s*(\S+)", re.M)


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def write(p: Path, s: str) -> None:
    p.write_text(s, encoding="utf-8")


def md_files(wiki: Path) -> list[Path]:
    return sorted(p for p in wiki.rglob("*.md") if p.is_file())


def source_url_map(wiki: Path) -> dict[str, str]:
    """slug -> url, read from each wiki/sources/*.md frontmatter `url:`."""
    out: dict[str, str] = {}
    sdir = wiki / "sources"
    if not sdir.is_dir():
        return out
    for p in sorted(sdir.glob("*.md")):
        fm = FM_RE.search(read(p))
        if fm:
            m = URL_FM_RE.search(fm.group(1))
            if m:
                out[p.stem] = m.group(1)
    return out


def _strip_links_footer(text: str) -> str:
    return LINKS_FOOTER_RE.sub("", text).rstrip() + "\n"


def lever_drop_links(wiki: Path) -> None:
    for p in md_files(wiki):
        write(p, _strip_links_footer(read(p)))


def lever_strip_frontmatter(wiki: Path) -> None:
    keep = ("type:", "title:", "url:")
    for p in md_files(wiki):
        text = read(p)
        m = FM_RE.search(text)
        if not m:
            continue
        kept = [ln for ln in m.group(1).splitlines() if ln.strip().startswith(keep)]
        new_fm = "---\n" + "\n".join(kept) + "\n---\n"
        write(p, new_fm + text[m.end():])


def _clean_citation_artifacts(text: str) -> str:
    # Tidy parens/middots left after removing [[sources/...]] links.
    text = re.sub(r"\(\s*(?:,\s*)*\)", "", text)          # empty ()
    text = re.sub(r"\(\s*,", "(", text)                    # leading comma
    text = re.sub(r",\s*\)", ")", text)                    # trailing comma
    text = re.sub(r"·(\s*·)+", "·", text)                  # collapsed middots
    text = re.sub(r"[ \t]+\n", "\n", text)
    return text


def lever_merge_sources(wiki: Path, mode: str) -> None:
    """Delete source pages; handle their [[sources/...]] citations per `mode`:
       strip   - remove inline citations (coverage lost; the bold/worse candidate)
       inline  - replace each citation with its full URL (coverage kept, but repeated -> bloat)
       compact - remove inline citations, append one '## Sources' block of distinct URLs per
                 page (coverage kept, each URL once -> low bloat; the stepping-stone payoff)."""
    urls = source_url_map(wiki)
    for p in md_files(wiki):
        if (wiki / "sources") in p.parents:
            continue  # source pages are being removed
        text = read(p)
        if mode == "inline":
            text = SRC_LINK_RE.sub(lambda m: urls.get(m.group(1), ""), text)
            text = _clean_citation_artifacts(text)
        elif mode == "compact":
            cited: list[str] = []

            def _rec(m):
                slug = m.group(1)
                if slug not in cited:
                    cited.append(slug)
                return ""
            text = _clean_citation_artifacts(SRC_LINK_RE.sub(_rec, text))
            refs = list(dict.fromkeys(u for s in cited if (u := urls.get(s))))
            if refs:
                text = text.rstrip() + "\n\n## Sources\n" + "\n".join(f"- {u}" for u in refs) + "\n"
        else:  # strip
            text = _clean_citation_artifacts(SRC_LINK_RE.sub("", text))
        write(p, text)
    # Remove the source PAGES (an empty sources/ dir is harmless - measurement globs *.md).
    sdir = wiki / "sources"
    if sdir.is_dir():
        for sp in sdir.glob("*.md"):
            try:
                sp.unlink()
            except OSError:
                pass
        try:
            sdir.rmdir()
        except OSError:
            pass  # Windows may keep the (now-empty) dir handle briefly; harmless


LEVERS = {
    "drop-links": lambda w: lever_drop_links(w),
    "strip-frontmatter": lambda w: lever_strip_frontmatter(w),
    "merge-sources": lambda w: lever_merge_sources(w, mode="strip"),
    "merge-sources-keep-urls": lambda w: lever_merge_sources(w, mode="inline"),
    "merge-sources-compact": lambda w: lever_merge_sources(w, mode="compact"),
}


def build(lever: str, base: Path, out: Path) -> None:
    # A lever may be a comma-separated CHAIN, applied in order - this is recombination
    # ("combine near-misses": stack a KEEP onto a big EXPLORE to test a building-block hypothesis).
    chain = [p.strip() for p in lever.split(",") if p.strip()]
    unknown = [p for p in chain if p not in LEVERS]
    if unknown:
        raise SystemExit(f"error: unknown lever(s) {unknown}. Choices: {', '.join(LEVERS)}")
    _robust_rmtree(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(base, out)
    for p in chain:
        LEVERS[p](out)


def measure(wiki: Path, questions: Path) -> dict:
    sys.path.insert(0, str(SCRIPT_DIR))
    from token_report import make_tokenizer, measure_arm  # type: ignore
    count, tok_name = make_tokenizer()
    m = measure_arm(wiki, count)
    if m is None:
        raise SystemExit(f"error: no markdown pages under {wiki}")

    # Deterministic quality proxy: gold-source-URL citation coverage.
    qdata = json.loads(read(questions))
    gold_urls = [q.get("source", "") for q in qdata.get("questions", []) if q.get("source")]
    blob = "\n".join(read(p) for p in md_files(wiki))
    present = sum(1 for u in gold_urls if u and u in blob)
    coverage = round(present / len(gold_urls), 4) if gold_urls else None

    return {
        "wiki": str(wiki),
        "tokenizer": tok_name,
        "n_pages": m["n_pages"],
        "fill_tokens": m["total_tokens"],
        "read_per_query": m["read_per_query"],
        "n_wikilinks": m["n_wikilinks"],
        "links_per_1k": m["links_per_1k_tokens"],
        "gold_questions": len(gold_urls),
        "citation_coverage": coverage,
        "citations_present": present,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Deterministic RSI method-mutation levers + measurement.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="apply a lever (or comma-separated chain) to a copy of a wiki")
    b.add_argument("--lever", required=True, help=f"one of {sorted(LEVERS)} or a comma-separated chain")
    b.add_argument("--base", required=True)
    b.add_argument("--out", required=True)

    me = sub.add_parser("measure", help="measure tokens + deterministic citation coverage")
    me.add_argument("--wiki", required=True)
    me.add_argument("--questions", required=True)
    me.add_argument("--json", metavar="PATH")

    args = ap.parse_args(argv)

    if args.cmd == "build":
        build(args.lever, Path(args.base).resolve(), Path(args.out).resolve())
        print(f"built lever '{args.lever}' -> {args.out}")
        return 0

    rep = measure(Path(args.wiki).resolve(), Path(args.questions).resolve())
    print(f"# measure {rep['wiki']}  (tokenizer: {rep['tokenizer']})")
    print(f"  pages={rep['n_pages']}  fill_tokens={rep['fill_tokens']:,}  read/q={rep['read_per_query']:,}"
          f"  links={rep['n_wikilinks']}")
    print(f"  citation_coverage={rep['citation_coverage']} "
          f"({rep['citations_present']}/{rep['gold_questions']} gold source URLs present)")
    if args.json:
        Path(args.json).write_text(json.dumps(rep, indent=2), encoding="utf-8")
        print(f"  wrote {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
