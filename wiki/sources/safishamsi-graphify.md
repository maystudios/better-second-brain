---
type: source
title: "graphify - repository and README (safishamsi/graphify)"
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

# graphify - repository and README (safishamsi/graphify)

graphify is a command-line tool that turns a folder of mixed inputs (code, SQL schemas, docs, papers, images, and audio/video) into a persistent, interactive knowledge graph, surfacing structure you did not explicitly encode: "god nodes" (highest-degree hubs), Leiden-detected communities, surprising connections, and suggested questions. Code-only extraction runs locally with no API key; semantic (doc/image) extraction supports many providers (Anthropic, Gemini, OpenAI, DeepSeek, Kimi, Ollama, Bedrock, Azure), and inside an AI IDE like Claude Code the host session can serve as the LLM. Within the BSB pattern it is the graph-traversal complement to the wiki: the wiki holds curated prose, graphify reveals how entities relate.

## Key claims

- Current README tagline: "Turn any folder of code, SQL schemas, R scripts, shell scripts, docs, papers, images, or videos into a queryable knowledge graph." Inputs include code (Python, TypeScript, Go, Rust, Java, C/C++, and more), SQL schemas (and live PostgreSQL introspection), Terraform/HCL, Markdown/text, PDFs with citation mining, Office (.docx/.xlsx) and Google Workspace docs, images via vision, and audio/video via transcription.
- Outputs land in `graphify-out/`: `graph.html` (interactive visualization with search/filter), `graph.json` (persistent graph reusable for GraphRAG-style queries), `GRAPH_REPORT.md` (god nodes, surprising connections, suggested questions), plus optional `obsidian/` and `wiki/` export folders and a SHA256 `cache/` for change detection.
- Every edge carries an audit trail tag: `EXTRACTED`, `INFERRED`, or `AMBIGUOUS` - keeping inferred relationships honest and distinguishable from literal ones.
- Community structure via Leiden clustering; god nodes are the highest-degree hub nodes.
- Optional flags/exports: `--obsidian`, `--wiki`, `--neo4j`, `--falkordb`, `--mcp`, `--watch` (background auto-sync with AST-only rebuilds for code), and `--update`. `graphify add <url>` fetches a paper or tweet, saves it into the raw collection, and updates the graph.
- Uses an immutable `/raw` source layer (the `graphify add <url>` flow saves fetched sources into it) - this matches Karpathy's `/raw` convention, though the *current* README no longer attributes it to Karpathy by name. Install via PyPI: the package is `graphifyy` (double-y) while the CLI is `graphify` - `pip install graphifyy && graphify install`.
- Code-only extraction needs no API key. Semantic (doc/image) extraction supports multiple providers (Anthropic, Gemini, OpenAI, DeepSeek, Kimi, Ollama, Bedrock, Azure); inside an AI IDE the host session can serve as the LLM. `GEMINI_API_KEY` / `GOOGLE_API_KEY` are one of several headless options, not a requirement.
- Caveat (reported in GitHub issue #514, not the README - current status unconfirmed): the bare shell CLI is subcommand-only, so a bare `graphify` invocation may not run the full interactive flow. Inside an IDE session, drive it through the `/graphify` skill.

## Notable quotes

> Turn any folder of code, SQL schemas, R scripts, shell scripts, docs, papers, images, or videos into a queryable knowledge graph.

(Current README tagline, fetched 2026-06-19. A claimed token-reduction figure of "up to 71.5x" on large corpora appears in the project's materials; treat such performance numbers as self-reported claims, not independently verified benchmarks.)

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

_Healed 2026-06-19: updated the README tagline (it changed), broadened the LLM-backend claim to multi-provider, expanded the supported-inputs list (SQL/Terraform/Office/audio), and qualified the Karpathy `/raw` attribution + the issue-#514 caveat as not stated in the current README. See [[wiki/syntheses/heal-2026-06-19]]._
