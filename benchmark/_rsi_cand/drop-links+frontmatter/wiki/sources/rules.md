---
type: source
title: "Ruff Rules Reference Overview"
url: https://docs.astral.sh/ruff/rules/
---

## Key claims
- Over 900 lint rules organized by prefix mapping to a source plugin/tool.
- Core prefixes: `F` Pyflakes, `E`/`W` pycodestyle, `C90` mccabe, `I` isort, `N` pep8-naming, `D` pydocstyle, `UP` pyupgrade.
- Flake8 plugin prefixes: `ANN`, `S` (bandit), `B` (bugbear), `A` (builtins), `C4` (comprehensions), `SIM` (simplify), `PTH` (use-pathlib), `PT`, `Q`, plus many more.
- Ecosystem prefixes: `PL` Pylint, `PD` pandas-vet, `NPY` NumPy, `RUF` Ruff-specific, `AIR` Airflow, `FAST` FastAPI, `PERF` Perflint, `FURB` refurb, `TRY` tryceratops.
- Status markers: 🧪 preview (unstable), ⚠️ deprecated, ❌ removed, 🛠️ automatic fix available; unmarked rules are stable.
- Default: Flake8 `F` rules + curated `E` subset, excluding stylistic rules that overlap the formatter.
