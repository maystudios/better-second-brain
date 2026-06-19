# Log

Append-only chronological record of every operation. Newest entries at the **bottom**.
Greppable prefix — recent activity: `grep "^## \[" log.md | tail -10`.

Ops: `ingest` · `query` · `lint` · `graph` · `improve` · `heal` · `schema`.

---

## [2026-06-19] schema | Bootstrap — Better Second Brain initialized

Created the repo from scratch as an open-source **Better Second Brain (BSB)** template: the Karpathy LLM-Wiki
pattern + three enhancement layers (graphify graph, auto-research self-improvement, autonomous self-healing) +
a research-discipline gate (no page from training memory; ≥3 fetched sources).

- Wrote the schema `CLAUDE.md` (§0 scope · §1 architecture · §1.5 research discipline · §2 page types ·
  §3 operations incl. Graph/Improve/Heal · §4 meta-docs + session protocol · §5 style · §6 tooling · §7 evolution
  · §8 for-other-people), plus `AGENTS.md` (@import), `bsb.config.md`, `README.md`, `LICENSE` (MIT), `Welcome.md`.
- Committed an Obsidian baseline (`.obsidian/`: Bases enabled, wikilinks, attachments → `raw/assets/`,
  graph color groups) and a `.gitignore`.
- Established the wiki taxonomy: sources / concepts / entities / cheatsheets / syntheses / moc.
- Decision: link-style = **full-path** (`[[wiki/concepts/x]]`); domain default = software + the second-brain
  pattern itself (the bootstrap domain doubles as the first benchmark corpus).
- Seed content (this commit): sourced pages documenting the LLM-Wiki pattern, graphify, qmd, Obsidian Bases,
  and prior art (Memex, Zettelkasten, PARA) — all grounded in verified primary sources (see each page's `## Sources`).

Next: see `roadmap.md`.

## [2026-06-19] publish | Public GitHub repo + README badges

Published to https://github.com/maystudios/better-second-brain (public, MIT, 10 topics). Added shields.io badges
(stars / forks / issues / last-commit / license + "built on Karpathy LLM Wiki" / Obsidian / graphify) and a
star-history graph to the README.

## [2026-06-19] query | Benchmark — BSB vs vanilla LLM-wiki (uv small, MCP medium)

Ran a controlled A/B: same fetched sources, two arms (vanilla Karpathy vs BSB research-gated), a gold question set,
an objective judge, plus a deterministic token report (`scripts/token_report.py`, new this run).
- Quality: small (uv) = tie 5.83/5.83; medium (MCP) = BSB 5.60 vs vanilla 5.00 (+12%) — margin entirely from
  citation quality (1.80 vs 1.00). Vanilla slightly ahead on correctness (memory is strong on popular topics);
  BSB's gate over-abstained once (MCP -32002) — a real failure mode logged for follow-up.
- Tokens: read/query 2.3× (small) → 5.8× (medium) cheaper than reading raw, ~1.3–1.8× vs naive RAG; BSB read ≈
  vanilla (lower at medium); BSB fill ~1.8× costlier but break-even in 1–4 queries; ~1.6× denser interconnections.
- Evidence committed under `benchmark/` (RESULTS.md + per-arm wikis, gold sets, scores, token JSON).

## [2026-06-19] query | Large benchmark (Ruff) + fill-cost optimization (bsb-lean) + over-abstention fix

Large/novel run: 15 sources, 14 detail/freshness-heavy questions, THREE arms (vanilla, bsb, **bsb-lean**), exact
tokenizer (`tiktoken`, now installed). Added `scripts/token_report.py` auto-discovery of arms.
- Quality: vanilla 5.64, bsb 5.93, **bsb-lean 5.93** (bsb-lean ties full bsb, Δ=0). All arms perfect correctness +
  faithfulness; spread is citation quality (BSB cites exact URLs, vanilla bare filenames). BSB +5.1% over vanilla.
- **Fill optimization works:** bsb-lean = 7,648 fill tokens vs full bsb 22,366 (**−66%**, ≈ vanilla's 7,485) with
  NO quality loss, the DENSEST interconnection (31.0 links/1k vs 20.8 vs 12.0) and LOWEST read cost (442 tok/query,
  17.9× vs raw). Break-even 1 query. → adopted **lean fill as the default** in `CLAUDE.md` §2.1.
- Over-abstention fix worked (BSB arms now answer detail facts + nailed the unsupported trap). One residual hedge (Q5).
- Honest: the "advantage grows with size" hypothesis did NOT hold — margin shrank (both wikis captured facts);
  BSB's repeatable edge is verifiability. Next open test: a private/novel corpus where one wiki lacks the facts.

## [2026-06-19] schema | Lean fill mode is now the default (§2.1)

Encoded the benchmark-validated lean fill discipline into `CLAUDE.md`: compact source pages, cite-don't-restate,
terse dense `## Links`. Updated §3.1 ingest step 4. Rationale + numbers in `benchmark/RESULTS.md`.

## [2026-06-19] schema | auto-research applied to CLAUDE.md (369 → 180 lines)

Ran the §3.5 Improve loop (the `auto-research` skill) ON BSB's own schema. 10 cited specialist agents (108 sources);
headline finding (Anthropic official docs): CLAUDE.md should be <200 lines — "bloated files cause Claude to ignore
your actual instructions." Condensed 369→180: hoisted the two inviolable rules (§1.5 gate + §2.1 lean) to a top
block with NEVER/MUST modals; moved detailed runbooks/command catalogs to `docs/` (progressive disclosure); added
the Two-Strikes rule (§7) and a graphify corpus-size gate (§3.4). All 17 §-headings preserved; §1.5/§2.1 strengthened,
not weakened. Format-validation PASS. Workspace + findings + diff: `.auto-research/CLAUDE/` (gitignored).

## [2026-06-19] graph | First graphify build over wiki/ (Graph loop live)

Ran the §3.4 Graph loop end-to-end: `/graphify ./wiki` (graphifyy installed). 21 docs → 22 nodes, 116 edges, 4
communities (cohesion 0.90–1.00): "LLM Wiki & Karpathy Origins", "Tooling Stack", "BSB Architecture & GraphRAG",
"PKM Prior Art". God nodes = the MOC hubs + core pattern pages (deg 20/19/16) — the wiki's hubs ARE its most
connected nodes, as designed; 0 orphans. Outputs: `graphify-out/graph.json` + `GRAPH_REPORT.md` (committed),
`graph.html` (local). `scripts/graphify_sync.py` then derived signals into the lint loop → `wiki/syntheses/lint-graph-2026-06-19.md`.
Fixed two real bugs the run surfaced: graphify_sync crashed on Windows cp1252 (UTF-8 stdout), and over-reported
"missing hubs" by slugifying labels instead of using each node's `source_file` across all wiki folders.

## [2026-06-19] heal | Self-heal pass over the 5 seed source pages (Heal loop live)

Ran the §3.6 Heal loop: re-fetched each seed source's cited URL and diffed claims against the live source. 1 current
(karpathy-llm-wiki), 1 unverifiable (x.com 402 login wall — page already self-documents), 3 minor-drift fixed at
autonomy level 2 (source-confirmed, recorded visibly on each page): graphify (README tagline changed, multi-provider
now, more input types, Karpathy/raw + #514 qualified), qmd (model size ~1.1GB, +status MCP tool), obsidian-bases
(+summaries syntax). Full record: `wiki/syntheses/heal-2026-06-19.md`. Added a `lint-*`/`heal-*` gate exclusion to
`lint_sources.py` so operational reports aren't graded as reference content.

## [2026-06-19] query | Validated BSB on an existing vanilla brain (Game-Dev, 368 pages) + fixed broad-task query depth

Applied the BSB method to a COPY of the real Game-Dev vault (368 pages, untouched, not pushed). graphify built a
382-node / 2161-edge / 9-community graph (works at real scale). A/B'd 7 grounded questions, answering with vs without
the graph (same model/effort).
- Token: graph arm −23% real tokens (291,961 vs 378,720) / −56% read-footprint (2.29×; 72,707 vs 166,821) — the win
  comes from skipping the index.md re-read (~68k tok) + less over-reading.
- Quality: equal full marks on 6/7; the broadest synthesis task (imp-1) initially under-read.
- FIX: "scale read-depth to task breadth + traverse-to-exemplar (graphify explain/path) + completeness check" lifted
  imp-1 to normal parity at −38% tokens (24,354 vs 39,285). Encoded into CLAUDE.md §3.2 + docs/graphify-integration.md.
- Also surfaced judge variance — score arms head-to-head with one judge. Full local report: bsb-gamedev-test/COMPARISON.md.
