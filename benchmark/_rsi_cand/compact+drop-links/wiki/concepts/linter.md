---
type: concept
title: The Linter (ruff check)
---

Ruff's linting engine, invoked with `ruff check`, that detects violations and applies automatic fixes.

- `ruff check` supports `--fix`, `--watch` (re-lint on change), and path arguments .
- Default rule set is Flake8 `F` rules plus a curated `E` subset, omitting stylistic rules that overlap the formatter .
- Selection controlled by `lint.select`/`extend-select`/`ignore`/`per-file-ignores`; CLI overrides config files .
- Drop-in Flake8 replacement implementing all Pyflakes rules plus a pycodestyle subset .
- Exit codes: 0 clean/fixed, 1 violations, 2 abnormal; modifiers `--exit-zero`, `--exit-non-zero-on-fix` .

## Sources
- https://docs.astral.sh/ruff/linter/
- https://docs.astral.sh/ruff/tutorial/
- https://docs.astral.sh/ruff/rules/
- https://docs.astral.sh/ruff/settings/
- https://docs.astral.sh/ruff/configuration/
- https://docs.astral.sh/ruff/faq/
- https://docs.astral.sh/ruff/
