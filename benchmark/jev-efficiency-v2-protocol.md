# Jev efficiency correction — frozen 2026-09-19

The v1 result is retained, not overwritten: its free BM25 control measures a
different alternative from the user's intended delegation of model decisions.
The v1 search implementation is preserved in commit `87041ff`.

Correct two measured sources of overhead before another controlled run:

1. Pack original contiguous page text up to the existing 8,000-byte bound instead
   of starting another request at each heading after 1,000 bytes. Preserve every
   source byte, line reference, conflict, unread-text flag and request limit.
2. Give the caller full original selected pages and compact source references,
   conflicts, omissions and gaps. Per-call usage and verbose descriptors remain
   in detailed Python results/local receipts, rather than the answer-model input.

Independent regressions must be red before these fixes and green afterward.
Existing source-integrity and safety tests continue to apply. No reduced quality
floor or selective omission of difficult questions is permitted.

Re-use all 14 public Ruff questions and the byte-identical v1 corpus copies.
Keep all gold and grades out of retrieval and answer prompts. Run full+Jev and
lean+Jev again with unchanged 24-call/12-page limits, no hand-authored needs,
and the corrected compact caller response. Retain the v1 free BM25 runs as a
separate cheap-baseline comparison. No historical answer is relabeled as v2.

Also measure a concrete model-guided retrieval pipeline for vanilla/full/lean:
one fresh Luna/max call sees the complete path/title/heading catalog and chooses
at most three evidence paths; code returns those full pages; a second fresh
Luna/max call answers. All selector and answer usage is charged. This is a
bounded two-stage navigator, not unrestricted native-agent filesystem search.
Using a fresh answering context avoids repeatedly charging navigation history.
The Jev variants replace that model selector with the internal gateway.

All answer arms use the same answer instruction/schema and isolated runtime.
Grade source-grounded correctness, citations and faithfulness with the unchanged
v1 0–2 rubric, hiding arm names, paths and costs. Use bounded grading batches;
retain failures and include grading overhead separately. Reconcile every query
call to its receipt. Report per-arm total cost, tokens, quality and solved count;
report regressions, including results that fail the quality floor. Claim savings
only for the measured comparator, never as a universal product improvement.
