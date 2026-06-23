#!/usr/bin/env python3
"""Multi-objective fitness for the BSB Recursive-Self-Improvement (RSI) loop.

This is the "validation metric" of the RSI loop (BSB docs/rsi-loop.md), playing
the role Karpathy's autoresearch gives to *bits-per-byte*: a single, deterministic,
reproducible verdict that decides whether a proposed change to the **method** (the
CLAUDE.md schema + page templates + fill/query policy) is KEPT or DISCARDED.

Unlike bits-per-byte it is **three objectives under a hard constraint**, because
the owner wants three things at once - cheaper, faster, and at least as good:

    cost     = build (fill) tokens + N * read-per-query tokens     (lower better)
    latency  = per-query read tokens, or measured wall-clock        (lower better)
    quality  = judge total 0-6 (correctness+citation+faithfulness)  (higher better)

In an LLM-wiki, cost and latency share most of one lever ("load less"), and
quality is the constraint that stops the degenerate "load nothing" optimum. So
the keep/discard rule is NOT a free 3-way Pareto search - it is **constrained**:

    KEEP a candidate iff
      (1) grounding floor holds        - §1.5: gated pages still Tier-A (>=3 sources)
      (2) quality does not regress      - total & citation & faithfulness >= baseline - eps
      (3) it is a Pareto improvement    - cost OR latency strictly drops, neither rises
    else DISCARD (with the binding reason).

This generalises Karpathy's "keep the change only if the metric improved": better
here means cheaper-or-faster *without* paying in quality or grounding.

Inputs are the artifacts the benchmark already writes per example dir:
    tokens.json   (scripts/token_report.py)   - fill + read-per-query, per arm
    scores.json   (the judge)                  - per-arm averages, 0-2 per dim
    timing.json   (optional)                   - {arm: {wall_clock_per_query_s,
                                                        build_wall_clock_s}}
Arm dirs are hyphenated (arm-bsb-lean); scores.json keys are underscored
(bsb_lean) - this tool normalises between them.

Usage:
    # report fitness of one arm
    python scripts/rsi_fitness.py benchmark/large --arm bsb-lean

    # before/after verdict (the RSI keep/discard decision)
    python scripts/rsi_fitness.py benchmark/large --before-arm bsb --after-arm bsb-lean

    # candidate re-benchmarked in a fresh dir, with the grounding gate enforced
    # (grounding-root is the repo root containing wiki/, exactly as CI lints it)
    python scripts/rsi_fitness.py benchmark/large --before-arm bsb-lean \\
        --after-dir benchmark/cand1 --after-arm bsb-lean \\
        --grounding-root . --json out.json
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_QUERIES = 20  # lifecycle horizon if an example has no questions.json


def _read_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def load_tokens(example_dir: Path) -> dict:
    """Return token_report data, reading tokens.json or computing it fresh."""
    cached = _read_json(example_dir / "tokens.json")
    if cached and "arms" in cached:
        return cached
    # Fall back to computing it (keeps fitness usable on a fresh candidate dir).
    sys.path.insert(0, str(SCRIPT_DIR))
    try:
        from token_report import build_report  # type: ignore
    except Exception as exc:  # pragma: no cover - import guard
        raise SystemExit(f"error: no tokens.json in {example_dir} and token_report "
                         f"import failed: {exc}")
    return build_report(example_dir, rag_k=3)


def n_queries_for(example_dir: Path, tokens: dict) -> int:
    if isinstance(tokens.get("n_queries"), int) and tokens["n_queries"] > 0:
        return tokens["n_queries"]
    q = _read_json(example_dir / "questions.json")
    if q and isinstance(q.get("questions"), list) and q["questions"]:
        return len(q["questions"])
    return DEFAULT_QUERIES


def objectives(example_dir: Path, arm: str) -> dict:
    """Extract the three objective values (+ provenance) for one arm."""
    tokens = load_tokens(example_dir)
    arms = tokens.get("arms", {})
    comps = tokens.get("comparisons", {})
    if arm not in arms:
        raise SystemExit(f"error: arm '{arm}' not found in {example_dir}/tokens.json "
                         f"(have: {', '.join(sorted(arms)) or 'none'})")

    fill = arms[arm]["total_tokens"]
    read = comps.get(arm, {}).get("read_per_query", arms[arm].get("read_per_query", 0))
    n = n_queries_for(example_dir, tokens)
    cost = fill + n * read

    # Quality from the judge (scores.json), arm key normalised to underscores.
    scores = _read_json(example_dir / "scores.json") or {}
    avg = (scores.get("averages") or {}).get(arm.replace("-", "_"), {})
    quality = {
        "total": float(avg.get("total", 0.0)),
        "correctness": float(avg.get("correctness", 0.0)),
        "citation": float(avg.get("citation", 0.0)),
        "faithfulness": float(avg.get("faithfulness", 0.0)),
        "measured": bool(avg),
    }

    # Latency: measured wall-clock per query if provided, else the deterministic
    # load proxy (read-per-query tokens). Flag which one was used.
    timing = _read_json(example_dir / "timing.json") or {}
    t_arm = timing.get(arm) or timing.get(arm.replace("-", "_")) or {}
    if "wall_clock_per_query_s" in t_arm:
        latency = float(t_arm["wall_clock_per_query_s"])
        latency_kind = "wall_clock_s"
    else:
        latency = float(read)
        latency_kind = "read_tokens_proxy"

    return {
        "example": example_dir.name,
        "arm": arm,
        "n_queries": n,
        "cost": {"fill_tokens": fill, "read_per_query": read,
                 "lifecycle_tokens": cost},
        "latency": {"value": latency, "kind": latency_kind},
        "quality": quality,
        "links_per_1k": arms[arm].get("links_per_1k_tokens", 0),
    }


def grounding_ok(root_dir: Path, min_tier: str = "A") -> tuple[bool, str]:
    """Run lint_sources on a repo root (containing wiki/); the sec-1.5 hard constraint.

    lint_sources grades pages by their wiki/<folder>/ path relative to the root,
    so this must point at a dir that *contains* wiki/ (the repo root, as CI does) -
    not a single arm dir. Returns (passed, detail); passed = no gated page below min_tier.
    """
    script = SCRIPT_DIR / "lint_sources.py"
    if not script.is_file():
        return True, "lint_sources.py not found - grounding gate SKIPPED (unchecked)"
    try:
        proc = subprocess.run(
            [sys.executable, str(script), str(root_dir),
             "--strict", "--strict-min-tier", min_tier, "--summary"],
            capture_output=True, text=True, timeout=120,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return False, f"lint_sources failed to run: {exc}"
    ok = proc.returncode == 0
    tail = (proc.stdout or proc.stderr or "").strip().splitlines()
    detail = tail[-1] if tail else f"exit {proc.returncode}"
    return ok, f"Tier-{min_tier} gate {'PASS' if ok else 'FAIL'}: {detail}"


def verdict(before: dict, after: dict, q_eps: float, cost_tol: float,
            grounding: tuple[bool, str] | None) -> dict:
    """The constrained-Pareto KEEP/DISCARD decision."""
    reasons: list[str] = []

    # (1) Grounding floor (§1.5) - inviolable.
    g_ok = True
    if grounding is not None:
        g_ok, g_detail = grounding
        reasons.append(("OK" if g_ok else "BLOCK") + f" grounding: {g_detail}")
    else:
        reasons.append("WARN grounding: not checked (pass --grounding-root to enforce sec-1.5)")

    # (2) Quality non-regression (total + citation + faithfulness).
    qb, qa = before["quality"], after["quality"]
    q_ok = True
    for dim in ("total", "citation", "faithfulness"):
        delta = qa[dim] - qb[dim]
        if delta < -q_eps:
            q_ok = False
            reasons.append(f"BLOCK quality.{dim}: {qb[dim]:.3f} -> {qa[dim]:.3f} "
                           f"(regressed by {-delta:.3f} > eps {q_eps})")
        else:
            reasons.append(f"OK quality.{dim}: {qb[dim]:.3f} -> {qa[dim]:.3f} ({delta:+.3f})")

    # (3) Pareto improvement on (cost, latency): one strictly down, neither up.
    cb, ca = before["cost"]["lifecycle_tokens"], after["cost"]["lifecycle_tokens"]
    lb, la = before["latency"]["value"], after["latency"]["value"]
    cost_drop = (cb - ca) / cb if cb else 0.0
    lat_drop = (lb - la) / lb if lb else 0.0
    cost_rose = cost_drop < -cost_tol
    lat_rose = lat_drop < -cost_tol
    improved = (cost_drop > cost_tol or lat_drop > cost_tol) and not cost_rose and not lat_rose
    reasons.append(f"{'OK' if not cost_rose else 'BLOCK'} cost: {cb:,} -> {ca:,} "
                   f"({cost_drop*100:+.1f}%)")
    reasons.append(f"{'OK' if not lat_rose else 'BLOCK'} latency({after['latency']['kind']}): "
                   f"{lb:g} -> {la:g} ({lat_drop*100:+.1f}%)")
    if not improved and not cost_rose and not lat_rose:
        reasons.append("BLOCK improvement: neither cost nor latency dropped beyond tolerance "
                       f"({cost_tol*100:.0f}%) - change is neutral, discard to avoid churn")

    keep = g_ok and q_ok and improved
    return {
        "keep": keep,
        "decision": "KEEP" if keep else "DISCARD",
        "cost_delta_pct": round(cost_drop * 100, 2),
        "latency_delta_pct": round(lat_drop * 100, 2),
        "quality_total_delta": round(qa["total"] - qb["total"], 3),
        "reasons": reasons,
    }


def print_obj(label: str, o: dict) -> None:
    q = o["quality"]
    qm = "" if q["measured"] else "  (no scores.json - quality unmeasured)"
    print(f"  {label}: arm={o['arm']} example={o['example']}")
    print(f"    cost     fill={o['cost']['fill_tokens']:,}  read/q={o['cost']['read_per_query']:,}"
          f"  lifecycle@{o['n_queries']}q={o['cost']['lifecycle_tokens']:,} tok")
    print(f"    latency  {o['latency']['value']:g} ({o['latency']['kind']})")
    print(f"    quality  total={q['total']:.3f}/6  cite={q['citation']:.3f}  "
          f"faith={q['faithfulness']:.3f}{qm}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Multi-objective fitness + KEEP/DISCARD "
                                             "verdict for the BSB RSI loop.")
    ap.add_argument("example_dir", help="Benchmark example dir (raw/, arm-*/wiki/, tokens.json, scores.json).")
    ap.add_argument("--arm", default="bsb-lean", help="Arm to report when no before/after (default bsb-lean).")
    ap.add_argument("--before-arm", help="Baseline arm for a verdict.")
    ap.add_argument("--after-arm", help="Candidate arm for a verdict.")
    ap.add_argument("--after-dir", help="Dir for the candidate arm if re-benchmarked separately.")
    ap.add_argument("--grounding-root", help="Repo root (containing wiki/) to enforce the sec-1.5 Tier-A gate; '.' for this repo.")
    ap.add_argument("--quality-epsilon", type=float, default=0.0,
                    help="Allowed quality slack before it counts as a regression (default 0.0).")
    ap.add_argument("--cost-tolerance", type=float, default=0.01,
                    help="Min fractional cost/latency change to count as real (default 0.01 = 1%%).")
    ap.add_argument("--json", metavar="PATH", help="Write the full result as JSON.")
    args = ap.parse_args(argv)

    before_dir = Path(args.example_dir).resolve()
    if not before_dir.is_dir():
        print(f"error: {before_dir} is not a directory", file=sys.stderr)
        return 2

    # Single-arm report.
    if not (args.before_arm and args.after_arm):
        o = objectives(before_dir, args.arm)
        print(f"# RSI fitness - '{o['example']}'")
        print_obj("fitness", o)
        if args.json:
            Path(args.json).write_text(json.dumps(o, indent=2), encoding="utf-8")
            print(f"\nWrote JSON: {args.json}")
        return 0

    # Before/after verdict.
    after_dir = Path(args.after_dir).resolve() if args.after_dir else before_dir
    before = objectives(before_dir, args.before_arm)
    after = objectives(after_dir, args.after_arm)
    grounding = grounding_ok(Path(args.grounding_root).resolve()) if args.grounding_root else None
    v = verdict(before, after, args.quality_epsilon, args.cost_tolerance, grounding)

    print(f"# RSI keep/discard verdict")
    print_obj("BEFORE", before)
    print_obj("AFTER ", after)
    print(f"\n  >>> {v['decision']}  "
          f"(cost {v['cost_delta_pct']:+.1f}%, latency {v['latency_delta_pct']:+.1f}%, "
          f"quality {v['quality_total_delta']:+.3f})")
    for r in v["reasons"]:
        print(f"      - {r}")

    if args.json:
        out = {"before": before, "after": after, "verdict": v,
               "params": {"quality_epsilon": args.quality_epsilon,
                          "cost_tolerance": args.cost_tolerance}}
        Path(args.json).write_text(json.dumps(out, indent=2), encoding="utf-8")
        print(f"\nWrote JSON: {args.json}")
    return 0 if v["keep"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
