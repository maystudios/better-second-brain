#!/usr/bin/env python3
"""Scaffold a new wiki page from a template in a BSB (Better Second Brain) repo.

Usage:
    new_page.py <type> <slug> [--title "Nice Title"] [--area <area>]

Copies ``templates/<type>.md`` into the correct ``wiki/`` folder:

  * ``cheatsheet``  -> ``wiki/cheatsheets/<area>/<slug>.md`` (``--area`` required)
  * everything else -> ``wiki/<type-plural>/<slug>.md``
        e.g. ``concept`` -> ``wiki/concepts/<slug>.md``
             ``source``  -> ``wiki/sources/<slug>.md``
             ``entity``  -> ``wiki/entities/<slug>.md``
             ``moc``     -> ``wiki/moc/<slug>.md``

Substitutes ``{{title}}`` (from ``--title`` or a Title-Cased slug) and
``{{date:YYYY-MM-DD}}`` (today, via ``datetime.date.today()``) in the template
body. Refuses to overwrite an existing file. Prints the path created.

Slugs must be kebab-case ASCII and equal the filename. Run from the repo root.
"""

from __future__ import annotations

import argparse
import datetime
import re
import sys
from pathlib import Path

# Map a singular type to its plural wiki folder. Types not listed here default
# to ``<type>s`` (e.g. an unknown ``thing`` -> ``things``).
TYPE_FOLDER = {
    "concept": "concepts",
    "source": "sources",
    "entity": "entities",
    "moc": "moc",
    "cheatsheet": "cheatsheets",
}

DATE_TOKEN_RE = re.compile(r"\{\{date:YYYY-MM-DD\}\}")
TITLE_TOKEN_RE = re.compile(r"\{\{title\}\}")

KEBAB_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def folder_for(page_type: str) -> str:
    return TYPE_FOLDER.get(page_type, page_type + "s")


def title_from_slug(slug: str) -> str:
    return " ".join(word.capitalize() for word in slug.split("-") if word)


def substitute(text: str, title: str, today: str) -> str:
    text = TITLE_TOKEN_RE.sub(lambda _m: title, text)
    text = DATE_TOKEN_RE.sub(lambda _m: today, text)
    return text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Scaffold a new BSB wiki page from templates/<type>.md.",
    )
    parser.add_argument("type", help="Page type, e.g. concept, source, entity, moc, cheatsheet.")
    parser.add_argument("slug", help="Kebab-case ASCII slug; becomes the filename.")
    parser.add_argument("--title", help="Human title; defaults to a Title-Cased slug.")
    parser.add_argument(
        "--area",
        help="Sub-area folder, required for cheatsheet type (wiki/cheatsheets/<area>/).",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="Repo root (default: current directory).",
    )
    args = parser.parse_args(argv)

    repo_root = args.root.resolve()
    page_type = args.type.strip().lower()
    slug = args.slug.strip()

    if not KEBAB_RE.match(slug):
        print(
            f"error: slug {slug!r} is not kebab-case ASCII "
            "(lowercase letters/digits separated by single hyphens).",
            file=sys.stderr,
        )
        return 2

    template = repo_root / "templates" / f"{page_type}.md"
    if not template.is_file():
        print(f"error: template not found: {template}", file=sys.stderr)
        return 2

    if page_type == "cheatsheet":
        if not args.area:
            print("error: --area is required for cheatsheet pages.", file=sys.stderr)
            return 2
        area = args.area.strip()
        if not KEBAB_RE.match(area):
            print(
                f"error: area {area!r} is not kebab-case ASCII.",
                file=sys.stderr,
            )
            return 2
        dest = repo_root / "wiki" / "cheatsheets" / area / f"{slug}.md"
    else:
        dest = repo_root / "wiki" / folder_for(page_type) / f"{slug}.md"

    if dest.exists():
        print(f"error: refusing to overwrite existing file: {dest}", file=sys.stderr)
        return 1

    title = args.title.strip() if args.title else title_from_slug(slug)
    today = datetime.date.today().isoformat()

    try:
        raw = template.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        print(f"error: could not read template {template}: {exc}", file=sys.stderr)
        return 2

    content = substitute(raw, title, today)

    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding="utf-8")

    print(dest.relative_to(repo_root).as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
