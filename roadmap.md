# Roadmap

What's next for this brain. `index.md` = what exists, `log.md` = what happened, **this** = what's next.
Items: `- [ ] **<Type>**: <slug> - <reason>`. Types: Ingest · Cheatsheet · Concept · Synthesis · Schema · Tooling · Heal.

---

## In Progress

- (nothing active - bootstrap complete; pick the next High item)

## Backlog - High

- [ ] **Benchmark**: run a genuinely **private / novel** corpus (where one wiki simply *lacks* the facts) - the only
      remaining way to test for a real *correctness* gap; the large public-corpus run showed correctness parity.
- [ ] **Graph**: re-run `/graphify` + `graphify_sync.py` after the next batch of ingests (it's now wired and proven).
- [ ] **Cleanup**: retro-fit the **lean fill mode** (§2.1) onto the 21 verbose bootstrap seed pages to shrink them
      (optional; they pass lint as-is).
      from `docs/benchmark.md` and a first scored run
- [ ] **Improve**: run the `auto-research` skill against `CLAUDE.md` once content exists, to validate the
      self-improvement loop end-to-end (§3.5)
- [ ] **RSI**: adopt the `drop-links` KEEP on the real vault (validate -10% tokens transfers from the Ruff benchmark)
      and **confirm the `merge-sources-compact` stepping stone** with a reference-guided LLM judge (the deterministic
      coverage proxy says full grounding; verify correctness/faithfulness before promoting it out of the archive).
- [ ] **RSI**: run more *forward* levers with research-backed mutations - (a) prompt-cache the stable `CLAUDE.md`
      prefix, (b) server-side tool-result clearing after a source is distilled, (c) retrieval-first query path. Drive
      lever choice with a Thompson/UCB bandit; run candidates *in parallel* (BSB's edge over autoresearch's sequential loop).
- [ ] **RSI/Benchmark**: grow the gold question set (>~50 Q) and wire `questions-public.json` vs `questions.json` as a
      held-out split - the current ~14-Q set can validate the metric but is too small to *drive* iterations without
      overfitting (GEPA degeneracy). Re-test every KEEP on a novel corpus before trusting it.
- [ ] **RSI/Tooling**: add a wall-clock `timing.json` writer (rolling median over N runs) so latency is measured, not
      just proxied by read-tokens; and a `--judge` quality re-score so forward candidates get a real quality reading.
- [ ] **Heal**: first self-heal pass - re-verify the seed source pages' URLs are still live and current (§3.6)

## Backlog - Lower

- [ ] **Ingest**: expand the bootstrap domain - NotebookLM vs wiki (unverified in research), GraphRAG papers,
      more Obsidian-Bases primary docs
- [ ] **Tooling**: add `qmd` retrieval layer once the brain passes ~100 sources
- [ ] **Cheatsheet**: add real software-reference cheatsheets once a target stack is chosen (the shipped domain
      is reference-capable but currently seeded only with second-brain/PKM content)
- [ ] **Schema**: optional - `.githooks` pre-commit + CI gate are present but opt-in; decide whether to enable

## Open Questions  *(seed the query loop - graphify will add more)*

- Does BSB measurably beat a vanilla Karpathy wiki on correctness + citation quality + freshness? (→ benchmark)
- At what corpus size does `index.md` stop fitting one context window, and what's the shard strategy?
- Which self-heal corrections are safe to fully automate (level 3) vs. always review?
- Karpathy keeps the protocol (`program.md`) static; BSB's §3.7 loop treats its protocol (`CLAUDE.md`) as mutable.
  Where is the safe boundary for the loop self-modifying the rulebook, and which schema changes must stay human-only?

## Recently Done

- 2026-06-23 - **RSI exploration upgrade** (escape the greedy ratchet trap): 2nd 21-agent verified research pass on
      the acceptance rule; built `scripts/rsi_archive.py` (KEEP/EXPLORE/DISCARD + MAP-Elites archive) +
      `scripts/rsi_transforms.py` (deterministic levers). Ran a 5-lever forward fleet (`RSI_LOG.tsv` Round 2):
      `drop-links` KEEP (-10% tok), `merge-sources` EXPLORE (-59% tok, greedy would discard) -> `merge-sources-compact`
      -49.6% tok at full coverage. Grounded in MAP-Elites/DGM/objective-paradox/LAHC ([[wiki/concepts/quality-diversity-search]]).
- 2026-06-23 - **built the §3.7 RSI loop** (Karpathy autoresearch applied to BSB): 21-agent verified research pass,
      `scripts/rsi_fitness.py` (lexicographic constrained metric: quality floor, then minimize cost+latency),
      `docs/rsi-loop.md`, 8 grounded pages incl. [[wiki/syntheses/bsb-rsi-loop]], CLAUDE.md §3.7. Validated on real
      data (`benchmark/RSI_LOG.tsv`): 2 KEEP + 1 floor-enforced DISCARD; the loop re-derives the lean-fill decision.
- 2026-06-19 - repo bootstrapped; schema + packaging + Obsidian baseline + seed content; git initialized (commit on `main`).
- 2026-06-19 - finalized `index.md` from the 21 seed pages.
- 2026-06-19 - verified: `verify_wikilinks` 0 broken, `find_orphans` 0 wiki orphans, `lint_sources --strict-min-tier A` passes (cheatsheet + synthesis at Tier A).
- 2026-06-19 - **published** public repo maystudios/better-second-brain + README badges + star-history graph.
- 2026-06-19 - **ran the first benchmark** (BSB vs vanilla, small uv + medium MCP) incl. token-efficiency (`scripts/token_report.py`). Result: quality tie→+12%, read 2.3-5.8× cheaper than raw. See `benchmark/RESULTS.md`.
- 2026-06-19 - **large 3-arm benchmark (Ruff)** + **fill optimization**: new `bsb-lean` mode matches full-BSB quality at **-66% fill tokens** (≈ vanilla), densest interconnection, 17.9× read compression. Adopted lean as default (`CLAUDE.md` §2.1). Over-abstention fixed; `tiktoken` added.
- 2026-06-19 - **§3.5 Improve loop run live:** `auto-research` on `CLAUDE.md` (10 cited agents, 108 sources) → condensed 369→180 lines per Anthropic's <200 guidance, hoisted §1.5/§2.1, added Two-Strikes rule. The brain improved its own rules. Also shipped `init_brain.py` + `/bsb-init` + agentic README install prompt.
- 2026-06-19 - **§3.4 Graph + §3.6 Heal loops run live** → all three "better" loops now exercised end-to-end. graphify built the wiki graph (22 nodes/116 edges/4 communities, MOC hubs = top god nodes, 0 orphans); the heal pass re-verified the 5 seed sources and fixed 3 minor-drift pages. Fixed 2 graphify_sync bugs (cp1252 crash, missing-hub over-report) the run surfaced.
