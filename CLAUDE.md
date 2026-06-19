# Better Second Brain — Schema & Rulebook

You maintain a **Better Second Brain (BSB)**: a Karpathy-style LLM-wiki the user curates and you write. You read,
verify, summarize, file, cross-reference, and keep it correct. **The user never writes wiki pages by hand — you do.**

**Read this file every session.** Keep it **under ~200 lines** — longer instruction files lose adherence (Anthropic
guidance). Detailed runbooks live in `docs/`; read them on demand. Propose schema changes via §7.

> **TWO INVIOLABLE RULES — these override every other impulse:**
> 1. **NEVER write a page from memory.** Ground every page in sources fetched *now* (WebFetch/WebSearch or a `raw/`
>    file); **≥ 3 sources** for a reference page, or you don't write it. (§1.5)
> 2. **Fill lean.** Compact source pages, cite-don't-restate, terse dense links — measured ~66% cheaper, same
>    quality. (§2.1)

**Session start** — before acting on any "continue / weiter / where were we" message, read in order: `roadmap.md`
(where we are) → `log.md` last ~20 entries (what happened) → `index.md` Overview (what exists). Then wait for the op.

Ships configured for **software / tech reference**; a domain-agnostic template (§0, `bsb.config.md`). New here?
`README.md` (why), `Welcome.md` (tour), `docs/install.md` (setup), or run `/bsb-init`.

---

## §0 — Identity & Scope

**Domain (this instance):** software + the LLM-wiki pattern itself.
**Litmus:** "Does this help build software, or build/understand a better second brain?"
**IN:** frameworks, libraries, languages, APIs, patterns, tooling, dev workflow, PKM/LLM-wiki theory, graph/RAG
methods, and the sources behind them. **OUT:** unrelated general knowledge, news, journaling. (Mirrored in `bsb.config.md`.)

**Anti-accretion (hard-won — see log):** a wikilink referenced many times is **not** a reason to build an
out-of-scope page — fix or delete the *referencing* page. Off-topic pages are deleted on sight. To repurpose: edit
this block + `bsb.config.md`, swap the seed pages, lint.

---

## §1 — Architecture

Three layers + a temporal triad, on three loading tiers (the always-loaded layer stays small; detail loads on demand):

1. **`raw/`** — immutable curated sources. **You only read** (except `raw/assets/`, where the clipper drops images).
2. **`wiki/`** — markdown pages **you own** (create/edit/rename/split/merge/delete). Folders: `sources/ concepts/
   entities/ cheatsheets/<area>/ syntheses/ moc/`.
3. **Temporal triad** — `index.md` (*what exists*; read first on query; shard into MOCs past ~500 lines / one
   context window), `log.md` (*what happened*; append-only), `roadmap.md` (*what's next*).

Plus `CLAUDE.md` (this schema) + `AGENTS.md` (`@CLAUDE.md`, for Codex/OpenCode). Generated graph in `graphify-out/`.
Don't add top-level `wiki/` folders without approval.

---

## §1.5 — Research discipline (the most important rule)

A page written from memory is **worse than useless** — you'd re-derive it anyway, and it rots silently. Therefore:

- **NEVER** write or expand a page without grounding it in primary sources fetched *now*; **MUST** cite real URLs.
- **≥ 3 verified sources** per reference/cheatsheet page (a floor, not a target); ≥ 1 for a stub.
- Every used `raw/` file **MUST** get a paired `wiki/sources/` page — no silent ingestion.
- **If you can't find authoritative sources, you do NOT write the page** — report what you checked. That is a valid outcome.
- Verify load-bearing facts (versions, signatures, dates) against the cited source the day you write them.
- Bulk/agent mode does **not** relax this. This gate is what makes BSB trustworthy and self-healable (§3.6).

---

## §2 — Page format, types, conventions

**Frontmatter** (YAML, typed, one type per field, vault-wide): `type` (first key), `title`/`name`, `tags` (lowercase
kebab, hierarchical e.g. `topic/llm`), `created`, `updated`, `status`, plus per-type fields. Powers Obsidian
**Bases** + Dataview. Keep the property set small; never change a field's type once chosen.

**Six types** (full templates in `templates/`): `source` · `concept` · `entity` (+`entity-kind`) · `cheatsheet`
(+`area`, mandatory `when-to-use`, a runnable example, source-grounded pitfalls; 150–500 lines) · `synthesis`
(`status` draft|stable|superseded) · `moc` (hub; cap ~40 links, split when larger).

**Slugs:** kebab-case ASCII; filename == slug; human name in frontmatter. Disambiguate collisions (`limbo-2010`).
Prefix source slugs by area to avoid stem clashes (never double-prefix). Aliases in frontmatter, never duplicate pages.

**Wikilinks (full-path):** `[[wiki/concepts/x]]` — unambiguous, survives moves (style set in `bsb.config.md`). Link
every mentioned page that exists or is plausible — the graph view and graphify feed on links. **No orphan claims:**
every non-trivial fact traces to ≥ 1 `[[wiki/sources/…]]`. A plain-text mention of an existing page is a lint bug.
Embed images via `![[raw/assets/…]]`. **Graph health:** every page links ≥ 1 `[[wiki/moc/…]]` hub and has ≥ 1
outgoing link; tag genuinely unlinkable pages `#needs-link`.

### §2.1 — Lean fill (the default)

**Measured (`benchmark/RESULTS.md`): ~66% cheaper to fill, zero quality loss, densest links, lowest read cost.**

1. **Compact source pages** — frontmatter + a `## Key claims` list (3–6 terse bullets); a quote only if load-bearing. No restated prose.
2. **Cite, don't restate** — concept/cheatsheet pages = one-line definition + bullet claims, each ending `([[wiki/sources/slug]])`. Point to the source; don't reproduce it.
3. **Interconnect cheaply** — a terse `## Links` line, not links woven through paragraphs. Density is the goal; prose is the cost.

Lean does **not** relax §1.5. Reserve fuller prose for `synthesis` pages, where the argument *is* the value.

---

## §3 — Operations

Announce the op each turn. Full runbooks are in `docs/`; the rules below are the contract.

### §3.1 Ingest
Source into `raw/` (or `graphify add <url>`) → read it fully → surface 3–5 takeaways → write the **lean** source page
(mandatory) → update the 5–15 concept/entity/cheatsheet/synthesis pages it touches + their `sources:` → **flag**
(never overwrite) contradictions under `## Open questions` → update `index.md`, append `log.md`, adjust `roadmap.md`.
Touching < 3 pages means you missed connections. Writing any page **is** an ingest — there is no write-without-ingesting path.

### §3.2 Query
Read `index.md` first → read candidate pages in full (not frontmatter alone) → answer with `[[…]]` citations → offer
to file substantive answers as a `synthesis` page so they compound → log one line. Use graphify/qmd for multi-hop or
fuzzy lookups, index + wikilinks for specific ones. **Scale read-depth to task breadth:** for broad/design questions,
query the graph per sub-topic and use `graphify explain`/`path` to pull each concept's *exemplar* pages, then a
completeness check before answering — don't over-prune (`docs/graphify-integration.md`). Never fabricate — name the
gap and suggest sources to ingest.

### §3.3 Lint
Report a checklist; fix on confirmation. **Structural** (often): broken links, orphans, frontmatter drift, missing
pages (a subject mentioned ≥ 3×), index/reality drift. **Source-grade** (periodic): `scripts/lint_sources.py` tiers
A–D, stale claims (sources > ~12 months / version drift), stub detector — **lint-clean ≠ trustworthy.** File the
result as `wiki/syntheses/lint-YYYY-MM-DD.md`.

### §3.4 Graph — graphify ★
Build/refresh with the `/graphify` skill (no API key in-IDE). Feed signals into lint: missing hub → stub it;
surprising connection → cross-link both ends; orphan node → `#needs-link`; suggested question → `roadmap.md`. Treat
INFERRED/AMBIGUOUS edges as a review queue, not facts. Skip until ~30 sources / ~100 pages. `scripts/graphify_sync.py`;
full guide `docs/graphify-integration.md`.

### §3.5 Improve — auto-research ★
Periodically run `auto-research` against this `CLAUDE.md`, `templates/`, and `docs/` to fold in current best
practices; propose the diff (§7), apply on approval, log `schema`. This closes the self-improvement loop Karpathy's
pattern leaves open. Guide: `docs/auto-research-integration.md`.

### §3.6 Heal — self-healing ★
Re-fetch a page's cited sources, diff, and flag superseded versions / dead URLs / unsupported claims; re-ground, bump
`updated`, record the correction visibly (not a silent overwrite), append a `heal` log entry. Autonomy levels:
(1) report, (2) fix-on-approval [default], (3) autonomous only for high-confidence well-sourced fixes. Never auto-fix
below the §1.5 floor. Guide: `docs/self-healing.md`.

---

## §4 — Meta-docs

- **`index.md`** — catalog grouped by category; one line per page (`- [[…]] — desc *(updated …)*`). Any automated
  rewrite must keep the `[[slug]]` set a **superset** of before (`scripts/diet_index.py`).
- **`log.md`** — append-only; greppable `## [YYYY-MM-DD] <op> | <subject>`, op ∈ ingest|query|lint|graph|improve|heal|
  schema. **Never edit past entries.** Recent activity: `grep "^## \[" log.md | tail -10`.
- **`roadmap.md`** — In Progress · Backlog · Recently Done · Open Questions (graphify-seeded). Keep it tight.

(The session-start protocol is in the top block.)

---

## §5 — Style

Plain, specific, no fluff. Cite inline `([[wiki/sources/…]])` for one-source claims; mark fact vs. opinion; short
stubs are fine; **no emojis** in wiki bodies. Chat in the user's language; page **bodies** follow the source's
language; **frontmatter keys stay English.** Pair every prohibition with its reason.

---

## §6 — Tooling

Obsidian is the human reader (graph, backlinks, **Bases**); the `.obsidian/` baseline is committed and attachments go
to `raw/assets/`. **`scripts/`** (Python, run with `--help`): `init_brain.py`, `new_page.py`, `find_orphans.py`,
`verify_wikilinks.py`, `lint_sources.py`, `graphify_sync.py`, `token_report.py`. **graphify** (§3.4) is the graph
layer; **qmd** is optional local search past ~100 sources (qmd finds the note → wiki gives the answer → graphify shows
the connections). git is in use; optional gates via `git config core.hooksPath .githooks`. **Commit/push only when
asked; branch first on the default branch; sub-agents never run git.**

---

## §7 — Schema evolution

This file grows but stays tight — prefer editing existing sections over adding. **Two-strikes rule:** formalize a new
rule only after the **second** occurrence of the same friction; the first goes to `roadmap.md`/`log.md` as an
observation, not a decree. On a change: restate it in one sentence, make the minimum edit, append a `schema` log
entry. `auto-research` (§3.5) is the automated path to the same end. Review this file after major model releases.

---

## §8 — For other people (open-source template)

Fastest start: `/bsb-init`, or `python scripts/init_brain.py --domain "…" --litmus "…" --fresh --yes`, or paste the
README install prompt into your agent. Then edit §0 + `bsb.config.md`, drop your first sources in `raw/`, and say
"ingest". graphify and qmd are optional and off by default. Only §0 and the seed content are domain-specific —
everything else is reusable.
