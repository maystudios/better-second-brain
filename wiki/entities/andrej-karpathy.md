---
type: entity
name: Andrej Karpathy
entity-kind: person
aliases: [karpathy]
tags: [llm, knowledge-management, ai, founder]
sources:
  - "[[wiki/sources/karpathy-llm-wiki]]"
  - "[[wiki/sources/karpathy-llm-knowledge-bases]]"
created: 2026-06-19
updated: 2026-06-19
status: verified
---

# Andrej Karpathy

Andrej Karpathy is an AI researcher and educator best known in this knowledge base as the originator of the "LLM Wiki" pattern: instead of treating documents as a pile of chunks retrieved at query time (RAG), an LLM incrementally builds and maintains a persistent, interlinked collection of markdown files that sits between the user and the raw sources. He published the pattern as a public gist and announced the broader idea as "LLM Knowledge Bases" on X around April 2026.

## Facts

- Author of the canonical pattern document, a public gist titled "LLM Wiki", which frames the contrast with RAG: RAG works "but the LLM is rediscovering knowledge from scratch on every question," whereas a wiki means "the cross-references are already there. The contradictions have already been flagged. The synthesis already reflects everything you've read." (see [[wiki/sources/karpathy-llm-wiki]]).
- The gist specifies a concrete structure: three layers (raw / wiki / schema), three operations (ingest / query / lint), plus an `index.md` and a `log.md`.
- Announced the broader idea on X (~2026-04-03) under the heading "LLM Knowledge Bases," describing it as "using LLMs to build personal knowledge bases for various topics of research interest" (see [[wiki/sources/karpathy-llm-knowledge-bases]]).
- Note on attribution: the X post is the primary public announcement. x.com is generally not fetchable due to its login wall, so the announcement is corroborated here via the gist and secondary coverage rather than a direct fetch. Widely circulated figures attributed to the announcement (e.g. ~100 articles / ~400k words, ~16M views, ~95% token reduction) are community claims, not verbatim from a primary source.
- This knowledge base deliberately avoids asserting further biographical specifics (employers, titles, dates) that are not grounded in a cited source in this research pass.

## Relationships

- Originated the [[wiki/concepts/llm-wiki-pattern]] that this whole project is built on.
- His framing motivates the comparison in [[wiki/concepts/rag-vs-llm-wiki]].
- The gist's insistence on grounding answers in maintained, cross-referenced notes underpins [[wiki/concepts/research-discipline]].
- Sits in the lineage of prior knowledge-management ideas: [[wiki/concepts/memex]] and [[wiki/concepts/zettelkasten]].
- Central node in [[wiki/moc/second-brain-pattern]] and [[wiki/moc/bsb-architecture]].

## Sources

- Karpathy, "LLM Wiki" (gist): https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f — primary, fetchable; quotes confirmed verbatim. See [[wiki/sources/karpathy-llm-wiki]].
- Karpathy, "LLM Knowledge Bases" (X post, ~2026-04-03): https://x.com/karpathy/status/2039805659525644595 — primary announcement; not directly fetchable (login wall), corroborated via the gist. See [[wiki/sources/karpathy-llm-knowledge-bases]].
