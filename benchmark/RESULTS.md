# Benchmark results — BSB vs. vanilla Karpathy wiki

First run: **2026-06-19**. This is an honest, small-N experiment — read the caveats at the bottom before quoting it.

## Method (one paragraph)

Two arms were built from the **same fetched source corpus**: **`vanilla`** (a minimal Karpathy-style wiki — loose
summaries, citations optional, memory allowed) and **`bsb`** (research-gated — a source page per raw file, every
non-trivial claim grounded in and citing a `[[sources/...]]` page, nothing asserted beyond the sources). A **gold
question set** (recall / detail / freshness / one "unsupported" trap per topic) was authored from the sources. Each
arm answered **only from its own wiki** (no web, no outside knowledge). An objective judge scored every answer
against gold on three 0–2 dimensions — **correctness, citation, faithfulness** — and `scripts/token_report.py`
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

### Read / "understand" — tokens to answer one query

| Example | raw (read all) | RAG top-3 | vanilla wiki | bsb wiki | **wiki vs raw** |
|---|--:|--:|--:|--:|:--:|
| small · uv | 2,435 | 1,461 | 1,042 | 1,136 | **~2.1–2.3×** |
| medium · MCP | 7,752 | 2,325 | 1,470 | **1,328** | **~5.3–5.8×** |

**The read-time saving grows with corpus size** (≈2.3× at 5 sources → ≈5.8× at 10) and ≈1.3–1.8× even vs. naive
RAG. BSB reads about the same as vanilla on the small set and **less** than vanilla on the medium set — its
structured, single-topic pages keep per-query reads tight as the corpus grows.

### Fill / "interconnection" — one-time build cost + cross-link density

| Example | Arm | Pages | Artifact tokens | Wikilinks | Links/page | Links/1k tok |
|---|---|--:|--:|--:|:--:|:--:|
| small · uv | vanilla | 5 | 2,638 | 30 | 6.0 | 11.4 |
| small · uv | bsb | 9 | 5,120 | **96** | **10.7** | **18.8** |
| medium · MCP | vanilla | 7 | 5,424 | 42 | 6.0 | 7.7 |
| medium · MCP | bsb | 15 | 9,894 | **124** | **8.3** | **12.5** |

BSB costs **~1.8–1.9× more tokens to fill** (it writes a source page per input + far more cross-links) and lays down
**~1.6–3.2× more interconnections** — the denser graph the `graphify` layer feeds on.

### Break-even — when the one-time fill cost is repaid by per-query read savings

| Example | Arm | vs. read-all-raw | vs. RAG top-3 |
|---|---|:--:|:--:|
| small · uv | vanilla | 1.9 queries | 6.3 queries |
| small · uv | bsb | 3.9 queries | 15.8 queries |
| medium · MCP | vanilla | 0.9 queries | 6.3 queries |
| medium · MCP | bsb | 1.5 queries | 9.9 queries |

Against the "re-read everything each time" baseline the wiki pays for itself in **1–4 queries**; even against naive
RAG, within **~6–16**. After that every query is pure savings. BSB's higher fill cost lengthens break-even only
slightly — trivial for any knowledge that gets queried more than a handful of times.

## Bottom line

- **Read efficiency: yes, and it scales.** A wiki is far cheaper to query than reading raw sources, and the gap
  widens as the corpus grows. BSB matches or beats vanilla on read cost.
- **Fill cost: BSB is the more expensive arm to build (~1.8×),** the honest price of source-grounding + denser
  interconnection — repaid within a few queries.
- **Quality: tie on a small, well-known topic; BSB wins on the larger one, entirely through verifiable citations.**
  The gate occasionally over-abstains — the main thing to fix next.
- **Extrapolation (hypothesis, not yet measured):** both the read-efficiency gap and the citation advantage *grew*
  from small→medium. Larger, less-popular corpora — where memory is unreliable and traceability matters most —
  should favour BSB more. Needs a large-corpus run to confirm.

## Caveats (don't oversell this)

- **Small N** (2 topics, 16 questions total). Directional, not definitive.
- **Not fully blinded:** the judge knew which arm was which (it scored against an objective gold set, which limits
  bias, but doesn't eliminate it).
- **Token counts are approximate** (`len/4` heuristic; `tiktoken` was not installed). The *ratios* are robust — the
  same estimator was applied to every arm — but absolute token figures are estimates.
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
