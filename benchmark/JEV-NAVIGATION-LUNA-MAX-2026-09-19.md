# Progressive Jev navigation with Luna max — 2026-09-19

**Result: the new navigation path reduces delivered page context, but it does
not save end-to-end tokens in this first controlled run.** It is therefore kept
as an optional quality and context-management path; it is not advertised as a
cost reduction.

## What was tested

The frozen six-question oracle and complete source snapshots from the earlier
Luna comparison were unchanged. A query-only Luna pass decomposed each question
into at most six evidence needs. Jev then classified bounded excerpts per need.
Luna received full pages selected by that plan, could report missing needs, and
the gateway followed deferred candidates and wikilinks for up to three answer
rounds. The mandatory roadmap evidence stayed available. All successful Luna
and Jev calls, repeated context, latency and fallback paths were recorded.

The implementation used four Luna CLI conversations and 35 Jev API calls. The
adaptive run produced 305,496 Luna input/output tokens and 591,306 bytes of
full-page context. The recorded lexical Luna baseline used 281,723 Luna
input/output tokens and 832,660 context bytes.

| Metric across both vaults | Lexical Luna baseline | Progressive Jev navigation |
|---|---:|---:|
| Luna input + output tokens | 281,723 | 305,496 (**+8.44%**) |
| Full-page context bytes | 832,660 | 591,306 (**−28.98%**) |
| Jev calls | 0 | 35 |
| Jev input + cached input tokens | 0 | 174,726 |
| Jev output tokens | 0 | 18,647 |
| Jev input + output tokens | 0 | 193,373 |
| Mean support-path recall | 100% | 91.67% |
| Mean frozen fact score | 96.67% | 97.62% |
| Mean citation-path coverage | 100% | 91.67% |
| Uncertainty score | 100% | 100% |
| Frozen quality floor | false | false |

The combined measured model tokens were therefore 498,869 versus 281,723 for
the baseline (**+77.04%**), before treating any subscription price or cache
discount as an assumption. This is a research total, not a billing statement.
The lower page-byte count is real for this snapshot; it does not compensate for
Jev classification and the extra adaptive turns. The exact routing question,
candidate count, cache behavior and host transport can change that balance.

The run still showed the intended behavior: direct technical questions received
the exact supporting pages, an absence question retained a scoped non-finding,
and the missing-evidence path requested more pages instead of inventing an
answer. The lower mechanical recall/citation values mean this version does not
pass the frozen acceptance floor and should not replace the retained-pool
baseline as the default.

## Decision

Keep progressive navigation behind the Jev opt-in switch. Use local `source`
lookup first for exact titles, aliases and URLs because it costs zero API calls.
Use `navigate` for broad or multi-hop questions, read every offered page in full,
and call `next` when a need remains unresolved. Do not interpret a Jev score or
an exhausted bounded frontier as global absence. Keep hard candidate pruning off.

The experiment was run against private snapshots. Only aggregate metrics and
the unchanged public oracle description are published; note text, private
questions, answers, prompts and credentials remain outside the repository.
