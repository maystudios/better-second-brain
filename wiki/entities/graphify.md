---
type: entity
name: graphify
entity-kind: tool
aliases: [graphifyy, "graphify CLI"]
tags: [knowledge-graph, graphrag, cli, tool, python]
sources:
  - "[[wiki/sources/safishamsi-graphify]]"
created: 2026-06-19
updated: 2026-06-19
status: verified
---

# graphify

graphify is an open-source tool by safishamsi that turns a folder of inputs — code, docs, papers, images, video — into a persistent knowledge graph. It identifies "god nodes" (the highest-degree hub nodes), detects communities via the Leiden algorithm, surfaces surprising connections and suggested questions, and keeps an EXTRACTED / INFERRED / AMBIGUOUS audit trail for every claim. It is built on Karpathy's `/raw` folder convention, making it a natural traversal companion to the LLM Wiki pattern.

## Facts

- Distributed on PyPI as the package `graphifyy` (note the double "y"), while the command-line entry point is `graphify`. PyPI: https://pypi.org/project/graphifyy/ .
- Outputs are written to a `graphify-out/` directory: `graph.html` (interactive view), `graph.json` (GraphRAG-compatible), and `GRAPH_REPORT.md` (the written report).
- Core graph features: god nodes (highest-degree hubs), Leiden community detection, "surprising connections," and suggested questions.
- Every extracted relationship carries an audit label — EXTRACTED, INFERRED, or AMBIGUOUS — so claims can be traced rather than taken on faith.
- Optional integrations/flags include `--obsidian`, `--wiki`, `--neo4j`, `--falkordb`, `--mcp`, `--watch`, and `--update`; `graphify add <url>` saves a source into `raw/` and updates the graph.
- Inside Claude Code, the host session itself acts as the LLM, so no API key is required. `GEMINI_API_KEY` / `GOOGLE_API_KEY` are only needed for headless extraction outside the host session.
- Caveat (issue #514): the bare shell CLI is subcommand-only; the recommended way to drive it interactively is via the `/graphify` skill rather than free-form CLI calls.

## Relationships

- Implements [[wiki/concepts/knowledge-graph-graphrag]] over a corpus.
- Built on the `/raw` convention from the [[wiki/concepts/llm-wiki-pattern]].
- Complements retrieval-style tools such as [[wiki/entities/qmd]]: qmd finds *which* note, graphify finds *how* entities relate.
- Can export into [[wiki/entities/obsidian]] via `--obsidian`.
- Authored by safishamsi; see source page [[wiki/sources/safishamsi-graphify]].
- Part of [[wiki/moc/bsb-architecture]].

## Sources

- safishamsi, graphify (GitHub): https://github.com/safishamsi/graphify — primary, fetchable.
- graphify README (raw): https://raw.githubusercontent.com/safishamsi/graphify/main/README.md — primary.
- PyPI package `graphifyy`: https://pypi.org/project/graphifyy/ — primary (confirms package name vs CLI name).
- See [[wiki/sources/safishamsi-graphify]].
