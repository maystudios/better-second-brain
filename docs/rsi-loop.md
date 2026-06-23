# RSI Loop - measured, multi-objective self-improvement (BSB §3.7)

How the Brain improves its own **method** on evidence, optimizing three things at once - **lower token cost,
lower latency, higher research quality** - without ever weakening the rule that every page is grounded in real
sources. This is the loop Karpathy's `autoresearch` repo implements for neural nets, generalized from one metric
to a constrained multi-objective and pointed at a markdown rulebook instead of `train.py`.

This doc is the design + runbook. The schema contract is `CLAUDE.md §3.7`; the metric is `scripts/rsi_fitness.py`;
the mutation engine is the `auto-research` skill (`docs/auto-research-integration.md`); the harness is the
benchmark (`docs/benchmark.md`).

## 1. The pattern we are copying: Karpathy's `autoresearch`

`github.com/karpathy/autoresearch` lets an agent do ML research overnight. Its structure is four parts:

- **`prepare.py`** - the fixed harness (data + utilities). The agent never touches it.
- **`train.py`** - the **mutable target**. The agent edits this to try a better model/optimizer.
- **`program.md`** - the instructions the human edits to steer the agent.
- **the loop** - the agent edits `train.py`, runs a **time-boxed ~5-minute (300s) experiment** on one GPU, reads a
  **single validation metric** (`val_bpb`, vocab-size-independent), and **keeps the change only if the metric
  strictly improved, else `git reset --hard HEAD~1`** - then repeats autonomously. A documented overnight run did
  **89 experiments (15 kept, 74 discarded, 0 crashes)**, moving `val_bpb` 0.997900 -> 0.977287 ([[wiki/sources/karpathy-autoresearch]]).

The whole thing works because the **harness is fixed and the metric is cheap, deterministic, and hard to game**.
The agent cannot "win" by editing the scorer (`prepare.py` is immutable); it can only win by actually producing a
better `train.py`. Note Karpathy draws **no** connection between this and his LLM-wiki - applying the loop to a wiki's
*method* is BSB's synthesis ([[wiki/syntheses/bsb-rsi-loop]]), not his claim.

## 2. The mapping: BSB already has every piece

The realization behind this loop is that BSB is one wiring change away from the same structure - it already built
the parts separately:

| `autoresearch` | BSB equivalent (already exists) |
|---|---|
| `prepare.py` (fixed harness) | the **benchmark**: locked gold question sets + an LLM judge + `scripts/token_report.py` |
| `train.py` (mutable target) | the **method**: `CLAUDE.md` schema + `templates/` + the fill (§2.1) and query (§3.2) policy |
| `program.md` (human steer) | `bsb.config.md` + the §7 confirmation gate |
| the mutation step | the **`auto-research` skill** (cited rewrite of a prompt artifact + its own eval loop) |
| bits-per-byte (one metric) | **`scripts/rsi_fitness.py`** - a *three*-objective fitness (this is the new piece) |
| keep-if-better | the constrained-Pareto verdict in §4 (the other new piece) |

So the only genuinely new code is the **metric** (`rsi_fitness.py`) and the **loop wiring** (this doc + §3.7).
Karpathy compounds *knowledge*; `auto-research` already compounds *method* one file at a time; this loop closes
that into a **measured** cycle that proves each method change actually paid off on all three axes.

## 3. Three objectives, one hard constraint - why it is *not* a free Pareto search

The owner wants three wins simultaneously:

- **cost** = build (fill) tokens + N x read-per-query tokens. Lower is better.
- **latency** = per-query read tokens (deterministic proxy), or measured wall-clock when available. Lower is better.
- **quality** = the judge total (correctness + citation + faithfulness, 0-6). Higher is better.

The trap: in an LLM-wiki, **cost and latency are mostly the same lever** - both are driven by "load less" - and the
degenerate optimum of "load nothing / write nothing" scores perfectly on both. **Quality is the constraint that
forbids that optimum.** So this is not a free three-way Pareto search; it is a **constrained** one:

> **minimize (cost, latency) subject to quality >= floor and quality not regressing.**

The floor is **§1.5 grounding** (every gated page Tier-A: >= 3 real sources). It is a hard constraint, never a
tradeable term - you may not buy a token saving with a citation. This is the single most important guardrail in the
whole loop (see §7).

## 4. The fitness function (the keep/discard rule)

`scripts/rsi_fitness.py` turns a before/after pair of benchmark arms into one verdict. A candidate method is
**KEPT** iff all three hold:

1. **Grounding floor (§1.5) holds** - `lint_sources.py --strict-min-tier A` passes on the real `wiki/` (this is the
   same gate CI runs). Enforced with `--grounding-root .`.
2. **Quality does not regress** - `total`, `citation`, and `faithfulness` each `>= baseline - epsilon`
   (default epsilon = 0: zero tolerance).
3. **It is a Pareto improvement** - `cost` OR `latency` drops by more than the tolerance, and **neither** rises.

Otherwise it is **DISCARDED**, and the tool prints the binding reason. A change that is merely *neutral* (no axis
improves) is discarded too, to avoid churn - same spirit as `auto-research`'s "decline a cosmetic rewrite".

This is exactly Karpathy's "keep the change only if the metric improved", generalized: *better* means
**cheaper-or-faster without paying in quality or grounding.**

```
# the verdict, on real historical data (see §9):
python scripts/rsi_fitness.py benchmark/large --before-arm bsb --after-arm bsb-lean --grounding-root .
```

## 5. The harness contract - what is FIXED vs MUTABLE

This is the anti-gaming core, lifted straight from `autoresearch` (the agent may edit `train.py`, never
`prepare.py`). For BSB:

**LOCKED (the agent must never edit these inside a loop):**
- the gold question sets (`benchmark/*/questions*.json`) and the judge rubric,
- `scripts/token_report.py`, `scripts/rsi_fitness.py`, `scripts/lint_sources.py` (the scorers),
- `CLAUDE.md §1.5` (the grounding floor itself).

**MUTABLE (the target the loop is allowed to rewrite):**
- `CLAUDE.md` §2.1 (fill policy), §3.2 (query policy), §2 (page format) and the per-type `templates/`,
- `bsb.config.md` tunables (e.g. cheatsheet length, link style),
- operational policy docs the method depends on.

If a proposed change touches a locked file, the iteration is **void** - just as editing the scorer would be in any
honest optimization loop.

## 6. The iteration protocol

One RSI iteration:

1. **Pick a lever.** A concrete, falsifiable method change aimed at cost or latency (e.g. "retrieval-first query
   path: stop re-reading `index.md` on graph-enabled brains", or "ultra-lean source stubs"). One lever per iteration
   so the attribution is clean.
2. **Measure baseline.** Run the benchmark on the current method -> `tokens.json` + `scores.json`. Record
   `rsi_fitness` for the baseline arm.
3. **Mutate the target.** Use `auto-research` (or a hand edit) to rewrite the mutable file(s) implementing the lever.
   Every change cited; locked files untouched.
4. **Re-measure.** Re-run the benchmark on the mutated method -> a candidate arm. Use **staged eval** to save cost
   (the Darwin-Godel-Machine pattern): a cheap small-corpus filter first, the full gold set only for survivors. For a
   noisy wall-clock latency reading, take the **rolling median over N runs**, not a single shot (network/load noise);
   the deterministic read-token proxy needs no repetition.
5. **Verdict.** `rsi_fitness` for a strict adopt/reject; `rsi_archive.py` to classify across a candidate set into
   **KEEP / EXPLORE / DISCARD** and update the archive (§11). Run several levers in parallel (a workflow) and classify
   them together.
6. **Commit, archive, or prune.** On KEEP, apply through the §7 gate and append a row to `benchmark/RSI_LOG.tsv`. On
   EXPLORE, **archive** the candidate (do not adopt) as a stepping stone to branch from. On DISCARD, log the negative
   (negatives are data - they prune the search and retire dead levers).
7. **Repeat** until the exploration budget is spent or K consecutive rounds yield no KEEP *and* no new niche.

Steps 2-5 run autonomously; step 6's commit passes the human gate (autonomy levels in §8).

## 7. Guardrails - keeping the loop honest (anti-Goodhart)

A self-improvement loop optimizing its own metric is the textbook setup for **reward hacking** and **eval
overfitting** (Goodhart's law: when a measure becomes a target it stops being a good measure). This is not
hypothetical: across self-improving code agents, **46-74% of optimization steps** showed proxy gains without real
improvement, and the rate **rises with iteration depth** (~26% at 10 steps to ~58% at 100) - so an unbounded loop
actively degrades the true objective ([[wiki/concepts/recursive-self-improvement]]). The mitigations, each mapped to a
concrete BSB mechanism:

- **The scorer and the floor are LOCKED** (§5). The loop cannot win by editing the metric or relaxing §1.5.
- **Grounding is a constraint, not a term** (§3), anchored to **externally verifiable** signals - real source counts
  and fetchable links checked by `lint_sources`/`verify_wikilinks`, not an LLM's self-assessment. No token saving can
  be bought with a weaker citation; a proposal that *weakens* §1.5 is rejected at the gate, full stop.
- **Quality is a floor, not a maximand - and the judge has a verbosity bias** (effect size 0.76-0.92) that *rewards
  longer pages*. Maximizing a raw judge score would push the loop **away** from lean (token-cheap) pages - directly
  against the token objective. So quality is gated on non-regression (use reference-guided, length-penalized judging),
  never inflated by spending tokens ([[wiki/concepts/llm-as-judge]]).
- **Held-out / novel corpus.** Optimizing against one fixed question set invites overfitting; the current ~14-question
  benchmark can *validate* the metric but is too small to *drive* many iterations (GEPA degenerates on scarce
  instances). Grow the gold set and re-test kept changes on a *different* corpus before trusting them (the roadmap's
  private/novel-corpus item, plus the existing `questions-public.json`/`questions.json` split, are this held-out set).
- **Archive + parallel exploration, not greedy hill-climbing.** Karpathy's strict keep-if-better has a **ratchet
  trap**: it cannot escape a local optimum needing a temporary regression. The Darwin Godel Machine showed an
  **archive of versions + open-ended exploration** is necessary for sustained progress. BSB's edge over a single GPU:
  it can evaluate **several levers in parallel as a workflow** and keep the `RSI_LOG.tsv` lineage as that archive
  ([[wiki/concepts/recursive-self-improvement]]).
- **Bounded depth + early stop.** Because hacking rises with depth, cap iterations and stop after K non-improving
  rounds (same hard-stop discipline as `auto-research`'s eval loop).
- **Human gate on commit** (schema §7). The fitness score *informs* the decision; it does not replace review of the
  diff and its sources.
- **One lever per iteration**, so a regression is always attributable and revertible; **negatives are logged** so the
  loop has memory and does not re-try dead levers.

## 8. Autonomy levels (mirrors §3.6 Heal)

1. **Report** - run the loop, propose the kept change, do nothing.
2. **Fix-on-approval [default]** - apply a KEEP through the §7 gate.
3. **Autonomous** - only for a KEEP that is unambiguous (clear cost/latency win, quality delta >= 0, grounding PASS,
   and the lever touches no schema rule, only a tunable). Never autonomous below the §1.5 floor.

## 9. Worked example - the loop reproduces a past human decision

Run retroactively on the Ruff benchmark, the loop **re-derives the adoption of lean fill** that was originally
decided by hand:

```
BEFORE  arm=bsb       fill=22,366  read/q=1,042  quality=5.929/6
AFTER   arm=bsb-lean  fill= 7,648  read/q=  442  quality=5.929/6
>>> KEEP  (cost -62.6%, latency -57.6%, quality +0.000, grounding Tier-A PASS)
```

The fitness function, with zero human input, would have accepted lean fill for the same reason the human did:
much cheaper and faster, identical quality, grounding intact. That is the evidence the metric is well-formed -
it agrees with the decision we already trust.

## 10. Cadence

Run an RSI pass on a deliberate schedule (when a new token/latency technique lands, after a major model release, or
quarterly), not continuously - method changes should be rare and considered. Knowledge ingest (§3.1) stays
continuous; *method* mutation is the slow loop.

## 11. Exploration - escaping the ratchet trap (the keep-if-better fix)

The §4 keep-if-Pareto-better rule is **greedy hill-climbing**, and that is a known failure mode, not a feature.
Karpathy's `program.md` is explicit: keep only if `val_bpb` strictly improves, *"else `git reset`"*, and on getting
stuck the only advice is *"you can rewind but you should probably do this very very sparingly (if ever)"* - no
mechanism at all ([[wiki/sources/karpathy-autoresearch]]). The cost is the **ratchet trap**: a change that is
*worse now but better later* (you must descend through a worse intermediate to reach a higher peak) is permanently
blocked. Theory makes this precise - strict elitism on a fitness valley runs in time exponential in the valley's
**length**, while accepting worse moves (Metropolis) is exponential only in its **depth** - a potentially exponential
speedup when valleys are long but shallow ([[wiki/concepts/quality-diversity-search]]). The community has already
forked autoresearch to fix exactly this (the GEAR genetic-search-graph fork; issue #179's "step back and explore a
better alternative"; SkyPilot's parallel grids). BSB builds the fix in from the start.

**Three tiers, not two** (`scripts/rsi_archive.py`):

- **KEEP** - adopt as the live method: Pareto-better on cost/latency, floor held, quality non-regressing.
- **EXPLORE** - do **not** adopt, but **archive as a stepping stone**: a large single-axis win or a new behavioral
  niche, *even if it regresses another axis or breaches the floor*. A discarded stepping stone can never be recovered,
  so we keep it to branch from. This is the Darwin-Godel-Machine rule (admit to the archive on a *functional* gate,
  not a performance gate) and the Quality-Diversity rule (keep the best per niche, not one global best) -
  ([[wiki/concepts/quality-diversity-search]]). Stanley & Lehman's objective paradox: *"almost no prerequisite to any
  major invention was invented for that invention's purposes."*
- **DISCARD** - dominated and not novel; logged as a negative.

**The §1.5 floor stays inviolable for the *live* method.** Exploration roams off it only *inside the archive* (a
floor-breaching variant is never served to users; it is a research artifact). This is how we get SpaceX's
"launch boldly, learn from failure" without ever shipping an ungrounded brain.

**The archive is a MAP-Elites grid**, not a single champion: one cost-optimal elite per (page-count x
coverage) niche, so a lean variant, a merged-pages variant, and a verbose variant coexist as parents for future
branches. **Pick the next lever by uncertainty** (a Thompson/UCB bandit over levers - try the under-explored arm, not
just the current best). **How willing to accept a regression** is a *temperature* that cools over a campaign
(simulated annealing), or - the recommended scale-invariant form - **Late-Acceptance Hill-Climbing**: accept if better
than the fitness *L_h* iterations ago, no temperature to calibrate ([[wiki/concepts/quality-diversity-search]]).
Economic backstop (Reinertsen): accept a regression now when the *asymmetric payoff* - the expected long-run gain if
the bet pays off - dominates the loss; and (Lean Startup) tolerate a failing lever once, but **retire a lever class
after K rejections** - never make the same mistake twice.

### 11.1 Worked forward fleet - the stepping stone pays off

Five deterministic levers (`scripts/rsi_transforms.py`) on the Ruff corpus, quality = gold-source citation coverage
(an external, un-gameable signal), classified by `rsi_archive.py`:

```
candidate                 tier      cost%  lat%   coverage   note
drop-links                KEEP      -9.9   -8.1   0.93       redundant footer; adopt now
strip-frontmatter         DISCARD   -1.2   -1.4   0.93       marginal -> prune
merge-sources             EXPLORE  -59.0  -12.2   0.00       greedy DISCARDS; archived (highest ceiling)
merge-sources-keep-urls   EXPLORE  -32.7  +43.9   0.93       branch: coverage back, but URLs bloat reads
merge-sources-compact     EXPLORE  -49.6   +5.4   0.93       branch: -49.6% tokens, coverage back, misses KEEP by 5.4% latency
```

The lesson a greedy loop could never learn: `merge-sources` looks like garbage (coverage 0.00, floor breached) but is
the **only doorway** to `merge-sources-compact` - a −49.6% token cut at full grounding, one small latency tweak away
from adoption. Discarding the stepping stone discards the destination. The diverse archive keeps all three merged
variants alive as the elites of their niches.

### 11.2 Recombination, and learning from a Goodhart failure

Running the loop forward, **recombination** ("combine near-misses" - the FunSearch/crossover idea) stacked the
`drop-links` KEEP onto the `merge-sources-compact` stepping stone. The result *looked* spectacular:
`compact+drop-links` = **−55.8% tokens AND −6.8% latency** at full coverage - a clean KEEP reachable only by branching
through the floor-breaching stepping stone a greedy loop had thrown away.

But it was a **Goodhart hit**: that variant had `links/1k = 0` - it cut tokens by **deleting the entire wikilink
graph** (237 links -> 0), an axis the citation-coverage proxy didn't measure. Interconnection is a real BSB quality
dimension (§2/§2.1: "density is the goal"; graphify feeds on links). So the loop **improved its own scorer**: an
**interconnection floor** was added to `rsi_archive.py` (`links/1k >= 0.5 x baseline`), a second hard constraint
alongside coverage. Re-classified, `compact+drop-links` and `merge-sources-compact` are correctly **demoted to
EXPLORE** (graph nuked / thinned), and the **honest adopted champion is `drop-links+frontmatter`**: −11.1% tokens,
−10.0% latency, coverage *and* interconnection intact.

**The plateau (honest).** Graph-preserving deterministic levers converge at ~−11% tokens / −10% latency. The big
−50% wins exist but each trades away interconnection or per-query latency - a genuine three-way tension
(tokens vs latency vs interconnection) that mechanical levers cannot dissolve. Pushing past this plateau needs the
next class of iteration: a reference-guided **LLM judge** to verify *content-level* compression the deterministic
proxy can't see, and **real-vault validation** before a benchmark win is promoted into the live method. That is the
boundary of what an autonomous, deterministic, no-human-judgment loop can safely do. (Full ledger:
`benchmark/RSI_LOG.tsv`, Rounds 2-4.)

## Sources

Anchor and primary:
- Karpathy `autoresearch` (fixed-harness / mutable-`train.py` / `val_bpb` / keep-if-better; 89-experiment run
  0.997900->0.977287) - https://github.com/karpathy/autoresearch ; https://github.com/karpathy/autoresearch/discussions/32 ; [[wiki/sources/karpathy-autoresearch]]
- Karpathy "LLM Wiki" gist (the wiki pattern this method keeps fresh) -
  https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f ; [[wiki/sources/karpathy-llm-wiki]]

Method and failure-mode evidence (full landscape in the wiki concept pages):
- [[wiki/concepts/recursive-self-improvement]] - RSI systems + reward-hacking rates (https://openreview.net/forum?id=ikrQWGgxYg) + Sakana RSI failure modes (https://sakana.ai/rsi-lab/).
- [[wiki/concepts/multi-objective-optimization]] - lexicographic vs weighted-sum vs Pareto; Goodhart (https://arxiv.org/abs/2310.09144).
- [[wiki/concepts/llm-as-judge]] - judge verbosity/self-preference bias + faithfulness/attribution metrics.
- [[wiki/sources/darwin-godel-machine]] (archive + exploration) ; [[wiki/sources/gepa-reflective-prompt-evolution]] (Pareto method opt) ; [[wiki/sources/anthropic-context-engineering]] (token/latency levers).

Exploration / escaping local optima (§11):
- [[wiki/concepts/quality-diversity-search]] - MAP-Elites, novelty search, the objective paradox, POET stepping
  stones, simulated annealing / LAHC accept-worse rules, bandits for lever selection.
- [[wiki/sources/map-elites-quality-diversity]] (https://arxiv.org/abs/1504.04909) ; non-elitism valley theorem
  (https://pmc.ncbi.nlm.nih.gov/articles/PMC6438649/) ; LAHC (https://ideas.repec.org/a/eee/ejores/v258y2017i1:p:70-78.html).
- Community forks of autoresearch that add exploration: GEAR genetic-search-graph (https://github.com/yibie/awesome-autoresearch);
  issue #179 (https://github.com/karpathy/autoresearch/issues/179); SkyPilot parallel grids (https://blog.skypilot.co/scaling-autoresearch/).

Local:
- BSB `benchmark/RESULTS.md` (the baselines this loop optimizes: lean fill -66%, read 17.9x) ; `benchmark/RSI_LOG.tsv` (iteration ledger) ; `scripts/rsi_fitness.py` (the metric) ; `docs/auto-research-integration.md` (the mutation engine).
