---
type: concept
title: File Discovery & Jupyter Support
---

How Ruff decides which files to analyze, including gitignore handling and notebook support.

- Default inclusions: `*.py`, `*.pyi`, `*.ipynb`, `pyproject.toml`, and `*.pyw` (preview) ([[sources/configuration]]).
- Respects `.gitignore`, `.git/info/exclude`, and global gitignore via `respect-gitignore` ([[sources/configuration]], [[sources/settings]]).
- `include`/`extend-include` add paths; `force-exclude` applies exclusions to directly-passed files ([[sources/configuration]]).
- Jupyter Notebooks linted and formatted by default (v0.6.0+); integrates with nbQA ([[sources/configuration]], [[sources/faq]]).
- In notebooks `E402` checks for imports at the top of each cell rather than the file ([[sources/configuration]]).

## Links
[[concepts/configuration]] · [[concepts/defaults]] · [[concepts/linter]] · [[sources/configuration]] · [[sources/settings]] · [[sources/faq]]
