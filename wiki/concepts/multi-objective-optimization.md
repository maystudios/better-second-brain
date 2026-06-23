---
type: concept
name: "Multi-Objective Optimization (cost / latency / quality)"
aliases: [Pareto front, scalarization, lexicographic optimization, epsilon-constraint]
tags: [topic/llm, optimization, pareto, goodhart]
sources:
  - "[[wiki/sources/gepa-reflective-prompt-evolution]]"
  - "[[wiki/sources/anthropic-context-engineering]]"
  - "[[wiki/sources/karpathy-autoresearch]]"
created: 2026-06-23
updated: 2026-06-23
status: active
---

# Multi-Objective Optimization (cost / latency / quality)

When you want to improve several things at once - here **token cost down, latency down, quality up** - you cannot just
average them. The choice of *how* to combine objectives determines what the optimizer is even able to find, and a
careless combination lets it trade away the thing you care about most. BSB's RSI loop uses **lexicographic
constrained** optimization: quality is a hard floor, and only cost+latency are minimized inside the feasible region
([[wiki/syntheses/bsb-rsi-loop]]).

## How it shows up

- **Weighted-sum scalarization** (one weighted average) is simple but **cannot reach concave regions of a Pareto
  front** - whole families of good solutions are mathematically unreachable for any weights (https://pmc.ncbi.nlm.nih.gov/articles/PMC6105305/).
  Worse for BSB: if the grounding floor is a *term* in the sum, the optimizer can legally buy token savings with
  weaker citations.
- **Pareto-front methods** keep every non-dominated configuration and defer the preference - this is what GEPA does
  with instance-wise Pareto sets, and it resists local optima ([[wiki/sources/gepa-reflective-prompt-evolution]]).
- **Constrained / lexicographic / epsilon-constraint**: optimize quality to its floor *first* (a hard gate), then
  minimize cost+latency only among configurations that pass. This is the formal mechanism for "quality cannot be
  traded away," and it reaches points weighted-sum cannot (https://www.numberanalytics.com/blog/lexicographic-method-optimization-guide).
- **The single-metric special case**: Karpathy's autoresearch deliberately uses one scalar (`val_bpb`) -
  "no ambiguity about what better means." With three competing objectives you recover that clarity by staging: a
  binary quality gate, then a single cost+latency scalar inside the passing set ([[wiki/sources/karpathy-autoresearch]]).
- **A practical encoding**: multiplicative reward `r = r_efficiency * r_quality_gate` where the gate is 0/1 - any
  configuration that breaks the floor earns zero regardless of token savings.
- **Goodhart's law is the central hazard**: pushing an imperfect proxy past a point *reduces* the true objective; the
  effect is structural, and gaming-resistance requires multiple orthogonal signals plus an externally verifiable floor
  rather than one self-assessed score (https://arxiv.org/abs/2310.09144).

## Related concepts

- [[wiki/concepts/recursive-self-improvement]] - the loop this combination rule lives inside.
- [[wiki/concepts/llm-as-judge]] - why a single quality score is gameable and must be anchored externally.
- [[wiki/concepts/research-discipline]] - BSB's grounding floor, the constraint that is never a tradeable term.

## Sources

- Scalarization limits / Pareto: https://pmc.ncbi.nlm.nih.gov/articles/PMC6105305/ ; lexicographic: https://www.numberanalytics.com/blog/lexicographic-method-optimization-guide
- Knee-point cost/latency/accuracy (63% latency, 58% cost, 1-2% accuracy loss): https://arxiv.org/html/2510.18905v1
- Goodhart in RL: https://arxiv.org/abs/2310.09144
- [[wiki/sources/gepa-reflective-prompt-evolution]] (Pareto), [[wiki/sources/karpathy-autoresearch]] (single-metric), [[wiki/sources/anthropic-context-engineering]] (the cost/latency levers)
