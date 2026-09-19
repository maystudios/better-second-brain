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
input/output tokens and 832,660 context bytes. The Jev plans consumed 174,726
reported input/cached-input tokens and 18,647 output tokens across 35 calls.

For the cost comparison below, the current standard API list prices are used:
Jev `$0.042/M` input with free output, GPT-5.6 Luna `$0.20/$1.20/M`, Claude Opus
5 `$5/$25/M`, Claude Fable 5.1 `$10/$50/M`, and GPT-6 Astra `$10/$50/M` for
input/output. These are list-price equivalents; subscription credits, cache
contracts and host-specific quotas are not invoices.

| Metric across both vaults | Lexical Luna baseline | Progressive Jev navigation |
|---|---:|---:|
| Luna input + output tokens | 281,723 | 305,496 (**+8.44%**) |
| Full-page context bytes | 832,660 | 591,306 (**−28.98%**) |
| Jev calls | 0 | 35 |
| Jev input + cached input tokens | 0 | 174,726 |
| Jev output tokens | 0 | 18,647 |
| Jev input + output tokens | 0 | 193,373 |
| Jev estimated input cost | $0.0000 | **$0.0073** |
| Mean support-path recall | 100% | 91.67% |
| Mean frozen fact score | 96.67% | 97.62% |
| Mean citation-path coverage | 100% | 91.67% |
| Uncertainty score | 100% | 100% |
| Frozen quality floor | false | false |

At the published Luna rates, the baseline's 274,787 input and 6,936 output
tokens are about **$0.0633**. The adaptive Luna answer turns are about
**$0.0843**, Jev adds **$0.0073**, and the combined adaptive run is about
**$0.0916** (**+44.8%** versus the baseline). The combined measured model
tokens were 498,869 versus 281,723 (**+77.04%**) before treating any
subscription price or cache discount as an assumption. These are research
estimates, not billing statements. The lower page-byte count is real for this
snapshot; it does not compensate for Jev classification and the extra adaptive
turns. The exact routing question, candidate count, cache behavior and host
transport can change that balance.

The run still showed the intended behavior: direct technical questions received
the exact supporting pages, an absence question retained a scoped non-finding,
and the missing-evidence path requested more pages instead of inventing an
answer. The fact score rose from 96.67% to 97.62%, but support-path recall and
citation coverage both fell from 100% to 91.67%; the frozen quality floor stayed
false. This version therefore does not yet replace the retained-pool baseline as
the default.

## Break-even scenario (not an observed result)

If a later implementation holds the baseline answer output and quality constant
while reducing only its input by the observed 28.98%, the same `$0.0073` Jev
overhead would still leave a theoretical saving. This isolates the price effect
from the failed extra-turn behavior in this run:

| Main model | Baseline task | 28.98% input reduction + Jev | Estimated change |
|---|---:|---:|---:|
| GPT-5.6 Luna | $0.0633 | $0.0547 | **−13.6%** |
| Claude Opus 5 | $1.5473 | $1.1565 | **−25.3%** |
| Claude Fable 5.1 | $3.0947 | $2.3057 | **−25.5%** |
| GPT-6 Astra | $3.0947 | $2.3057 | **−25.5%** |

This is the reason to keep Jev available as a cheap classifier before an
expensive model, not evidence that the current navigation path already saves
money. Jev's official price is [documented by TypeSafe](https://docs.typesafe.ai/models);
the main-model prices are the standard API rates published by [OpenAI](https://developers.openai.com/api/docs/models/gpt-5.6-luna),
[OpenAI Astra](https://developers.openai.com/api/docs/models/gpt-6-astra), and
[Anthropic](https://platform.claude.com/docs/en/models/fable-5-1/overview).

## Decision

Keep progressive navigation behind the Jev opt-in switch. Use local `source`
lookup first for exact titles, aliases and URLs because it costs zero API calls.
Use `navigate` for broad or multi-hop questions, read every offered page in full,
and call `next` when a need remains unresolved. Do not interpret a Jev score or
an exhausted bounded frontier as global absence. Keep hard candidate pruning off.

The experiment was run against private snapshots. Only aggregate metrics and
the unchanged public oracle description are published; note text, private
questions, answers, prompts and credentials remain outside the repository.
