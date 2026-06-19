#!/usr/bin/env python3
"""Verify wikilink targets in a Better Second Brain (BSB) repo.

Scans ``[[link]]`` targets and reports three categories of problems:

  (a) BROKEN     - the target file does not exist (under any case).
  (b) CASE       - the target exists only under a different case (kebab/case
                   mismatch); a cross-platform footgun on case-sensitive hosts.
  (c) MD-SUFFIX  - the link wrongly includes a ``.md`` suffix.

Wikilinks are full-path style: ``[[wiki/concepts/slug]]`` or
``[[wiki/sources/slug|alias]]``; root links look like ``[[index]]``. Anchors
(``#...``) and aliases (``|...``) are stripped before resolving.

SCOPE. By default only *content* files are checked: ``wiki/**/*.md`` plus
``index.md`` (the catalog). Schema/docs/meta files (CLAUDE.md, README.md,
roadmap.md, docs/...) legitimately contain illustrative ``[[slug]]`` examples,
so they are NOT gated by default. Pass ``--all`` to scan every markdown file.
Either way, links inside inline code (`` `...` ``) and fenced code blocks are
ignored so documentation examples never trip the gate.

The *resolvable* page set always includes every wiki page plus the root-level
markdown files, so real cross-links such as ``[[index]]`` or ``[[CLAUDE]]``
resolve regardless of scope.

Exits non-zero when any BROKEN links exist so it can gate CI. Pass
``--fix-md-suffix`` to strip accidental ``.md`` suffixes in place (idempotent).

Run from the repo root.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Directories never scanned and never used as link targets.
EXCLUDE_DIRS = {".git", ".obsidian", "node_modules", "__pycache__", ".trash"}

WIKILINK_RE = re.compile(r"\[\[([^\]]+?)\]\]")
FENCED_RE = re.compile(r"```.*?```|~~~.*?~~~", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)


def strip_code(text: str) -> str:
    """Remove anything that may hold *example* wikilinks rather than real ones:
    fenced code blocks, inline code spans, HTML comments, and YAML-frontmatter
    ``#`` comments. Template scaffolds (e.g. ``new_page.py`` output) carry example
    links inside comments — those must not be reported as broken.
    """
    # Strip `#` comments inside the leading YAML frontmatter block only.
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = re.sub(r"(?m)#.*$", "", text[:end]) + text[end:]
    text = HTML_COMMENT_RE.sub("", text)
    text = FENCED_RE.sub("", text)
    text = INLINE_CODE_RE.sub("", text)
    return text


def split_target(raw: str) -> tuple[str, bool]:
    """Return (normalized_slug, had_md_suffix)."""
    target = raw.split("|", 1)[0]
    target = target.split("#", 1)[0]
    target = target.strip().replace("\\", "/")
    had_md = target.lower().endswith(".md")
    if had_md:
        target = target[:-3]
    return target.strip("/"), had_md


def _iter_md(repo_root: Path):
    for path in repo_root.rglob("*.md"):
        if any(part in EXCLUDE_DIRS for part in path.relative_to(repo_root).parts):
            continue
        yield path


def resolvable_pages(repo_root: Path) -> list[Path]:
    """Every page a wikilink may legitimately point at: all wiki/ pages plus
    root-level markdown files (index, log, roadmap, CLAUDE, README, ...)."""
    pages: list[Path] = []
    wiki_dir = repo_root / "wiki"
    if wiki_dir.is_dir():
        pages.extend(sorted(wiki_dir.rglob("*.md")))
    pages.extend(sorted(repo_root.glob("*.md")))
    return pages


def scan_targets(repo_root: Path, scan_all: bool) -> list[Path]:
    """Files whose links are actually verified."""
    if scan_all:
        return list(_iter_md(repo_root))
    targets: list[Path] = []
    wiki_dir = repo_root / "wiki"
    if wiki_dir.is_dir():
        targets.extend(sorted(wiki_dir.rglob("*.md")))
    index = repo_root / "index.md"
    if index.is_file():
        targets.append(index)
    return targets


def build_index(repo_root: Path) -> tuple[set[str], dict[str, str]]:
    exact: set[str] = set()
    lower_map: dict[str, str] = {}
    for page in resolvable_pages(repo_root):
        rel = page.relative_to(repo_root).as_posix()
        if rel.lower().endswith(".md"):
            rel = rel[:-3]
        exact.add(rel)
        lower_map.setdefault(rel.lower(), rel)
    return exact, lower_map


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Verify wikilink targets (broken / case / .md-suffix) in a BSB repo.",
    )
    parser.add_argument("--root", type=Path, default=Path("."),
                        help="Repo root (default: current directory).")
    parser.add_argument("--all", action="store_true", dest="scan_all",
                        help="Scan every markdown file, not just wiki/ + index.md.")
    parser.add_argument("--fix-md-suffix", action="store_true",
                        help="Strip accidental '.md' suffixes from wikilink targets in place.")
    args = parser.parse_args(argv)

    repo_root = args.root.resolve()
    exact, lower_map = build_index(repo_root)
    targets = scan_targets(repo_root, args.scan_all)

    broken: list[tuple[str, str]] = []
    case_mismatch: list[tuple[str, str, str]] = []
    md_suffix: list[tuple[str, str]] = []

    for page in targets:
        src_rel = page.relative_to(repo_root).as_posix()
        try:
            text = page.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            print(f"# warning: could not read {page}: {exc}", file=sys.stderr)
            continue

        scan_text = strip_code(text)
        for match in WIKILINK_RE.finditer(scan_text):
            inner = match.group(1)
            slug, had_md = split_target(inner)
            if not slug:
                continue
            if had_md:
                md_suffix.append((src_rel, inner))
            if slug in exact:
                continue
            canonical = lower_map.get(slug.lower())
            if canonical is not None:
                case_mismatch.append((src_rel, slug, canonical))
            else:
                broken.append((src_rel, slug))

        if args.fix_md_suffix:
            def _strip(m: re.Match[str]) -> str:
                inner = m.group(1)
                left, anchor, alias = inner, "", ""
                if "|" in left:
                    left, alias = left.split("|", 1)
                    alias = "|" + alias
                if "#" in left:
                    left, anchor = left.split("#", 1)
                    anchor = "#" + anchor
                if left.rstrip().lower().endswith(".md"):
                    left = left.rstrip()[:-3]
                return "[[" + left + anchor + alias + "]]"

            new_text = WIKILINK_RE.sub(_strip, text)
            if new_text != text:
                page.write_text(new_text, encoding="utf-8")

    print("== Wikilink verification report ==")
    print(f"  scope: {'all markdown' if args.scan_all else 'wiki/ + index.md'}  "
          f"({len(targets)} file(s), {len(exact)} resolvable pages)")
    print()

    print(f"[MD-SUFFIX] {len(md_suffix)} link(s) include a '.md' suffix")
    for src, inner in md_suffix:
        print(f"  {src}: [[{inner}]]")
    print()

    print(f"[CASE] {len(case_mismatch)} link(s) match only under a different case")
    for src, slug, canonical in case_mismatch:
        print(f"  {src}: [[{slug}]] -> exists as [[{canonical}]]")
    print()

    print(f"[BROKEN] {len(broken)} link(s) point at a missing page")
    for src, slug in broken:
        print(f"  {src}: [[{slug}]]")
    print()

    if args.fix_md_suffix:
        print("# --fix-md-suffix applied; re-run to confirm a clean MD-SUFFIX list.")

    if broken:
        print(f"# FAIL: {len(broken)} broken link(s) found.", file=sys.stderr)
        return 1

    print("# OK: no broken links.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
