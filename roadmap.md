# Roadmap

What's next for this brain. `index.md` = what exists, `log.md` = what happened, **this** = what's next.
Items: `- [ ] **<Type>**: <slug> — <reason>`. Types: Ingest · Cheatsheet · Concept · Synthesis · Schema · Tooling · Heal.

---

## In Progress

- (nothing active — bootstrap complete; pick the next High item)

## Backlog — High

- [ ] **Tooling**: install graphify (`uv tool install graphifyy`) and run the first `/graphify .` build;
      wire `scripts/graphify_sync.py` into the lint loop (§3.4)
- [ ] **Heal/Schema**: fix the benchmark-revealed **over-abstention** failure mode — when a fact isn't in the KB,
      allow a flagged low-confidence answer instead of a hard "the wiki does not say" abstain (MCP -32002 case)
- [ ] **Benchmark**: run a **large / novel-corpus** example (the read-efficiency gap and citation edge both grew
      small→medium; test whether they keep growing where memory is unreliable). Add `tiktoken` for exact token counts.
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

- 2026-06-19 — repo bootstrapped; schema + packaging + Obsidian baseline + seed content; git initialized (commit on `main`).
- 2026-06-19 — finalized `index.md` from the 21 seed pages.
- 2026-06-19 — verified: `verify_wikilinks` 0 broken, `find_orphans` 0 wiki orphans, `lint_sources --strict-min-tier A` passes (cheatsheet + synthesis at Tier A).
- 2026-06-19 — **published** public repo maystudios/better-second-brain + README badges + star-history graph.
- 2026-06-19 — **ran the first benchmark** (BSB vs vanilla, small uv + medium MCP) incl. token-efficiency (`scripts/token_report.py`). Result: quality tie→+12%, read 2.3–5.8× cheaper than raw. See `benchmark/RESULTS.md`.
