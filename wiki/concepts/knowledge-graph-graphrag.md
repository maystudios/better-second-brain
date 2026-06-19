---
type: concept
name: Knowledge Graph and GraphRAG
aliases:
  - knowledge graph
  - GraphRAG
  - graph retrieval
tags:
  - knowledge-management
  - knowledge-graph
  - graphrag
  - retrieval
  - second-brain
sources:
  - "[[wiki/sources/safishamsi-graphify]]"
created: 2026-06-19
updated: 2026-06-19
status: complete
---

# Knowledge Graph and GraphRAG

A knowledge graph represents a corpus as entities (nodes) joined by typed relationships (edges), so that questions can be answered by *traversing* connections rather than only matching text. GraphRAG is retrieval-augmented generation that retrieves over such a graph: instead of pulling isolated chunks, it pulls connected subgraphs, which lets a model answer multi-hop questions ("how does A relate to C via B?") and summarize whole communities of related nodes. Where a flat wiki tells you *which note* to read, a knowledge graph tells you *how the entities relate*, making it the natural complement to the LLM wiki pattern for relational and exploratory questions.

## How it shows up

[[wiki/sources/safishamsi-graphify|graphify]] is a concrete embodiment: it turns a folder of code, docs, papers, images, and video into a persistent knowledge graph and emits its outputs into a `graphify-out/` directory (`graph.html` for browsing, `graph.json` in a GraphRAG-friendly shape, and a `GRAPH_REPORT.md` summary). The graph it builds surfaces several structures characteristic of knowledge-graph analysis:

- **God nodes** — the highest-degree hub entities, the nodes that connect to the most others and therefore anchor the corpus.
- **Communities** — clusters of densely interlinked nodes found with Leiden community detection, each a coherent topic region of the graph.
- **Surprising connections and suggested questions** — edges or paths the system flags as non-obvious, plus questions the graph is well-positioned to answer, which support exploration rather than lookup.
- **Multi-hop traversal** — the ability to follow chains of edges (A to B to C) to answer questions no single chunk contains.

graphify also keeps an audit trail, labeling each extracted relationship as EXTRACTED (stated in a source), INFERRED (derived), or AMBIGUOUS (uncertain), which keeps the graph honest about provenance. It is built on Karpathy's `/raw` convention, so it sits alongside the wiki over the same source set; `graphify add <url>` saves a new source to raw and updates the graph. Inside Claude Code the host session acts as the extracting LLM (no API key needed); `GEMINI_API_KEY` / `GOOGLE_API_KEY` are only required for headless extraction. Per project issue #514, the bare shell CLI is subcommand-only, so in practice the graph is driven through the `/graphify` skill rather than free-form commands.

## Related concepts

- [[wiki/concepts/llm-wiki-pattern]] — the prose-synthesis layer the graph complements with relational structure.
- [[wiki/concepts/rag-vs-llm-wiki]] — GraphRAG as the retrieval side of that contrast, with graph structure added.
- [[wiki/concepts/maps-of-content]] — hand-curated hubs that play a role analogous to god nodes for human navigation.
- [[wiki/moc/second-brain-pattern]] — the map of content for the pattern family.
- [[wiki/moc/bsb-architecture]] — where graph retrieval fits in the BSB stack.

## Sources

- [[wiki/sources/safishamsi-graphify]] — graphify. https://github.com/safishamsi/graphify ; README https://raw.githubusercontent.com/safishamsi/graphify/main/README.md ; PyPI https://pypi.org/project/graphifyy/ (primary; source of god nodes, Leiden communities, surprising connections, suggested questions, the EXTRACTED/INFERRED/AMBIGUOUS audit trail, the `graphify-out/` outputs, the `/raw` convention, and the issue #514 subcommand-only caveat).
