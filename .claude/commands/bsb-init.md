---
description: Initialize a fresh Better Second Brain from this template (guided)
argument-hint: [domain] — optional; the command will ask if omitted
---

You are initializing a **Better Second Brain (BSB)** in this repository. Work through these steps, asking the user
only for what is missing. Be concise.

## 1. Gather two inputs
- **Domain** — what this brain is about (e.g. "Rust game engines", "EU privacy law", "my PhD on X"). If the user
  passed it as `$ARGUMENTS`, use that; otherwise ask.
- **Litmus** — a one-line in/out test (e.g. "Does this help build a game engine in Rust?"). Ask if not given.

Also confirm (with sensible defaults): clear the demo seed pages? (**`--fresh` = yes, recommended** for a real
brain) and which optional layers to note — graphify / qmd / none.

## 2. Run the scaffolder
Optionally show `--dry-run` first if the user is unsure. Then run (substitute the answers; include `--fresh --yes`
only when starting an empty brain):

    python scripts/init_brain.py --domain "<DOMAIN>" --litmus "<LITMUS>" --link-style full-path --layers <layers> --fresh --yes

## 3. Verify
Run `python scripts/verify_wikilinks.py` and `python scripts/lint_sources.py --summary`. Both should be clean on a
fresh, empty brain.

## 4. Read the schema and take over
Read `CLAUDE.md` — from now on you are the **maintainer** of this brain and must follow it, especially the
research-discipline gate (§1.5 — never write a page from memory; ground every page in ≥ 3 fetched sources) and lean
fill (§2.1 — compact source pages, cite-don't-restate, terse dense links).

## 5. Hand off
Tell the user the brain is ready, point them to `FIRST-RUN.md`, and ask for their first source (a URL or file) to
ingest into `raw/`. The user curates; you read, verify, file, and cross-reference.
