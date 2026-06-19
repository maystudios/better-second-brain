---
type: source
title: "graphify — repository and README (safishamsi/graphify)"
source-url: https://github.com/safishamsi/graphify
source-kind: repo
author: safishamsi
published: 2026
ingested: 2026-06-19
created: 2026-06-19
updated: 2026-06-19
tags: [knowledge-graph, graphrag, tooling, primary-source, claude-code]
status: verified
---

# graphify — repository and README (safishamsi/graphify)

graphify is a command-line tool that turns a folder of mixed inputs (code, documents, papers, images, and video) into a persistent, interactive knowledge graph, surfacing structure you did not explicitly encode: "god nodes" (highest-degree hubs), Leiden-detected communities, surprising connections, and suggested questions. It is built on Karpathy's `/raw` immutable-sources convention and is designed to run inside Claude Code, where the host session itself acts as the LLM (no API key required); a Gemini/Google API key is only needed for headless extraction. Within the BSB pattern it is the graph-traversal complement to the wiki: the wiki holds curated prose, graphify reveals how entities relate.

## Key claims

- Reads a folder and "builds a knowledge graph, and gives you back structure you didn't know was there." Inputs include code (Python, TypeScript, Go, Rust, Java, C/C++, and more), Markdown/text, PDFs with citation mining, and images via vision.
- Outputs land in `graphify-out/`: `graph.html` (interactive visualization with search/filter), `graph.json` (persistent graph reusable for GraphRAG-style queries), `GRAPH_REPORT.md` (god nodes, surprising connections, suggested questions), plus optional `obsidian/` and `wiki/` export folders and a SHA256 `cache/` for change detection.
- Every edge carries an audit trail tag: `EXTRACTED`, `INFERRED`, or `AMBIGUOUS` — keeping inferred relationships honest and distinguishable from literal ones.
- Community structure via Leiden clustering; god nodes are the highest-degree hub nodes.
- Optional flags/exports: `--obsidian`, `--wiki`, `--neo4j`, `--falkordb`, `--mcp`, `--watch` (background auto-sync with AST-only rebuilds for code), and `--update`. `graphify add <url>` fetches a paper or tweet, saves it into the raw collection, and updates the graph.
- Built on Karpathy's `/raw` convention (immutable source layer). Install via PyPI: the package is named `graphifyy` (double-y) while the CLI is `graphify` — `pip install graphifyy && graphify install`.
- Inside Claude Code the host session is the LLM, so no API key is needed; `GEMINI_API_KEY` / `GOOGLE_API_KEY` are only required for headless (non-IDE) extraction.
- Caveat (issue #514): the bare shell CLI is subcommand-only — a bare `graphify` invocation does not run the interactive flow. Inside an IDE session, drive it through the `/graphify` skill rather than the bare CLI.

## Notable quotes

> reads your files, builds a knowledge graph, and gives you back structure you didn't know was there.

(README. A claimed token-reduction figure of "up to 71.5x" on large corpora appears in the README; treat such performance numbers as the project's own self-reported claims rather than independently verified benchmarks.)

## Connections

- Implements [[wiki/concepts/knowledge-graph-graphrag]] and reuses the `/raw` convention from [[wiki/concepts/llm-wiki-pattern]].
- The tool entity is [[wiki/entities/graphify]]; it complements [[wiki/entities/qmd]] (graphify = how entities relate; qmd = which note).
- Exports to [[wiki/entities/obsidian]] vault format and to a `wiki/` mirror of the [[wiki/concepts/llm-wiki-pattern]].
- The EXTRACTED/INFERRED/AMBIGUOUS audit trail is an instance of [[wiki/concepts/research-discipline]].
- Part of the [[wiki/moc/bsb-architecture]] and the [[wiki/moc/second-brain-pattern]].

## Sources

- https://github.com/safishamsi/graphify (primary repository)
- https://raw.githubusercontent.com/safishamsi/graphify/main/README.md (primary README; fetched 2026-06-19)
- https://pypi.org/project/graphifyy/ (package distribution; CLI named `graphify`, package `graphifyy`)
