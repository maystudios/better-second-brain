---
type: source
title: "Ruff: Python Linter & Formatter (Overview)"
url: https://docs.astral.sh/ruff/
---

## Key claims
- Extremely fast Python linter + code formatter written in Rust; aims to replace multiple tools with one.
- 10-100x faster than Flake8/Black; benchmarked from scratch on CPython.
- 900+ built-in rules; native implementations of popular Flake8 plugins; built-in caching; auto-fix (e.g. unused imports).
- Feature parity with Flake8, isort, and Black; installable via pip; `pyproject.toml` support; Python 3.14 compatible.
- Consolidates Flake8 (+plugins), Black, isort, pydocstyle, pyupgrade, autoflake.
- Adopted by Apache Airflow, Apache Superset, FastAPI, Hugging Face, Pandas, SciPy.
