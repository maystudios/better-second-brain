---
type: concept
name: Research Discipline
aliases:
  - research-discipline gate
  - grounding gate
  - no-page-from-memory rule
tags:
  - knowledge-management
  - second-brain
  - principle
  - bsb
sources:
  - "[[wiki/sources/karpathy-llm-wiki]]"
created: 2026-06-19
updated: 2026-06-19
status: complete
---

# Research Discipline

Research discipline is BSB's core authoring gate: a page is grounded in real, fetched sources or it is not written. In practice this means no page is produced from the model's training memory alone; claims are tied to cited URLs, primary sources are kept separate from secondary or community claims, and an unsupported claim is either dropped or the page is marked `status: stub` with an explicit note of what is missing. The rationale is that a persistent wiki is only worth more than nothing if its contents are more trustworthy than what a model would regenerate on demand; a page that merely restates re-derivable model output adds maintenance burden without adding verified knowledge. This is a deliberate design stance of BSB, not a claim made by any of the cited upstream sources.

## How it shows up

The discipline follows from the [[wiki/concepts/llm-wiki-pattern|LLM wiki pattern]]'s central promise. The value of a compiled wiki, in Karpathy's framing, is that "the synthesis already reflects everything you've read" and that contradictions "have already been flagged." That promise only holds if what was read was real: synthesis over hallucinated inputs flags no genuine contradictions and reflects nothing you actually read. So the pattern's payoff is contingent on grounding, which is exactly what this gate enforces.

Concretely, BSB applies the gate as:

- **No page from training memory.** Every assertion traces to a source that was actually fetched, not to recalled facts.
- **A minimum sourcing bar.** Aim for at least three independently fetched sources behind a substantive page; below that bar, mark it `status: stub` and state the gap rather than padding it.
- **Primary vs secondary separation.** Verbatim quotes and figures from primary sources are cited as such; community-attributed numbers or claims are labeled as community claims and never promoted to fact.
- **Honest absence.** If a claim cannot be supported, it is left out. A short, honest page beats a long, confident, unverifiable one.

The freshness limits noted in the [[wiki/concepts/rag-vs-llm-wiki|RAG comparison]] reinforce this: because a wiki does not auto-propagate when raw sources change, stale or ungrounded pages do not self-correct. Re-derivable "slop" is therefore worse than an empty page — it looks authoritative, persists by default, and must be actively caught and removed during lint. The gate keeps that failure mode out at ingest time.

## Related concepts

- [[wiki/concepts/llm-wiki-pattern]] — the pattern whose payoff depends on grounded ingest.
- [[wiki/concepts/rag-vs-llm-wiki]] — the freshness and propagation limits that make ungrounded pages persist.
- [[wiki/concepts/knowledge-graph-graphrag]] — graphify's EXTRACTED/INFERRED/AMBIGUOUS labels apply the same provenance discipline to a graph.
- [[wiki/moc/second-brain-pattern]] — the map of content for the pattern family.

## Sources

- [[wiki/sources/karpathy-llm-wiki]] — Andrej Karpathy, "LLM Wiki" gist. https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f (primary; the "synthesis already reflects everything you've read" / contradictions "already flagged" framing that this gate exists to protect).
- Atlan, "LLM Wiki vs RAG Knowledge Base." https://atlan.com/know/llm-wiki-vs-rag-knowledge-base/ (secondary; the no-auto-propagation and manual-freshness limits cited as the reason ungrounded pages persist).
- The minimum-three-sources bar and the "no page from memory" rule are BSB's own design stance (CLAUDE.md §1.5), stated here as such rather than attributed to the upstream sources.
