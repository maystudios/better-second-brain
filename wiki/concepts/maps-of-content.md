---
type: concept
name: Maps of Content
aliases:
  - MOC
  - map of content
  - hub note
tags:
  - knowledge-management
  - navigation
  - second-brain
  - obsidian
sources:
  - "[[wiki/sources/obsidian-bases]]"
created: 2026-06-19
updated: 2026-06-19
status: complete
---

# Maps of Content

A Map of Content (MOC) is a hand-curated hub note whose job is to gather and order links to other notes on a theme, giving a knowledge base human-navigable entry points instead of relying on search or graph traversal alone. In a growing wiki, most pages are leaves; MOCs are the deliberately maintained intersections that let a reader (or model) start broad and drill down. They also serve graph health: by linking out to many related pages, an MOC reduces orphan notes and keeps the link graph connected, which is why BSB requires every source, concept, and entity page to link to at least one MOC.

## How it shows up

MOCs are a navigation layer rather than a content layer. A few characteristic uses:

- **Topic hubs.** A single page like [[wiki/moc/second-brain-pattern]] enumerates the concepts, sources, and entities that make up a pattern family, so a newcomer has one place to begin.
- **Architecture maps.** [[wiki/moc/bsb-architecture]] orders pages by how the system is built rather than by topic, acting as a structural index.
- **Graph-health anchors.** Because MOCs link outward to many pages, they pull otherwise-isolated notes into the connected component of the graph.

MOCs complement organizing schemes rather than replacing them. Tiago Forte's [[wiki/sources/obsidian-bases|PARA method]] sorts notes by actionability into Projects, Areas, Resources, and Archives - "organize it according to the projects and goals you are committed to right now" - which answers *where a note lives*; an MOC answers *how related notes connect for reading*. In Obsidian practice, MOCs are typically plain notes full of wikilinks, and they pair naturally with [[wiki/sources/obsidian-bases|Obsidian Bases]], where a `.base` file can generate a Table, Card, or List view over note frontmatter to produce a dynamic, query-driven complement to the hand-written hub. The two coexist: the MOC supplies curated narrative order, the base supplies an always-current generated view.

## Related concepts

- [[wiki/concepts/llm-wiki-pattern]] - the wiki that MOCs make navigable as it grows.
- [[wiki/concepts/zettelkasten]] - the prior-art note system whose dense links MOCs help organize at a higher level.
- [[wiki/concepts/knowledge-graph-graphrag]] - automated hubs (god nodes) versus the hand-curated hubs MOCs provide.
- [[wiki/moc/second-brain-pattern]] - the principal MOC for this knowledge base.

## Sources

- [[wiki/sources/obsidian-bases]] - Obsidian Bases. https://obsidian.md/help/bases ; syntax https://obsidian.md/help/bases/syntax ; shipped as a core plugin in Obsidian 1.9 (desktop, 2025-05-21) https://obsidian.md/changelog/2025-05-21-desktop-v1.9.0/ (primary; the `.base` YAML view mechanism over frontmatter that complements hand-written MOCs).
- Tiago Forte, "The PARA Method." https://fortelabs.com/blog/para/ (secondary; the Projects/Areas/Resources/Archives organizing scheme and the "organize it according to the projects and goals you are committed to right now" framing. Note: this page does not itself define MOCs, which are described here as general PKM practice.)
