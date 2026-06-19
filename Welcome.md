---
type: moc
title: Welcome
updated: 2026-06-19
---

# Welcome to your Better Second Brain

This is an **LLM Wiki**: an AI agent reads your sources and maintains an interlinked knowledge base so you don't
have to. You curate and ask; the agent reads, verifies, files, and cross-references. **You never write wiki pages
by hand.**

## How to use it

- **Browse** → start at [[index]] (the catalog of everything) or the Maps of Content in `wiki/moc/`.
- **See the graph** → open Obsidian's Graph view (left sidebar). Colors: green = MOC hubs, blue = sources,
  red = `#needs-link` pages that need attention.
- **Track activity** → [[log]] (what happened, newest at the bottom) and [[roadmap]] (what's planned).
- **Ingest** → drop a file into `raw/`, or tell the agent *"ingest this link: …"*. It writes a source page and
  updates everything the source touches.
- **Ask** → *"what does the wiki say about X?"* — the agent answers with citations and offers to save good answers
  as new pages.
- **Keep healthy** → say *"lint"* now and then. With graphify installed, say *"rebuild the graph"* to surface
  missing hubs and surprising connections.

## What makes this one "better"

It refuses to write a page from the model's memory — every page is grounded in real, fetched sources (≥ 3 for a
reference page). It builds an actual knowledge **graph** over your notes (graphify), it **improves its own rules**
over time (auto-research), and it **re-checks and fixes itself** when sources change (self-healing). See
[[README]] and [[CLAUDE]] for the full story.

## The rules the agent follows

The schema lives in [[CLAUDE]]. Read it if you want to understand or change how the brain behaves. Per-instance
settings (domain, link style, thresholds) are in [[bsb.config]].

*You can delete this Welcome page once it's all second nature.*
