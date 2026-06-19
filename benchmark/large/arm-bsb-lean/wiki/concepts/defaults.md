---
type: concept
title: Default Settings
---

Ruff's out-of-the-box configuration values for formatting, linting, and file handling.

- Top-level: `line-length=88` (matches Black), `indent-width=4`, `target-version="py310"`, `respect-gitignore=true` ([[sources/settings]], [[sources/configuration]], [[sources/github-astral-sh-ruff]]).
- Lint default `select=["E4","E7","E9","F"]` ([[sources/settings]], [[sources/configuration]]).
- Format defaults: `quote-style="double"`, `indent-style="space"`, `line-ending="auto"`, `docstring-code-format=false` ([[sources/settings]], [[sources/formatter]]).
- 4-space indent per PEP 8; double quotes preferred per PEP 257 ([[sources/settings]]).
- Cache stored in `.ruff_cache`; common dev dirs auto-excluded ([[sources/settings]], [[sources/configuration]]).

## Links
[[concepts/configuration]] · [[concepts/formatter]] · [[concepts/file-discovery]] · [[sources/settings]] · [[sources/configuration]] · [[sources/github-astral-sh-ruff]] · [[sources/formatter]]
