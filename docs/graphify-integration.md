# graphify Integration (BSB §3.4)

How [graphify](https://github.com/safishamsi/graphify) plugs into the Brain. graphify takes a folder of mixed inputs (code, docs, papers, images, video) and builds a persistent knowledge graph with an explicit audit trail. In BSB it is the *traversal* layer: where the wiki tells you what a concept means and `qmd` finds *which* note, graphify answers *how* entities relate — which hubs dominate the corpus, which clusters exist, and which cross-links the wiki is still missing. Its output feeds four concrete signals into the lint loop, so the graph does not just visualize the brain, it tells the brain what to fix next.

## What graphify produces

graphify writes everything under `graphify-out/`. The three artifacts that matter for BSB:

- `graph.json` — the full graph in a GraphRAG-compatible shape (nodes, edges, communities, metadata). This is the machine-readable source of truth that `scripts/graphify_sync.py` parses.
- `GRAPH_REPORT.md` — the human-readable digest: god nodes, communities, surprising connections, suggested questions.
- `graph.html` — a standalone interactive visualization for browsing by eye.

The analytical concepts graphify surfaces:

- **God nodes** — the highest-degree hub nodes. These are the concepts everything else connects to. If a god node has no wiki page, that is a structural gap.
- **Leiden communities** — clusters found via the Leiden community-detection algorithm. Each cluster is a candidate topic area / MOC.
- **Surprising connections** — edges between nodes that are topologically close but were not obviously related, i.e. cross-links the author likely has not written yet.
- **Suggested questions** — open questions the graph implies, useful as roadmap seeds.
- **EXTRACTED / INFERRED / AMBIGUOUS audit trail** — every edge is tagged by how it was derived. `EXTRACTED` came directly from a source, `INFERRED` was reasoned across sources, `AMBIGUOUS` is low-confidence. This tagging is what makes the graph safe to act on and is consumed by the self-healing loop (§3.6).

graphify is built on Karpathy's `/raw` convention (see [the LLM Wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)), so it reads the same raw-source folder the rest of BSB already maintains.

## Install on Windows

graphify is published on PyPI under the package name `graphifyy` (double-y), while the CLI it installs is `graphify`. Install it as an isolated tool with `uv`:

```powershell
uv tool install graphifyy
```

Pull in the extras you need (PDF/office parsing, the Leiden algorithm, the MCP server):

```powershell
uv tool install "graphifyy[pdf,office,leiden,mcp]"
```

**No API key inside Claude Code.** When graphify runs inside a Claude Code session, the host session *is* the LLM, so no key is required for graph construction. `GEMINI_API_KEY` / `GOOGLE_API_KEY` are only needed for headless extraction outside a Claude Code session.

## Build and refresh — drive it through the skill

There is a known caveat (graphify issue #514): the bare shell CLI is **subcommand-only** — invoking it as a plain command without a subcommand does not behave as a top-level entrypoint. In BSB you therefore drive graphify through the `/graphify` skill rather than calling the bare CLI for graph builds. Conceptually the skill runs:

- `graphify .` — build the graph from the current folder (the raw-source tree).
- `--update` — incremental refresh; reprocess only what changed instead of rebuilding from scratch.
- `--watch` — keep the graph live during a working session, refreshing as files change.
- `graphify add <url>` — fetch a URL, save it into the raw-source folder, and update the graph in one step.

```text
/graphify .            # full build
/graphify . --update   # incremental refresh
/graphify . --watch    # live refresh during a session
```

Run a build after any substantial ingest; run `--update` on a normal lint pass; use `--watch` only during an active editing session.

## The four feedback signals into the lint loop

This is the core of the integration. Each graphify output maps to one lint action, and `scripts/graphify_sync.py` parses `graph.json` / `GRAPH_REPORT.md` to automate the mapping:

1. **God nodes -> stub the missing hub pages.** For every god node without a corresponding `wiki/concepts/<slug>` (or `wiki/entities/<slug>`) page, create a `status: stub` page. The most-connected ideas must have a home.
2. **Surprising connections -> add See-also cross-links.** Each surprising-connection edge becomes a candidate `[[wiki/...]]` cross-link added to the relevant pages' See-also sections.
3. **Orphan nodes -> tag `#needs-link`.** Nodes with no (or near-no) edges indicate isolated content; the corresponding pages get tagged `#needs-link` so a later pass can wire them in.
4. **Suggested questions -> roadmap open questions.** graphify's suggested questions are appended to [[roadmap]] as open questions to research.

`scripts/graphify_sync.py` reads the graph artifacts and emits the stubs/tags/roadmap entries, so the loop is mechanical rather than manual.

## Relational queries and the MCP server

Beyond build/refresh, graphify exposes relational query verbs for interrogating the graph directly:

- `graphify query "<question>"` — ask a question answered by graph traversal (GraphRAG-style), not flat retrieval.
- `graphify path <a> <b>` — find the connection path between two entities.
- `graphify explain <edge>` — explain why an edge exists, including its EXTRACTED/INFERRED/AMBIGUOUS provenance.

The `--mcp` server exposes these to an MCP client (including Claude Code), so the graph becomes a live tool the assistant can call mid-session rather than a static report.

## Outputs, the Obsidian export, and gitignore

graphify can emit several optional outputs: `--obsidian`, `--wiki`, `--neo4j`, `--falkordb`, `--mcp`, `--watch`, `--update`.

**Never let graphify write into `wiki/`.** The BSB `wiki/` tree is hand-curated and source-graded. When you want an Obsidian-shaped view, emit `--obsidian` to a *separate, read-only* vault at `graphify-out/obsidian/`, and treat it as a generated artifact you browse — not as canonical pages. Do not point `--obsidian` (or `--wiki`) at the real `wiki/` directory.

**gitignore policy:** commit the two artifacts that are small, reviewable, and useful in history — `graph.json` (the GraphRAG source of truth) and `GRAPH_REPORT.md` (the human digest). Ignore everything else graphify generates, including `graph.html`, the `--obsidian` vault, and any database exports.

```gitignore
# graphify
graphify-out/*
!graphify-out/graph.json
!graphify-out/GRAPH_REPORT.md
```

## Query depth — scale read-depth to task breadth (validated 2026-06-19)

The graph makes querying far cheaper by pointing straight at the answer-bearing pages and eliminating the `index.md`
re-read. But on a **broad, "use everything" synthesis task** (e.g. "design a full spec citing every relevant page"),
a single keyword `graphify query` + reading the top few hits **under-reads** and misses required citations. Measured
on a real 368-page vault: a naive graph query reached only partial coverage on the broadest task; the strategy below
lifted it to parity with reading the whole corpus — at ~38% fewer tokens and without ever reading `index.md`.

Use it for any broad / comprehensive / design question:

1. **Query per sub-topic, not once.** Decompose the question into its parts and run one `graphify query "<part>"` per
   part, so each part's relevant concept pages surface.
2. **Traverse from concept to exemplar.** A concept page alone is not enough — every principle should be backed by a
   concrete example the wiki documents. For each key concept, run `graphify explain "<Concept>"` (or
   `graphify path "<Concept>" "<Example>"`) to list its **direct neighbours**, and read + cite the specific
   case-study page that exemplifies it (the game, the source, the failure case), not just the abstraction.
3. **Completeness check before answering.** For each required part of the question confirm: a grounded page, a
   concrete example, and the documented failure mode it guards against. Re-query / `explain` for anything still
   missing, and read those pages.
4. **Don't over-prune.** A narrow read budget is for narrow questions. A graph that lets you read 12 pages instead of
   23 is only a win if those 12 still cover the answer.

Narrow/single-fact and standard multi-hop questions do **not** need this — one or two queries + the named pages is
both cheaper and complete. Reserve the per-sub-topic + `explain` + completeness-check pass for genuinely broad tasks.

## Sources

- graphify repository — https://github.com/safishamsi/graphify
- graphify README (raw) — https://raw.githubusercontent.com/safishamsi/graphify/main/README.md
- graphify on PyPI (package `graphifyy`) — https://pypi.org/project/graphifyy/
- Andrej Karpathy, "LLM Wiki" gist (the `/raw` convention and the wiki pattern graphify builds on) — https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
