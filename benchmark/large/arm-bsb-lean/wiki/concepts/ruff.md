---
type: concept
title: Ruff
---

An extremely fast Python linter and code formatter written in Rust, built by Astral to replace a stack of legacy tools with one binary.

- Tagline: "an extremely fast Python linter and code formatter, written in Rust" ([[sources/ruff-overview]], [[sources/github-astral-sh-ruff]]).
- 10-100x faster than Flake8/Black, benchmarked on CPython; one report cited 0.4s vs 2.5min Pylint on 250k lines ([[sources/ruff-overview]], [[sources/github-astral-sh-ruff]]).
- Consolidates Flake8 (+plugins), Black, isort, pydocstyle, pyupgrade, autoflake into one tool ([[sources/ruff-overview]], [[sources/faq]]).
- Maintained by Astral (also uv and ty); MIT-licensed; 900+ rules; built-in caching ([[sources/github-astral-sh-ruff]], [[sources/ruff-overview]]).
- Adopted by FastAPI, Pandas, SciPy, Hugging Face, Apache Airflow, and 100+ orgs ([[sources/ruff-overview]], [[sources/github-astral-sh-ruff]]).

## Links
[[concepts/linter]] · [[concepts/formatter]] · [[concepts/rules-and-plugins]] · [[concepts/configuration]] · [[concepts/installation]] · [[sources/ruff-overview]] · [[sources/github-astral-sh-ruff]] · [[sources/faq]]
