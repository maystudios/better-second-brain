---
type: concept
title: Default Settings
---

Ruff's out-of-the-box configuration values for formatting, linting, and file handling.

- Top-level: `line-length=88` (matches Black), `indent-width=4`, `target-version="py310"`, `respect-gitignore=true` .
- Lint default `select=["E4","E7","E9","F"]` .
- Format defaults: `quote-style="double"`, `indent-style="space"`, `line-ending="auto"`, `docstring-code-format=false` .
- 4-space indent per PEP 8; double quotes preferred per PEP 257 .
- Cache stored in `.ruff_cache`; common dev dirs auto-excluded .

## Sources
- https://docs.astral.sh/ruff/settings/
- https://docs.astral.sh/ruff/configuration/
- https://github.com/astral-sh/ruff
- https://docs.astral.sh/ruff/formatter/
