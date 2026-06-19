---
type: entity
name: qmd
entity-kind: tool
aliases: ["@tobilu/qmd"]
tags: [search, retrieval, cli, markdown, local-llm, mcp]
sources:
  - "[[wiki/sources/tobi-qmd]]"
created: 2026-06-19
updated: 2026-06-19
status: verified
---

# qmd

qmd is a local command-line search tool for markdown and notes by an author publishing under the handle "tobi." It performs hybrid retrieval — BM25 keyword search (via SQLite FTS5) combined with vector search and an LLM reranking step — running entirely locally through `node-llama-cpp` and local GGUF models, and it ships an MCP server so the same search is callable from agents. In a Second Brain it is the retrieval layer: it answers "which note?" while leaving relationship traversal to a graph tool.

## Facts

- Installed globally via npm: `npm i -g @tobilu/qmd`. npm: https://www.npmjs.com/package/@tobilu/qmd .
- Retrieval is hybrid: BM25 (SQLite FTS5) + vector similarity + an LLM rerank pass.
- Runs locally using `node-llama-cpp` with local GGUF model files; no remote API is required for its core search.
- Exposes an MCP server, so it can be wired into agent tooling as a search backend.
- Authorship note: the npm/GitHub owner handle is "tobi," widely attributed to Shopify CEO Tobi Lutke. State this as a widely-attributed identification; the README does not biographically confirm it, so it is not asserted as fact here.

## Relationships

- A retrieval tool that frames the trade-off discussed in [[wiki/concepts/rag-vs-llm-wiki]] (retrieval over a corpus vs. a maintained wiki).
- Complements [[wiki/entities/graphify]]: qmd finds *which* note (retrieval); graphify finds *how* entities relate (traversal).
- Searches markdown notes of the kind produced by the [[wiki/concepts/llm-wiki-pattern]], and works over vaults managed in [[wiki/entities/obsidian]].
- Part of [[wiki/moc/bsb-architecture]].

## Sources

- tobi, qmd (GitHub): https://github.com/tobi/qmd — primary, fetchable.
- npm package `@tobilu/qmd`: https://www.npmjs.com/package/@tobilu/qmd — primary (install command, package name).
- See [[wiki/sources/tobi-qmd]].
