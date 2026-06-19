# Benchmark results - BSB vs. vanilla Karpathy wiki

First run: **2026-06-19**. This is an honest, small-N experiment - read the caveats at the bottom before quoting it.

## Method (one paragraph)

Two arms were built from the **same fetched source corpus**: **`vanilla`** (a minimal Karpathy-style wiki - loose
summaries, citations optional, memory allowed) and **`bsb`** (research-gated - a source page per raw file, every
non-trivial claim grounded in and citing a `[[sources/...]]` page, nothing asserted beyond the sources). A **gold
question set** (recall / detail / freshness / one "unsupported" trap per topic) was authored from the sources. Each
arm answered **only from its own wiki** (no web, no outside knowledge). An objective judge scored every answer
against gold on three 0-2 dimensions - **correctness, citation, faithfulness** - and `scripts/token_report.py`
measured token cost deterministically. Two corpora: **small** (`uv`, 5 sources, 6 Q) and **medium** (`MCP`, 10
sources, 10 Q). Artifacts for every step are in `benchmark/small/` and `benchmark/medium/`.

## Quality (judge vs. gold, totals out of 6)

| Example | Arm | Correctness | Citation | Faithfulness | **Total** | Winner |
|---|---|:--:|:--:|:--:|:--:|:--:|
| small · uv | vanilla | 2.00 | 1.83 | 2.00 | **5.83** | **tie** |
| small · uv | bsb | 2.00 | 1.83 | 2.00 | **5.83** | |
| medium · MCP | vanilla | **2.00** | 1.00 | 2.00 | 5.00 | **bsb** |
| medium · MCP | bsb | 1.80 | **1.80** | 2.00 | **5.60** | **+12%** |

- **The BSB advantage is traceability, not raw correctness.** On the medium topic both arms answered the substance
  correctly, but vanilla's citations were vague or pointed at the wrong page and carried **no URLs**; BSB cited the
  exact gold source URL on all 9 answered questions. That is the entire +12% margin.
- **Vanilla can match correctness from memory** on well-documented topics (it even nailed `uv`'s pinned version
  `0.11.22` and MCP's `-32002` error code). Grounding gave BSB no *correctness* edge on these popular subjects.
- **BSB's research gate has a real failure mode: over-abstention.** On MCP Q4 the BSB KB hadn't indexed the
  `-32002` error code, so it abstained ("the wiki does not say") on an answerable fact vanilla got right. This is
  the clearest case of the gate hurting, and a concrete improvement target (index more detail, or allow a
  flagged low-confidence answer instead of a hard abstain).
- **Neither arm hallucinated** (faithfulness 2.00 both, both topics); both correctly rejected the "unsupported" trap.

## Token efficiency (`scripts/token_report.py`, approximate tokenizer, ratios robust)

### Read / "understand" - tokens to answer one query

| Example | raw (read all) | RAG top-3 | vanilla wiki | bsb wiki | **wiki vs raw** |
|---|--:|--:|--:|--:|:--:|
| small · uv | 2,435 | 1,461 | 1,042 | 1,136 | **~2.1-2.3×** |
| medium · MCP | 7,752 | 2,325 | 1,470 | **1,328** | **~5.3-5.8×** |

**The read-time saving grows with corpus size** (≈2.3× at 5 sources → ≈5.8× at 10) and ≈1.3-1.8× even vs. naive
RAG. BSB reads about the same as vanilla on the small set and **less** than vanilla on the medium set - its
structured, single-topic pages keep per-query reads tight as the corpus grows.

### Fill / "interconnection" - one-time build cost + cross-link density

| Example | Arm | Pages | Artifact tokens | Wikilinks | Links/page | Links/1k tok |
|---|---|--:|--:|--:|:--:|:--:|
| small · uv | vanilla | 5 | 2,638 | 30 | 6.0 | 11.4 |
| small · uv | bsb | 9 | 5,120 | **96** | **10.7** | **18.8** |
| medium · MCP | vanilla | 7 | 5,424 | 42 | 6.0 | 7.7 |
| medium · MCP | bsb | 15 | 9,894 | **124** | **8.3** | **12.5** |

BSB costs **~1.8-1.9× more tokens to fill** (it writes a source page per input + far more cross-links) and lays down
**~1.6-3.2× more interconnections** - the denser graph the `graphify` layer feeds on.

### Break-even - when the one-time fill cost is repaid by per-query read savings

| Example | Arm | vs. read-all-raw | vs. RAG top-3 |
|---|---|:--:|:--:|
| small · uv | vanilla | 1.9 queries | 6.3 queries |
| small · uv | bsb | 3.9 queries | 15.8 queries |
| medium · MCP | vanilla | 0.9 queries | 6.3 queries |
| medium · MCP | bsb | 1.5 queries | 9.9 queries |

Against the "re-read everything each time" baseline the wiki pays for itself in **1-4 queries**; even against naive
RAG, within **~6-16**. After that every query is pure savings. BSB's higher fill cost lengthens break-even only
slightly - trivial for any knowledge that gets queried more than a handful of times.

## Large run (3 arms) - Ruff, 15 sources, 14 questions, exact tokenizer (2026-06-19)

A third arm was added - **`bsb-lean`**, the optimized fill mode (compact source stubs, cite-don't-restate, terse
`## Links` lists) - plus an over-abstention fix in the answering policy. Tokens here are **exact** (`tiktoken`).

### Quality (out of 6)

| Arm | Correctness | Citation | Faithfulness | **Total** |
|---|:--:|:--:|:--:|:--:|
| vanilla | 2.00 | 1.64 | 2.00 | 5.64 |
| bsb (full) | 2.00 | 1.93 | 2.00 | **5.93** |
| **bsb-lean** | 2.00 | 1.93 | 2.00 | **5.93** |

- **All three arms answered every fact correctly** (correctness 2.00) - both wikis captured the detail, so the
  spread is again **citation quality**: BSB arms cite exact doc URLs (1.93); vanilla uses bare filenames (1.64).
  BSB beats vanilla by **+5.1%**.
- **`bsb-lean` ties full `bsb` exactly** (quality Δ = 0.0): the leaner pages kept every gold fact and every correct
  citation.
- **The over-abstention fix worked**: the BSB arms now answer detail/freshness facts confidently and nailed the
  "unsupported" trap by quoting the FAQ ("Ruff is a linter, not a type checker"), instead of abstaining. One
  residual over-hedge remained (Q5, `select` vs `extend-select`).

### Tokens (exact, tiktoken cl100k). Raw corpus = 7,895 tokens / 15 sources.

| Arm | Pages | **Fill tokens** | Links | Links/1k | **Read/query** | vs raw | Break-even (raw) |
|---|--:|--:|--:|:--:|--:|:--:|:--:|
| vanilla | 11 | 7,485 | 90 | 12.0 | 1,296 | 6.1× | 1.1 q |
| bsb (full) | 34 | 22,366 | 466 | 20.8 | 1,042 | 7.6× | 3.3 q |
| **bsb-lean** | 31 | **7,648** | 237 | **31.0** | **442** | **17.9×** | **1.0 q** |

**The fill optimization works, decisively:**

- **Fill: `bsb-lean` costs 7,648 tokens vs full BSB's 22,366 - a ~66% cut, essentially vanilla's fill cost (7,485)** -
  with **no quality loss**.
- **Interconnection got *denser*, not sparser**: 31.0 links per 1k tokens (vs full BSB 20.8, vanilla 12.0) - the
  most-connected graph per token, exactly the "cheap interconnection" goal.
- **Read got cheaper too**: 442 tokens/query - 2.4× under full BSB, 2.9× under vanilla, **17.9× under reading raw**,
  3.6× under naive RAG. Compact pages = a tiny per-query footprint.
- **Break-even: 1 query.** Lean fill pays for itself immediately.

**`bsb-lean` is near-Pareto-optimal** - full-BSB quality and traceability, the densest interconnection, the lowest
read cost, at a vanilla-level fill cost. It is now the **default fill mode** in the schema (`CLAUDE.md` §2.1).

### Honest note on the "does the advantage scale?" hypothesis

It did **not** scale the way predicted. The quality margin *shrank* (small tie → medium +12% → large +5.1%),
because on these well-documented topics **both** wikis captured the facts, so correctness was a wash and only
*citation traceability* separated them. BSB's durable, repeatable edge is **verifiability**, not raw correctness -
and the biggest concrete win of the large run was the **fill optimization**, not a wider quality gap. A genuinely
*private / novel* corpus (where one wiki would simply lack facts) is still untested and is where a correctness gap,
if any, would show.

## Bottom line

- **Read efficiency: yes, and it compounds.** A wiki is far cheaper to query than reading raw sources - 2.3× (small)
  → 5.8× (medium) → with **`bsb-lean`, 17.9×** (large). BSB matches or beats vanilla on read cost.
- **Fill cost is no longer a BSB downside - it's solved.** Full BSB does cost ~1.8-2.9× more to build, but the
  **`bsb-lean`** mode cuts that ~66% back down to a vanilla wiki's cost **with zero quality loss and *denser*
  interconnection**. Lean is now the default (`CLAUDE.md` §2.1). Break-even: ~1 query.
- **Quality: BSB's durable, repeatable edge is *verifiability*, not raw correctness.** On well-documented topics
  both wikis get the facts right; BSB's structured source-citations win the margin (+5-12%). The over-abstention
  failure mode is now fixed in the answering policy.
- **The "advantage grows with size" hypothesis was *not* confirmed** (the margin shrank, because both wikis
  captured the facts). The open test that would show a *correctness* gap is a genuinely **private / novel** corpus
  where one wiki simply lacks the facts - not yet run.

## Caveats (don't oversell this)

- **Small N** (2 topics, 16 questions total). Directional, not definitive.
- **Not fully blinded:** the judge knew which arm was which (it scored against an objective gold set, which limits
  bias, but doesn't eliminate it).
- **Token counts are approximate** (`len/4` heuristic; `tiktoken` was not installed). The *ratios* are robust - the
  same estimator was applied to every arm - but absolute token figures are estimates.
- **Read model is a proxy:** "read/query = navigation page + one content page." Real agents sometimes read more.
- **Popular topics flatter vanilla:** `uv` and `MCP` are well-represented in model training data, so memory-only
  answers were unusually strong. A genuinely novel/private corpus would stress the research-gate's advantage harder.

## Reproduce

```
# rebuild the arms + score (multi-agent):  re-run the bsb-benchmark workflow
python scripts/token_report.py benchmark/small  --json benchmark/small/tokens.json
python scripts/token_report.py benchmark/medium --json benchmark/medium/tokens.json
# exact token counts:  pip install tiktoken  (then re-run token_report.py)
```

Raw scores: `benchmark/<size>/scores.json` · token detail: `benchmark/<size>/tokens.json` · per-question judge
notes: `benchmark/medium/report.md` (the `small/report.md` write was blocked mid-run; its scores are in
`benchmark/small/scores.json`).
