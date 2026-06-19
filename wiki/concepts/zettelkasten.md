---
type: concept
name: Zettelkasten
aliases:
  - slip-box
  - slip box
  - Luhmann's Zettelkasten
tags:
  - knowledge-management
  - prior-art
  - note-taking
  - second-brain
sources:
  - "[[wiki/sources/karpathy-llm-wiki]]"
created: 2026-06-19
updated: 2026-06-19
status: complete
---

# Zettelkasten

The Zettelkasten ("slip-box") is a note-taking method built from many small, atomic notes that are densely cross-referenced, most famously realized by the German sociologist Niklas Luhmann (1927–1998). Beginning in 1952–1953, Luhmann accumulated roughly 90,000 index cards, each carrying a single focused idea and a unique index number assigned by a branching hierarchical scheme, with extensive links from card to card. The result was less a filing cabinet than a thinking tool: a semantic network in which unexpected connections could surface. It is direct prior art for the LLM wiki pattern, which likewise prizes small interlinked units of knowledge and the cross-references between them over monolithic documents.

## How it shows up

The features that make the Zettelkasten relevant to a second brain are structural, and they map closely onto modern practice.

- **Atomic notes.** Each card holds one idea, so notes can be recombined and linked freely rather than being trapped inside long documents — the same impulse behind small, single-topic wiki pages.
- **Dense cross-referencing.** Cards reference other cards by their index numbers, building "dense semantic networks of interconnected thoughts." This is the analog of wikilinks between wiki pages.
- **Stable unique identifiers.** Luhmann's branching numbers gave every card a permanent address that new cards could attach to without reorganizing the whole box — comparable to stable slugs and kebab-case filenames in a markdown wiki.
- **Emergent structure over imposed taxonomy.** Order arose from links accumulated over decades rather than a fixed top-down hierarchy, the same way an LLM wiki grows its structure through ingest.

Luhmann credited the system with enabling his output of roughly 50 books and 550 articles, and his card collection was digitized and published online in 2019. For a second brain, the lesson is that the link graph, not the individual note, is where the value compounds.

## Related concepts

- [[wiki/concepts/memex]] — the other principal prior-art ancestor, emphasizing associative trails between records.
- [[wiki/concepts/llm-wiki-pattern]] — the modern descendant: atomic interlinked markdown maintained by an LLM.
- [[wiki/concepts/maps-of-content]] — higher-level hubs that organize a dense field of atomic notes.
- [[wiki/moc/second-brain-pattern]] — the map of content for this lineage.

## Sources

- "Zettelkasten," Wikipedia. https://en.wikipedia.org/wiki/Zettelkasten (secondary; source of the ~90,000 cards, the 1952–1953 start, the branching unique-index numbering, the atomic-note and dense-cross-reference description, the "about 50 books and 550 articles" output, and the 2019 digitization).
- [[wiki/sources/karpathy-llm-wiki]] — Andrej Karpathy, "LLM Wiki" gist. https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f (primary, for the modern pattern this prior art anticipates; the interlinked-markdown framing).
