# Five-arm retrieval experiment — frozen 2026-09-19

Acceptance: Identical frozen questions and snapshots across vanilla, full, lean,
full+Jev and lean+Jev; costs include all measured calls; quality graded blind and
regressions disclosed.

Use all 14 questions in `large/questions-public.json`, with the existing
`large/questions.json` gold visible only to graders. Preserve the three existing
`large/arm-*/wiki` corpora byte-for-byte in isolated copies; record SHA-256 hashes.
Create a deterministic root catalog index grouping original paths by folder for
each copy, without adding facts, gold answers or question-specific descriptions.

Arms: vanilla, BSB full, BSB lean, BSB full + Jev, BSB lean + Jev.
The first three use the same local BM25 retrieval (k=3, k1=1.5, b=0.75,
case-insensitive alphanumeric tokenization) and return full pages. The last two
use the shipped `find` with default 24-call, 12-page budgets and no hand-authored
needs or fallback. No hidden reruns to improve results. Failed attempts remain
recorded. One repetition per question; fixed seed interleaves the arm order.

Every question receives a fresh GPT-5.6 Luna/max answer session with the identical
prompt/schema and all retrieved original page text. No web, tools, gold, other
answers or previous sessions. No extra source selection by the answer model.
The full public Jev response (including coverage, gaps and usage) is supplied to
the Jev answer sessions: its serialization overhead is part of the measurement.
Baseline retrieval is free local code, not an artificially expensive LLM scan.

Count actual CLI input, cached input (a subset of input), output (including
reasoning where reported), all Jev usage, calls and wall latency. Also count
delivered page text with tiktoken/cl100k_base as a diagnostic, not API usage.
Price both uncached list-price equivalents and cache-aware estimates separately:
Luna $0.20/$0.02/$1.20 per million input/cached-input/output tokens; Jev $0.042/M
input including any separately reported cached input, output free. These are
API equivalents, not subscription invoices. Setup and grading costs are separate
experiment overhead, not per-query system costs.

Blind answer IDs hide arm names and token counts from an independent grader.
Preserve answer text, cited paths/quotes and question gold. Machines validate that
cited paths were delivered and quotes occur in their pages. Grade correctness,
citation quality and faithfulness 0–2 each (6 total); only 6/6 is a solved query.
Correctness: 2 covers all requested gold facts, 1 partly correct/abstains on a
required fact, 0 wrong core answer. Citation: 2 relevant checkable support for
all material claims, 1 incomplete support, 0 absent/fabricated/non-supporting.
Faithfulness: 2 no unsupported assertion or false completeness, 1 minor
overstatement, 0 material unsupported claim. Source abstention is faithful but
not automatically correct/complete. This is a new grading run, not the old scores.

Report each arm, paired changes versus its own no-Jev baseline and versus vanilla,
and quality regressions per question. Claim improvement only within the measured
axes: lower cost alone is not an overall improvement if quality decreases.
Cost per solved query is total arm cost divided by its solved count; zero solved
means undefined. No significance/generalization claims from one topic/one repeat.

This tests retrieval plus answer generation against a strong cheap lexical
baseline. It does not measure free-form native agent search, hook enforcement,
ingestion costs, production latency or a percentage improvement of the whole
product. Keep the historical artifact-size table separate; its read/query values
are index-plus-median-page estimates, not measured API consumption.
