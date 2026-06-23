---
type: source
title: "Mouret & Clune - Illuminating search spaces by mapping elites (MAP-Elites)"
source-url: https://arxiv.org/abs/1504.04909
source-kind: paper
author: Jean-Baptiste Mouret, Jeff Clune
published: 2015-04
ingested: 2026-06-23
created: 2026-06-23
updated: 2026-06-23
tags: [topic/llm, quality-diversity, map-elites, optimization, archive, primary-source]
status: verified
---

# Mouret & Clune - Illuminating search spaces by mapping elites (MAP-Elites)

The paper that defines MAP-Elites, the archive algorithm at the heart of BSB's exploration tier
([[wiki/syntheses/bsb-rsi-loop]], [[wiki/concepts/quality-diversity-search]]). Instead of converging on one global
best, MAP-Elites keeps a *diverse* grid of the best solution found per behavioral niche - which is exactly the
mechanism that preserves "worse-now" stepping stones a greedy loop would discard.

## Key claims

- The search space is reduced to a few user-chosen **behavior descriptors** forming a grid; each cell ("niche") holds
  exactly one **elite** (the highest-performing solution found with that behavior).
- **Acceptance rule:** a new candidate enters a cell iff the cell is **empty** OR the candidate's fitness **exceeds the
  current occupant's**. Competition is *local to the cell*, never global - so a candidate that is globally sub-optimal
  survives if it lands in a distinct (empty or weaker) niche.
- **Illumination subsumes optimization:** "Any illumination algorithm can also be used as an optimization algorithm,
  making illumination algorithms a superset of optimization algorithms" - the grid returns a *map* of best-achievable
  performance across the whole behavior space, not a single point.
- Empirically (later QD work, robotics): MAP-Elites covers a far larger share of behavior niches than single-objective
  search (~90% vs ~30%) and often reaches a *higher* global maximum, because the diverse archive supplies stepping
  stones that let search escape deceptive local optima.

## Connections

- Defines the archive used by [[wiki/concepts/quality-diversity-search]]; the always-add variant is
  [[wiki/sources/darwin-godel-machine]]'s archive rule.
- The grid is implemented for BSB in `scripts/rsi_archive.py` (one elite per page-count x coverage niche).
- Hub: [[wiki/moc/bsb-architecture]].

## Sources

- PRIMARY: https://arxiv.org/abs/1504.04909 ; https://ar5iv.labs.arxiv.org/html/1504.04909
- QD survey (illumination vs optimization, QD-score): https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2016.00040/full
- CVT-MAP-Elites for >4 dimensions: https://arxiv.org/abs/1610.05729
