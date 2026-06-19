---
type: source
title: "Ruff Tutorial"
url: https://docs.astral.sh/ruff/tutorial/
kind: official-docs
---

## Key claims
- Workflow: `ruff check`, `ruff check --fix`, `ruff format`; `--fix` auto-corrects many fixable violations (e.g. unused imports).
- Config discovery: searches `pyproject.toml`/`ruff.toml`/`.ruff.toml` from the target file's dir upward through parents.
- Default rules: Flake8 `F` rules plus a subset of `E` rules, deliberately omitting stylistic rules that overlap formatters.
- Rule selection via `extend-select` (e.g. `["UP"]`, `["D"]`); pydocstyle `convention="google"`.
- Suppression: line `# noqa: UP035`; whole file `# ruff: noqa: UP035`; bulk-add via `--add-noqa`.
- pre-commit integration with `astral-sh/ruff-pre-commit` (rev v0.15.18), hooks `ruff-check`/`ruff-format`; default line length 88; 900+ rules across 50+ plugins.
