---
type: concept
title: Rules & Plugins
---

Ruff's catalog of 900+ lint rules, organized by prefix codes mapping to the source tool or Flake8 plugin each reimplements.

- Rule codes mirror Flake8: 1-3 letter prefix + 3 digits, e.g. `F401` ([[sources/linter]], [[sources/rules]]).
- Core prefixes: `F` Pyflakes, `E`/`W` pycodestyle, `I` isort, `UP` pyupgrade, `B` bugbear, `SIM` simplify, `D` pydocstyle ([[sources/rules]], [[sources/linter]]).
- Reimplements 50+ popular Flake8 plugins natively plus Pylint, pandas-vet, NumPy, Airflow, FastAPI, refurb, etc. ([[sources/faq]], [[sources/rules]], [[sources/github-astral-sh-ruff]]).
- Status markers: 🧪 preview, ⚠️ deprecated, ❌ removed, 🛠️ fix available; unmarked = stable ([[sources/rules]], [[sources/preview]]).
- `ALL` enables every rule and auto-disables conflicting ones (e.g. `D203`/`D211`) ([[sources/linter]]).
