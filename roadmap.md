# Roadmap

What's next for this brain. `index.md` = what exists, `log.md` = what happened, **this** = what's next.
Items: `- [ ] **<Type>**: <slug> — <reason>`. Types: Ingest · Cheatsheet · Concept · Synthesis · Schema · Tooling · Heal.

---

## In Progress

- [x] **Schema**: bootstrap BSB (CLAUDE.md, meta-docs, .obsidian, packaging) — done 2026-06-19
- [ ] **Tooling**: finalize `index.md` from the seeded page set

## Backlog — High

- [ ] **Tooling**: install graphify (`uv tool install graphifyy`) and run the first `/graphify .` build;
      wire `scripts/graphify_sync.py` into the lint loop (§3.4)
- [ ] **Tooling**: dry-run `scripts/lint_sources.py` and `find_orphans.py` against the seed pages; fix any orphans
- [ ] **Synthesis**: flesh out `wiki/syntheses/is-bsb-better-than-vanilla-llm-wiki` with the benchmark protocol
      from `docs/benchmark.md` and a first scored run
- [ ] **Improve**: run the `auto-research` skill against `CLAUDE.md` once content exists, to validate the
      self-improvement loop end-to-end (§3.5)
- [ ] **Heal**: first self-heal pass — re-verify the seed source pages' URLs are still live and current (§3.6)

## Backlog — Lower

- [ ] **Ingest**: expand the bootstrap domain — NotebookLM vs wiki (unverified in research), GraphRAG papers,
      more Obsidian-Bases primary docs
- [ ] **Tooling**: add `qmd` retrieval layer once the brain passes ~100 sources
- [ ] **Cheatsheet**: add real software-reference cheatsheets once a target stack is chosen (the shipped domain
      is reference-capable but currently seeded only with second-brain/PKM content)
- [ ] **Schema**: optional — `.githooks` pre-commit + CI gate are present but opt-in; decide whether to enable

## Open Questions  *(seed the query loop — graphify will add more)*

- Does BSB measurably beat a vanilla Karpathy wiki on correctness + citation quality + freshness? (→ benchmark)
- At what corpus size does `index.md` stop fitting one context window, and what's the shard strategy?
- Which self-heal corrections are safe to fully automate (level 3) vs. always review?

## Recently Done

- 2026-06-19 — repo bootstrapped; schema + packaging + Obsidian baseline + seed content scaffolded.
