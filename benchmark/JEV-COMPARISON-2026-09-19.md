# Jev branching: five-arm cost and quality comparison

Measured 2026-09-19 on the existing public Ruff corpus: 14 frozen questions,
one response per arm/question, GPT-5.6 Luna at max, Jev 1.13.0. These are
query-pipeline measurements, not a universal percentage improvement of BSB.

## Corrected experiment: model-guided retrieval

The vanilla/full/lean controls use one Luna call to select up to three pages from
the complete path/heading catalog, then a fresh Luna call to answer from those
full pages. H1 titles are included in headings; filename stems are the fallback.
The Jev arms replace the model selector with internal index/branch/text decisions
and return a compact evidence packet to one Luna answer call. All selector,
answer and Jev usage is included. This measures a bounded two-stage navigator,
not an unrestricted native agent doing arbitrary filesystem/tool searches.

Fresh answer contexts avoid charging navigation history repeatedly. The same
answer prompt/schema, original corpus bytes and questions apply to every arm.
No gold answers enter retrieval or answer generation. No hidden fallback to
another search method is used. Jev retains 24-call/12-page limits.

| Arm | Quality /6 | Solved /14 | Main-model tokens | Jev calls | Query cost, USD |
|---|---:|---:|---:|---:|---:|
| Vanilla Karpathy | 5.71 | 11 | 408,298 | 0 | $0.09428 |
| BSB Full | 5.79 | 12 | 423,905 | 0 | $0.10075 |
| BSB Lean | 4.86 | 7 | 401,322 | 0 | $0.09775 |
| BSB Full + Jev | 5.71 | 12 | 236,088 | 124 | $0.06825 |
| BSB Lean + Jev | 5.57 | 10 | 209,653 | 130 | $0.05979 |

Main-model tokens include reported input and output; reasoning is already a
subset of output. Costs are totals across **14 queries per arm**, standardized
to uncached API list prices and including Jev. They are not subscription invoices.

| Jev variant vs its model-guided baseline | Main tokens | Total cost incl. Jev | Paired median cost | Quality delta /6 | Lower-scoring question IDs |
|---|---:|---:|---:|---:|---|
| BSB Full + Jev vs BSB Full | -44.3% | -32.3% | -29.9% | -0.07 | 5 |
| BSB Lean + Jev vs BSB Lean | -47.8% | -38.8% | -37.9% | +0.71 | none |

The listed regressions are part of the result. Lower cost does not by itself
establish equal answer quality. “Solved” requires all three grading dimensions
to score 2/2 (6/6 total), not merely a successful API call or `ready` retrieval.

Full + Jev has unchanged mean correctness/citation (1.86/1.93 out of 2), but
faithfulness falls from 2.00 to 1.93: Q5 loses one point. This is a cost/quality
tradeoff. Lean + Jev improves correctness 1.50→1.71, citation 1.64→1.86 and
faithfulness 1.71→2.00, with no dimension-level regression in this sample.
Per-question dimension deltas are retained in both summary files. Paired median
cost is the median of the 14 individual percentage changes, not the ratio of totals.

## What was wrong in the first implementation

The first comparison used **free local BM25 top-3** as its control. This is a
useful cheap alternative, but it contains no main-model search decision to
offload. Treating that alone as a test of the user's proposed agent delegation
answered the wrong question.

The implementation also split text at headings after only 1,000 bytes, despite
an 8,000-byte bound. Its 174 evaluated pages caused 316 evidence requests plus
81 routing requests. Finally, the answer model received detailed accounting and
catalog metadata. These costs exceeded the saved page context.

The correction packs contiguous source text to the existing byte bound and uses
`caller_result()` for the CLI. Per-call accounting remains in detailed Python
results and local receipts. Full selected pages, hashes, source lines, conflicts,
omissions and gaps remain visible. Independent regressions observed the old
heading-rich fixture split into three requests, then one after the fix.

## Preserved first result: free local retrieval control

The original negative result is retained. This is the earlier implementation
(`87041ff`), a different retrieval control, and a separate grading run.

| Arm | Quality /6 | Solved /14 | Main-model tokens | Jev calls | Query cost, USD |
|---|---:|---:|---:|---:|---:|
| Vanilla Karpathy | 5.86 | 13 | 229,908 | 0 | $0.05419 |
| BSB Full | 5.86 | 13 | 229,633 | 0 | $0.05449 |
| BSB Lean | 5.64 | 11 | 205,797 | 0 | $0.04994 |
| BSB Full + Jev | 5.71 | 12 | 246,070 | 262 | $0.08174 |
| BSB Lean + Jev | 5.71 | 12 | 212,935 | 135 | $0.06104 |

V1 Full + Jev cost **50.0% more** than free-local Full; Lean + Jev cost **22.2%
more** than free-local Lean. Lean's delivered page text shrank 14.6%, but its
main-model input grew 3.55% because the full result envelope outweighed that saving.

## Code correction and cheap-baseline cross-check

| Jev arm, corrected vs v1 | Jev calls | Jev input tokens | Main-model tokens | Query cost |
|---|---:|---:|---:|---:|
| BSB Full + Jev | 262 → 124 | -46.0% | -4.1% | -16.5% |
| BSB Lean + Jev | 135 → 130 | -5.0% | -1.5% | -2.0% |

The two changes are measured together; stochastic model decisions also vary.
The following cross-check compares corrected Jev with the preserved free BM25
answers, so it is not a fresh interleaved rerun of those controls:

| Corrected Jev vs free BM25 | Cost change | Quality difference /6 |
|---|---:|---:|
| BSB Full + Jev vs BSB Full | +25.3% | -0.14 |
| BSB Lean + Jev vs BSB Lean | +19.7% | -0.07 |

## Complete usage and cost ledger (corrected run)

| Arm | Main input | Cached subset | Main output | Jev input | Jev output | All-model tokens | Cache-aware USD |
|---|---:|---:|---:|---:|---:|---:|---:|
| Vanilla Karpathy | 395,681 | 198,400 | 12,617 | 0 | 0 | 408,298 | $0.05856 |
| BSB Full | 407,936 | 204,544 | 15,969 | 0 | 0 | 423,905 | $0.06393 |
| BSB Lean | 383,834 | 216,576 | 17,488 | 0 | 0 | 401,322 | $0.05877 |
| BSB Full + Jev | 226,744 | 168,448 | 9,344 | 278,310 | 23,607 | 538,005 | $0.03793 |
| BSB Lean + Jev | 200,846 | 168,448 | 8,807 | 215,551 | 20,890 | 446,094 | $0.02947 |

Cache-aware estimates use observed cache counters; scheduling and server cache
state were not controlled. Uncached equivalents are the primary paired comparison.
Combined model token counts may rise while cost falls: tokens on the two models
have different prices. Neither metric measures subscription credits directly.

Rates checked on 2026-09-19: Luna $0.20/M input, $0.02/M cached input and $1.20/M
output; Jev $0.042/M input with free output. Source:
[OpenAI model pricing](https://developers.openai.com/api/docs/models/gpt-5.6-luna),
[TypeSafe model pricing](https://docs.typesafe.ai/models).

## Quality, verification and limitations

Fresh Luna grading sessions receive shuffled opaque answer IDs, question gold
and supporting source quotations, without arm names or costs. Paths are mapped
to page IDs. Source style can still hint at a corpus variant; this is not perfect
blinding. Exact path/quote checks are mechanical; nonexact quotations receive
the original full cited source for semantic evaluation. Correctness, citation
quality and faithfulness each score 0–2 under the frozen rubric.

In v2, one five-answer grading batch omitted one ID. Only that missing answer
was graded separately; all other grades were retained and all 15 completed
grader calls are charged in the overhead ledger.

The initial v1 70-answer grading batch timed out. Two other unfinished grading
attempts have no completed usage receipt after interruption. Final v1 scores
come from 13 completed question batches and five individual Q11 checks; no
answer/retrieval result was rerun or selected for a better score. Grading and
orchestration are separate experiment overhead, not part of per-query inference
cost. Unknown failed-grader usage is explicitly unknown, not zero. See the
overhead ledgers; no exact whole-project spending claim is made.

The audit reconciles source bytes/hashes, every completed main-model call and
every Jev usage record. Detailed per-question scores, regressions, dimension and
category means, median/p95 latencies, and cost per solved question are in the JSON.
CLI/system scaffolding is included in observed main-model usage and accounts for
a substantial fixed input footprint; an API-only host can have different economics.

Small sample: one public, well-known English topic, one repetition, existing
historical gold. No significance, general recall, German-language or production
latency claim. This is not a new ingestion/fill benchmark or live native-hook test.
The historical index-plus-median-page read estimates are kept separate.

## Artifacts and reproduction

- [Frozen v1 protocol](./jev-comparison-protocol.md), [v2 protocol](./jev-efficiency-v2-protocol.md).
- [V1 summary](./jev-comparison-2026-09-19/v1/summary.json), [V1 per-question results](./jev-comparison-2026-09-19/v1/results.json).
- [V2 summary](./jev-comparison-2026-09-19/v2/summary.json), [V2 per-question results](./jev-comparison-2026-09-19/v2/results.json).
- Each artifact directory contains manifests, independent grades, audits and overhead information. Raw grading prompts and receipts remain in the ignored local run directories; the public grading-provenance manifest records their hashes.

```sh
python benchmark/jev_compare_v2.py --out .bsb-jev/my-comparison --workers 3
python benchmark/jev_compare_v2_audit.py .bsb-jev/my-comparison
python benchmark/jev_compare_report.py .bsb-jev/my-comparison --prepare-grading
python benchmark/jev_compare_grade.py .bsb-jev/my-comparison/blind-answers.json --out .bsb-jev/my-comparison/grading --batches
python benchmark/jev_compare_report.py .bsb-jev/my-comparison --grades .bsb-jev/my-comparison/grading/answer.json --publish benchmark/my-comparison
```

Paid calls require authenticated Codex CLI and TypeSafe credentials. `tiktoken`
is required. Re-running model calls can yield different decisions. V1 uses the
search code from commit `87041ff` and `jev_compare.py`; its artifacts are preserved.
