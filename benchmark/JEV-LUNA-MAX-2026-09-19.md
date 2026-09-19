# Jev with GPT-5.6 Luna at max — 2026-09-19

**Result: no demonstrated token saving from the active retained-pool mode.**
Jev prioritization retained all evidence and used almost exactly the same Luna
tokens as lexical retrieval alone. Experimental top-4 pruning saved 53.4% of
Luna input/output tokens, but removed needed evidence. It remains disabled by
default. No new optimization is promoted from this trial.

## Controlled comparison

The user requested a repeat with `gpt-5.6-luna`, reasoning effort `max`.
Six fresh Codex CLI 0.154.0 runs answered the same six frozen questions across
two private populated vault snapshots, with three questions per run:

- **A — lexical:** the corrected 12-document candidate packets from the
  [Gemini experiment](JEV-2026-09-19.md), with complete pages and mandatory roadmap.
- **B — top 4:** exactly the previously captured Jev-pruned packets.
- **P — retained pool:** exactly A's pages, reordered using captured Jev
  classifications; no page removed, mandatory roadmap retained.

P was specified before these model calls. The questions, answer oracle, scorer,
source pages and prior Jev classifications were not retuned. No new Jev API
calls were needed: the saved classifications were reused. Their input usage
and measured historical retrieval latency are reported as deployment overhead.

A first file-reading preflight was blocked by the local Codex execution policy.
The measured trial therefore supplied each complete, unchanged JSON source
packet directly through stdin and required final structured JSON. All six
successful runs used this same transport, read-only sandbox, ignored user
configuration, and no model tool calls or delegation. **This differs from the
earlier Gemini file-reading host**, so cross-host token differences cannot be
attributed to the model or to Jev alone. The failed preflight is recorded
separately as setup overhead, not silently scored as a model-quality failure.
That failed preflight consumed 613,985 input tokens (570,624 cached), 6,510
output tokens and 146.4 seconds. Including it, the six successful answer runs
plus failed setup consumed **1,315,329 Luna input/output tokens** in this pilot,
of which 586,752 were cached input. These are research-execution totals, not
the per-query savings comparison or a bill; independent report review is
additional overhead recorded separately.

## Measurements

| Metric, total across both vaults | A: lexical | B: top 4 | P: retained pool |
|---|---:|---:|---:|
| Luna input tokens | 274,787 | 120,010 | 274,783 |
| Luna output tokens, including reasoning | 6,936 | 11,211 | 7,107 |
| Luna input + output tokens | 281,723 | 131,221 | 281,890 |
| Change in Luna input + output vs A | — | **−53.42%** | **+0.06%** |
| Cached input tokens, already included in input | 0 | 0 | 16,128 |
| Full-page context bytes | 832,660 | 297,094 | 832,660 |
| Answer seconds, sum of two runs | 158.4 | 221.9 | 140.5 |
| Historical retrieval seconds | 12.7 | 19.6 | 19.6 |
| Answer + historical retrieval seconds | 171.2 | 241.5 | 160.1 |
| Expected support-path recall | 100% | **83.3%** | 100% |
| Expected citation-path coverage | 100% | 83.3% | 91.7% |
| Frozen substring fact score | 96.7% | 82.1% | 86.4% |
| Frozen uncertainty-marker score | 100% | 50% | 50% |
| Reused Jev input tokens, additional to Luna | 0 | 25,759 | 25,759 |

Reasoning tokens are included in output, not added twice. P's cache hits may
affect charged cost and latency, but cache warmth/run order are uncontrolled;
they do not establish a Jev saving. Time is summed per-run elapsed time, not
parallel campaign wall time. P's roughly 6.5% lower summed answer-plus-retrieval
time is a single observation, not a reliable speedup estimate. B was slower
despite its smaller input and spent more reasoning/output tokens.

## Quality and decision

Readback confirmed that A and P supplied the requested technical configuration
fix and cited the supporting page. B correctly reported that its packet lacked
the exact configuration recipe. A different answer model cannot recover evidence
that the retrieval policy removed without fetching more sources or relying on
outside knowledge, which this trial prohibited.

The mechanical scorer is deliberately unchanged. Some lower scores reflect
literal matching limitations: English hyphenated paraphrases, a creator's name
not repeated from the question, or alternative explicit uncertainty wording.
Readback is reported alongside the scores; it does not override the frozen
gate. The formal quality floor is false for all three arms. Citation coverage
is separately reported because the frozen floor does not itself check it.
These metrics are not calibrated estimates of factual accuracy.

**Keep hard pruning experimental and off.** The retained-pool integration
preserves the candidate evidence but has no demonstrated net token benefit in
this test. For cost planning, treat Jev as optional prioritization and bounded
maintenance review, not a proven percentage reduction in end-to-end expense.
One run per vault/arm and different cache behavior do not justify a stable
cost, speed, or model-quality claim. Actual subscription billing was not measured.

## Reproduction and privacy

The private trial retains packet and prompt hashes, raw Codex JSONL usage,
invocation model/effort, answers, timing and the initial blocked preflight.
No private questions, note text, secrets or evaluation answers are published.
The same frozen oracle hashes as the Gemini report apply. Reproduce with your
own fixed questions and full-page packets; run each policy under the same host
transport and report token usage, cache behavior, evidence coverage and failures
together. Do not substitute a smaller context-byte count for total task cost.
