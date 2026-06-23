---
type: source
title: "Darwin Godel Machine (paper)"
source-url: https://arxiv.org/abs/2505.22954
source-kind: paper
author: Zhang et al. (Sakana AI)
published: 2025-05
ingested: 2026-06-23
created: 2026-06-23
updated: 2026-06-23
tags: [topic/llm, rsi, self-improving-agents, archive, primary-source]
status: verified
---

# Darwin Godel Machine (paper)

The Darwin Godel Machine (DGM, Sakana AI) is a self-improving coding agent that **rewrites its own Python codebase**
(tools, workflow, prompting - not model weights) and validates each change empirically against a benchmark. Its
central, hard-won result - that an **archive of past versions plus open-ended exploration is necessary**, not just
greedy hill-climbing - is the lesson BSB's RSI loop borrows to avoid getting stuck ([[wiki/syntheses/bsb-rsi-loop]]).

## Key claims

- DGM mutates the agent's own runtime code and scores candidates with a **staged benchmark eval** (a cheap ~10-task
  filter, then ~50 tasks, then ~200 tasks only for top performers) - a cost-control pattern directly reusable for
  BSB's benchmark harness.
- Measured improvement: **SWE-bench 20.0% -> 50.0%** and **Polyglot 14.2% -> 30.7%** over the self-improvement run.
- **Ablation is the key claim**: removing self-improvement makes gains taper quickly; removing the open-ended
  **archive** (greedy single-path) gets the agent **stuck** when a poor modification makes later progress harder.
  Both components are necessary - this is the formal case against pure keep-if-better hill-climbing.
- DGM is a practical, empirical relaxation of Schmidhuber's theoretical Godel Machine (which required a formal proof
  of improvement before any self-rewrite - intractable in real ML settings).

## Connections

- Core evidence for the **archive + parallel exploration** guardrail in [[wiki/concepts/recursive-self-improvement]]
  and [[wiki/syntheses/bsb-rsi-loop]] (BSB's answer to the autoresearch "ratchet trap",
  [[wiki/sources/karpathy-autoresearch]]).
- Sakana's RSI Lab separately documents the real failure modes (drift, benchmark-pass/deploy-fail, constraint
  shortcuts). https://sakana.ai/rsi-lab/
- Hub: [[wiki/moc/bsb-architecture]].

## Sources

- PRIMARY: https://arxiv.org/abs/2505.22954 ; https://arxiv.org/html/2505.22954v2
- https://sakana.ai/rsi-lab/ (documented RSI failure modes)
- Related self-improvers: https://arxiv.org/abs/2408.08435 (ADAS) ; https://arxiv.org/abs/2310.02304 (STOP) ; https://arxiv.org/abs/2401.10020 (Self-Rewarding LMs)
