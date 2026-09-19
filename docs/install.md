# Install and Setup

This page gets BSB (Second Brain) running on your machine: clone the repo, open it for both the human reader (Obsidian) and the agent (Claude Code or Codex), make it yours, run your first ingest, and - optionally - enable the extra layers (graphify, the git hooks, qmd). Commands are written for Windows PowerShell.

## 1. Clone

Requirements: **Python ≥ 3.10** (the helper scripts use 3.10+ syntax) and git. Obsidian, graphify and qmd are all optional.

```powershell
git clone https://github.com/maystudios/better-second-brain "Second Brain"
cd "Second Brain"
```

## 2. Open it twice: once for you, once for the agent

BSB has two readers, and you open it once for each.

- **Obsidian - the human reader.** Open the cloned folder as an Obsidian vault: in Obsidian choose **Open folder as vault** and point it at the `Second Brain` directory. Wikilinks like `[[wiki/concepts/...]]` resolve into a navigable graph, and the meta pages [[index]], [[log]] and [[roadmap]] become your entry points.
- **Claude Code or Codex - the agent reader.** Open the same folder in your coding agent. The agent reads its operating instructions from `CLAUDE.md` (Claude Code) or `AGENTS.md` (Codex) at the repo root. That file is what teaches the agent the BSB conventions: wikilink format, frontmatter, the layers, and the research-discipline gate. You do not paste anything in - opening the folder is enough, because the agent loads that file automatically.

## 3. Make it yours

**Fastest:** run the `/bsb-init` slash command in Claude Code, or `python scripts/init_brain.py --domain "…" --litmus "…" --fresh --yes`. It sets `CLAUDE.md` §0 **and** `bsb.config.md` for you and resets the brain to empty (the two edits below). Or do them by hand:

1. **`CLAUDE.md` §0** - the top-of-file identity block. Set who this brain is for and the topics it covers. This steers every ingest and every page the agent writes.
2. **`bsb.config.md`** - the project config. Set the things that are mechanical rather than editorial: which layers are enabled, your default folders, and any per-project switches.

Keep both edits small and specific; they are read on every run, so verbosity here costs tokens on every operation.

**What "clean" looks like on a fresh brain:** `index.md` shows 0 pages and 0 sources, and a freshly scaffolded stub will show up as `D`-tier in `lint_sources.py` (and may warn about example links) until you fill it with real, cited content - that is expected, not breakage.

## 4. First ingest

Drop a source (a URL, a PDF, a pasted note) into `raw/`, then ask the agent to ingest it. The agent reads the raw source, writes or updates the relevant `wiki/...` pages with real citations, and appends a line to [[log]]. Start with two or three sources so you can see the cross-links form before you scale up.

The research-discipline gate (CLAUDE.md §1.5) applies from the very first ingest: every page is grounded in real, cited sources, primary sources are separated from secondary, unsupported claims are marked `status: stub` rather than asserted, and quotes are verbatim only.

## 5. Optional layers

These are off by default. Enable the ones you want.

### jev - semantic gateway and safe mutation review

BSB integrates with TypeSafe's Jev System One (`jev-1.13.0`) as an optional semantic gateway. When enabled, it provides:
1. **Bounded semantic query search**: Local lexical extraction followed by Jev prioritization, with source paths, lines and hashes. The default retains all generated candidates; hard pruning failed the [initial quality experiment](../benchmark/JEV-2026-09-19.md).
2. **Progressive full-page navigation**: `navigate --need` selects pages per explicit subquestion, `read` returns an offered page in full with a stale hash check, and `next` follows unresolved needs and safe wikilinks. Exact titles, aliases and URLs use the zero-API `source` lookup. The [Luna navigation run](../benchmark/JEV-NAVIGATION-LUNA-MAX-2026-09-19.md) reduced page bytes but increased total measured tokens, so it is optional and not a savings guarantee.
3. **Advisory recommendations**: Placement advice for new notes across wiki directories, cross-linking suggestions, and deletion evaluation.
4. **Safe reversible mutation gateway**: Enforces that `raw/` and schema files are immutable, requires caller citations, checks stale file hashes, strictly refuses deletions when active backlinks exist, creates atomic backups under `.bsb-jev/backups/`, rolls back on errors, and maintains an append-only audit log under `.bsb-jev/audit.jsonl`.
5. **Native host hooks**: Antigravity (`.agents/hooks.json`), Claude Code (`.claude/settings.json`) and Codex (`.codex/hooks.json`) intercept supported native edits/searches. Strict `enforce_reads` additionally gates supported wiki reads and arbitrary shell through exact gateway commands; immutable `raw/` reads remain available for primary-source grounding. Codex requires the generated hook to be reviewed/trusted by the host before it runs.

**Enable or disable:**
```powershell
# Enable and install native host hooks
python scripts/bsb_jev.py configure --enabled on --enforce-reads on --install-hooks

# Check status
python scripts/bsb_jev.py configure --status

# Disable (makes zero network calls)
python scripts/bsb_jev.py configure --enabled off
```

**Credentials:**
Set `TYPESAFE_API_KEY` in your environment, or provide a DPAPI-encrypted file via `TYPESAFE_KEY_FILE` (or `~/.config/harness-workflow/typesafe-key.dpapi` on Windows). Keys are never printed in outputs or stored in git configs. If missing, query searches fail open to deterministic lexical candidates, while mutations fail closed.

**Security boundary & shell bypass:**
Supported host shell commands and protected reads are denied in strict mode unless they are exact gateway invocations. Unsupported wrappers, external processes and host trust settings remain outside the hook's view; this is workflow enforcement, not an OS sandbox. See [Jev operations and limits](jev.md).

**Upgrade an existing brain without reinitializing:** run from a current BSB checkout:

```powershell
python scripts/install_jev.py --target "C:/path/to/existing-brain" --enabled on --hooks
```

This backs up existing managed files, copies the standalone tools and adds a small instruction block. It preserves wiki content and instance conventions. Use `--dry-run` to inspect the target first. Never use `init_brain.py --fresh` to upgrade a populated brain.

### graphify - the knowledge graph

[[wiki/sources/graphify|graphify]] turns your `raw/` folder into a persistent knowledge graph (god nodes, communities, surprising connections). It needs Python >= 3.10. The PyPI package is `graphifyy` (double-y); the CLI it installs is `graphify`.

Install with `uv` (preferred):

```powershell
uv tool install graphifyy
```

If you do not have `uv`, use `pipx`:

```powershell
pipx install graphifyy
```

**API key.** Inside Claude Code, the host session *is* the LLM - no API key is required. A key is only needed for **headless** extraction (running graphify outside an agent session). In that case set `GEMINI_API_KEY` (or `GOOGLE_API_KEY`). To persist it across PowerShell sessions:

```powershell
[Environment]::SetEnvironmentVariable("GEMINI_API_KEY", "your-key-here", "User")
```

Open a new terminal afterward so the persisted variable is picked up.

**Important caveat (issue #514).** The bare shell `graphify` CLI is subcommand-only and does not accept a free-form query as its first argument. Do **not** drive it by typing questions at the bare CLI. Instead, drive graphify through the **`/graphify` skill** inside your agent session - type `/graphify` and let the skill orchestrate the run. Use the bare CLI only for explicit subcommands such as `graphify add <url>` (which saves a source to `raw/` and updates the graph). Outputs land in `graphify-out/` (`graph.html`, `graph.json` for GraphRAG, `GRAPH_REPORT.md`).

### git hooks - source lint on commit

BSB ships hooks under `.githooks` that enforce the source-lint rules (for example, refusing to commit a page that asserts a claim with no source). Enable them:

```powershell
git config core.hooksPath .githooks
```

To bypass the source lint for a single commit (use sparingly - it exists to protect the trust gate):

```powershell
$env:SKIP_SOURCE_LINT = "1"; git commit -m "wip"; Remove-Item Env:\SKIP_SOURCE_LINT
```

### qmd - local semantic search over your notes

[[wiki/sources/qmd|qmd]] is a local CLI that searches your markdown with hybrid retrieval (BM25 over SQLite FTS5, plus vector search and an LLM rerank). It complements graphify: qmd finds *which* note answers a question (retrieval), while graphify shows *how* entities relate (traversal).

```powershell
npm i -g @tobilu/qmd
```

## Troubleshooting

- **Wikilinks do not resolve in Obsidian.** Confirm you opened the repo root *as a vault* (not a single file), and that links use the full path including folder, e.g. `[[wiki/concepts/slug]]`.
- **The agent ignores BSB conventions.** Confirm `CLAUDE.md` (or `AGENTS.md` for Codex) is at the repo root and that you opened the repo root - not a subfolder - in the agent.
- **`graphify: command not found`.** Re-open the terminal after install so PATH updates; confirm the package installed is `graphifyy` (double-y) and that Python is >= 3.10 (`python --version`).
- **graphify errors on a free-form question at the bare CLI.** Expected - see issue #514 above. Run it via the `/graphify` skill instead of the bare CLI.
- **Headless graphify fails with an auth error.** Set `GEMINI_API_KEY` (or `GOOGLE_API_KEY`) and open a new terminal. Inside Claude Code no key is needed.
- **A commit is blocked by the source lint.** A page asserts something without a real source. Add the citation (preferred), or set `SKIP_SOURCE_LINT=1` for that single commit if you must.
- **`npm i -g` permission error (qmd).** Run the terminal as Administrator, or configure an npm global prefix you own.

## Sources

- graphify (install, CLI behavior, /raw convention, issue #514) - https://github.com/safishamsi/graphify ; PyPI `graphifyy` - https://pypi.org/project/graphifyy/
- qmd (install, hybrid search, MCP) - https://github.com/tobi/qmd ; npm - https://www.npmjs.com/package/@tobilu/qmd
- Obsidian (vault model) - https://obsidian.md/help/bases
- Karpathy, "LLM Wiki" gist (`raw`/`wiki`/`schema` layers, `index.md` + `log.md`) - https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
