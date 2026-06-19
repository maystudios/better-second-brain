# Source: Ruff - GitHub README (astral-sh/ruff)

- **Citation / URL:** https://github.com/astral-sh/ruff
- **Raw file:** `benchmark/large/raw/github-astral-sh-ruff.md`
- **Type:** Project README / repository page

## Key claims

- Ruff is an exceptionally fast Python linter and code formatter implemented in Rust.
- Maintained by **Astral**, "the company behind the uv package manager and ty type checker."
- Performance: 10-100x faster than existing tools like Flake8 and Black; benchmarked on CPython codebase. One maintainer noted analysis in **0.4 seconds versus 2.5 minutes with Pylint** on a 250k-line codebase.
- Installation via pip, uv, pipx, Homebrew, Conda, and standalone installers.
- Configuration files: `pyproject.toml`, `ruff.toml`, `.ruff.toml`.
- Python 3.14 compatibility; 900+ built-in rules; drop-in parity with Flake8, isort, Black.
- Built-in caching; automatic fixes (e.g., removing unused imports); editor integrations; monorepo support with hierarchical configuration.

## Installation methods (quoted)

```bash
uv tool install ruff@latest
pip install ruff
pipx install ruff
curl -LsSf https://astral.sh/ruff/install.sh | sh  # macOS/Linux
```

## Default configuration example

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

## Supported rule categories

- Core: Pyflakes, pycodestyle.
- 40+ Flake8 plugins (flake8-bugbear, flake8-comprehensions, etc.).
- Tools: isort, Black, pyupgrade, pydocstyle, autoflake, pandas-vet, pep8-naming.

## Adoption

FastAPI, Pandas, SciPy, Hugging Face Transformers, Apache Airflow, "and 100+ organizations."

## Repository statistics (as fetched)

- Stars: 48.1k; Forks: 2.2k; Open issues: 1.7k.
- Latest release: **0.15.18 (June 18, 2026)**.
- Languages: Rust (96.5%), Python (2.5%), TypeScript (0.9%).
- License: **MIT**.

## Notable quotes

> "An extremely fast Python linter and code formatter, written in Rust."

## Prose summary

The README restates the docs-landing positioning but adds repository-level facts: the maintaining organization (Astral, also responsible for `uv` and the `ty` type checker), the MIT license, language breakdown, and concrete repo statistics including a pinned latest release of 0.15.18. It contributes the most vivid performance anecdote in the corpus - 0.4s vs 2.5 minutes against Pylint on a 250k-line codebase - and broadens the installation matrix (adding uv, Homebrew, Conda, and standalone installers).
