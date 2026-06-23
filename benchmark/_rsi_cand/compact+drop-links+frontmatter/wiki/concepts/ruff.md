---
type: concept
title: Ruff
---

An extremely fast Python linter and code formatter written in Rust, built by Astral to replace a stack of legacy tools with one binary.

- Tagline: "an extremely fast Python linter and code formatter, written in Rust" .
- 10-100x faster than Flake8/Black, benchmarked on CPython; one report cited 0.4s vs 2.5min Pylint on 250k lines .
- Consolidates Flake8 (+plugins), Black, isort, pydocstyle, pyupgrade, autoflake into one tool .
- Maintained by Astral (also uv and ty); MIT-licensed; 900+ rules; built-in caching .
- Adopted by FastAPI, Pandas, SciPy, Hugging Face, Apache Airflow, and 100+ orgs .

## Sources
- https://docs.astral.sh/ruff/
- https://github.com/astral-sh/ruff
- https://docs.astral.sh/ruff/faq/
