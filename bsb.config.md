---
type: config
title: BSB instance config
updated: 2026-06-19
---

# bsb.config.md — per-instance configuration

This file holds the few choices that differ between BSB forks. The schema (`CLAUDE.md`) reads these as the
authoritative settings for *this* instance. Edit here, not in the schema.

## Domain

```
DOMAIN:   Software / tech reference + the "second brain" / LLM-wiki pattern
LITMUS:   "Does this help someone build software, or build/understand a better second brain?"
```

(The full IN / OUT / litmus block lives in `CLAUDE.md` §0. Keep them in sync.)

## Conventions

| setting | value | notes |
|---------|-------|-------|
| link-style | `full-path` | `[[wiki/concepts/x]]` — unambiguous, survives moves. Alt: `bare-slug`. |
| wiki body language | follows source | frontmatter keys stay English |
| chat language | follows user | currently German |
| source floor | `3` | min verified sources per reference/cheatsheet page (§1.5) |
| cheatsheet length | `150–500` lines | split if longer, merge if shorter |
| lint tier gate | `A` (CI) / `B` (local pre-commit) | `scripts/lint_sources.py --strict` |
| self-heal autonomy | `2` (fix-and-report on approval) | per-area override allowed (§3.6) |

## Optional layers (off by default, degrade gracefully)

| layer | status | enable with |
|-------|--------|-------------|
| graphify (graph) | available as `/graphify` skill | `uv tool install graphifyy` for the CLI; see `docs/graphify-integration.md` |
| auto-research (improve) | available as skill | see `docs/auto-research-integration.md` |
| qmd (retrieval) | not installed | `npm i -g @tobilu/qmd`; add when > ~100 sources |
| git hooks (gate) | present, opt-in | `git config core.hooksPath .githooks` |
