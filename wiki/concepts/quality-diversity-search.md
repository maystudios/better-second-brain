---
type: concept
name: "Quality-Diversity & accept-worse search (escaping local optima)"
aliases: [MAP-Elites, novelty search, simulated annealing, late-acceptance hill climbing, exploration-exploitation, objective paradox]
tags: [topic/llm, optimization, quality-diversity, rsi, exploration]
sources:
  - "[[wiki/sources/map-elites-quality-diversity]]"
  - "[[wiki/sources/darwin-godel-machine]]"
  - "[[wiki/sources/karpathy-autoresearch]]"
created: 2026-06-23
updated: 2026-06-23
status: active
---

# Quality-Diversity & accept-worse search (escaping local optima)

Greedy hill-climbing (keep a change only if it is immediately better) gets stuck: on a rugged fitness landscape the
path to a higher peak often runs *downhill first*. A family of methods deliberately **keeps worse-now candidates** -
as a diverse archive, or by probabilistic acceptance - so the search can cross valleys and recombine stepping stones.
This is the mechanism BSB's RSI loop uses to avoid the ratchet trap ([[wiki/syntheses/bsb-rsi-loop]], `docs/rsi-loop.md` §11).

## How it shows up

- **The ratchet trap is real, not theoretical.** Karpathy's autoresearch keeps a change only if `val_bpb` strictly
  improves, else `git reset`; its only stuck-advice is "rewind very very sparingly (if ever)" - no mechanism. The
  community forked it to add exploration (the GEAR genetic-search-graph; issue #179) ([[wiki/sources/karpathy-autoresearch]]).
- **Why it matters mathematically:** strict elitism crossing a fitness valley runs in time exponential in the valley's
  *length*; Metropolis-style acceptance (take a worse move with some probability) is exponential only in its *depth* -
  a potentially exponential speedup on long, shallow valleys (https://pmc.ncbi.nlm.nih.gov/articles/PMC6438649/).
- **MAP-Elites / Quality-Diversity:** keep one elite per behavioral niche; a globally weaker solution survives if it
  occupies a distinct niche. Illumination is a *superset* of optimization ([[wiki/sources/map-elites-quality-diversity]]).
- **Always-add archives:** the Darwin Godel Machine admits any *functional* candidate (compiles + can self-edit) to
  the archive - performance is **not** the admission gate, only the parent-sampling weight (sigmoid of score x novelty
  bonus) - and ablations show this open-ended archive is *necessary* (SWE-bench 20->50%) ([[wiki/sources/darwin-godel-machine]]).
- **Novelty search & the objective paradox:** Lehman & Stanley reward behavioral novelty (k-NN distance) with no
  fitness signal at all; Stanley & Lehman argue ambitious objectives prune the very stepping stones needed - "almost
  no prerequisite to any major invention was invented for that invention's purposes" (https://link.springer.com/article/10.1007/s10710-015-9250-8).
  POET shows a flat-ground walking gait (a local optimum) becomes the prerequisite for learning to jump (https://arxiv.org/abs/1901.01753).
- **Probabilistic acceptance rules (how worse-now is kept):** Simulated annealing accepts a worse move with
  probability `exp(-delta/T)`, cooling `T` over time (https://en.wikipedia.org/wiki/Simulated_annealing). **Late-Acceptance
  Hill-Climbing** is the scale-invariant, near-parameter-free version - accept if better than the fitness `L_h` steps
  ago - recommended for BSB because the fitness is a composite score, not a physical energy (https://ideas.repec.org/a/eee/ejores/v258y2017i1:p:70-78.html).
- **Which lever to try next:** a multi-armed bandit (UCB1 `mu + sqrt(2 ln t / n)`, or Thompson sampling) spends the
  experiment budget on the *under-explored* arm, not just the current best - exploration tied to uncertainty (https://www.jmlr.org/papers/volume3/auer02a/auer02a.pdf).
- **Evolutionary program search** keeps populations: FunSearch islands (periodic purge of the worst half), AlphaEvolve
  (MAP-Elites over islands) - LLM as mutation/crossover operator over a diverse pool (https://www.nature.com/articles/s41586-023-06924-6).
- **The hard constraint survives exploration:** accept-worse roams only *inside the archive*; the live artifact never
  drops below its floor (for BSB, §1.5 grounding). Fail-fast economics (Reinertsen): take the regression when the
  asymmetric payoff favors it; (Lean Startup) tolerate a failing lever once, never twice.

## Related concepts

- [[wiki/concepts/recursive-self-improvement]] - the loop this exploration layer lives in.
- [[wiki/concepts/multi-objective-optimization]] - QD niches vs Pareto fronts; quality as a hard floor.
- [[wiki/concepts/llm-as-judge]] - the externally-verifiable signal that keeps the floor un-gameable during exploration.

## Sources

- [[wiki/sources/map-elites-quality-diversity]] (MAP-Elites / illumination) ; [[wiki/sources/darwin-godel-machine]] (always-add archive) ; [[wiki/sources/karpathy-autoresearch]] (the greedy ratchet it fixes).
- Non-elitism valley theorem: https://pmc.ncbi.nlm.nih.gov/articles/PMC6438649/ ; objective paradox: https://link.springer.com/article/10.1007/s10710-015-9250-8 ; POET: https://arxiv.org/abs/1901.01753
- Accept-worse rules: https://en.wikipedia.org/wiki/Simulated_annealing ; LAHC: https://ideas.repec.org/a/eee/ejores/v258y2017i1:p:70-78.html ; bandits: https://www.jmlr.org/papers/volume3/auer02a/auer02a.pdf
- Evolutionary program search: https://www.nature.com/articles/s41586-023-06924-6 (FunSearch) ; https://arxiv.org/abs/2506.13131 (AlphaEvolve)
