---
type: cheatsheet
topic: "Set up and run a Better Second Brain"
area: second-brain
when-to-use: "When you want to stand up a BSB vault from scratch: ingest your first sources, build the graph, and start asking grounded questions inside Claude Code + Obsidian."
related-topics:
  - "[[wiki/concepts/llm-wiki-pattern]]"
  - "[[wiki/concepts/knowledge-graph-graphrag]]"
  - "[[wiki/concepts/research-discipline]]"
  - "[[wiki/moc/bsb-architecture]]"
stack-versions:
  obsidian: "1.9+"
  graphifyy: "latest"
  node: "for qmd"
sources:
  - name: "Karpathy - LLM Wiki gist"
    url: "https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f"
  - name: "graphify"
    url: "https://github.com/safishamsi/graphify"
  - name: "Obsidian Bases"
    url: "https://obsidian.md/help/bases"
  - name: "qmd"
    url: "https://github.com/tobi/qmd"
tags: [cheatsheet, second-brain, bsb, setup]
created: 2026-06-19
updated: 2026-06-19
status: active
---

# BSB Quickstart

A practical cheatsheet for standing up and running a Better Second Brain (BSB): a vault that follows Karpathy's LLM Wiki pattern ([[wiki/sources/karpathy-llm-wiki]]) and adds a graph layer (graphify, [[wiki/sources/safishamsi-graphify]]), local search (qmd, [[wiki/sources/tobi-qmd]]), and Obsidian Bases views ([[wiki/sources/obsidian-bases]]). It covers the minimal first run, the everyday operations, and the pitfalls that bite first-timers. For the architecture behind these steps, see [[wiki/moc/bsb-architecture]].

## TL;DR

Open the vault in both Obsidian and Claude Code. Drop sources into `/raw`. Ask Claude Code to ingest them into `wiki/` pages with real citations, build a graphify graph from the corpus, then query the wiki/graph instead of re-reading raw files. Every page must cite real sources or be marked `status: stub`.

## Minimal example

```bash
# 1. Get the vault
git clone <your-bsb-repo> "Second Brain"
cd "Second Brain"

# 2. Open it two ways
#    - Obsidian 1.9+: "Open folder as vault" -> point at "Second Brain"
#    - Claude Code: run `claude` from inside the vault directory

# 3. Edit CLAUDE.md section 0 (project conventions): set your wiki paths,
#    slug rules, and the research-discipline gate so ingest writes
#    grounded pages, not memory.

# 4. First ingest: drop a file or URL into /raw, then in Claude Code:
#    "Ingest raw/<file> into the wiki following the §1.5 research gate."
```

## Common patterns

```bash
# Ingest a URL (graphify saves it to raw and updates the graph)
graphify add https://example.com/article

# Ask a question (inside Claude Code: query wiki + graph, not raw)
#   "Using the wiki and graphify-out/, how does graphify relate to qmd?"

# Run a lint pass (freshness + unsupported-claim check)
#   "Lint the wiki: flag broken wikilinks and any claim without a Sources entry."

# Rebuild the graph after new ingests
graphify .            # writes graphify-out/graph.html, graph.json, GRAPH_REPORT.md
```

## API surface

The six BSB operations (detail in [[wiki/moc/bsb-architecture]]):

- Ingest - raw source to wiki pages.
- Query - answer from wiki + graph.
- Lint - freshness and gate checks.
- Graph - `graphify .` builds `graphify-out/`.
- Improve - autonomous research passes.
- Heal - auto-repair stale/broken pages.

Key graphify commands:

- `graphify .` - build a graph from the current folder.
- `graphify add <url>` - save a source to `/raw` and update the graph.
- `graphify . --obsidian` - also emit Obsidian-friendly output.
- `graphify . --update` / `--watch` - incremental / continuous rebuild.
- `graphify . --mcp` - expose the graph over MCP.

## Common pitfalls

- graphify bare CLI is subcommand-only (issue #514): running plain `graphify` without a subcommand does not do a full extract. Drive it via the `/graphify` skill, or use explicit subcommands like `graphify .` / `graphify add`. See [[wiki/sources/safishamsi-graphify]].
- Writing pages from memory violates the research-discipline gate. Every page needs a `## Sources` section with real URLs; separate primary from community claims; mark unsupported pages `status: stub`. See [[wiki/concepts/research-discipline]].
- `index.md` outgrowing the context window (~50k-100k tokens). Past that the model can no longer hold the whole map in one pass; split into Maps of Content and lean on the graph and qmd retrieval instead of one giant index. See [[wiki/concepts/rag-vs-llm-wiki]].
- Inside Claude Code the host session is the LLM, so no API key is needed; `GEMINI_API_KEY` / `GOOGLE_API_KEY` are only for headless extract. Setting them is harmless but not required interactively.
- PyPI package is `graphifyy` (double-y) but the CLI is `graphify`. Installing `graphify` from PyPI gets the wrong thing.

## Integration with the rest of the stack

- qmd ([[wiki/entities/qmd]]) finds *which* note (BM25 + vector + LLM rerank); install with `npm i -g @tobilu/qmd`. graphify ([[wiki/entities/graphify]]) finds *how* entities relate. Use qmd to locate, graphify to traverse.
- Obsidian Bases ([[wiki/entities/obsidian]]) turns the frontmatter your wiki already writes into Table/Card/List views; a `.base` file is plain YAML and stays fast even at large vaults.
- Both qmd and graphify can expose an MCP server, so Claude Code can call them as tools during Query and Graph.

## See also

- [[wiki/moc/bsb-architecture]] - the build-time architecture.
- [[wiki/moc/second-brain-pattern]] - the topic hub.
- [[wiki/syntheses/is-bsb-better-than-vanilla-llm-wiki]] - is this worth it?

## Sources

- [[wiki/sources/karpathy-llm-wiki]] - LLM Wiki pattern. https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
- [[wiki/sources/safishamsi-graphify]] - graphify, including issue #514 caveat. https://github.com/safishamsi/graphify
- [[wiki/sources/obsidian-bases]] - Bases views (Obsidian 1.9+). https://obsidian.md/help/bases
- [[wiki/sources/tobi-qmd]] - qmd local search. https://github.com/tobi/qmd
