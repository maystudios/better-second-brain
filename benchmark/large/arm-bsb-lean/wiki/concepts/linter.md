---
type: concept
title: The Linter (ruff check)
---

Ruff's linting engine, invoked with `ruff check`, that detects violations and applies automatic fixes.

- `ruff check` supports `--fix`, `--watch` (re-lint on change), and path arguments ([[sources/linter]], [[sources/tutorial]]).
- Default rule set is Flake8 `F` rules plus a curated `E` subset, omitting stylistic rules that overlap the formatter ([[sources/tutorial]], [[sources/rules]], [[sources/settings]]).
- Selection controlled by `lint.select`/`extend-select`/`ignore`/`per-file-ignores`; CLI overrides config files ([[sources/linter]], [[sources/configuration]]).
- Drop-in Flake8 replacement implementing all Pyflakes rules plus a pycodestyle subset ([[sources/faq]], [[sources/ruff-overview]]).
- Exit codes: 0 clean/fixed, 1 violations, 2 abnormal; modifiers `--exit-zero`, `--exit-non-zero-on-fix` ([[sources/linter]]).

## Links
[[concepts/rules-and-plugins]] · [[concepts/fix-safety]] · [[concepts/suppression]] · [[concepts/formatter]] · [[sources/linter]] · [[sources/tutorial]] · [[sources/faq]]
