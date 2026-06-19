# Ruff: Python Linter and Formatter (GitHub README)

Source: https://github.com/astral-sh/ruff

## Overview

Ruff is an exceptionally fast Python linter and code formatter implemented in Rust. The project is maintained by **Astral**, the company behind the uv package manager and ty type checker.

**Tagline:** "An extremely fast Python linter and code formatter, written in Rust."

## Performance Claims

- 10-100x faster than existing tools like Flake8 and Black
- Benchmarked on CPython codebase
- One maintainer noted analysis in 0.4 seconds versus 2.5 minutes with Pylint on a 250k line codebase

## Key Features

- Installation via pip, uv, pipx, Homebrew, Conda, standalone installers
- Configuration: `pyproject.toml`, `ruff.toml`, `.ruff.toml`
- Python 3.14 compatibility
- 900+ built-in rules with native implementations of popular Flake8 plugins
- Drop-in parity with Flake8, isort, and Black
- Built-in caching
- Automatic fixes (e.g., removing unused imports)
- Editor integrations for VS Code and others
- Monorepo support with hierarchical configuration

## Installation Methods

```bash
uv tool install ruff@latest
pip install ruff
pipx install ruff
curl -LsSf https://astral.sh/ruff/install.sh | sh  # macOS/Linux
```

## Configuration Example (defaults)

```toml
line-length = 88
indent-width = 4
target-version = "py310"

[lint]
select = ["E4", "E7", "E9", "F"]
fixable = ["ALL"]

[format]
quote-style = "double"
indent-style = "space"
```

## Supported Rule Categories

- Core: Pyflakes, pycodestyle
- 40+ Flake8 plugins (flake8-bugbear, flake8-comprehensions, etc.)
- Tools: isort, Black, pyupgrade, pydocstyle, autoflake, pandas-vet, pep8-naming

## Comparison

- Flake8: Ruff replaces Flake8 plus dozens of plugins with a single tool
- Black: Formatter parity while executing significantly faster
- isort: Integrates import sorting without separate tooling

## Notable Adoption

FastAPI, Pandas, SciPy, Hugging Face Transformers, Apache Airflow, and 100+ organizations.

## Repository Statistics (as fetched)

- Stars: 48.1k; Forks: 2.2k; Open issues: 1.7k
- Latest release: 0.15.18 (June 18, 2026)
- Languages: Rust (96.5%), Python (2.5%), TypeScript (0.9%)

## License

MIT License
