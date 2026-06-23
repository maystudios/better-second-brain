---
type: synthesis
title: "Applying Karpathy's autoresearch as a multi-objective RSI loop to BSB"
sources-cited:
  - "[[wiki/sources/karpathy-autoresearch]]"
  - "[[wiki/sources/gepa-reflective-prompt-evolution]]"
  - "[[wiki/sources/darwin-godel-machine]]"
  - "[[wiki/sources/anthropic-context-engineering]]"
  - "[[wiki/sources/karpathy-llm-wiki]]"
  - "[[wiki/sources/map-elites-quality-diversity]]"
tags: [topic/llm, rsi, optimization, bsb]
created: 2026-06-23
updated: 2026-06-23
status: stable
supersedes: ""
---

# Applying Karpathy's autoresearch as a multi-objective RSI loop to BSB

Can we apply a Recursive Self-Improvement loop - in the spirit of Karpathy's `autoresearch` - to make this Second
Brain cheaper (fewer tokens), faster, and higher-quality at the same time?

## Short answer

Yes, and BSB is unusually well-positioned for it: it already owns every part of the autoresearch loop except the
metric and the wiring. The correct formulation is **lexicographic constrained optimization** - grounding quality is an
inviolable hard floor, and only token-cost and latency are minimized inside the feasible region - not a weighted blend
that could trade citations for tokens. The loop is built (`scripts/rsi_fitness.py`, `docs/rsi-loop.md`, `CLAUDE.md
§3.7`) and validated: run retroactively, it autonomously re-derives the human decision to adopt lean fill (KEEP,
cost -62.6%, quality unchanged) and correctly rejects a cheaper-but-worse-cited alternative (DISCARD).

## Reasoning

**1. Autoresearch is a four-part pattern, and BSB already has three parts.** Karpathy's loop is: a *fixed harness*
(`prepare.py`), a *single mutable target* (`train.py`), *one cheap deterministic metric* (`val_bpb`), and a
*keep-if-better commit/revert* loop ([[wiki/sources/karpathy-autoresearch]]). BSB's equivalents already exist: the
benchmark (gold questions + LLM judge + `token_report.py`) is the fixed harness; the **method** (the [[wiki/sources/karpathy-llm-wiki|schema]],
templates, and the lean-fill/query policies) is the mutable target; the installed `auto-research` skill is the
mutation engine. The only genuinely missing pieces were a *multi-objective metric* and the *closed loop* - which is
exactly what this work added.

**2. Three objectives demand a constraint, not an average.** The owner wants tokens down, latency down, and quality
up together. But in an LLM-wiki, cost and latency share one lever ("load less"), whose degenerate optimum is "write
and load nothing" - which scores perfectly until quality stops it. So quality must be a **hard floor**, never a term
in a weighted sum: weighted-sum scalarization both fails to reach concave Pareto regions and would let the optimizer
legally buy token savings with weaker citations ([[wiki/concepts/multi-objective-optimization]]). The defensible
formulation is lexicographic: pass the grounding gate first, then minimize a single cost+latency scalar among the
survivors - recovering Karpathy's single-metric clarity *inside* the feasible region.

**3. The metric is `rsi_fitness.py`, and the floor is anchored to externally verifiable facts.** A candidate method is
KEPT iff (a) the §1.5 grounding floor holds - `lint_sources --strict-min-tier A` passes on the real `wiki/`, the same
gate CI runs; (b) quality does not regress on total / citation / faithfulness; and (c) cost OR latency strictly drops
with neither rising. The floor checks *real source counts and fetchable links* (`lint_sources`, `verify_wikilinks`),
not an LLM's self-assessment - which is what makes it Goodhart-resistant ([[wiki/concepts/llm-as-judge]]).

**4. BSB beats the autoresearch loop on its own weak spot - and now has the code to prove it.** Karpathy's strict
keep-if-better loop has a **ratchet trap**: `program.md` keeps a change only if `val_bpb` strictly improves, *else
`git reset`*, and on getting stuck offers only "rewind very very sparingly (if ever)" - no mechanism
([[wiki/sources/karpathy-autoresearch]]). The community has already forked it to add exploration (the GEAR
genetic-search-graph; issue #179). BSB builds the fix in: `scripts/rsi_archive.py` adds a third tier, **EXPLORE** -
a worse-now candidate that is a big single-axis win or a new niche is **archived as a stepping stone** rather than
discarded - backed by the Darwin-Godel-Machine always-add archive, MAP-Elites quality-diversity, and the non-elitism
valley theorem (elitism is exponential in valley *length*; accepting worse moves, only in *depth*)
([[wiki/concepts/quality-diversity-search]], [[wiki/sources/map-elites-quality-diversity]], [[wiki/sources/darwin-godel-machine]]).
A forward fleet of five deterministic levers demonstrates it: `merge-sources` (-59% tokens, citations destroyed) is
exactly the candidate a greedy loop *discards* - yet it is the only doorway to `merge-sources-compact` (-49.6% tokens
at **full** grounding, one small latency tweak from adoption). The diverse archive keeps all three merged variants
alive; `drop-links` is adopted outright (-10% tokens, quality intact). BSB also runs hypotheses **in parallel** (a
workflow) where autoresearch is single-GPU sequential, and grows toward GEPA-style reflective Pareto evolution
([[wiki/sources/gepa-reflective-prompt-evolution]]).

**5. The forward levers are concrete and sourced.** The candidate "method mutations" the loop will try next are not
guesses: server-side tool-result clearing (48-67% peak-token cut), caching the stable CLAUDE.md prefix (up to ~85%
latency on re-sent tokens), model-tiering per step, and sub-agent context isolation - all measurable by the existing
harness ([[wiki/sources/anthropic-context-engineering]]).

## Counter-points

- **The judge can be gamed, and verbosity bias actively fights lean fill.** LLM judges reward longer, well-formatted
  answers (effect size 0.76-0.92), so a judge-score-maximizing loop could push *away* from BSB's token-cheap pages
  ([[wiki/concepts/llm-as-judge]]). Mitigation: reference-guided scoring + length penalties, and keeping quality a
  *floor* (don't regress) rather than a maximand the loop spends tokens to inflate.
- **Reward hacking rises with iteration depth** (~26% of steps at 10 -> ~58% at 100 in code-agent studies). Mitigation:
  cap iterations, early-stop, and re-validate kept changes on a **held-out / novel corpus** the loop never optimized
  against (the roadmap's private-corpus item) - the locked harness alone is not enough.
- **Small gold sets can't drive optimization.** GEPA degenerates when training instances are too few, and BSB's
  current benchmark is ~14 questions per corpus - enough to *validate* the metric, not yet to *drive* many iterations.
  Growing the gold set (and using the existing `questions-public.json` / `questions.json` split as held-out) is a
  prerequisite for running the loop hard.
- **Karpathy never connected the LLM-wiki to autoresearch.** The RSI-on-schema idea is a BSB synthesis, not his
  claim; he frames schema evolution as human-directed co-evolution. The loop here keeps a human gate precisely
  because autonomous schema self-modification is the unproven, riskier step.

## What would change my mind

- If running the loop forward produced KEEP decisions that a held-out novel-corpus re-test then reversed, the metric
  would be overfitting and the whole approach would need a stronger held-out gate before any autonomy.
- If a benchmark with a real *correctness* gap (not just citation traceability) showed lean/optimized methods losing
  facts, "quality as a non-regression floor" would be too weak and quality would have to become a maximized objective.

## Sources

PRIMARY / anchor:
- [[wiki/sources/karpathy-autoresearch]] - the fixed-harness / mutable-target / one-metric / keep-if-better loop. https://github.com/karpathy/autoresearch
- [[wiki/sources/karpathy-llm-wiki]] - the wiki pattern whose *method* this loop improves. https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f

METHOD / EVIDENCE:
- [[wiki/sources/darwin-godel-machine]] - archive + exploration beats greedy hill-climbing. https://arxiv.org/abs/2505.22954
- [[wiki/sources/gepa-reflective-prompt-evolution]] - reflective Pareto method optimization. https://arxiv.org/abs/2507.19457
- [[wiki/sources/anthropic-context-engineering]] - the concrete token/latency levers. https://platform.claude.com/docs/en/build-with-claude/context-editing
- [[wiki/sources/map-elites-quality-diversity]] - the diverse archive that keeps stepping stones. https://arxiv.org/abs/1504.04909

Concepts: [[wiki/concepts/recursive-self-improvement]], [[wiki/concepts/multi-objective-optimization]], [[wiki/concepts/llm-as-judge]], [[wiki/concepts/quality-diversity-search]]. Runbook: `docs/rsi-loop.md` (§11 exploration). Metric: `scripts/rsi_fitness.py`; archive: `scripts/rsi_archive.py`; levers: `scripts/rsi_transforms.py`; ledger: `benchmark/RSI_LOG.tsv`. Hub: [[wiki/moc/bsb-architecture]].
