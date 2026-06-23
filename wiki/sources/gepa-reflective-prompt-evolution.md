---
type: source
title: "GEPA - Reflective Prompt Evolution (paper)"
source-url: https://arxiv.org/abs/2507.19457
source-kind: paper
author: Agrawal et al.
published: 2025-07
ingested: 2026-06-23
created: 2026-06-23
updated: 2026-06-23
tags: [topic/llm, prompt-optimization, pareto, rsi, primary-source]
status: verified
---

# GEPA - Reflective Prompt Evolution (paper)

GEPA ("Genetic-Pareto", accepted as an ICLR 2026 oral) optimizes the *instructions* of an LLM system by reflecting on
execution traces in natural language and evolving candidates against a **Pareto front** rather than a single scalar.
It is the closest published engine to what BSB's RSI loop needs - a multi-objective method optimizer that keeps a
diverse archive instead of greedily chasing one number ([[wiki/syntheses/bsb-rsi-loop]]).

## Key claims

- GEPA maintains **instance-wise Pareto sets**: a candidate survives if it scores best on at least one training
  instance and is not strictly dominated; mutation parents are sampled in proportion to how many instances a
  candidate "wins". This preserves diversity and avoids the local optima a single-metric greedy optimizer falls into.
- Mutation is driven by **natural-language reflection over rollout traces** - no scalar gradient - which is why the
  approach transfers to evolving a human-readable rulebook (a CLAUDE.md), not just a numeric prompt.
- Reported gains: up to **+11.1% over DSPy MIPROv2** and up to **+19% over GRPO**, using as much as **35x fewer
  rollouts** - reflective/Pareto search is sample-efficient.
- Failure mode (relevant to BSB): with **too few training instances the Pareto front degenerates** - nearly every
  candidate "wins" somewhere, so selective pressure collapses. A small gold set cannot drive reliable optimization.

## Connections

- The archive + Pareto idea informs [[wiki/concepts/multi-objective-optimization]] and the anti-ratchet design in
  [[wiki/syntheses/bsb-rsi-loop]].
- A prompt/method-mutation engine alongside DSPy MIPROv2/InferRules, TextGrad, OPRO, APE (see
  [[wiki/concepts/recursive-self-improvement]]).
- Hub: [[wiki/moc/bsb-architecture]].

## Sources

- PRIMARY: https://arxiv.org/abs/2507.19457 ; https://arxiv.org/html/2507.19457v1
- Contrast engines: https://dspy.ai/api/optimizers/MIPROv2/ ; https://arxiv.org/abs/2406.07496 (TextGrad) ; https://arxiv.org/abs/2309.03409 (OPRO)
