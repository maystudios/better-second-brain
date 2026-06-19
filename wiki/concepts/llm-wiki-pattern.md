---
type: concept
name: LLM Wiki Pattern
aliases:
  - LLM-built wiki
  - persistent wiki pattern
  - compile-time knowledge base
tags:
  - knowledge-management
  - llm
  - second-brain
  - pattern
sources:
  - "[[wiki/sources/karpathy-llm-wiki]]"
  - "[[wiki/sources/karpathy-llm-knowledge-bases]]"
created: 2026-06-19
updated: 2026-06-19
status: complete
---

# LLM Wiki Pattern

The LLM wiki pattern is a workflow in which a large language model incrementally builds and maintains a persistent, interlinked collection of markdown files that sits between a person and their raw sources, rather than re-deriving knowledge from those sources on every question. Andrej Karpathy's canonical write-up frames it as the alternative to retrieval-augmented generation (RAG): instead of the model "rediscovering knowledge from scratch on every question," it compiles synthesis once into a wiki whose "cross-references are already there," whose "contradictions have already been flagged," and whose "synthesis already reflects everything you've read." The wiki is the durable artifact; the work compounds because each pass adds to a structure that persists.

## How it shows up

The pattern, as described in Karpathy's [[wiki/sources/karpathy-llm-wiki|LLM Wiki gist]], is organized around three layers and three operations.

Three layers:

- **raw/** — the source material, unmodified: the documents, papers, and notes you feed in.
- **wiki/** — the structured, interlinked markdown the LLM writes: a "structured, interlinked collection of markdown files that sits between you and the raw sources."
- **schema** — the conventions that govern how wiki pages are typed, named, and linked, so the model can extend the structure consistently.

Three operations:

- **ingest** — read new raw material and fold it into the wiki, creating or updating pages and cross-links.
- **query** — answer a question from the already-compiled wiki rather than re-reading raw sources.
- **lint** — check the wiki for broken links, stale pages, and unflagged contradictions.

A root `index.md` provides the entry point and a `log.md` records what has been ingested over time. The defining move is that synthesis happens at **compile time** (during ingest) and is written down, so later queries traverse a finished structure instead of regenerating it. Karpathy introduced the broader idea publicly in his [[wiki/sources/karpathy-llm-knowledge-bases|"LLM Knowledge Bases" announcement]], describing "using LLMs to build personal knowledge bases for various topics of research interest." BSB itself is an instance of this pattern: this very page lives in a `wiki/` layer over a `raw/` source set.

## Related concepts

- [[wiki/concepts/rag-vs-llm-wiki]] — the explicit contrast between compile-time synthesis and query-time retrieval, including where RAG still wins.
- [[wiki/concepts/research-discipline]] — the gate that keeps ingest grounded in real fetched sources rather than model memory.
- [[wiki/concepts/knowledge-graph-graphrag]] — a complementary structure that captures how entities relate, not just which note to read.
- [[wiki/concepts/maps-of-content]] — hub notes that keep the wiki navigable as it grows.
- [[wiki/moc/second-brain-pattern]] — the map of content for this whole pattern family.
- [[wiki/moc/bsb-architecture]] — how the layers and operations are realized in BSB.

## Sources

- [[wiki/sources/karpathy-llm-wiki]] — Andrej Karpathy, "LLM Wiki" gist. https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f (primary; the canonical pattern document, including the three-layer / three-operation structure and the verbatim quotes used above).
- [[wiki/sources/karpathy-llm-knowledge-bases]] — Andrej Karpathy, "LLM Knowledge Bases," X post, ~2026-04-03. https://x.com/karpathy/status/2039805659525644595 (primary announcement; x.com is typically behind a login wall and was not fetchable, so it is corroborated here by the gist).
