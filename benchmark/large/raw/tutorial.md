# Ruff Tutorial

Source: https://docs.astral.sh/ruff/tutorial/

## Getting Started

```bash
uv init --lib numbers
uv add --dev ruff
uv run ruff check
uv run ruff check --fix
uv run ruff format
```

Ruff highlights problems like unused imports; many are fixable with `--fix`.

## Configuration

Ruff searches for configuration in `pyproject.toml`, `ruff.toml`, or `.ruff.toml`, starting from the target file's directory and moving up through parent directories.

### pyproject.toml
```toml
[project]
requires-python = ">=3.10"

[tool.ruff]
line-length = 79

[tool.ruff.lint]
extend-select = ["E501"]
```

### ruff.toml
```toml
target-version = "py310"
line-length = 79

[lint]
extend-select = ["E501"]
```

## Rule Selection

Default behavior: Ruff enables Flake8's `F` rules plus a subset of `E` rules, deliberately omitting stylistic rules that overlap with formatters.

```toml
[tool.ruff.lint]
extend-select = ["UP"]
```

Multiple rule sets:
```toml
[tool.ruff.lint]
extend-select = [
  "UP",  # pyupgrade
  "D",   # pydocstyle
]

[tool.ruff.lint.pydocstyle]
convention = "google"
```

## Ignoring Errors

Single line:
```python
from typing import Iterable  # noqa: UP035
```

Entire file:
```python
# ruff: noqa: UP035
from typing import Iterable
```

## Adding Rules to Existing Codebases

```bash
uv run ruff check --select UP035 --add-noqa .
```

## Integrations (pre-commit)

```yaml
- repo: https://github.com/astral-sh/ruff-pre-commit
  rev: v0.15.18
  hooks:
    - id: ruff-check
    - id: ruff-format
```

## Key Defaults

- Line length: 88 characters
- Default rule set focuses on errors and common issues, avoiding formatter overlap
- Over 900 lint rules across 50+ plugins
- `--fix` flag automatically corrects fixable violations
