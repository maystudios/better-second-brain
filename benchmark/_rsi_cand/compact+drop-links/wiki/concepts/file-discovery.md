---
type: concept
title: File Discovery & Jupyter Support
---

How Ruff decides which files to analyze, including gitignore handling and notebook support.

- Default inclusions: `*.py`, `*.pyi`, `*.ipynb`, `pyproject.toml`, and `*.pyw` (preview) .
- Respects `.gitignore`, `.git/info/exclude`, and global gitignore via `respect-gitignore` .
- `include`/`extend-include` add paths; `force-exclude` applies exclusions to directly-passed files .
- Jupyter Notebooks linted and formatted by default (v0.6.0+); integrates with nbQA .
- In notebooks `E402` checks for imports at the top of each cell rather than the file .

## Sources
- https://docs.astral.sh/ruff/configuration/
- https://docs.astral.sh/ruff/settings/
- https://docs.astral.sh/ruff/faq/
