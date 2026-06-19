# Log

Append-only chronological record of every operation. Newest entries at the **bottom**.
Greppable prefix — recent activity: `grep "^## \[" log.md | tail -10`.

Ops: `ingest` · `query` · `lint` · `graph` · `improve` · `heal` · `schema`.

---

## [2026-06-19] schema | Bootstrap — Better Second Brain initialized

Created the repo from scratch as an open-source **Better Second Brain (BSB)** template: the Karpathy LLM-Wiki
pattern + three enhancement layers (graphify graph, auto-research self-improvement, autonomous self-healing) +
a research-discipline gate (no page from training memory; ≥3 fetched sources).

- Wrote the schema `CLAUDE.md` (§0 scope · §1 architecture · §1.5 research discipline · §2 page types ·
  §3 operations incl. Graph/Improve/Heal · §4 meta-docs + session protocol · §5 style · §6 tooling · §7 evolution
  · §8 for-other-people), plus `AGENTS.md` (@import), `bsb.config.md`, `README.md`, `LICENSE` (MIT), `Welcome.md`.
- Committed an Obsidian baseline (`.obsidian/`: Bases enabled, wikilinks, attachments → `raw/assets/`,
  graph color groups) and a `.gitignore`.
- Established the wiki taxonomy: sources / concepts / entities / cheatsheets / syntheses / moc.
- Decision: link-style = **full-path** (`[[wiki/concepts/x]]`); domain default = software + the second-brain
  pattern itself (the bootstrap domain doubles as the first benchmark corpus).
- Seed content (this commit): sourced pages documenting the LLM-Wiki pattern, graphify, qmd, Obsidian Bases,
  and prior art (Memex, Zettelkasten, PARA) — all grounded in verified primary sources (see each page's `## Sources`).

Next: see `roadmap.md`.
