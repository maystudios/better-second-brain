---
type: source
title: "Ruff FAQ"
url: https://docs.astral.sh/ruff/faq/
kind: official-docs
---

## Key claims
- Ruff linter is Black-compatible out of the box as long as line-length is consistent; formatter ~>99.9% line-compatible (Django, Zulip).
- Drop-in Flake8 replacement (without plugins, alongside Black, on Python 3); reimplements 50+ Flake8 plugins natively; can replace Black, isort, yesqa, eradicate, most pyupgrade rules.
- Lints Python 3.7-3.13; does not support Python 2; ships pre-built PyPI wheels needing no Rust install.
- "Ruff is a linter, not a type checker"; complementary to Mypy/Pyright/Pyre.
- Import sorting targets isort's "black" profile; recognizes extra stdlib modules isort misses (e.g. `_string`, `idlelib`).
- `ruff.toml` shares pyproject's schema; no INI support; user-level defaults at `~/.config/ruff/ruff.toml` (Linux/macOS) or AppData (Windows); docstring conventions google/numpy/pep257.
