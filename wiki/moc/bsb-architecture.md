---
type: moc
title: "BSB Architecture (Map of Content)"
covers: [topic/llm, topic/pkm]
tags: [moc]
created: 2026-06-19
updated: 2026-06-19
---

# BSB Architecture (Map of Content)

This hub describes how a Better Second Brain (BSB) is built: the layered concepts it inherits from the LLM Wiki pattern, the tools (entities) that add traversal and search, the six operations that act on the corpus, and the docs/ guides that implement each one. For the broader topic-navigation view, see [[wiki/moc/second-brain-pattern]]. For the open question of whether this architecture actually beats a vanilla wiki, see the thesis [[wiki/syntheses/is-bsb-better-than-vanilla-llm-wiki]].

## Concepts (the layers)

- [[wiki/concepts/llm-wiki-pattern]] - raw / wiki / schema layers; the foundation BSB builds on.
- [[wiki/concepts/rag-vs-llm-wiki]] - the retrieval-vs-persistent-synthesis trade-off.
- [[wiki/concepts/knowledge-graph-graphrag]] - the graph layer: god nodes, communities, GraphRAG.
- [[wiki/concepts/research-discipline]] - the gate: real cited sources, primary vs community, stub marking.

## Entities (the tools)

- [[wiki/entities/graphify]] - folder to knowledge graph; built on Karpathy's /raw convention.
- [[wiki/entities/qmd]] - local hybrid markdown search (retrieval).
- [[wiki/entities/obsidian]] - editor plus Bases views over frontmatter.

## The six operations

- Ingest - pull a raw source into /raw and write/update wiki pages from it. See [[wiki/concepts/llm-wiki-pattern]], `docs/auto-research-integration.md`.
- Query - answer a question from the wiki and graph rather than re-reading raw. See [[wiki/concepts/rag-vs-llm-wiki]].
- Lint - check freshness, broken links, and unsupported claims against the gate. See [[wiki/concepts/research-discipline]], `docs/self-healing.md`.
- Graph - (re)build the knowledge graph from the corpus. See [[wiki/concepts/knowledge-graph-graphrag]], `docs/graphify-integration.md`.
- Improve - run autonomous research/optimization passes to deepen pages. See `docs/auto-research-integration.md`.
- Heal - auto-repair stale or broken pages flagged by lint. See `docs/self-healing.md`.

## Build guides (docs/)

- `docs/graphify-integration.md` - wiring graphify into the corpus.
- `docs/auto-research-integration.md` - automated ingest and improvement.
- `docs/self-healing.md` - lint and heal operations.
- `docs/benchmark.md` - how BSB-vs-vanilla is measured.

## Demo and thesis

- [[wiki/cheatsheets/second-brain/bsb-quickstart]] - set up and run a BSB.
- [[wiki/syntheses/is-bsb-better-than-vanilla-llm-wiki]] - is BSB actually better?

## Sources

- [[wiki/sources/karpathy-llm-wiki]] - pattern and operations. https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- [[wiki/sources/safishamsi-graphify]] - graph layer. https://github.com/safishamsi/graphify
- [[wiki/sources/tobi-qmd]] - search layer. https://github.com/tobi/qmd
- [[wiki/sources/obsidian-bases]] - views layer. https://obsidian.md/help/bases
