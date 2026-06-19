---
type: entity
name: Obsidian
entity-kind: tool
aliases: [obsidian.md]
tags: [pkm, markdown, notes, obsidian, bases]
sources:
  - "[[wiki/sources/obsidian-bases]]"
created: 2026-06-19
updated: 2026-06-19
status: verified
---

# Obsidian

Obsidian is a desktop and mobile personal knowledge management (PKM) application that stores notes as plain markdown files in a local vault, with wikilinks and a graph view connecting them. In the Second Brain pattern it serves as the human reader: the place a person browses, links, and reviews the markdown the LLM maintains. Its core "Bases" plugin adds database-like views (Table, Card, List) computed from note frontmatter, turning a folder of notes into a queryable database without leaving markdown.

## Facts

- Notes are plain markdown in a local vault, so the same files are readable and writable by other tools (the LLM, graph builders, search CLIs).
- "Bases" shipped as a core plugin in Obsidian 1.9 (desktop release 2025-05-21). Changelog: https://obsidian.md/changelog/2025-05-21-desktop-v1.9.0/ .
- A `.base` file is plain YAML defining filters, formulas, properties, and views; it renders DB-like Table / Card / List views over note frontmatter. Help: https://obsidian.md/help/bases , syntax: https://obsidian.md/help/bases/syntax .
- Bases is reported to stay fast even at large vault sizes (on the order of 50k notes).
- Dataview is the older community-plugin alternative that reads the same frontmatter via its own query language; Bases is the newer built-in approach.

## Relationships

- Renders frontmatter-driven views that operationalize [[wiki/concepts/maps-of-content]].
- The human-facing reader for notes produced under the [[wiki/concepts/llm-wiki-pattern]].
- Receives graph exports from [[wiki/entities/graphify]] via its `--obsidian` flag.
- Its markdown vaults are the corpus searched by [[wiki/entities/qmd]].
- Part of [[wiki/moc/bsb-architecture]] and supports [[wiki/moc/second-brain-pattern]].

## Sources

- Obsidian Bases (help): https://obsidian.md/help/bases — primary, fetchable.
- Bases syntax: https://obsidian.md/help/bases/syntax — primary.
- Obsidian 1.9 desktop changelog (Bases shipped as core plugin, 2025-05-21): https://obsidian.md/changelog/2025-05-21-desktop-v1.9.0/ — primary.
- See [[wiki/sources/obsidian-bases]].
