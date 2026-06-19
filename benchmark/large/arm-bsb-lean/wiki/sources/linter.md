---
type: source
title: "The Ruff Linter"
url: https://docs.astral.sh/ruff/linter/
kind: official-docs
---

## Key claims
- `ruff check` supports `--fix`, `--watch` (re-lint on change), and path args.
- Rule selection settings: `lint.select`, `extend-select`, `ignore`, `extend-ignore`, `per-file-ignores`.
- Rule codes mirror Flake8: 1-3 letter prefix + 3 digits (e.g. `F401`); `F`=Pyflakes, `E`=pycodestyle, `B`=bugbear, `I`=isort, `UP`=pyupgrade.
- `ALL` enables all rules and auto-disables conflicting ones (e.g. `D203`/`D211`); CLI > pyproject.toml > inherited config.
- Fix safety: safe fixes preserve runtime behavior; unsafe fixes may change it (e.g. `RUF015` `list(...)[0]`→`next(iter(...))` swaps IndexError→StopIteration); `--unsafe-fixes` applies them; `extend-safe-fixes`/`extend-unsafe-fixes` adjust per rule.
- Suppression: `# noqa[: CODE]` line-level, `# ruff: noqa` file-level (own line), respects `# flake8: noqa`; `RUF100` flags unused noqa; exit codes 0/1/2 with `--exit-zero` and `--exit-non-zero-on-fix` modifiers.
