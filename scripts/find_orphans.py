#!/usr/bin/env python3
"""Find orphan wiki pages in a BSB (Better Second Brain) repo.

Walks ``wiki/**/*.md`` plus the root meta files (``index.md``, ``log.md``,
``roadmap.md``, ``CLAUDE.md``) and builds a map of every page's slug
(its repo-relative path without the ``.md`` extension) to the number of
inbound wikilinks pointing at it. It then prints a TSV with the columns

    rel_path    type    slug    inbound    outbound

sorted orphans-first (pages with ``inbound == 0`` come first), followed by a
per-type orphan-count summary. Pages reachable only from ``index`` or that are
themselves MOCs still have their inbound links counted normally.

Wikilinks are full-path style: ``[[wiki/concepts/slug]]`` or
``[[wiki/sources/slug|alias]]``; root meta links look like ``[[index]]``.
Anchors (``#...``) and aliases (``|...``) are stripped before matching.

Run from the repo root. Idempotent and read-only; exits 0 normally.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

# Root meta files (no folder, slug == stem).
META_FILES = ("index.md", "log.md", "roadmap.md", "CLAUDE.md")

# [[ target ]] capturing everything up to a closing ]] ; alias/anchor stripped later.
WIKILINK_RE = re.compile(r"\[\[([^\]]+?)\]\]")


def normalize_target(raw: str) -> str:
    """Strip an alias (``|...``) and anchor (``#...``) and surrounding whitespace.

    Also strips an accidental trailing ``.md`` so a sloppy link still resolves
    to the canonical slug.
    """
    target = raw.split("|", 1)[0]
    target = target.split("#", 1)[0]
    target = target.strip()
    target = target.replace("\\", "/")
    if target.lower().endswith(".md"):
        target = target[:-3]
    return target.strip("/")


def slug_for(path: Path, repo_root: Path) -> str:
    """Repo-relative POSIX path without the ``.md`` suffix."""
    rel = path.relative_to(repo_root).as_posix()
    if rel.lower().endswith(".md"):
        rel = rel[:-3]
    return rel


def type_for(slug: str) -> str:
    """Derive a page 'type' from its slug.

    ``wiki/concepts/x`` -> ``concepts``; ``wiki/cheatsheets/area/x`` ->
    ``cheatsheets``; a bare root file (``index``) -> ``meta``.
    """
    parts = slug.split("/")
    if parts[0] == "wiki" and len(parts) >= 2:
        return parts[1]
    return "meta"


def collect_pages(repo_root: Path) -> list[Path]:
    pages: list[Path] = []
    wiki_dir = repo_root / "wiki"
    if wiki_dir.is_dir():
        pages.extend(sorted(wiki_dir.rglob("*.md")))
    for name in META_FILES:
        meta = repo_root / name
        if meta.is_file():
            pages.append(meta)
    return pages


def parse_outbound(text: str) -> list[str]:
    """Return normalized link targets found in a page body."""
    targets: list[str] = []
    for match in WIKILINK_RE.finditer(text):
        norm = normalize_target(match.group(1))
        if norm:
            targets.append(norm)
    return targets


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Find orphan wiki pages (zero inbound wikilinks) in a BSB repo.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Repo root (default: current directory).",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Print only the per-type orphan summary, not the full TSV.",
    )
    args = parser.parse_args(argv)

    repo_root = args.root.resolve()
    pages = collect_pages(repo_root)

    # slug -> Path, and per-page outbound target lists.
    slug_to_path: dict[str, Path] = {}
    outbound: dict[str, list[str]] = {}
    inbound: dict[str, int] = defaultdict(int)

    for page in pages:
        slug = slug_for(page, repo_root)
        slug_to_path[slug] = page
        try:
            text = page.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            print(f"# warning: could not read {page}: {exc}", file=sys.stderr)
            outbound[slug] = []
            continue
        outbound[slug] = parse_outbound(text)

    # Tally inbound counts only for links whose target is a known page.
    for src_slug, targets in outbound.items():
        for target in targets:
            if target in slug_to_path and target != src_slug:
                inbound[target] += 1

    rows = []
    for slug in slug_to_path:
        rel_path = slug_to_path[slug].relative_to(repo_root).as_posix()
        rows.append(
            {
                "rel_path": rel_path,
                "type": type_for(slug),
                "slug": slug,
                "inbound": inbound.get(slug, 0),
                "outbound": len(outbound.get(slug, [])),
            }
        )

    # Orphans first (inbound == 0), then by inbound asc, then by slug.
    rows.sort(key=lambda r: (r["inbound"] != 0, r["inbound"], r["slug"]))

    if not args.quiet:
        print("rel_path\ttype\tslug\tinbound\toutbound")
        for r in rows:
            print(
                f"{r['rel_path']}\t{r['type']}\t{r['slug']}\t{r['inbound']}\t{r['outbound']}"
            )
        print()

    # Per-type orphan summary.
    orphan_by_type: dict[str, int] = defaultdict(int)
    total_by_type: dict[str, int] = defaultdict(int)
    for r in rows:
        total_by_type[r["type"]] += 1
        if r["inbound"] == 0:
            orphan_by_type[r["type"]] += 1

    total_orphans = sum(orphan_by_type.values())
    print(f"# orphan summary ({total_orphans} orphan(s) of {len(rows)} page(s))")
    for ptype in sorted(total_by_type):
        print(f"{ptype}\t{orphan_by_type.get(ptype, 0)} / {total_by_type[ptype]}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
