# Judgment Report - Ruff (Astral Python linter & formatter)

Three knowledge-base arms (vanilla, bsb, bsb_lean) scored vs a 14-question gold set.
Each answer scored 0-2 on correctness, citation, faithfulness. Total = sum (0-6).

## Per-question totals (out of 6)

| # | Type | Vanilla | BSB | BSB-lean | Notes |
|---|------|--------:|----:|---------:|-------|
| 1 | recall | 5 | 6 | 6 | All correct (Rust, Astral). Vanilla cites bare "(Ruff.md)" = vague; bsb/lean cite real doc URL + github. |
| 2 | recall | 5 | 6 | 6 | All list the six gold tools. Vanilla citation vague; bsb/lean cite doc URLs. |
| 3 | detail | 5 | 6 | 6 | All give ["E4","E7","E9","F"]. Vanilla cites Configuration/Rules (gold src=settings); bsb/lean cite settings. |
| 4 | detail | 5 | 6 | 6 | All give 88 / 4. Same vanilla citation gap. |
| 5 | detail | 6 | 5 | 5 | Vanilla states select=replace/extend=add cleanly + cites Linter -> full marks. bsb/lean mark it "(inferred)" with vague linter+tutorial cite: correct+grounded so faithfulness=2, citation only partial -> 5. |
| 6 | detail | 6 | 6 | 6 | All correct on three formats + precedence. |
| 7 | detail | 6 | 6 | 6 | All: safe-only default, --unsafe-fixes to enable. Lean omits config form but still correct. |
| 8 | detail | 6 | 6 | 6 | All: double/space, drop-in Black, >99.9%. |
| 9 | detail | 6 | 6 | 6 | All: docstring-code-format=true, line-length default "dynamic". |
| 10 | detail | 6 | 6 | 6 | All eight rule-prefix mappings correct. |
| 11 | freshness | 6 | 6 | 6 | All: non-SemVer, minor=breaking, patch=bug-fix. |
| 12 | freshness | 6 | 6 | 6 | All: preview rules need preview mode; select=ALL alone doesn't enable. |
| 13 | freshness | 6 | 6 | 6 | All: ruff server, beta v0.4.5, stable v0.5.3, ext charliermarsh.ruff. |
| 14 | unsupported | 5 | 6 | 6 | bsb/lean cite FAQ + quote "Ruff is a linter, not a type checker". Vanilla reaches right "No" but wrongly hedges "(inferred)" + cites Ruff.md -> citation 1. |

## Dimension averages (0-2) and totals (0-6)

| Arm | Correctness | Citation | Faithfulness | Total |
|-----|------------:|---------:|-------------:|------:|
| vanilla  | 2.000 | 1.643 | 2.000 | 5.643 |
| bsb      | 2.000 | 1.929 | 2.000 | 5.929 |
| bsb_lean | 2.000 | 1.929 | 2.000 | 5.929 |

## Summary

- Winner: tie between bsb and bsb_lean (5.929 each), both ahead of vanilla (5.643). bsb is +5.1% over vanilla.
- Correctness maxed (2.0) for all three arms. Entire spread is citation quality: vanilla's bare filenames score vague/partial and it mis-cited the unsupported question; bsb/lean cite specific correct doc URLs.
- (a) Over-abstention fix worked: on detail/freshness facts and especially unsupported Q14, bsb/bsb_lean answer precise facts correctly and confidently rather than abstaining. Only residual hedge is Q5 (correct grounded inference still labeled "(inferred)", costing one citation point). Q14 is the biggest payoff: bsb/lean nail the explicit FAQ quote while vanilla under-claims it.
- (b) bsb_lean held parity with bsb: identical correctness (2.0) and citation (1.929). Lean trimmed prose without dropping gold-required facts or correct sources. lean_vs_bsb_quality_delta = 0.0.
