---
type: source
title: "Andrej Karpathy - autoresearch (repo)"
source-url: https://github.com/karpathy/autoresearch
source-kind: repo
author: Andrej Karpathy
published: 2026-03-07
ingested: 2026-06-23
created: 2026-06-23
updated: 2026-06-23
tags: [topic/llm, rsi, eval-loop, autonomous-agents, primary-source]
status: verified
---

# Andrej Karpathy - autoresearch (repo)

`autoresearch` is Karpathy's minimal harness for letting an agent do ML research autonomously overnight on a single
GPU. It is the anchor pattern for the BSB RSI loop ([[wiki/syntheses/bsb-rsi-loop]]): a **fixed harness**, a **single
mutable target**, **one cheap deterministic metric**, and a **keep-if-better commit/revert loop**. Its discipline -
the agent may edit only the target, never the scorer - is exactly what makes self-improvement honest.

## Key claims

- Three files matter: `prepare.py` is the **fixed** harness (data pipeline, tokenizer, the `evaluate_bpb` function,
  the `TIME_BUDGET` constant) and the agent must never edit it; `train.py` is the **sole mutable** file (~540 lines:
  a GPT with RMSNorm, rotary embeddings, sliding-window attention, a Muon+AdamW hybrid optimizer); `program.md` is the
  human-written, static instruction file. ([[wiki/sources/karpathy-autoresearch]])
- The loop: read `train.py` -> propose a change with reasoning -> run a **5-minute (300s) wall-clock** training job
  (compile time excluded) -> evaluate **validation bits-per-byte (`val_bpb`)** -> **commit if `val_bpb` strictly
  improved, else `git reset --hard HEAD~1`** -> log to `results.tsv` -> repeat. No numerical threshold; any strict
  improvement is kept.
- `val_bpb` is chosen because it is **vocabulary-size-independent**, so architecturally different candidates compare
  fairly - the single-metric clarity ("no ambiguity about what better means") is treated as essential.
- A documented overnight run did **89 experiments (15 kept, 74 discarded, 0 crashes)** on an H100 80GB, moving
  `val_bpb` from **0.997900 to 0.977287**. `program.md` explicitly says *"do NOT pause to ask the human if you should
  continue"* - maximum autonomy within fixed constraints.
- Anti-gaming is **structural, not explicit**: only `prepare.py` immutability + the single-file scope stop the agent
  from rewriting its own scorer. The short-horizon proxy is itself gameable - a derivative (a Shopify fork's "53%
  speedup") was flagged for optimizing the 5-min metric rather than real capability. The strict keep-if-better rule
  also creates a **ratchet trap**: changes needing a temporary regression to escape a local minimum are impossible.

## Notable quotes

> only really has three files that matter

(Stars: ~88k on GitHub by mid-2026 per the repo page; exact count not independently confirmable. Released 2026-03-07.)

## Connections

- Anchors [[wiki/concepts/recursive-self-improvement]] and the design in [[wiki/syntheses/bsb-rsi-loop]].
- Generalized by BSB from one metric to a constrained [[wiki/concepts/multi-objective-optimization]] problem.
- Same author and lineage as [[wiki/sources/karpathy-llm-wiki]] / [[wiki/entities/andrej-karpathy]]; note Karpathy
  draws **no** explicit link between the LLM-wiki and autoresearch - the RSI-on-schema connection is a BSB synthesis.
- Hub: [[wiki/moc/bsb-architecture]].

## Open questions

- Karpathy keeps `program.md` (the protocol) static; BSB's loop instead treats its protocol (CLAUDE.md) as mutable.
  Where is the safe boundary for self-modifying the protocol itself?

## Sources

- PRIMARY: https://github.com/karpathy/autoresearch ; https://raw.githubusercontent.com/karpathy/autoresearch/master/program.md ; https://raw.githubusercontent.com/karpathy/autoresearch/master/train.py
- https://github.com/karpathy/autoresearch/discussions/32 (the 89-experiment run: 0.997900 -> 0.977287)
- https://deepwiki.com/karpathy/autoresearch/1.1-system-architecture (architecture)
- https://www.verdent.ai/guides/what-is-autoresearch-karpathy (loop + metric walkthrough)
