# Source: Ruff — Python Linter & Formatter (Overview)

- **Citation / URL:** https://docs.astral.sh/ruff/
- **Raw file:** `benchmark/large/raw/ruff-overview.md`
- **Type:** Official documentation landing page

## Key claims

- Ruff is an extremely fast Python linter and code formatter written in Rust, designed to replace multiple traditional tools with a unified solution.
- Performance: claimed **10–100x faster** than existing linters (Flake8) and formatters (Black); benchmarked on the CPython codebase from scratch.
- Installable via pip; supports `pyproject.toml`; Python 3.14 compatibility.
- Feature parity with Flake8, isort, and Black.
- Built-in caching to skip re-analyzing unchanged files.
- Automatic error correction (e.g., removing unused imports).
- **Over 900 built-in rules**, including native implementations of popular Flake8 plugins.
- First-party editor integrations for VS Code and others.
- Monorepo-friendly with hierarchical configuration.

## What it replaces

Ruff consolidates the functionality of: Flake8 (plus dozens of plugins), Black, isort, pydocstyle, pyupgrade, and autoflake — "all while executing tens to hundreds of times faster than individual tools."

## Adoption

Named adopters: Apache Airflow, Apache Superset, FastAPI, Hugging Face, Pandas, and SciPy.

## Notable quotes

> "An extremely fast Python linter and code formatter, written in Rust."

## Prose summary

This is the canonical positioning page for Ruff. Its thesis is consolidation plus speed: a single Rust-implemented tool that subsumes a fragmented ecosystem of Python quality tools (linting, import sorting, formatting, docstring checking, upgrade automation, dead-code removal) while running dramatically faster than each tool it replaces. The page anchors the two recurring marketing claims — the "10–100x faster" figure and the "900+ rules" count — that reappear across the documentation set, and it lists a roster of prominent adopters as social proof.
