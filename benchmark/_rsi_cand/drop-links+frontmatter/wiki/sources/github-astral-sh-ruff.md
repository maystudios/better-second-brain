---
type: source
title: "Ruff (GitHub README, astral-sh/ruff)"
url: https://github.com/astral-sh/ruff
---

## Key claims
- Maintained by Astral (makers of uv package manager and ty type checker); MIT License.
- One maintainer cited 0.4s analysis vs 2.5min with Pylint on a 250k-line codebase.
- Install via pip, uv, pipx, Homebrew, Conda, standalone installers; config via `pyproject.toml`/`ruff.toml`/`.ruff.toml`.
- Defaults: `line-length=88`, `indent-width=4`, `target-version="py310"`, lint `select=["E4","E7","E9","F"]`, format `quote-style="double"`.
- Core sources Pyflakes + pycodestyle plus 40+ Flake8 plugins, isort, Black, pyupgrade, pydocstyle, autoflake, pandas-vet, pep8-naming.
- Stats as fetched: 48.1k stars, latest release 0.15.18 (June 18, 2026); Rust 96.5%; 100+ orgs adopting.
