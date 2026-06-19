# Source: Ruff FAQ

- **Citation / URL:** https://docs.astral.sh/ruff/faq/
- **Raw file:** `benchmark/large/raw/faq.md`
- **Type:** Official documentation — FAQ

## Key claims

### Compatibility & replacement
- **Black compatibility:** "The Ruff linter is compatible with Black out-of-the-box, as long as the line-length setting is consistent between the two." The formatter aims for near-identical output (>99.9% line compatibility on Django and Zulip).
- **Flake8 replacement:** drop-in Flake8 replacement when used without plugins, alongside Black, on Python 3 code. Implements all Pyflakes rules plus a subset of pycodestyle rules.
- **Additional tool replacement:** can replace Black, isort, yesqa, eradicate, and most pyupgrade rules. Re-implements 50+ popular Flake8 plugins natively (flake8-bugbear, flake8-comprehensions, flake8-docstrings, flake8-django, etc.).

### Python version support
- Ruff can lint code for **Python 3.7 through 3.13** and "does not support Python 2." Installable on any Python 3.7+ environment; requires no Rust installation (ships as pre-built wheels on PyPI).

### Type checking
- "Ruff is a linter, not a type checker." A type checker (Mypy, Pyright, Pyre) catches type errors Ruff misses. They are complementary tools.

### Import sorting vs isort
- Ruff's import sorting targets isort's "black" profile. Differences: Ruff groups non-aliased imports from the same module on single lines, while isort splits at aliased boundaries. Ruff also recognizes additional standard-library modules isort misses (e.g., `_string`, `idlelib`).

### Jupyter & preview
- Built-in Jupyter Notebook support for linting and formatting; integrates with nbQA. Preview mode enables experimental rules and fixes.

### Docstring support
- NumPy and Google-style docstrings supported via the `convention` setting in pydocstyle config (accepts "google", "numpy", or "pep257").

### Configuration flexibility
- `ruff.toml` is an alternative to `pyproject.toml` with an identical schema. No INI file support. User-level defaults at `~/.config/ruff/ruff.toml` (Linux/macOS) or `~\AppData\Roaming\ruff\ruff.toml` (Windows).

## Notable quotes

> "Ruff is a linter, not a type checker."

> "The Ruff linter is compatible with Black out-of-the-box, as long as the line-length setting is consistent between the two."

## Prose summary

The FAQ clarifies scope and compatibility boundaries. It states precisely what Ruff replaces (Black, isort, yesqa, eradicate, most pyupgrade rules, and 50+ Flake8 plugins) and what it does not (it is not a type checker — Mypy/Pyright/Pyre remain complementary). It pins the supported lint targets at Python 3.7–3.13 with no Python 2 support and no Rust toolchain requirement (prebuilt PyPI wheels). It details how Ruff's import sorting differs from isort's "black" profile, documents Jupyter/nbQA support, lists the three pydocstyle conventions, and gives the user-level config-file locations per OS.
