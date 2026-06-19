# Ruff

**Ruff** is an extremely fast Python linter and code formatter, written in Rust and maintained by [Astral](https://astral.sh) - the same company behind the `uv` package manager and the `ty` type checker. Its goal is simple: replace a whole drawer of slow, single-purpose Python tools with one unified binary that runs tens to hundreds of times faster.

In practice, a single install of Ruff stands in for [[Linter|Flake8 (plus dozens of plugins)]], [[Formatter|Black]], isort, pydocstyle, pyupgrade, and autoflake. One maintainer reported analyzing a 250k-line codebase in 0.4 seconds where Pylint took 2.5 minutes, and the project advertises being 10-100x faster than the legacy tools it replaces (benchmarked against the CPython codebase).

## Why people use it

- **Speed.** Because it's compiled Rust with built-in caching, re-running on an unchanged tree is nearly instant.
- **One tool, one config.** Everything lives in `pyproject.toml`, `ruff.toml`, or `.ruff.toml`. See [[Configuration]].
- **Familiar rules.** Over 900 lint rules, including native reimplementations of popular Flake8 plugins, organized by prefix. See [[Rules]].
- **Auto-fixing.** Many violations (like unused imports) are corrected automatically with `--fix`. See [[Linter]].
- **Formatter parity.** A drop-in [[Formatter|Black-compatible formatter]] matching >99.9% of lines on large projects.
- **Editor integration.** A built-in language server powers [[Editors|VS Code, Neovim, and more]].

## The two halves

Ruff is really two tools sharing one binary and one config file:

- **`ruff check`** - the [[Linter]], which finds (and optionally fixes) problems.
- **`ruff format`** - the [[Formatter]], which rewrites code to a consistent style.

A common workflow runs both: sort imports and fix lint issues, then format.

```bash
ruff check --fix
ruff format
```

## Getting started

To install and run Ruff for the first time, see [[Installation]]. For a hands-on walkthrough of linting, fixing, and configuring a real project, see the [[Tutorial]].

## Adoption

Ruff is used by FastAPI, Pandas, SciPy, Hugging Face Transformers, Apache Airflow, Apache Superset, and 100+ other organizations. It's MIT-licensed, with the latest release (0.15.18) shipped June 2026.

## Map of this wiki

- [[Installation]] - every way to get Ruff onto your machine
- [[Tutorial]] - a guided first run on a real project
- [[Linter]] - `ruff check`, rule selection, fixes, and suppression
- [[Formatter]] - `ruff format` and Black compatibility
- [[Rules]] - the rule catalog and prefix-to-plugin map
- [[Configuration]] - config files, settings, and hierarchical layouts
- [[Editors]] - language server and per-editor setup
- [[Integrations]] - pre-commit, CI, Docker, and [[Versioning]]
