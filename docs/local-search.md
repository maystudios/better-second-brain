# Optional local retrieval-first search

An optional stage in front of `python scripts/bsb_jev.py find`. When it is on,
`find` first searches a local index of the brain's pages. If the local result is
**confident** (a documented rule, below), `find` returns the top pages in its usual
output shape with `"source": "local"` and `api_calls: 0`, **without loading the API
key or calling the Jev transport**. Otherwise the existing Jev route runs, with the
local candidates evaluated first. **Default: off**; with it off, `find` behaves
exactly as before.

Code: [`scripts/bsb_local_search.py`](../scripts/bsb_local_search.py) (standard
library; optional embedding backend). Tests: `tests/test_local_search.py`.
Related: [docs/jev.md](jev.md).

## Why: measured, one Vault

On the ParkIt project's Vault (a BSB instance), 11 test questions written by a
separate agent, 2026-10-15:

| route | right page | time per question | paid API tokens per question | returned into context |
|---|---|---|---|---|
| local hybrid (EmbeddingGemma 2 + SQLite FTS5 keyword) | rank 1 for 11/11 | ~0.13 s | 0 | ~1,800 tokens (10 snippets) |
| local keyword only (SQLite FTS5 BM25) | top 5 for 10/11, rank 1 for 7/11 | - | 0 | - |
| Jev `find` | 9/11 | ~9.2 s | ~53,200 input + ~4,400 output | ~6,100 tokens (full pages) |

**This is one Vault and 11 questions: indicative, not a general claim.** Those
local numbers come from a separate tool (`seek`) using the same model and SQLite
FTS5 keyword search; its chunking and fusion may differ from this module.

This module's `find --local-first --dry-run` on the same 11 questions (measured by a
separate agent that held the questions; the module's author never saw them):

| backend | answered locally | correct at rank 1 | fell through to Jev | wall time per CLI call |
|---|---|---|---|---|
| keyword (stdlib default) | 7/11 | 7/7 | 4 | ~0.45 s (first call 5 s, builds the index) |
| hybrid (EmbeddingGemma 2) | 10/11 | 10/10 | 1 | ~12 s (model cold start every call) |

No local answer was wrong; the questions it was unsure about went to Jev. Measured
before the review fixes, which only tighten exclusions and the output budget. BSB's own
[five-arm comparison](../benchmark/JEV-COMPARISON-2026-09-19.md) likewise found
free local BM25 cheaper than Jev. The point of the stage is to pay for Jev only
where local retrieval is unsure, and to keep Jev's navigation for questions that
need reasoning across pages.

## Enable

From your own terminal (strict agent hooks only permit `configure --status`):

```sh
python scripts/bsb_jev.py configure --local-first on          # find tries local first
python scripts/bsb_jev.py configure --local-backend hybrid    # optional embeddings
python scripts/bsb_jev.py configure --local-first off
python scripts/bsb_jev.py configure --status                  # shows the local settings
```

Per call, `--local-first` or `--no-local` overrides the config (they are mutually
exclusive). The stage works whether Jev is enabled or not.

## What `find` returns

| situation | `status` | `source` | API calls |
|---|---|---|---|
| local confident | `local` | `local` | 0, key never loaded |
| not confident, Jev enabled | Jev status (`ready`, `partial`, ...) | `jev` | Jev budget; local candidates evaluated first |
| not confident, Jev disabled | `disabled` | `jev` | 0 |
| `--dry-run` | `local` if confident, else `dry_run` | `local` / `jev` | 0 |

A local result keeps the `find` shape: `pages` (relative `path`, full `text`,
`file_sha256`, `full_page: true`), `evidence_refs` (the best-matching chunk's line
range per need, `relation: "local_match"`), `conflicts: []`, `unresolved_needs: []`,
`coverage` (`stop_reason: "local_confident"`, `global_absence_proven: false`),
`session_id: null` (no receipt is written) and a `local` block: backend, per-need
decision (`rule` or `reason` plus the signals), candidates, index counts, latency
and `next_step`. Whenever the stage ran, the `local` block is also attached to a
fall-through result (`source: "jev"`), and the CLI prints ASCII-escaped JSON.

**For the agent:** read every returned page in full. Local ranks are retrieval
matches, not Jev evidence judgments (`evidence_judged: false`). If the pages do not
answer every need, run `find` again with `--no-local` or report the gap. As
everywhere in BSB, no result proves absence.

## Confidence rule

Applied to each need (the question itself when no `--need` is given; an explicit
need is searched together with the question). **Every need must be confident**,
otherwise the call falls through. The first matching rule wins:

1. `exact_name`: the top page's title, alias, slug or a wikilink display name
   pointing to it equals the question's content words (stopwords removed), or is
   the only page whose name occurs as a phrase in the question.
2. `route_agreement` (hybrid only): the keyword and the vector route both rank
   the same page first.
3. `keyword_margin`: the keyword route ranks the top page first, its BM25 page
   score leads the second page by at least `local_min_margin` (relative,
   `(s1 - s2) / s1`), and it contains at least `local_min_coverage` of the
   question's content words.

Not confident reasons: `no_results`, `routes_disagree`, `top_not_keyword_first`,
`keyword_margin_below_threshold`, `term_coverage_below_threshold`; and
`local_unavailable:<error>` if the stage itself failed (it never breaks `find`).
A confident result returns the top `local_pages` pages per need (union, at most
512 KiB like Jev). If that byte budget would drop any need's top page, the call
falls through instead (`local_output_budget`, with the affected needs listed),
so a `local` result never reports a need as resolved without its page. A
fall-through seeds Jev with the top `local_seeds` candidates.
The thresholds are **uncalibrated heuristics**, deliberately conservative: a
paraphrased or cross-language question usually falls through.

| config key (`.bsb-jev/config.json`) | default | env override | meaning |
|---|---|---|---|
| `local_first` | `false` | (flags `--local-first` / `--no-local`) | run the stage in `find` |
| `local_backend` | `keyword` | `BSB_LOCAL_BACKEND` | `keyword` or `hybrid` |
| `local_model` | `google/embeddinggemma-2` | `BSB_LOCAL_MODEL` | model id or local model folder |
| `local_pages` | `3` | `BSB_LOCAL_PAGES` | pages returned when confident (1..8) |
| `local_seeds` | `3` | `BSB_LOCAL_SEEDS` | candidates Jev evaluates first (0..8) |
| `local_min_margin` | `0.25` | `BSB_LOCAL_MIN_MARGIN` | rule 3 relative BM25 lead (0..1) |
| `local_min_coverage` | `0.5` | `BSB_LOCAL_MIN_COVERAGE` | rule 3 share of question words (0..1) |

Set them with `configure --local-...` flags. The environment overrides let you
measure another brain without writing into its config; invalid values are errors.

## Backends

**`keyword` (default, standard library).** Pages under the configured
`search_roots` are split into heading chunks (heading path, 1-based line range;
frontmatter skipped, fenced code never read as a heading, long sections split at
line boundaries). SQLite FTS5 (`porter unicode61 remove_diacritics 2`) scores
chunks with BM25 over sub-heading, prose and bare-wikilink slug words (weights
1.5 / 1.0 / 0.3), and pages over title, aliases and slug in a separate table. That
avoids FTS5's whole-row length normalisation, which otherwise rewards short link
lists. Page score = best chunk + 0.25 × second chunk + title score. A name route
finds exact or phrase matches of titles, aliases, slugs and wikilink display names.
Routes are fused with reciprocal-rank fusion (RRF, k = 60); an exact name gets one
extra rank-1 term.

**`hybrid` (optional).** Used only if `sentence-transformers` and `torch` import;
otherwise, or if the model fails to load, the call degrades to `keyword` and
reports `backend_fallback`. Default model `google/embeddinggemma-2`, bf16 on CUDA,
fp32 on CPU, never fp16. Query prompt `task: search result | query: {q}`, document
prompt `title: {title or none} | text: {content}`. Vectors are stored as a
float32 matrix (`vectors.f32` + `vectors.json`); only new or changed chunks are
embedded. Vector, keyword and name ranks are fused with RRF. No download is
attempted beyond what sentence-transformers does by itself: set
`HF_HUB_OFFLINE=1` to forbid it. If a cache lacks `refs/main`, the single cached
snapshot of the named model is used, or point `local_model` at a model folder.

## State and freshness

The index lives in `<root>/.bsb-local/` (gitignored), or in `$BSB_LOCAL_STATE`.
Every search refreshes it incrementally: unchanged size and mtime skip a file;
otherwise the SHA-256 decides between `touched` and re-indexed; deleted files are
removed. A schema or brain-root change rebuilds it; a corrupt database is rebuilt
once. Never indexed: hidden files and folders (including `.git`, `.bsb-jev`,
`.bsb-local`, `.obsidian`, `.trash`); a configured root containing such a component
is refused (`local_unavailable:ValueError`, `find` falls through). Also never indexed:
secret-looking names, checked with the Markdown suffix removed (`.env*`, `*.pem`,
`*.key`, `*.pfx`, `*.p12`, `credentials.json`, `id_rsa`, `id_ed25519`, ... so
`id_rsa.md` counts), linked paths, pages over 256 KiB, binary pages and pages that
look like they contain a key. A returned page is re-read through the gateway's page reader, and its hash
must still match the index, or the call falls through.

```sh
python scripts/bsb_local_search.py index [--rebuild]
python scripts/bsb_local_search.py search "What is a memex?" [--json] [--limit 5]
python scripts/bsb_local_search.py status          # pages, chunks, pending changes, backend
python scripts/bsb_local_search.py --root /other/brain --backend hybrid search "..."
```

Under strict hooks, use `find`. The standalone CLI is not on the gateway
allowlist, and native writes to `scripts/bsb_local_search.py` or `.bsb-local/`
are denied. `install_jev.py` copies the module and this page and adds
`.bsb-local/` to `.gitignore`.

## Measured on this repository (2026-10-15, one Windows PC)

`wiki/`: 38 pages, 194 chunks. Python 3.14 (keyword) and 3.12 + CUDA (hybrid).

| measurement | keyword | hybrid |
|---|---|---|
| first index build | 0.05 s | 12.3 s (model load and 194 chunk embeddings) |
| no-change refresh | 7 ms | 18 ms |
| search, warm process | 2.3 ms (9 ms with refresh) | 49 ms (59 ms with refresh) |
| `find --local-first` CLI wall time | 0.13 s | ~11 s, every call |

The hybrid CLI time is the cold start of each process: torch import ~1.5 s,
sentence-transformers import ~5.3 s, model load ~2.9 s, first encode ~0.7 s;
a warm query encode takes ~53 ms. The ~0.13 s Vault figure came from the separate
`seek` tool; since a cold start alone takes ~10 s here, it implies a model kept
loaded between calls. This module loads the model once per process, so keep
`keyword` for agent calls unless the quality gain is worth ~10 s per call. A confident local `find` returned three
full pages, ~2,700-4,100 tokens of JSON (characters / 4). `local_pages: 1` or `2`
lowers that. These are timings on one machine, not a benchmark.

## Limits

- The confidence thresholds are not calibrated; check them on your own frozen
  questions before trusting a lower margin.
- Keyword search misses paraphrases and other languages. The vector route helps
  ranking, but on its own it never makes a result confident.
- Local results have no navigation receipt; use `source "<literal>"` or `find --no-local`
  to obtain one.
- SQLite FTS5 is required. Without it, the stage reports `local_unavailable` and
  `find` falls through.
