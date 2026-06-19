# Better Second Brain (BSB)

<p align="center">
  <a href="https://github.com/maystudios/better-second-brain/stargazers"><img src="https://img.shields.io/github/stars/maystudios/better-second-brain?style=flat-square&logo=github" alt="Stars"></a>
  <a href="https://github.com/maystudios/better-second-brain/network/members"><img src="https://img.shields.io/github/forks/maystudios/better-second-brain?style=flat-square&logo=github" alt="Forks"></a>
  <a href="https://github.com/maystudios/better-second-brain/issues"><img src="https://img.shields.io/github/issues/maystudios/better-second-brain?style=flat-square" alt="Issues"></a>
  <a href="https://github.com/maystudios/better-second-brain/commits/main"><img src="https://img.shields.io/github/last-commit/maystudios/better-second-brain?style=flat-square" alt="Last commit"></a>
  <a href="./LICENSE"><img src="https://img.shields.io/github/license/maystudios/better-second-brain?style=flat-square" alt="License: MIT"></a>
  <img src="https://img.shields.io/badge/built%20on-Karpathy%20LLM%20Wiki-8A2BE2?style=flat-square" alt="Built on Karpathy's LLM Wiki">
  <img src="https://img.shields.io/badge/Obsidian-vault-7C3AED?style=flat-square&logo=obsidian&logoColor=white" alt="Obsidian vault">
  <img src="https://img.shields.io/badge/graph-graphify-2EA043?style=flat-square" alt="graphify graph layer">
</p>

> An LLM-maintained knowledge base built on Andrej Karpathy's **LLM Wiki** pattern — and measurably *better*.
> Karpathy's pattern compiles your sources into a persistent, interlinked wiki instead of re-deriving answers
> from raw chunks on every query (RAG). **BSB keeps that, then adds three layers that close the gaps the original
> pattern leaves open:** an automatic knowledge **graph**, a self-**improvement** loop, and autonomous
> self-**healing**.

BSB is an open-source template. Clone it, point it at your sources, and an LLM agent (Claude Code, Codex,
OpenCode, …) maintains a trustworthy, browsable, version-controlled knowledge base for you. Ships configured for
**software / tech reference**, but works for any domain — change one config block.

---

## Why this exists

The LLM Wiki pattern (Karpathy, April 2026 — [X post](https://x.com/karpathy/status/2039805659525644595),
[gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)) is brilliant but deliberately minimal.
In practice it has three soft spots. BSB targets each one:

| The gap in vanilla LLM-Wiki | BSB's answer |
|---|---|
| **You only find connections you think to ask about.** Cross-links are manual. | **graphify** builds a real knowledge graph over `raw/`+`wiki/` — community detection, hub ("god") nodes, *surprising connections*, GraphRAG queries — and feeds what it finds back into the lint loop. |
| **The method never improves itself.** The schema is static; quality drifts. | **auto-research** periodically re-researches PKM/LLM-wiki best practices and proposes verified upgrades to the schema and page formats. The brain's *method* compounds, not just its data. |
| **Pages rot. A wrong/outdated doc just sits there.** | **Self-healing**: because every page cites its sources, the brain re-verifies itself, detects superseded versions / dead links / unsupported claims, and fixes them — report-only, on-approval, or autonomously per area. |

Plus a **research-discipline gate** the original lacks: *no page may be written from the model's memory* — every
page must be grounded in ≥ 3 fetched primary sources, or it isn't written. That single rule is what makes the
result trustworthy instead of plausible-sounding slop.

---

## Architecture

Three layers (Karpathy) + a temporal triad of control files:

```
raw/      immutable sources you curate   (the LLM only reads)
wiki/     interlinked markdown pages      (the LLM owns + maintains)
          ├ sources/ concepts/ entities/ cheatsheets/ syntheses/ moc/
index.md  what exists   ·  log.md  what happened  ·  roadmap.md  what's next
CLAUDE.md the schema/rulebook the agent follows   (AGENTS.md = same, for Codex/OpenCode)
```

Six operations the agent runs: **Ingest · Query · Lint** (classic) + **Graph · Improve · Heal** (the "better" part).
Full spec: [`CLAUDE.md`](./CLAUDE.md).

---

## Quickstart

```bash
git clone <your-fork-url> "Second Brain" && cd "Second Brain"
# Open the folder as a vault in Obsidian (optional but recommended — it's the human reader).
# Open the folder in Claude Code (or Codex/OpenCode) — the agent reads CLAUDE.md automatically.
```

Then, in the agent:

1. **Make it yours** — edit the `DOMAIN` / `LITMUS` block in [`CLAUDE.md`](./CLAUDE.md) §0 and
   [`bsb.config.md`](./bsb.config.md). (Skip to use the shipped software/PKM domain.)
2. **Add a source** — drop a file in `raw/`, or say *"ingest https://…"*. The agent fetches it, writes a source
   page, updates the affected wiki pages, and logs it.
3. **Ask** — *"what does the wiki say about X?"* The agent reads `index.md`, the relevant pages, and answers with
   citations — then offers to file good answers back as new pages.
4. **Keep it healthy** — say *"lint"* periodically. Add the optional layers when you want them (below).

Full setup, including the optional layers and git hooks: [`docs/install.md`](./docs/install.md).

## The optional layers (off by default, degrade gracefully)

- **graphify** — `uv tool install graphifyy`, then the agent uses the `/graphify` skill. → [`docs/graphify-integration.md`](./docs/graphify-integration.md)
- **auto-research** — a Claude Code skill that self-improves the schema. → [`docs/auto-research-integration.md`](./docs/auto-research-integration.md)
- **self-healing** — runs on the source-grade lint. → [`docs/self-healing.md`](./docs/self-healing.md)
- **qmd** — local hybrid search when you outgrow `index.md`. → `github.com/tobi/qmd`

## Is it actually better? (the experiment)

BSB ships a benchmark to *test* the claim rather than assert it: the same question set answered by a vanilla
Karpathy wiki vs. a BSB instance, scored on correctness, citation quality, freshness, and token cost.
See [`docs/benchmark.md`](./docs/benchmark.md). The repo's own bootstrap content (the seed pages under `wiki/`,
which document the second-brain pattern itself) is the first benchmark corpus.

## Star history

<p align="center">
  <a href="https://star-history.com/#maystudios/better-second-brain&Date">
    <img src="https://api.star-history.com/svg?repos=maystudios/better-second-brain&type=Date" alt="Star History Chart" width="600">
  </a>
</p>

If BSB is useful to you, a ⭐ helps other people find it.

## Credit & license

Built on Andrej Karpathy's LLM Wiki pattern. Graph layer by [graphify](https://github.com/safishamsi/graphify).
Retrieval layer by [qmd](https://github.com/tobi/qmd). MIT licensed — see [`LICENSE`](./LICENSE).
