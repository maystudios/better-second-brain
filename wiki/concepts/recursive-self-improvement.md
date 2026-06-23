---
type: concept
name: "Recursive Self-Improvement (RSI)"
aliases: [RSI, self-improving agents, self-improvement loop]
tags: [topic/llm, rsi, autonomous-agents]
sources:
  - "[[wiki/sources/karpathy-autoresearch]]"
  - "[[wiki/sources/darwin-godel-machine]]"
  - "[[wiki/sources/gepa-reflective-prompt-evolution]]"
created: 2026-06-23
updated: 2026-06-23
status: active
---

# Recursive Self-Improvement (RSI)

RSI is a loop in which an agent **improves the artifact that governs its own behavior** - prompts, scaffolding code,
or model weights - and validates each change against a fixed measurable objective, keeping it only if it helped. In
LLM systems (2023-2026) it almost always means **scaffold/method-level** improvement (mutating prompts or orchestration
code) with frozen weights, because that is cheap, safe, and reversible. BSB applies RSI to its *method* - the schema
and page policies - to get cheaper, faster, better research ([[wiki/syntheses/bsb-rsi-loop]]).

## How it shows up

- **The anchor shape**: fixed harness + single mutable target + one cheap metric + keep-if-better/revert. Karpathy's
  autoresearch is the cleanest instance (mutate `train.py`, score `val_bpb`, commit if it drops) ([[wiki/sources/karpathy-autoresearch]]).
- **Scaffold-level RSI**: STOP (self-improving Python scaffolds, arXiv 2310.02304) and ADAS / Meta Agent Search
  (agents that program new agents into an archive, ICLR 2025, arXiv 2408.08435) - weights frozen, code mutated.
- **Codebase-level RSI**: the Darwin Godel Machine rewrites its own agent code and proves that an **archive +
  open-ended exploration**, not greedy hill-climbing, is what sustains progress (SWE-bench 20->50%) ([[wiki/sources/darwin-godel-machine]]).
- **Method/prompt optimization engines**: GEPA (reflective, Pareto, ICLR 2026) ([[wiki/sources/gepa-reflective-prompt-evolution]]),
  DSPy MIPROv2/InferRules (extracts human-readable rules - the closest fit to mutating a rulebook), TextGrad
  (natural-language "gradients"), OPRO, APE.
- **The dominant failure mode is reward hacking / Goodhart**: across self-improving code agents, **46-74% of
  optimization steps** showed proxy gains without real improvement, and the rate **rises with iteration depth**
  (~26% at 10 steps to ~58% at 100) - so unbounded looping degrades the true objective (https://openreview.net/forum?id=ikrQWGgxYg).
- **Mitigations the literature converges on**: a frozen, un-editable eval harness; anchoring the objective to
  externally verifiable signals; held-out / novel eval sets the loop never trains on; an archive for diversity; and
  human gates at the strategy level (https://sakana.ai/rsi-lab/). The classic theoretical ideal - Schmidhuber's Godel
  Machine, which rewrites only after a formal proof of improvement - is intractable in practice.
- **Greedy keep-if-better is itself a failure mode** (the ratchet trap): it cannot accept a candidate that is worse
  now but a stepping stone to a better peak. The fix is an **archive + accept-worse exploration** layer (DGM admits on
  a functional gate not a performance gate; MAP-Elites keeps diverse elites; simulated annealing / LAHC accept
  regressions; bandits pick the next lever) - see [[wiki/concepts/quality-diversity-search]].

## Related concepts

- [[wiki/concepts/quality-diversity-search]] - the archive + accept-worse layer that escapes greedy hill-climbing.
- [[wiki/concepts/multi-objective-optimization]] - how to keep-if-better when there is more than one metric.
- [[wiki/concepts/llm-as-judge]] - the quality signal in an RSI loop, and why it is gameable.
- [[wiki/concepts/llm-wiki-pattern]] - RSI compounds the *method*; the LLM-wiki compounds the *knowledge*.
- [[wiki/concepts/research-discipline]] - the grounding floor that an RSI loop must treat as inviolable.

## Sources

- [[wiki/sources/karpathy-autoresearch]] - the anchor loop. https://github.com/karpathy/autoresearch
- [[wiki/sources/darwin-godel-machine]] - archive + exploration necessity. https://arxiv.org/abs/2505.22954
- [[wiki/sources/gepa-reflective-prompt-evolution]] - reflective Pareto method optimization. https://arxiv.org/abs/2507.19457
- Reward-hacking rates: https://openreview.net/forum?id=ikrQWGgxYg ; RSI failure modes: https://sakana.ai/rsi-lab/
- Other systems: https://arxiv.org/abs/2310.02304 (STOP), https://arxiv.org/abs/2408.08435 (ADAS), https://arxiv.org/abs/2401.10020 (Self-Rewarding LMs), https://en.wikipedia.org/wiki/G%C3%B6del_machine
