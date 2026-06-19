---
type: source
title: "Andrej Karpathy — LLM Wiki (gist)"
source-url: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
source-kind: gist
author: Andrej Karpathy
published: 2026-04
ingested: 2026-06-19
created: 2026-06-19
updated: 2026-06-19
tags: [llm-wiki, knowledge-management, rag, primary-source, pattern]
status: verified
---

# Andrej Karpathy — LLM Wiki (gist)

Karpathy's gist is the canonical specification of the LLM-wiki pattern: instead of treating an LLM as a retrieval engine that re-derives knowledge from raw documents on every query (RAG), you have the LLM incrementally build and maintain a persistent, interlinked markdown wiki that sits between you and the raw sources. The gist defines a three-layer architecture (raw sources, the wiki, the schema), three operations (ingest, query, lint), and two bookkeeping files (an `index.md` catalog and an append-only `log.md`). It is the direct ancestor of the BSB ("Better Second Brain") pattern documented in this vault.

## Key claims

- The common workflow today is RAG: upload files, retrieve relevant chunks at query time, generate an answer. It works, but the LLM rediscovers knowledge from scratch on every question, with no accumulation.
- The alternative is a persistent wiki the LLM incrementally builds and maintains: a structured, interlinked collection of markdown files between you and the raw sources.
- Three layers: **raw sources** (immutable; the LLM reads but never edits them), **the wiki** (LLM-generated summaries, entity pages, concept pages; the LLM owns this layer entirely), and **the schema** (a config document such as CLAUDE.md describing conventions and workflows).
- Three operations: **ingest** (drop a source in, the LLM extracts and integrates it, updating cross-references and flagging contradictions), **query** (the LLM searches relevant pages and synthesizes a cited answer; good answers can be filed back as new pages), and **lint** (a periodic health-check for contradictions, stale claims, orphan pages, and missing cross-references).
- `index.md` is the content catalog (each page with a link and one-line summary), updated on every ingest and read first on every query. `log.md` is a chronological, append-only record of ingests, queries, and lint passes.
- Knowledge is compiled once and kept current, not re-derived on every query. The human curates sources, directs analysis, and asks good questions; the LLM handles summarizing, cross-referencing, filing, and bookkeeping.

## Notable quotes

> Most people's experience with LLMs and documents looks like RAG: you upload a collection of files, the LLM retrieves relevant chunks at query time, and generates an answer. This works, but the LLM is rediscovering knowledge from scratch on every question.

> incrementally builds and maintains a persistent wiki — a structured, interlinked collection of markdown files that sits between you and the raw sources.

> The cross-references are already there. The contradictions have already been flagged. The synthesis already reflects everything you've read.

## Connections

- Defines [[wiki/concepts/llm-wiki-pattern]] in full, and frames [[wiki/concepts/rag-vs-llm-wiki]].
- Authored by [[wiki/entities/andrej-karpathy]]; announced publicly in [[wiki/sources/karpathy-llm-knowledge-bases]].
- The `/raw` immutable-sources convention is reused by [[wiki/entities/graphify]] (see [[wiki/sources/safishamsi-graphify]]).
- Establishes [[wiki/concepts/research-discipline]] (synthesis grounded in real sources, contradictions flagged).
- Anchors the [[wiki/moc/second-brain-pattern]] and [[wiki/moc/bsb-architecture]].

## Sources

- https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f (primary; fetched and quoted verbatim 2026-06-19)
