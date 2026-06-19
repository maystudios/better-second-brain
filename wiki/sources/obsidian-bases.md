---
type: source
title: "Obsidian Bases — documentation"
source-url: https://obsidian.md/help/bases
source-kind: docs
author: Obsidian
published: 2025-05-21
ingested: 2026-06-19
created: 2026-06-19
updated: 2026-06-19
tags: [obsidian, database-views, frontmatter, tooling, primary-source]
status: verified
---

# Obsidian Bases — documentation

Obsidian Bases is a core plugin that turns any set of notes into a database-like view, letting you view, edit, sort, and filter files and their properties. A Base is configured in plain YAML (filters, formulas, properties, and views) and can live as a standalone `.base` file or be embedded in a Markdown code block; all underlying data stays in your local Markdown files and their frontmatter properties. Bases shipped as a core plugin in Obsidian 1.9 (desktop, 2025-05-21) and remains fast at large vault sizes. In the BSB pattern it is the structured-view layer over the wiki's frontmatter — the practical, no-code answer to "show me every source page ingested this month."

## Key claims

- Bases is a core plugin that "lets you create database-like views of your notes" — view, edit, sort, and filter files and their properties.
- All data lives in local Markdown files and their properties (frontmatter); Bases does not create a separate database.
- A configuration is written in YAML and can be saved as a `.base` file or embedded in a code block inside a Markdown note. The syntax covers filters, formulas, properties, and views (see the syntax reference).
- View types include Table (rows/columns of file properties), List, Cards (gallery/grid, image-capable), and Map (pins).
- Introduced as a new core plugin in Obsidian 1.9.0 desktop, released 2025-05-21.
- Dataview is the older community alternative that reads the same note frontmatter; Bases is the built-in, performance-oriented successor and is reported to stay fast even at very large vault sizes (~50k notes).

## Notable quotes

> Bases is a core plugin that lets you create database-like views of your notes.

> Introducing Bases, a new core plugin that lets you turn any set of notes into a powerful database.

(The second quote is from the Obsidian 1.9.0 desktop changelog, 2025-05-21.)

## Connections

- A feature of the [[wiki/entities/obsidian]] application; provides structured views for the [[wiki/concepts/llm-wiki-pattern]] (acting like a queryable `index.md`).
- Reads the same frontmatter that [[wiki/entities/qmd]] searches and that [[wiki/entities/graphify]] can export to.
- Relates to [[wiki/concepts/maps-of-content]] as a generated, filterable alternative to hand-maintained MOCs.
- Part of the [[wiki/moc/bsb-architecture]] and the [[wiki/moc/second-brain-pattern]].

## Sources

- https://obsidian.md/help/bases (primary documentation; fetched 2026-06-19)
- https://obsidian.md/help/bases/syntax (primary; YAML syntax reference)
- https://obsidian.md/changelog/2025-05-21-desktop-v1.9.0/ (primary; core-plugin release announcement, fetched 2026-06-19)
