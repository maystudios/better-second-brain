---
type: concept
name: RAG vs LLM Wiki
aliases:
  - RAG versus LLM wiki
  - retrieval vs synthesis
  - query-time vs compile-time knowledge
tags:
  - knowledge-management
  - rag
  - llm
  - second-brain
  - comparison
sources:
  - "[[wiki/sources/karpathy-llm-wiki]]"
created: 2026-06-19
updated: 2026-06-19
status: complete
---

# RAG vs LLM Wiki

RAG (retrieval-augmented generation) and the LLM wiki pattern are two ways to put a corpus behind a language model, and they differ in *when synthesis happens and what persists*. In RAG, the model retrieves relevant chunks at query time and generates an answer, so it is, in Karpathy's words, "rediscovering knowledge from scratch on every question." In the LLM wiki pattern, synthesis is compiled once into a durable structure, so a later query traverses finished pages where "the cross-references are already there," "the contradictions have already been flagged," and "the synthesis already reflects everything you've read." Neither is strictly superior: the wiki wins on coherence and compounding effort for bounded, much-revisited corpora, while RAG wins on scale and freshness for large or fast-changing ones.

## How it shows up

The two approaches make a clean tradeoff along a few axes.

- **When synthesis happens.** RAG: at query time, regenerated per question. Wiki: at compile time (ingest), written down once and reused.
- **What persists between questions.** RAG: nothing but the raw chunks and an index; the synthesis is ephemeral. Wiki: the cross-references, contradiction flags, and synthesized prose all persist as files.
- **Cost profile.** RAG re-pays the synthesis cost on every query; the wiki front-loads it and amortizes it across all later reads.

Where RAG wins, per the [[wiki/sources/karpathy-llm-wiki|Atlan analysis]] of LLM-wiki limits:

- **Corpus scale.** A wiki's index eventually outgrows the context window (roughly 50-100k tokens of index before it stops fitting), while RAG retrieves only the chunks it needs and scales to far larger corpora.
- **Freshness.** When raw sources change, a wiki does not auto-propagate the update; pages go stale and must be re-linted. RAG re-retrieves current chunks each time.
- **Access control.** A flat markdown wiki has no per-document permissions; RAG systems can filter retrieval by entitlement.

The practical reading is that the two compose: use a wiki for the curated core you revisit constantly, and reach for RAG when the corpus is too big, too fresh, or too access-sensitive to compile by hand.

## Related concepts

- [[wiki/concepts/llm-wiki-pattern]] - the compile-time pattern this page contrasts against RAG.
- [[wiki/concepts/research-discipline]] - why grounding ingest in real sources matters more when synthesis is persisted rather than regenerated.
- [[wiki/concepts/knowledge-graph-graphrag]] - GraphRAG as a retrieval approach that adds relational structure on the RAG side.
- [[wiki/moc/second-brain-pattern]] - the map of content situating this comparison.

## Sources

- [[wiki/sources/karpathy-llm-wiki]] - Andrej Karpathy, "LLM Wiki" gist. https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f (primary; source of the "rediscovering knowledge from scratch" framing and the compile-time synthesis quotes).
- Atlan, "LLM Wiki vs RAG Knowledge Base." https://atlan.com/know/llm-wiki-vs-rag-knowledge-base/ (secondary analysis; source of the limits where RAG wins: index outgrowing the context window at ~50-100k tokens, no access control, no auto-propagation on source change, manual freshness lint).
