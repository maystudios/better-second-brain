#!/usr/bin/env python3
"""Initialize a Better Second Brain (BSB) from this template.

Reconfigures the schema for YOUR domain and (optionally) clears the bootstrap
seed content so you start from an empty, ready-to-fill brain. Deterministic and
safe: destructive actions require --yes (or an interactive confirm), and --dry-run
prints the plan without touching anything.

What it does:
  - sets the DOMAIN / LITMUS lines in CLAUDE.md (§0) and bsb.config.md
  - optionally sets the wikilink style in bsb.config.md
  - with --fresh: clears wiki/ seed pages, resets index.md / log.md / roadmap.md to
    empty skeletons, and removes the demo benchmark/ (keep it with --keep-benchmark)
  - git init (unless --no-git or already a repo) — never auto-commits
  - writes FIRST-RUN.md with the next steps

Examples:
  python scripts/init_brain.py --domain "Rust game engines" \
      --litmus "Does this help build a game engine in Rust?" --fresh --yes
  python scripts/init_brain.py --domain "My research topic" --dry-run
"""

from __future__ import annotations

import argparse
import datetime
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

WIKI_FOLDERS = ["sources", "concepts", "entities", "cheatsheets", "syntheses", "moc"]


class Planner:
    """Collects planned actions; applies them unless dry-run."""

    def __init__(self, dry_run: bool):
        self.dry_run = dry_run
        self.actions: list[str] = []

    def note(self, msg: str) -> None:
        self.actions.append(msg)

    def do(self, msg: str, fn) -> None:
        self.actions.append(msg)
        if not self.dry_run:
            fn()


def set_domain_litmus(text: str, domain: str | None, litmus: str | None) -> tuple[str, int]:
    """Update DOMAIN/LITMUS in BOTH the bare config form (``DOMAIN: x``) and the
    CLAUDE.md §0 prose form (``**Domain (this instance):** x`` / ``**Litmus:** x``).
    Returns (new_text, n_substitutions) so the caller can warn when nothing matched."""
    nchg = 0
    if domain is not None:
        for pat in (r"(?m)^(\s*DOMAIN:\s*).*$", r"(?m)^(\*\*Domain[^*\n]*\*\*\s*).*$"):
            text, n = re.subn(pat, lambda m: m.group(1) + domain, text)
            nchg += n
    if litmus is not None:
        # Keep the quotes convention used in the templates / §0.
        val = litmus if litmus.startswith('"') else f'"{litmus}"'
        for pat in (r"(?m)^(\s*LITMUS:\s*).*$", r"(?m)^(\*\*Litmus:\*\*\s*).*$"):
            text, n = re.subn(pat, lambda m, val=val: m.group(1) + val, text)
            nchg += n
    return text, nchg


def set_link_style(text: str, style: str) -> tuple[str, bool]:
    new, n = re.subn(r"(\|\s*link-style\s*\|\s*)`[^`]*`", lambda m: m.group(1) + f"`{style}`", text)
    return (new, bool(n))


def fresh_index(domain: str, today: str) -> str:
    return (
        "# Index\n\n"
        "The content catalog — *what exists* in this brain. Read this first on any query, then drill into pages.\n"
        "Grouped by category. (`log.md` = what happened; `roadmap.md` = what's next.)\n\n"
        "## Overview\n\n"
        f"_Empty — this brain was initialized {today} for: **{domain}**. "
        "Drop sources into `raw/` and say \"ingest\"._\n\n"
        "## Sources\n\n## Concepts\n\n## Entities\n\n## Cheatsheets\n\n## Syntheses\n\n## Maps of Content\n\n"
        "## Stats\n\n"
        f"- Pages: 0 wiki. Initialized {today}.\n"
    )


def fresh_log(domain: str, today: str) -> str:
    return (
        "# Log\n\n"
        "Append-only chronological record of every operation. Newest entries at the **bottom**.\n"
        "Greppable prefix — recent activity: `grep \"^## \\[\" log.md | tail -10`.\n\n"
        "Ops: `ingest` · `query` · `lint` · `graph` · `improve` · `heal` · `schema`.\n\n---\n\n"
        f"## [{today}] schema | Initialized brain from the BSB template\n\n"
        f"Domain set to: {domain}. Bootstrap seed content cleared. Ready for the first ingest.\n"
    )


def fresh_roadmap(domain: str, today: str) -> str:
    return (
        "# Roadmap\n\n"
        "What's next for this brain. `index.md` = what exists, `log.md` = what happened, **this** = what's next.\n\n"
        "---\n\n## In Progress\n\n- (nothing yet)\n\n## Backlog — High\n\n"
        "- [ ] **Ingest**: add your first sources to `raw/` and ingest them\n"
        "- [ ] **Schema**: refine `CLAUDE.md` §0 (IN / OUT / litmus) for your domain\n\n"
        "## Open Questions\n\n## Recently Done\n\n"
        f"- {today} — initialized from the BSB template for **{domain}**.\n"
    )


def first_run(domain: str, litmus: str | None, layers: list[str], today: str) -> str:
    layer_line = ", ".join(layers) if layers else "none (all optional layers off — enable later)"
    lit = litmus or "(set your litmus test in CLAUDE.md §0)"
    return (
        "# First run — your Better Second Brain is ready\n\n"
        f"- **Domain:** {domain}\n- **Litmus:** {lit}\n- **Layers chosen:** {layer_line}\n"
        f"- **Initialized:** {today}\n\n"
        "## Next steps\n\n"
        "1. Open this folder **as a vault in Obsidian** and **in Claude Code / Codex** (the agent reads `CLAUDE.md`).\n"
        "2. Double-check `CLAUDE.md` §0 (IN / OUT / litmus) and `bsb.config.md` fit your topic.\n"
        "3. **Add a source** — drop a file into `raw/`, or tell the agent *\"ingest https://…\"*.\n"
        "4. **Ask** — *\"what does the wiki say about X?\"* — and let good answers be filed back as pages.\n"
        "5. Periodically say **\"lint\"**; run `python scripts/lint_sources.py --summary` and `verify_wikilinks.py`.\n\n"
        "## Optional layers\n\n"
        "- **graphify** (graph): `uv tool install graphifyy`, then use the `/graphify` skill. See `docs/graphify-integration.md`.\n"
        "- **qmd** (search): `npm i -g @tobilu/qmd`. See README.\n"
        "- **git hooks** (gate): `git config core.hooksPath .githooks`.\n\n"
        "_Delete this file once you're set up._\n"
    )


def clear_wiki(root: Path, planner: Planner) -> None:
    wiki = root / "wiki"
    md = sorted(wiki.rglob("*.md")) if wiki.is_dir() else []
    if md:
        planner.do(f"delete {len(md)} seed wiki page(s) under wiki/",
                   lambda files=md: [f.unlink() for f in files])
    # Ensure the canonical folders exist with a .gitkeep so the structure is tracked.
    for folder in WIKI_FOLDERS:
        d = wiki / folder
        planner.do(f"ensure wiki/{folder}/.gitkeep",
                   lambda d=d: (d.mkdir(parents=True, exist_ok=True),
                                (d / ".gitkeep").write_text("", encoding="utf-8")))
    # Remove now-empty nested subdirs (e.g. cheatsheets/<area>/).
    if wiki.is_dir() and not planner.dry_run:
        for dirpath, dirnames, filenames in os.walk(wiki, topdown=False):
            p = Path(dirpath)
            if p == wiki or p.name in WIKI_FOLDERS:
                continue
            if not any(p.iterdir()):
                p.rmdir()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Initialize a Better Second Brain from this template.")
    ap.add_argument("--domain", help='Your brain\'s domain, e.g. "Rust game engines".')
    ap.add_argument("--litmus", help='One-line in/out test, e.g. "Does this help build a game engine?".')
    ap.add_argument("--name", help="Optional display name (informational).")
    ap.add_argument("--link-style", choices=["full-path", "bare-slug"], help="Wikilink style for bsb.config.md.")
    ap.add_argument("--layers", default="", help="Comma list of optional layers to note as chosen (graphify,qmd).")
    ap.add_argument("--fresh", action="store_true", help="Clear bootstrap seed content for an empty brain.")
    ap.add_argument("--keep-benchmark", action="store_true", help="With --fresh, keep the demo benchmark/ dir.")
    ap.add_argument("--no-git", action="store_true", help="Do not run git init.")
    ap.add_argument("--yes", action="store_true", help="Confirm destructive actions non-interactively.")
    ap.add_argument("--dry-run", action="store_true", help="Print the plan; change nothing.")
    ap.add_argument("--root", default=".", help="Repo root (default: current directory).")
    args = ap.parse_args(argv)

    root = Path(args.root).resolve()
    if not (root / "CLAUDE.md").is_file():
        print(f"error: {root} does not look like a BSB repo (no CLAUDE.md).", file=sys.stderr)
        return 2

    layers = [s.strip() for s in args.layers.split(",") if s.strip()]
    today = datetime.date.today().isoformat()

    # Safety gate for destructive --fresh.
    if args.fresh and not args.dry_run and not args.yes:
        if sys.stdin.isatty():
            resp = input("--fresh deletes all seed wiki pages and the demo benchmark/. Continue? [y/N] ")
            if resp.strip().lower() not in ("y", "yes"):
                print("aborted.")
                return 1
        else:
            print("refusing --fresh without --yes (non-interactive). Re-run with --yes or --dry-run.",
                  file=sys.stderr)
            return 2

    planner = Planner(args.dry_run)

    # 1) Reconfigure schema files.
    if args.domain or args.litmus:
        for rel in ("CLAUDE.md", "bsb.config.md"):
            p = root / rel
            if not p.is_file():
                continue
            text = p.read_text(encoding="utf-8")
            new, nchg = set_domain_litmus(text, args.domain, args.litmus)
            if nchg:
                planner.do(f"update DOMAIN/LITMUS in {rel} ({nchg} line(s))",
                           lambda p=p, new=new: p.write_text(new, encoding="utf-8"))
            else:
                planner.note(f"WARNING: no DOMAIN/LITMUS lines matched in {rel} — set §0 by hand")
    if args.link_style:
        p = root / "bsb.config.md"
        if p.is_file():
            new, changed = set_link_style(p.read_text(encoding="utf-8"), args.link_style)
            if changed:
                planner.do(f"set link-style = {args.link_style} in bsb.config.md",
                           lambda p=p, new=new: p.write_text(new, encoding="utf-8"))

    # 2) Fresh: clear seed content + reset meta-docs + drop demo benchmark.
    if args.fresh:
        clear_wiki(root, planner)
        domain = args.domain or "(set your domain in CLAUDE.md §0)"
        planner.do("reset index.md to empty skeleton",
                   lambda: (root / "index.md").write_text(fresh_index(domain, today), encoding="utf-8"))
        planner.do("reset log.md to a fresh init entry",
                   lambda: (root / "log.md").write_text(fresh_log(domain, today), encoding="utf-8"))
        planner.do("reset roadmap.md to a fresh backlog",
                   lambda: (root / "roadmap.md").write_text(fresh_roadmap(domain, today), encoding="utf-8"))
        bench = root / "benchmark"
        if bench.is_dir() and not args.keep_benchmark:
            planner.do("remove demo benchmark/ (use --keep-benchmark to keep)",
                       lambda: shutil.rmtree(bench))

    # 3) git init (never auto-commit).
    if not args.no_git and not (root / ".git").exists():
        def _git_init():
            try:
                subprocess.run(["git", "init", "-b", "main"], cwd=root, check=False,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except (OSError, FileNotFoundError):
                pass
        planner.do("git init -b main (no commit)", _git_init)

    # 4) First-run checklist.
    domain = args.domain or "your domain"
    planner.do("write FIRST-RUN.md",
               lambda: (root / "FIRST-RUN.md").write_text(
                   first_run(domain, args.litmus, layers, today), encoding="utf-8"))

    # Report.
    head = "PLAN (dry-run, nothing changed):" if args.dry_run else "Initialized Better Second Brain:"
    print(head)
    for i, a in enumerate(planner.actions, 1):
        print(f"  {i:>2}. {a}")
    if not planner.actions:
        print("  (nothing to do — pass --domain/--litmus/--fresh)")
    if args.dry_run:
        print("\nRe-run without --dry-run (add --yes for --fresh) to apply.")
    else:
        print(f"\nDone. Domain: {domain}. See FIRST-RUN.md for next steps.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
