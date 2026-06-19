# Why BSB Is Better Than a Plain Karpathy LLM Wiki

BSB (Second Brain) starts from Andrej Karpathy's "LLM Wiki" pattern and closes the three gaps that pattern leaves open: manual cross-linking, no self-improvement, and page rot. This page explains the base pattern, what BSB adds, why the research-discipline gate is the real trust differentiator, and - honestly - when you should just use vanilla Karpathy or plain RAG instead.

## 1. The Karpathy LLM Wiki pattern, and why it beats RAG

Most people use LLMs over their documents through retrieval-augmented generation (RAG). Karpathy describes the limitation directly in his LLM Wiki gist:

> Most people's experience with LLMs and documents looks like RAG: you upload a collection of files, the LLM retrieves relevant chunks at query time, and generates an answer. This works, but the LLM is rediscovering knowledge from scratch on every question.

His alternative is to have the LLM "incrementally build and maintain a persistent wiki - a structured, interlinked collection of markdown files that sits between you and the raw sources." The payoff he names:

> The cross-references are already there. The contradictions have already been flagged. The synthesis already reflects everything you've read.

In other words, the expensive synthesis work happens once, at ingest time, and is committed to disk as durable markdown - instead of being re-derived from raw chunks on every query. The wiki is a cache of understanding, not just a cache of text.

The pattern has a fixed shape: three layers (raw sources, the wiki, and a schema/lint layer), three operations (ingest, query, lint), and two meta files at the root (`index.md` as the entry point and `log.md` as the running record). BSB follows this shape exactly; see [[index]] and [[log]].

Karpathy also announced the broader idea on X ("LLM Knowledge Bases"), opening with:

> LLM Knowledge Bases. Something I'm finding very useful recently: using LLMs to build personal knowledge bases for various topics of research interest...

A note on evidence: the gist (the canonical pattern document) is publicly fetchable and the quotes above are verbatim. The X post is the primary announcement but x.com is typically behind a login wall and not reliably fetchable; we cite it as the announcement and corroborate the substance through the gist. Figures circulated in community discussion (for example ~100 articles / ~400k words, ~16M views, ~95% token reduction) are **community claims**, not numbers stated verbatim in the primary sources, and should be treated as such.

Why the pattern beats RAG, summarized:

- **Synthesis is durable.** Contradictions and cross-references are resolved once and stored, not rediscovered per query.
- **It is auditable.** The wiki is plain markdown you can read, diff, and version-control.
- **It is cheaper at query time.** A well-built index answers many questions without re-reading the raw corpus (the basis of the community-claimed token reductions).

## 2. The three gaps - and the BSB answer to each

The base pattern is excellent, but it assumes a diligent human (or a perfectly diligent agent) keeps doing three things forever. In practice three gaps open up.

### Gap A: Manual cross-linking

Karpathy's claim that "the cross-references are already there" only holds if someone actually created them. As a wiki grows, the highest-value links - the non-obvious connection between two pages written months apart - are exactly the ones a human forgets to make. The graph silently degrades into disconnected islands.

**BSB answer: a real knowledge graph from graphify.** BSB runs the same `raw/` folder through [[wiki/sources/graphify|graphify]], which builds a persistent knowledge graph: god nodes (the highest-degree hub entities), Leiden community detection, surprising connections between distant entities, and suggested questions. Crucially graphify ships an EXTRACTED / INFERRED / AMBIGUOUS audit trail on every edge, so an inferred link is never silently presented as a stated fact. The graph is mechanically derived and re-derivable, so cross-linking no longer depends on anyone remembering.

### Gap B: No self-improvement

A vanilla wiki is only ever as good as the last manual ingest. It does not notice that a page is thin, that two pages disagree, or that a claim was never sourced. Improvement is entirely operator-initiated.

**BSB answer: an auto-research improve loop.** BSB pairs the wiki with an autonomous research loop that finds the weakest pages (stubs, unsourced assertions, contradictions flagged by lint), researches them against real sources, and rewrites them - then re-scores. The wiki gets better between your sessions instead of decaying between them.

### Gap C: Page rot

Markdown does not know when the world changed. A page that was correct at ingest quietly becomes wrong when the underlying source ships a new version, and nothing flags it. Karpathy's pattern relies on manual lint to catch this.

**BSB answer: self-healing lint.** BSB's lint layer treats freshness as a first-class signal: pages carry their sources and review dates, and the lint/heal pass flags pages whose primaries have moved on, contradictions that re-emerged, and links that broke - and can queue them for the improve loop. Rot is detected, not endured.

## 3. The research-discipline gate: the real trust differentiator

The features above are only worth anything if you can trust the output. The thing that separates BSB from "an LLM that confidently writes markdown" is the **research-discipline gate** (CLAUDE.md §1.5): every page must be grounded in real, cited sources, never written from memory alone.

Concretely the gate enforces:

- **Real URLs only.** Every assertion traces to a fetchable source. If a claim cannot be supported, it is not asserted - the page is marked `status: stub` and explicitly states what is missing.
- **Primary vs. secondary separation.** A primary source (the author's own gist, the project's README) is distinguished from secondary/community coverage, so the reader knows the provenance of each claim.
- **No fabricated quotes.** Quotes are verbatim from a verified source or they do not appear.

This is the inverse of the usual LLM failure mode. A plain wiki built by an unconstrained agent inherits the model's hallucinations and freezes them into "durable synthesis" - which is worse than RAG, because a confident wrong page outlives the conversation. The gate is what makes BSB's durability an asset rather than a liability.

## 4. When vanilla Karpathy - or plain RAG - is the better choice

BSB is not always the right tool. The honest limits of the LLM-wiki pattern are well summarized in Atlan's analysis of LLM wikis vs. RAG knowledge bases.

Use **plain RAG** instead of any wiki when:

- **Your corpus is large.** The wiki's index has to fit in the context window to be useful as an entry point; once it outgrows roughly 50k-100k tokens it stops fitting, and RAG scales far better to huge corpora.
- **You need access control.** The wiki is flat markdown with no per-page permissions; RAG systems can enforce row/document-level access.
- **You need concurrency and auto-propagation.** When many writers or automated sources change the underlying data continuously, RAG re-indexes; a wiki needs a manual (or, in BSB, a scheduled) pass to propagate changes, and there is no built-in concurrency control on the markdown files.

Use **vanilla Karpathy** (the base pattern, without BSB's extra layers) when:

- The corpus is small and stable, and a single diligent maintainer is genuinely keeping links and freshness current by hand.
- You want zero extra dependencies - no graphify, no lint hooks, no improve loop - and value the simplicity over the automation.
- You are doing a one-off research project that will not be maintained, where rot and self-improvement simply do not matter.

BSB earns its complexity exactly when a wiki is meant to **live**: maintained over time, by an agent as much as a human, where unlinked islands, stale pages, and unsourced claims would otherwise accumulate. If that is not your situation, prefer the simpler tool.

## Sources

- Karpathy, "LLM Wiki" gist (primary, canonical pattern document) - https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- Karpathy, "LLM Knowledge Bases" X post (primary announcement; not reliably fetchable behind login wall, cited as announcement) - https://x.com/karpathy/status/2039805659525644595
- graphify (project) - https://github.com/safishamsi/graphify ; README - https://raw.githubusercontent.com/safishamsi/graphify/main/README.md
- Atlan, "LLM Wiki vs RAG Knowledge Base" (secondary analysis of limits) - https://atlan.com/know/llm-wiki-vs-rag-knowledge-base/
