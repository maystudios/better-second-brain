# Tutorial

This page walks through a first real run of [[Ruff]] on a small project, from linting to fixing to configuration. For installation options, see [[Installation]].

## Set up a project

```bash
uv init --lib numbers
uv add --dev ruff
uv run ruff check
uv run ruff check --fix
uv run ruff format
```

On the first `ruff check`, Ruff highlights problems such as unused imports. Many of these are fixable - re-run with `--fix` and they vanish. Then `ruff format` tidies the layout. See the [[Linter]] and [[Formatter]] pages for the full behavior of each command.

## Where config lives

Ruff searches for configuration in `pyproject.toml`, `ruff.toml`, or `.ruff.toml`, starting in the target file's directory and walking up through parents. A minimal `pyproject.toml`:

```toml
[project]
requires-python = ">=3.10"

[tool.ruff]
line-length = 79

[tool.ruff.lint]
extend-select = ["E501"]
```

The same in a standalone `ruff.toml` drops the `[tool.ruff]` prefix. The mechanics of all this are covered in [[Configuration]].

## Choosing rules

By default Ruff enables Pyflakes' `F` rules plus a curated subset of `E` rules, deliberately omitting stylistic rules that overlap with the formatter. You add more by prefix:

```toml
[tool.ruff.lint]
extend-select = [
  "UP",  # pyupgrade
  "D",   # pydocstyle
]

[tool.ruff.lint.pydocstyle]
convention = "google"
```

The full prefix catalog lives in [[Rules]].

## Silencing a specific warning

```python
from typing import Iterable  # noqa: UP035
```

To suppress a rule across an entire file, put the comment on its own line:

```python
# ruff: noqa: UP035
from typing import Iterable
```

More on suppression (including detecting unused `noqa`s) is in the [[Linter]] page.

## Onboarding an existing codebase

When adopting a new rule on a large project, you can grandfather in the existing violations:

```bash
uv run ruff check --select UP035 --add-noqa .
```

## Running in CI

Wire Ruff into pre-commit so it runs on every commit:

```yaml
- repo: https://github.com/astral-sh/ruff-pre-commit
  rev: v0.15.18
  hooks:
    - id: ruff-check
    - id: ruff-format
```

See [[Integrations]] for GitHub Actions, GitLab, and Docker variants.

## Defaults worth remembering

- Line length: 88 characters
- Default rules focus on errors and common issues, avoiding formatter overlap
- 900+ lint rules across 50+ plugins
- `--fix` auto-corrects fixable violations
