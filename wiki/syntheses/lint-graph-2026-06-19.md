---
title: Graphify Lint Sync 2026-06-19
type: synthesis
status: stub
slug: lint-graph-2026-06-19
created: 2026-06-19
tags: [lint, graphify]
sources: []
---

# Graphify Lint Sync 2026-06-19

Auto-generated lint synthesis derived from the latest graphify run. It lists missing hub pages, orphan nodes, and surfaced graph questions so they can be turned into properly sourced wiki pages. This page is a stub and is not source-grounded yet; it must be filled with real, cited sources before it can pass the lint gate.

## Graphify Lint Sync (2026-06-19)

Derived from graphify outputs (CLAUDE.md s3.4). graphify-out present: graph.json=True, GRAPH_REPORT.md=True.

## God / hub nodes (top 15 by degree)

### Missing hub pages (candidate stubs)
- none; all top hubs already have pages.

### Existing hub pages
- Second Brain Pattern (Map of Content) (degree 20) -> [[wiki/moc/second-brain-pattern]]
- LLM Wiki Pattern (degree 19) -> [[wiki/concepts/llm-wiki-pattern]]
- BSB Architecture (Map of Content) (degree 16) -> [[wiki/moc/bsb-architecture]]
- BSB Quickstart (degree 14) -> [[wiki/cheatsheets/second-brain/bsb-quickstart]]
- Andrej Karpathy - LLM Wiki (gist) (degree 13) -> [[wiki/sources/karpathy-llm-wiki]]
- Knowledge Graph and GraphRAG (degree 12) -> [[wiki/concepts/knowledge-graph-graphrag]]
- graphify (degree 11) -> [[wiki/entities/graphify]]
- graphify - repository and README (safishamsi/graphify) (degree 11) -> [[wiki/sources/safishamsi-graphify]]
- qmd - repository (tobi/qmd) (degree 11) -> [[wiki/sources/tobi-qmd]]
- RAG vs LLM Wiki (degree 11) -> [[wiki/concepts/rag-vs-llm-wiki]]
- Obsidian (degree 10) -> [[wiki/entities/obsidian]]
- Obsidian Bases - documentation (degree 10) -> [[wiki/sources/obsidian-bases]]
- qmd (degree 10) -> [[wiki/entities/qmd]]
- Research Discipline (degree 10) -> [[wiki/concepts/research-discipline]]
- Andrej Karpathy (degree 9) -> [[wiki/entities/andrej-karpathy]]

## Orphan graph nodes (degree 0)

- none.

## Surprising Connections

Quoted from GRAPH_REPORT.md:

> - `Maps of Content` --conceptually_related_to--> `PARA Method`  [INFERRED]
>   wiki/concepts/maps-of-content.md → wiki/entities/tiago-forte.md
> - `BSB Architecture (Map of Content)` --references--> `BSB Quickstart`  [EXTRACTED]
>   wiki/moc/bsb-architecture.md → wiki/cheatsheets/second-brain/bsb-quickstart.md
> - `BSB Quickstart` --references--> `Knowledge Graph and GraphRAG`  [EXTRACTED]
>   wiki/cheatsheets/second-brain/bsb-quickstart.md → wiki/concepts/knowledge-graph-graphrag.md
> - `BSB Quickstart` --references--> `LLM Wiki Pattern`  [EXTRACTED]
>   wiki/cheatsheets/second-brain/bsb-quickstart.md → wiki/concepts/llm-wiki-pattern.md
> - `BSB Quickstart` --references--> `RAG vs LLM Wiki`  [EXTRACTED]
>   wiki/cheatsheets/second-brain/bsb-quickstart.md → wiki/concepts/rag-vs-llm-wiki.md

## Suggested Questions

Quoted from GRAPH_REPORT.md:

> _Questions this graph is uniquely positioned to answer:_
>
> - **Why does `Second Brain Pattern (Map of Content)` connect `LLM Wiki & Karpathy Origins` to `Tooling Stack: graphify/qmd/Obsidian`, `BSB Architecture & GraphRAG`, `PKM Prior Art: PARA & Zettelkasten`?**
>   _High betweenness centrality (0.146) - this node is a cross-community bridge._
> - **Why does `LLM Wiki Pattern` connect `LLM Wiki & Karpathy Origins` to `Tooling Stack: graphify/qmd/Obsidian`, `BSB Architecture & GraphRAG`, `PKM Prior Art: PARA & Zettelkasten`?**
>   _High betweenness centrality (0.127) - this node is a cross-community bridge._
> - **Why does `Maps of Content` connect `PKM Prior Art: PARA & Zettelkasten` to `LLM Wiki & Karpathy Origins`, `Tooling Stack: graphify/qmd/Obsidian`, `BSB Architecture & GraphRAG`?**
>   _High betweenness centrality (0.073) - this node is a cross-community bridge._

## Sources

- (stub) No external sources yet; populate per CLAUDE.md s1.5 before promoting beyond status: stub.
