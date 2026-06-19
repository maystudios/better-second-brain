# Ruff FAQ

Source: https://docs.astral.sh/ruff/faq/

## Compatibility & Replacement

Black Compatibility: "The Ruff linter is compatible with Black out-of-the-box, as long as the line-length setting is consistent between the two." Formatter aims for near-identical output (>99.9% line compatibility on Django and Zulip).

Flake8 Replacement: drop-in Flake8 replacement when used without plugins, alongside Black, on Python 3 code. Implements all Pyflakes rules plus a subset of pycodestyle rules.

Additional Tool Replacement: can replace Black, isort, yesqa, eradicate, and most pyupgrade rules. Re-implements 50+ popular Flake8 plugins natively (flake8-bugbear, flake8-comprehensions, flake8-docstrings, flake8-django, etc.).

## Python Version Support

Ruff can lint code for Python 3.7 through 3.13 and "does not support Python 2." Installable on any Python 3.7+ environment; requires no Rust installation (ships as pre-built wheels on PyPI).

## Type Checking

"Ruff is a linter, not a type checker." A type checker (Mypy, Pyright, Pyre) catches type errors Ruff misses. Complementary tools.

## Import Sorting vs isort

Ruff's import sorting targets isort's "black" profile. Differences: Ruff groups non-aliased imports from the same module on single lines, while isort splits at aliased boundaries. Ruff also recognizes additional standard-library modules isort misses (e.g., `_string`, `idlelib`).

## Jupyter & Preview

Built-in Jupyter Notebook support for linting and formatting; integrates with nbQA. Preview mode enables experimental rules and fixes.

## Docstring Support

NumPy and Google-style docstrings supported via `convention` setting in pydocstyle config (accepts "google", "numpy", or "pep257").

## Configuration Flexibility

`ruff.toml` as alternative to `pyproject.toml` with identical schema. No INI file support. User-level defaults at `~/.config/ruff/ruff.toml` (Linux/macOS) or `~\AppData\Roaming\ruff\ruff.toml` (Windows).
