---
type: source
title: "qmd — repository (tobi/qmd)"
source-url: https://github.com/tobi/qmd
source-kind: repo
author: tobi
published: 2026
ingested: 2026-06-19
created: 2026-06-19
updated: 2026-06-19
tags: [search, retrieval, local-llm, tooling, primary-source]
status: verified
---

# qmd — repository (tobi/qmd)

qmd is a local-first command-line search engine for markdown notes, transcripts, and documentation: an on-device tool that lets you search a personal knowledge base with keywords or natural language. It combines three retrieval methods — BM25 full-text search (SQLite FTS5), vector semantic search, and LLM re-ranking — running entirely on-device via `node-llama-cpp` with local GGUF models, and exposes an MCP server so agents like Claude can query it. In the BSB pattern, qmd answers "which note?" (retrieval) while graphify answers "how do these entities relate?" (traversal); qmd complements the wiki rather than replacing it.

## Key claims

- Described as "an on-device search engine for everything you need to remember"; indexes markdown notes, meeting transcripts, documentation, and knowledge bases, searchable by keyword or natural language.
- Hybrid retrieval pipeline: (1) BM25 full-text via SQLite FTS5 for keyword matching, (2) vector semantic search via embeddings, and (3) LLM re-ranking to score relevance.
- Runs locally via `node-llama-cpp` with GGUF models — no external API calls. Reported local models include EmbeddingGemma (300M) for embeddings, Qwen3-Reranker (0.6B) for scoring, and a Qwen3-based query-expansion model (~1.7B params, ~1.1GB on disk per the live README).
- Ships an MCP server exposing tools such as `query`, `get`, `multi_get`, and `status` (index health / collection info), for integration with Claude and other agents.
- Install globally with Node or Bun: `npm install -g @tobilu/qmd`.
- Owner handle is `tobi`; this is widely attributed to Shopify CEO Tobi Lutke. State as widely-attributed only — the README does not biographically confirm the identity.

## Notable quotes

> An on-device search engine for everything you need to remember.

> runs locally via node-llama-cpp with GGUF models

## Connections

- A retrieval tool entity: [[wiki/entities/qmd]]; the local-search complement to [[wiki/entities/graphify]] within [[wiki/concepts/knowledge-graph-graphrag]].
- Supplies the "find which note" leg of the [[wiki/concepts/llm-wiki-pattern]] query operation; contrasts with chunk-time RAG in [[wiki/concepts/rag-vs-llm-wiki]].
- Searches the same frontmatter-bearing markdown that [[wiki/entities/obsidian]] and [[wiki/sources/obsidian-bases]] organize.
- Part of the [[wiki/moc/bsb-architecture]] and the [[wiki/moc/second-brain-pattern]].

## Sources

- https://github.com/tobi/qmd (primary repository; fetched 2026-06-19)
- https://www.npmjs.com/package/@tobilu/qmd (package distribution)

_Healed 2026-06-19: query-expansion model size aligned to the live README (~1.1GB) and the `status` MCP tool added. See [[wiki/syntheses/heal-2026-06-19]]._
