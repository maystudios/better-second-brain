#!/usr/bin/env python3
"""Exploration-aware acceptance for the BSB RSI loop: KEEP / EXPLORE / DISCARD + archive.

`rsi_fitness.py` is a strict, greedy gate: keep a candidate only if it is Pareto-better
right now. That is hill-climbing, and it has a documented **ratchet trap** - it cannot keep
a candidate that is WORSE NOW but a stepping-stone to something BETTER LATER (see
docs/rsi-loop.md and Karpathy's own program.md, which only says "you can rewind but ...
very very sparingly (if ever)").

This tool adds the exploration layer the literature says is necessary (Darwin Godel
Machine: archive + open-ended exploration both required; MAP-Elites / Quality-Diversity:
keep diverse elites, not one global best; Simulated Annealing: accept worse moves under a
temperature). It classifies each candidate against a baseline into three tiers:

  KEEP    - adopt as the new live method. Passes the inviolable grounding floor (§1.5),
            quality does not regress, and it is Pareto-better on (cost, latency).
  EXPLORE - do NOT adopt, but ARCHIVE as a stepping stone to branch from later. It is either
            a large single-axis win (even if it regresses/breaks another axis) or a NEW
            niche elite (a distinct point on the cost/quality tradeoff surface). The §1.5
            floor stays inviolable for the *live* method; exploration may roam off it in the
            archive, because a discarded stepping stone can never be recovered.
  DISCARD - dominated AND not novel AND not a big win. Logged as a negative (still data).

It also maintains a **MAP-Elites grid** keyed by a behavior descriptor (pages-bucket x
coverage-bucket) to illuminate the tradeoff surface rather than collapse it to one champion.
A `temperature` (0..1) governs exploration appetite: high early in a campaign (accept more
EXPLORE), cooled later toward KEEP-only - the annealing schedule.

Candidate JSONs are produced by `scripts/rsi_transforms.py measure --json`.

Usage:
  python scripts/rsi_archive.py --baseline base.json cand1.json cand2.json ... \\
      [--temperature 0.7] [--big-win 0.25] [--min-coverage 0.9] [--archive arch.json]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load(p: str) -> dict:
    return json.loads(Path(p).read_text(encoding="utf-8"))


def name_of(rec: dict, path: str) -> str:
    return rec.get("name") or Path(path).stem


def pages_bucket(n: int) -> str:
    if n <= 10:
        return "<=10p"
    if n <= 20:
        return "11-20p"
    if n <= 30:
        return "21-30p"
    return ">30p"


def coverage_bucket(c: float | None) -> str:
    if c is None:
        return "unk"
    if c >= 0.9:
        return "cov-high"
    if c >= 0.5:
        return "cov-mid"
    return "cov-low"


def classify(base: dict, cand: dict, *, min_cov: float, min_links: float, big_win: float,
             temperature: float, tol: float) -> dict:
    bf, cf = base["fill_tokens"], cand["fill_tokens"]
    br, cr = base["read_per_query"], cand["read_per_query"]
    bc = base.get("citation_coverage")
    cc = cand.get("citation_coverage")
    cl = cand.get("links_per_1k")                        # interconnection (BSB §2/§2.1 graph health)

    cost_delta = (bf - cf) / bf if bf else 0.0           # >0 = cheaper
    lat_delta = (br - cr) / br if br else 0.0             # >0 = faster
    qual_delta = (cc - bc) if (cc is not None and bc is not None) else 0.0

    cov_ok = (cc is None) or (cc >= min_cov)
    links_ok = (cl is None) or (cl >= min_links)         # a token win that nukes the link graph is Goodhart
    floor_ok = cov_ok and links_ok
    quality_ok = qual_delta >= -1e-9
    cost_rose = cost_delta < -tol
    lat_rose = lat_delta < -tol
    pareto_better = (cost_delta > tol or lat_delta > tol) and not cost_rose and not lat_rose

    best_axis = max(cost_delta, lat_delta)
    # Temperature lowers the bar for what counts as a "big" win worth exploring.
    explore_threshold = max(0.05, big_win * (1.0 - 0.6 * temperature))

    floor_reason = ""
    if not cov_ok:
        floor_reason = f"coverage {cc} < {min_cov}"
    elif not links_ok:
        floor_reason = f"links/1k {cl} < {min_links:.1f} (interconnection nuked - Goodhart)"

    reasons = []
    if floor_ok and quality_ok and pareto_better:
        tier = "KEEP"
        reasons.append("Pareto-better, floor held (coverage+links), quality non-regressing -> adopt as champion")
    elif (best_axis >= explore_threshold) or (not floor_ok and best_axis >= explore_threshold):
        tier = "EXPLORE"
        why = []
        if not floor_ok:
            why.append(f"breaches floor ({floor_reason}) but ")
        why.append(f"big single-axis win {best_axis*100:.1f}% >= {explore_threshold*100:.1f}% "
                   f"(T={temperature}) -> archive as stepping stone")
        reasons.append("".join(why))
    else:
        tier = "DISCARD"
        if not floor_ok:
            reasons.append(f"floor breached ({floor_reason}) and not a big enough win to explore")
        elif not pareto_better:
            reasons.append("neither cost nor latency improved beyond tolerance, and not novel/big -> prune")
        else:
            reasons.append("dominated; pruned")

    return {
        "name": cand.get("_name", "?"),
        "tier": tier,
        "cost_delta_pct": round(cost_delta * 100, 1),
        "latency_delta_pct": round(lat_delta * 100, 1),
        "quality_delta": round(qual_delta, 4),
        "floor_ok": floor_ok,
        "niche": f"{pages_bucket(cand['n_pages'])}|{coverage_bucket(cc)}",
        "fill_tokens": cf,
        "read_per_query": cr,
        "coverage": cc,
        "links_per_1k": cl,
        "reasons": reasons,
    }


def map_elites(base: dict, cands: list[dict]) -> dict:
    """One elite per (pages,coverage) niche; elite = lowest fill_tokens (cost-optimal)."""
    grid: dict[str, dict] = {}
    for rec in [base] + cands:
        niche = f"{pages_bucket(rec['n_pages'])}|{coverage_bucket(rec.get('citation_coverage'))}"
        cur = grid.get(niche)
        if cur is None or rec["fill_tokens"] < cur["fill_tokens"]:
            grid[niche] = {"name": rec.get("_name", "baseline"), "fill_tokens": rec["fill_tokens"],
                           "read_per_query": rec["read_per_query"],
                           "coverage": rec.get("citation_coverage")}
    return grid


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="KEEP/EXPLORE/DISCARD + MAP-Elites archive for the RSI loop.")
    ap.add_argument("candidates", nargs="+", help="candidate measurement JSONs (rsi_transforms measure --json)")
    ap.add_argument("--baseline", required=True, help="baseline measurement JSON")
    ap.add_argument("--min-coverage", type=float, default=None,
                    help="grounding floor (default = baseline coverage; never adopt below it)")
    ap.add_argument("--min-links-per-1k", type=float, default=None,
                    help="interconnection floor, BSB graph-health (default = 0.5 x baseline links/1k)")
    ap.add_argument("--big-win", type=float, default=0.25,
                    help="single-axis improvement that qualifies a regressing/floor-breaking cand for EXPLORE (default 0.25)")
    ap.add_argument("--temperature", type=float, default=0.7,
                    help="exploration appetite 0..1 (high early, cool later); lowers the EXPLORE bar (default 0.7)")
    ap.add_argument("--cost-tolerance", type=float, default=0.02)
    ap.add_argument("--archive", metavar="PATH", help="write the elite grid + classifications as JSON")
    args = ap.parse_args(argv)

    base = load(args.baseline)
    base["_name"] = name_of(base, args.baseline)
    min_cov = args.min_coverage if args.min_coverage is not None else (base.get("citation_coverage") or 0.0)
    base_links = base.get("links_per_1k") or 0.0
    min_links = args.min_links_per_1k if args.min_links_per_1k is not None else 0.5 * base_links

    cands = []
    for c in args.candidates:
        rec = load(c)
        rec["_name"] = name_of(rec, c)
        cands.append(rec)

    results = [classify(base, c, min_cov=min_cov, min_links=min_links, big_win=args.big_win,
                        temperature=args.temperature, tol=args.cost_tolerance) for c in cands]
    for r, c in zip(results, cands):
        r["name"] = c["_name"]

    grid = map_elites(base, cands)

    print(f"# RSI archive - exploration-aware acceptance")
    print(f"  baseline '{base['_name']}': fill={base['fill_tokens']:,} read/q={base['read_per_query']:,} "
          f"coverage={base.get('citation_coverage')} links/1k={base_links}  | floors: coverage>={min_cov} "
          f"links/1k>={min_links:.1f}  T={args.temperature}")
    print(f"\n  {'candidate':<28}{'tier':<9}{'cost%':>7}{'lat%':>7}{'qual':>8}{'links/1k':>9}  niche")
    for r in results:
        print(f"  {r['name']:<28}{r['tier']:<9}{r['cost_delta_pct']:>+7.1f}{r['latency_delta_pct']:>+7.1f}"
              f"{r['quality_delta']:>+8.3f}{(r['links_per_1k'] or 0):>9.1f}  {r['niche']}")
    for r in results:
        print(f"    - [{r['tier']}] {r['name']}: {r['reasons'][0]}")

    print(f"\n  MAP-Elites grid (one cost-optimal elite per niche - the diverse archive):")
    for niche, e in sorted(grid.items()):
        print(f"    {niche:<20} elite={e['name']:<26} fill={e['fill_tokens']:,} cov={e['coverage']}")

    keeps = [r for r in results if r["tier"] == "KEEP"]
    explores = [r for r in results if r["tier"] == "EXPLORE"]
    champion = max(keeps, key=lambda r: r["cost_delta_pct"] + r["latency_delta_pct"], default=None)
    # Best stepping stone: biggest single-axis win among EXPLORE (highest ceiling to branch from).
    branch = max(explores, key=lambda r: max(r["cost_delta_pct"], r["latency_delta_pct"]), default=None)
    # Closest-to-adoptable: an EXPLORE that holds the floor + quality and fails KEEP only by a
    # small regression on one axis (the practical payoff of having explored).
    adoptable = [r for r in explores if r["floor_ok"] and r["quality_delta"] >= -1e-9]
    near = max(adoptable, key=lambda r: min(r["cost_delta_pct"], r["latency_delta_pct"]), default=None)
    print("\n  recommendation:")
    print(f"    adopt now (KEEP):      {champion['name'] if champion else '(none - hold baseline)'}")
    print(f"    branch next (ceiling): {branch['name'] if branch else '(none)'}"
          + (f"  <- worse now (qual {branch['quality_delta']:+.3f}, cost {branch['cost_delta_pct']:+.1f}%) "
             f"but highest ceiling; a greedy loop would have DISCARDED it" if branch else ""))
    if near and near is not branch:
        worst = min(near["cost_delta_pct"], near["latency_delta_pct"])
        print(f"    closest to adoptable:  {near['name']}  <- floor+quality held, cost {near['cost_delta_pct']:+.1f}%, "
              f"fails KEEP only by {abs(worst):.1f}% on one axis (adopt if that objective is reweighted)")

    if args.archive:
        Path(args.archive).write_text(json.dumps(
            {"baseline": base["_name"], "min_coverage": min_cov, "temperature": args.temperature,
             "classifications": results, "elite_grid": grid,
             "champion": champion["name"] if champion else None,
             "branch_next": branch["name"] if branch else None}, indent=2), encoding="utf-8")
        print(f"\n  wrote archive: {args.archive}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
