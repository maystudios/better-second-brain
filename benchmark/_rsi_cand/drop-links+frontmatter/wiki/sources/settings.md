---
type: source
title: "Ruff Settings Reference"
url: https://docs.astral.sh/ruff/settings/
---

## Key claims
- Top-level defaults: `line-length=88`, `indent-width=4`, `target-version="py310"`, `respect-gitignore=true`.
- Default `exclude` covers common dev dirs (`.git`, `.venv`, `.mypy_cache`, `.ruff_cache`, `dist`, `node_modules`, `venv`, etc.).
- Format defaults: `quote-style="double"`, `indent-style="space"`, `line-ending="auto"`, `docstring-code-format=false`, `docstring-code-line-length="dynamic"`.
- Lint defaults: `select=["E4","E7","E9","F"]`; `dummy-variable-rgx` distinguishes intentional throwaways.
- 4-space indent per PEP 8; double quotes preferred per PEP 257 for docstrings/triple-quoted strings.
- Cache stored in `.ruff_cache` by default.
