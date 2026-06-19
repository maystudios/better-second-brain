# Graph Report - .  (2026-06-19)

## Corpus Check
- Corpus is ~9,785 words - fits in a single context window. You may not need a graph.

## Summary
- 22 nodes · 116 edges · 4 communities
- Extraction: 99% EXTRACTED · 1% INFERRED · 0% AMBIGUOUS · INFERRED: 1 edges (avg confidence: 0.85)
- Token cost: 0 input · 95,368 output

## Community Hubs (Navigation)
- [[_COMMUNITY_LLM Wiki & Karpathy Origins|LLM Wiki & Karpathy Origins]]
- [[_COMMUNITY_Tooling Stack graphifyqmdObsidian|Tooling Stack: graphify/qmd/Obsidian]]
- [[_COMMUNITY_BSB Architecture & GraphRAG|BSB Architecture & GraphRAG]]
- [[_COMMUNITY_PKM Prior Art PARA & Zettelkasten|PKM Prior Art: PARA & Zettelkasten]]

## God Nodes (most connected - your core abstractions)
1. `Second Brain Pattern (Map of Content)` - 20 edges
2. `LLM Wiki Pattern` - 19 edges
3. `BSB Architecture (Map of Content)` - 16 edges
4. `BSB Quickstart` - 14 edges
5. `Andrej Karpathy - LLM Wiki (gist)` - 13 edges
6. `Knowledge Graph and GraphRAG` - 12 edges
7. `RAG vs LLM Wiki` - 11 edges
8. `graphify` - 11 edges
9. `graphify - repository and README (safishamsi/graphify)` - 11 edges
10. `qmd - repository (tobi/qmd)` - 11 edges

## Surprising Connections (you probably didn't know these)
- `Maps of Content` --conceptually_related_to--> `PARA Method`  [INFERRED]
  wiki/concepts/maps-of-content.md → wiki/entities/tiago-forte.md
- `BSB Architecture (Map of Content)` --references--> `BSB Quickstart`  [EXTRACTED]
  wiki/moc/bsb-architecture.md → wiki/cheatsheets/second-brain/bsb-quickstart.md
- `BSB Quickstart` --references--> `Knowledge Graph and GraphRAG`  [EXTRACTED]
  wiki/cheatsheets/second-brain/bsb-quickstart.md → wiki/concepts/knowledge-graph-graphrag.md
- `BSB Quickstart` --references--> `LLM Wiki Pattern`  [EXTRACTED]
  wiki/cheatsheets/second-brain/bsb-quickstart.md → wiki/concepts/llm-wiki-pattern.md
- `BSB Quickstart` --references--> `RAG vs LLM Wiki`  [EXTRACTED]
  wiki/cheatsheets/second-brain/bsb-quickstart.md → wiki/concepts/rag-vs-llm-wiki.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **BSB tool stack (graphify + qmd + Obsidian over the LLM wiki)** - entities_graphify_graphify, entities_qmd_qmd, entities_obsidian_obsidian, concepts_llm_wiki_pattern_llm_wiki_pattern [EXTRACTED 0.85]
- **Knowledge-management prior-art lineage feeding the LLM wiki pattern** - concepts_memex_memex, concepts_zettelkasten_zettelkasten, concepts_llm_wiki_pattern_llm_wiki_pattern [INFERRED 0.85]
- **Compile-time wiki vs query-time RAG trade-off and its grounding gate** - concepts_rag_vs_llm_wiki_rag_vs_llm_wiki, concepts_llm_wiki_pattern_llm_wiki_pattern, concepts_research_discipline_research_discipline, concepts_knowledge_graph_graphrag_knowledge_graph_graphrag [INFERRED 0.75]

## Communities (4 total, 0 thin omitted)

### Community 0 - "LLM Wiki & Karpathy Origins"
Cohesion: 0.90
Nodes (7): LLM Wiki Pattern, Memex, RAG vs LLM Wiki, Andrej Karpathy, Second Brain Pattern (Map of Content), Andrej Karpathy - LLM Knowledge Bases (X post), Andrej Karpathy - LLM Wiki (gist)

### Community 1 - "Tooling Stack: graphify/qmd/Obsidian"
Cohesion: 1.00
Nodes (6): graphify, Obsidian, qmd, BSB Quickstart, Obsidian Bases - documentation, qmd - repository (tobi/qmd)

### Community 2 - "BSB Architecture & GraphRAG"
Cohesion: 1.00
Nodes (5): Knowledge Graph and GraphRAG, Research Discipline, BSB Architecture (Map of Content), graphify - repository and README (safishamsi/graphify), Is a Better Second Brain better than a vanilla LLM Wiki?

### Community 3 - "PKM Prior Art: PARA & Zettelkasten"
Cohesion: 0.83
Nodes (4): Maps of Content, PARA Method, Zettelkasten, Tiago Forte

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Second Brain Pattern (Map of Content)` connect `LLM Wiki & Karpathy Origins` to `Tooling Stack: graphify/qmd/Obsidian`, `BSB Architecture & GraphRAG`, `PKM Prior Art: PARA & Zettelkasten`?**
  _High betweenness centrality (0.146) - this node is a cross-community bridge._
- **Why does `LLM Wiki Pattern` connect `LLM Wiki & Karpathy Origins` to `Tooling Stack: graphify/qmd/Obsidian`, `BSB Architecture & GraphRAG`, `PKM Prior Art: PARA & Zettelkasten`?**
  _High betweenness centrality (0.127) - this node is a cross-community bridge._
- **Why does `Maps of Content` connect `PKM Prior Art: PARA & Zettelkasten` to `LLM Wiki & Karpathy Origins`, `Tooling Stack: graphify/qmd/Obsidian`, `BSB Architecture & GraphRAG`?**
  _High betweenness centrality (0.073) - this node is a cross-community bridge._