# Contributing to Better Second Brain

Thanks for being here. BSB is two things in one repo, and they're contributed to differently:

1. **The method** — the schema (`CLAUDE.md`), the page templates, the docs, and the tooling (`scripts/`). This is
   the reusable product. Improvements here help everyone who forks it.
2. **The seed wiki** (`wiki/`) — the example knowledge base that documents the second-brain pattern itself. It's
   maintained the BSB way: by an LLM agent, grounded in sources.

## Ground rule for any `wiki/` content

BSB has one inviolable rule (`CLAUDE.md` §1.5): **no wiki page may be written from a model's memory.** Every page is
grounded in **≥ 3 real, fetched sources** and cites them, or it isn't written. If you contribute or edit wiki
content, it must follow this — and the **lean fill** style (§2.1: compact source pages, cite-don't-restate, terse
dense links). PRs that add un-sourced prose will be asked to add citations.

## Good ways to contribute

- **Method/tooling:** sharper `scripts/` (lint, graph-sync, hygiene), better templates, clearer docs, new optional
  integrations. Bug fixes welcome.
- **Benchmarks:** the honest part of this project. New benchmark scenarios, a fairer scoring harness, or a
  **private/novel-corpus** run (the one test we haven't done — see `benchmark/RESULTS.md`).
- **Portability:** make the scripts / `init_brain.py` work cleanly on more setups (we develop on Windows; macOS/Linux
  reports and fixes are valued).
- **Docs & onboarding:** anything that makes a newcomer's first 60 seconds smoother.

Start with the [good first issues](https://github.com/maystudios/better-second-brain/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).

## Dev setup & checks

```bash
git clone https://github.com/maystudios/better-second-brain && cd better-second-brain
python --version   # 3.10+
# the gates that CI runs — keep them green:
python scripts/verify_wikilinks.py            # 0 broken wikilinks
python scripts/lint_sources.py --strict --strict-min-tier A --summary   # source-grade gate
python scripts/find_orphans.py --quiet
python -m py_compile scripts/*.py
```

- Scripts are **Python 3.10+, standard library only** (plus optional `tiktoken` for exact token counts). Keep them
  dependency-free and cross-platform.
- Keep `CLAUDE.md` **under ~200 lines** (it's an agent instruction file — longer = lower adherence; see §7). Put
  detail in `docs/` and reference it.

## PRs

- Branch, keep the diff focused, explain the *why*. End commits with a real description.
- If your change touches behavior an agent relies on, update the relevant `docs/` page too.
- Be honest in claims — this project's whole pitch is "measured, not asserted." Numbers beat adjectives.

## Conduct

Be kind and concrete. Assume good faith. No spam, no hype-for-hype's-sake.

MIT licensed — by contributing you agree your work is released under the same license.
