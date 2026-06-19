# Index

The content catalog — *what exists* in this brain. Read this first on any query, then drill into pages.
Grouped by category, not alphabetically. One line per page. (`log.md` = what happened; `roadmap.md` = what's next.)

## Overview

This brain's bootstrap domain is **the Better Second Brain pattern itself**: how Karpathy's LLM Wiki works, how
graphify / qmd / Obsidian extend it, and the prior art it stands on. Start at the two hubs:

- [[wiki/moc/second-brain-pattern]] — the topic hub (sources, concepts, entities).
- [[wiki/moc/bsb-architecture]] — how BSB is built (the six operations + the enhancement layers).

## Sources

- [[wiki/sources/karpathy-llm-wiki]] — Karpathy's "LLM Wiki" gist; the canonical pattern doc *(2026-06-19)*
- [[wiki/sources/karpathy-llm-knowledge-bases]] — Karpathy's X post announcing the pattern *(2026-06-19)*
- [[wiki/sources/safishamsi-graphify]] — graphify repo/README; the knowledge-graph layer *(2026-06-19)*
- [[wiki/sources/tobi-qmd]] — qmd; local hybrid markdown search *(2026-06-19)*
- [[wiki/sources/obsidian-bases]] — Obsidian Bases docs; DB views over frontmatter *(2026-06-19)*

## Concepts

- [[wiki/concepts/llm-wiki-pattern]] — the core pattern: raw → wiki → schema; ingest/query/lint *(2026-06-19)*
- [[wiki/concepts/rag-vs-llm-wiki]] — synthesis at compile-time vs query-time; where each wins *(2026-06-19)*
- [[wiki/concepts/knowledge-graph-graphrag]] — graphs + GraphRAG; god nodes, communities, multi-hop *(2026-06-19)*
- [[wiki/concepts/research-discipline]] — BSB's gate: no page from memory; ≥3 fetched sources *(2026-06-19)*
- [[wiki/concepts/maps-of-content]] — MOC hub notes for navigation and graph health *(2026-06-19)*
- [[wiki/concepts/zettelkasten]] — Luhmann's slip-box; atomic notes, dense linking (prior art) *(2026-06-19)*
- [[wiki/concepts/memex]] — Vannevar Bush 1945; associative trails (the ancestor) *(2026-06-19)*

## Entities

- [[wiki/entities/andrej-karpathy]] — person; originator of the LLM Wiki pattern *(2026-06-19)*
- [[wiki/entities/graphify]] — tool; folder → knowledge graph (pip `graphifyy`) *(2026-06-19)*
- [[wiki/entities/qmd]] — tool; local hybrid markdown search *(2026-06-19)*
- [[wiki/entities/obsidian]] — tool; the markdown PKM app / human reader (Bases) *(2026-06-19)*
- [[wiki/entities/tiago-forte]] — person; "Building a Second Brain" + PARA *(2026-06-19)*

## Cheatsheets

- [[wiki/cheatsheets/second-brain/bsb-quickstart]] — set up and run a BSB vault end-to-end *(2026-06-19)*

## Syntheses

- [[wiki/syntheses/is-bsb-better-than-vanilla-llm-wiki]] — the thesis + how we test it (draft) *(2026-06-19)*
- [[wiki/syntheses/heal-2026-06-19]] — first self-heal pass over the seed sources *(2026-06-19)*
- [[wiki/syntheses/lint-graph-2026-06-19]] — graphify-derived lint signals (god nodes, orphans) *(2026-06-19)*

## Maps of Content

- [[wiki/moc/second-brain-pattern]] — topic hub for the bootstrap domain *(2026-06-19)*
- [[wiki/moc/bsb-architecture]] — build-architecture hub *(2026-06-19)*

## Stats

- Pages: 23 wiki (5 sources · 7 concepts · 5 entities · 1 cheatsheet · 3 syntheses incl. 2 reports · 2 MOCs)
- Bootstrap commit: 2026-06-19 — all pages grounded in verified primary sources (see each page's `## Sources`).
- Last lint (2026-06-19): `verify_wikilinks` 0 broken · `find_orphans` 0 wiki orphans · `lint_sources` gated pages Tier A.
- Benchmark (2026-06-19): 3 runs (uv/MCP/Ruff). BSB +5–12% on citation; **`bsb-lean` = full quality at −66% fill tokens**, reads up to 17.9× cheaper than raw. See `benchmark/RESULTS.md`.
- Graph (2026-06-19): built via `/graphify ./wiki` — 22 nodes, 116 edges, 4 communities; MOC hubs are the top god nodes; 0 orphans. See `graphify-out/GRAPH_REPORT.md`.
