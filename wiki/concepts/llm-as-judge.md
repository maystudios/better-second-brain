---
type: concept
name: "LLM-as-Judge & research-quality measurement"
aliases: [LLM judge, faithfulness, FActScore, RAGAS, citation attribution]
tags: [topic/llm, evaluation, quality, faithfulness]
sources:
  - "[[wiki/sources/karpathy-autoresearch]]"
  - "[[wiki/sources/darwin-godel-machine]]"
  - "[[wiki/sources/anthropic-context-engineering]]"
created: 2026-06-23
updated: 2026-06-23
status: active
---

# LLM-as-Judge & research-quality measurement

To make "research quality" an optimization target you must measure it, and the measuring instrument is usually another
LLM scoring answers against a gold set - exactly what BSB's benchmark judge does. The catch: an LLM judge is biased
and gameable, so in an RSI loop the quality signal must be **anchored to externally verifiable facts**, not the
judge's opinion alone, or the loop will optimize the judge instead of the truth ([[wiki/syntheses/bsb-rsi-loop]]).

## How it shows up

- **Grounding/faithfulness metrics** decompose an answer into atomic claims and check each against its cited source.
  FActScore is the canonical pipeline (best-config error <2% vs humans; ChatGPT scored 58% on biographies)
  (https://arxiv.org/abs/2305.14251). RAGAS adds faithfulness + answer-relevancy + context-precision (context-recall
  needs a reference) (https://arxiv.org/pdf/2309.15217).
- **Citation attribution** is distinct from citation *count*: AIS / AttrScore / CiteEval check whether text is
  actually supported by the cited source; ALCE found even top models lack full citation support ~50% of the time.
  Raw citation count is gameable; attribution-checked scores are not (https://arxiv.org/pdf/2305.14627).
- **Judge biases** are real and measured: **verbosity/style bias dominates (effect size 0.76-0.92)**, position bias is
  smaller (debiasable), and **self-preference bias** makes a judge favor text from its own model family
  (https://arxiv.org/html/2604.23178 ; https://arxiv.org/html/2410.21819v2).
- **Why this matters for lean fill**: verbosity bias means a terse, accurate page can score *lower* than a verbose
  one - so a judge-score-maximizing loop would push *against* BSB's token-cheap lean pages. The fix is reference-guided
  scoring (score against the cited source, not an "ideal" answer) and length-penalized prompts.
- **Robust judging via debate**: a multi-judge / prover-skeptic ensemble with adaptive stopping lifts accuracy ~+4-6pp
  over a single judge (https://arxiv.org/html/2510.12697v1). This is the same adversarial-verification pattern BSB's
  research workflow uses - and it costs more, so reserve it for the confirmation gate, not every candidate.
- **Composite, gaming-resistant quality**: quality = faithfulness + attribution-checked citation + source-tier +
  freshness, with a **hard floor** (score = 0 if sources < 3 or faithfulness < threshold). The floor is anchored to
  things an optimizer cannot fake without doing the work - the role BSB's >=3-real-sources rule already plays.

## Related concepts

- [[wiki/concepts/research-discipline]] - BSB's grounding rule, the externally-verifiable quality floor.
- [[wiki/concepts/recursive-self-improvement]] - the loop whose quality signal this is.
- [[wiki/concepts/multi-objective-optimization]] - quality as a hard constraint, not a tradeable term.

## Sources

- Faithfulness: https://arxiv.org/abs/2305.14251 (FActScore), https://arxiv.org/pdf/2309.15217 (RAGAS)
- Attribution: https://arxiv.org/pdf/2305.14627 (ALCE/AIS), https://arxiv.org/pdf/2506.01829 (CiteEval)
- Judge bias: https://arxiv.org/html/2604.23178 (verbosity/position), https://arxiv.org/html/2410.21819v2 (self-preference); debate: https://arxiv.org/html/2510.12697v1
- [[wiki/sources/karpathy-autoresearch]], [[wiki/sources/darwin-godel-machine]], [[wiki/sources/anthropic-context-engineering]]
