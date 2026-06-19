---
type: synthesis
title: "Is a Better Second Brain better than a vanilla LLM Wiki?"
sources-cited:
  - "[[wiki/sources/karpathy-llm-wiki]]"
  - "[[wiki/sources/safishamsi-graphify]]"
  - "[[wiki/sources/obsidian-bases]]"
  - "[[wiki/sources/tobi-qmd]]"
  - "https://atlan.com/know/llm-wiki-vs-rag-knowledge-base/"
tags: [synthesis, llm-wiki, bsb, rag]
created: 2026-06-19
updated: 2026-06-19
status: draft
---

# Is a Better Second Brain better than a vanilla LLM Wiki?

A Better Second Brain (BSB) extends Andrej Karpathy's LLM Wiki pattern with a graph layer, a local search layer, and an enforced research-discipline gate. This page states the hypothesis that BSB improves answer quality and trust over a vanilla wiki, explains the reasoning grounded in the source pattern, gives the counter-points where the simpler vanilla approach (or plain RAG) still wins, and lists the concrete benchmark outcomes that would confirm or refute the claim. Treat the conclusion as a hypothesis, not a measured result.

## Short answer

**Partly confirmed by a first measured run (small-N).** On a small, well-known topic BSB and a vanilla wiki *tied*
on answer quality; on a medium topic **BSB won by ~12%**, and the entire margin came from **verifiable citations**,
not raw correctness. On token cost, querying a wiki is **~2–6× cheaper than reading the raw sources** (the gap grows
with corpus size), and BSB reads about the same as — or less than — vanilla per query while laying down ~1.6× denser
interconnections; its higher one-time fill cost is repaid within **1–4 queries**. The honest nuance: vanilla matches
BSB on *correctness* for popular topics (memory is strong there) and BSB's research gate occasionally **over-abstains**.
Full numbers and caveats: `benchmark/RESULTS.md`.

## Measured results (first run — 2026-06-19)

See `benchmark/RESULTS.md` for the full tables. Headlines:

- **Quality:** small (`uv`) = tie 5.83/5.83; medium (`MCP`) = BSB 5.60 vs vanilla 5.00 (+12%), driven by citation
  quality (1.80 vs 1.00). Vanilla was slightly ahead on *correctness* (2.00 vs 1.80) because BSB's gate abstained on
  one answerable detail its KB hadn't indexed — a real failure mode to fix.
- **Read tokens/query:** wiki vs read-all-raw ≈ 2.3× (small) → 5.8× (medium); ≈ 1.3–1.8× vs naive RAG. BSB ≈ vanilla
  (lower at medium: 1,328 vs 1,470).
- **Fill tokens:** BSB ~1.8–1.9× more than vanilla (source pages + denser links); break-even in 1–4 queries vs raw.
- **Caveats:** 2 topics / 16 questions, not fully blinded, approximate tokenizer, popular topics flatter vanilla.
  Directional, not definitive — a large/novel-corpus run is the next test.

## Reasoning

The vanilla wiki already beats naive retrieval-augmented generation on the three gaps Karpathy names in the canonical gist ([[wiki/sources/karpathy-llm-wiki]]): plain RAG makes the model rediscover knowledge from scratch on every question, whereas a persistent wiki means "the cross-references are already there", "the contradictions have already been flagged", and "the synthesis already reflects everything you've read". BSB keeps those three layers (raw, wiki, schema) intact and adds three things on top.

1. Traversal. The wiki's wikilinks are edges, but the model reads them one file at a time. graphify ([[wiki/sources/safishamsi-graphify]]) compiles the same corpus into an explicit graph with god nodes (highest-degree hubs), Leiden communities, and surprising connections, plus a GraphRAG `graph.json`. This is what lets a question be answered by following relationships rather than re-reading prose. See [[wiki/concepts/knowledge-graph-graphrag]].
2. Retrieval precision. qmd ([[wiki/sources/tobi-qmd]]) adds local hybrid search (BM25 over SQLite FTS5 + vector + LLM rerank) so the right note is surfaced before synthesis. qmd answers *which* note; graphify answers *how* entities relate.
3. The research-discipline gate. Every page must be grounded in real, cited sources, with primary sources separated from community claims and unsupported assertions marked `status: stub`. See [[wiki/concepts/research-discipline]]. This is the trust mechanism the vanilla pattern leaves to author habit.

Browsing and querying are made ergonomic by Obsidian Bases ([[wiki/sources/obsidian-bases]]), which turns the frontmatter the wiki already writes into Table/Card/List views without a separate database.

## Counter-points

Where vanilla Karpathy, or even plain RAG, wins (limits documented at https://atlan.com/know/llm-wiki-vs-rag-knowledge-base/):

- Scale. The wiki index outgrows the context window (around 50k-100k tokens). Past that, the model can no longer hold the map in one pass; plain RAG scales better to very large corpora. BSB's extra layers do not remove this ceiling.
- Freshness. When raw sources change, nothing auto-propagates into the wiki; freshness still needs a manual lint pass. BSB adds a heal operation but does not eliminate the maintenance burden.
- No access control. Neither vanilla wiki nor BSB provides per-document permissions.
- Cost of the extra layers. graphify and qmd are real install/maintenance surface. For a small corpus or a one-off question, the vanilla wiki (or just RAG) is cheaper to stand up and is likely good enough.

## What would change my mind

Concrete benchmark outcomes (procedure in `docs/benchmark.md`) that would confirm BSB is better:

- On a held-out set of multi-hop questions, BSB-with-graph answers correctly more often than the vanilla wiki at matched token budget.
- Citation accuracy (every claim traceable to a real source) is measurably higher with the discipline gate on than off, with fewer unsupported assertions.
- qmd retrieval surfaces the gold note in top-k more often than reading the index linearly, at lower token cost.

And outcomes that would refute it:

- No accuracy delta on multi-hop questions once both systems are given the same token budget.
- The graph/search maintenance cost outweighs any quality gain for the target corpus size.
- The discipline gate slows ingestion enough that the corpus stays too small to matter.

## Sources

- [[wiki/sources/karpathy-llm-wiki]] — canonical LLM Wiki pattern (three layers, three ops, RAG critique). https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- [[wiki/sources/safishamsi-graphify]] — folder-to-knowledge-graph; god nodes, Leiden communities, GraphRAG output. https://github.com/safishamsi/graphify
- [[wiki/sources/tobi-qmd]] — local hybrid markdown search (BM25 + vector + LLM rerank). https://github.com/tobi/qmd
- [[wiki/sources/obsidian-bases]] — DB-like views over note frontmatter. https://obsidian.md/help/bases
- Atlan, "LLM Wiki vs RAG Knowledge Base" — scale, freshness, access-control limits. https://atlan.com/know/llm-wiki-vs-rag-knowledge-base/
- Benchmark procedure (relative): `docs/benchmark.md`
- Measured results, first run (relative): `benchmark/RESULTS.md`
- Architecture hub: [[wiki/moc/bsb-architecture]]
