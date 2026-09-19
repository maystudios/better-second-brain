# Jev branching retrieval — implementation and validation

Implemented on 2026-09-19 against the frozen [contract](../docs/jev-branching-contract.md).
Entry point: `python scripts/bsb_jev.py find "question"`, with optional repeated
`--need`, `--max-calls`, and `--max-pages` arguments.

The gateway builds the allowed Markdown catalog, including unindexed pages, and
lets Jev choose index branches, follow links and inspect full selected page text
in bounded chunks. Traversal, deferred alternatives, cycle prevention and budgets
run internally. The caller receives original pages, exact line/hash references,
conflicts, unresolved needs and coverage in one response. Selection distributions
remain in local receipts. The gateway does not generate the final answer.

## Machine and independent checks

- Full suite: `python -m unittest discover -s tests` — **114 passed**.
- Independent acceptance tests: 17 retrieval tests and 6 host/install tests,
  observed failing before implementation and passing afterward.
- Independent review found three defects: missing previous-page evidence in
  conflict assessment, lost conflict references at the output cap, and failure on
  an invalid optional index. All three were fixed.
- GPT-5.6 Luna at max independently added three regressions, observed red then
  green, and accepted these fixes. Earlier lanes had unnecessarily inherited
  Astra; subsequent delegation followed the user's explicit Luna-max correction.
- Additional probes covered traversal across 30 pages and conservative rejection
  of an oversized multi-need request. No fabricated success at either limit.
- Existing redirect tests emit two HTTPError cleanup ResourceWarnings; all pass.

## Live TypeSafe smoke trial

Runnable fixture: `python benchmark/jev_branching_smoke.py --out .bsb-jev/branching-smoke.json`.
Eight synthetic pages, three frozen questions, at most 60 API calls. Actual model:
`jev-1.13.0`. Result artifact: ignored `.bsb-jev/branching-smoke-v2.json`.

| Case | Result | Calls | Pages evaluated |
| --- | --- | ---: | ---: |
| German query, relevant page absent from index | ready; required original page returned | 9 | 5 |
| Two explicit needs on two different pages | ready; both required original pages returned | 8 | 3 |
| Missing encryption detail | unresolved; no invented source | 14 | 8 |

All three frozen observable checks passed. Total: 31 calls, 27,846 input tokens,
3,774 output tokens, 23.563 seconds. These checks establish basic live API and
retrieval behavior, not a general quality or cost advantage.

The first run's source comparator incorrectly compared Windows-written CRLF
files with the fixture's in-memory LF strings. It failed the first two cases.
The comparator now checks against actual source bytes; questions, expected paths
and acceptance criteria were unchanged. The first artifact remains preserved as
`.bsb-jev/branching-smoke.json`.

A separate real-vault integration check asked in German about Maps of Content.
With an explicit 18-call/8-page limit it evaluated 5 of 38 catalog pages and
returned 4 original pages, including `wiki/concepts/maps-of-content.md`.
All returned text and SHA-256 hashes matched disk. It correctly reported
`partial`, `request_budget`, 33 unvisited pages and 2 unread chunks. Artifact:
`.bsb-jev/live-vault-branching.json`. This is not an independently graded answer.

## Practical limits

Default limits are 24 calls, 12 evaluated pages, 120 seconds, 24 KiB per request,
and 512 KiB returned page text. Long pages use contiguous chunks up to 8,000 UTF-8
bytes; previous supporting evidence for conflict comparisons has a 4,000-byte
budget. Truncation and unread text are reported. Omitted full pages retain compact
references and can be fetched using the session receipt.

Top-two branching and the 0.5 evidence confidence threshold are uncalibrated
heuristics. `ready` is provisional, and global absence is never claimed. A packet
too large is reported explicitly rather than automatically split into new calls.
No end-to-end main-model token savings have been measured for this implementation.

Strict hook configuration routes supported native search/read/shell operations
through the gateway. Process/contract tests verify the new `find` allowlist.
Live interception in this Codex session is not established: repository hooks need
host trust and outer wrappers are outside the native event contract. These hooks
are not operating-system isolation. See [enforcement details](../docs/jev.md#hooks-and-enforcement-boundary).
