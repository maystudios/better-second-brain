# The Linter (`ruff check`)

The **linter** is one of [[concepts/ruff]]'s two halves; it is invoked with `ruff check` ([[sources/linter]]). The other half is the [[concepts/formatter]].

## Commands

- `ruff check` - lint files in the current directory ([[sources/linter]]; [[sources/installation]]).
- `ruff check --fix` - lint and fix fixable errors ([[sources/linter]]; [[sources/tutorial]]).
- `ruff check --watch` - re-lint on file changes ([[sources/linter]]).
- `ruff check path/to/code/` - lint a specific directory ([[sources/linter]]).

## Rule selection

Rule selection is controlled by `lint.select`, `lint.extend-select`, `lint.ignore`, `lint.extend-ignore`, and `lint.per-file-ignores` ([[sources/linter]]). The full code grammar and family map are documented in [[concepts/rules-and-rule-codes]]. The `ALL` meta-selector enables all rules and causes Ruff to auto-disable conflicting rules such as `D203`/`D211` ([[sources/linter]]). Selection precedence is CLI options > `pyproject.toml` > inherited config files ([[sources/linter]]), consistent with the broader override model in [[concepts/configuration]] ([[sources/configuration]]).

A recommended baseline selection is `["E", "F", "UP", "B", "SIM", "I"]` ([[sources/linter]]).

## Fixes and fix safety

`ruff check --fix` applies all **safe** fixes by default ([[sources/linter]]). The safe/unsafe distinction is the linter's most important behavioral contract and is detailed in [[concepts/fix-safety]]: safe fixes preserve runtime behavior, while unsafe fixes may change it ([[sources/linter]]). Automatic correction (e.g., removing unused imports) is one of Ruff's headline features ([[sources/ruff-overview]]; [[sources/github-astral-sh-ruff]]).

## Error suppression

Violations can be suppressed inline or per file; the mechanics (`# noqa`, file-level `# ruff: noqa`, `RUF100`, `--add-noqa`, and isort action comments) are covered in [[concepts/error-suppression]] ([[sources/linter]]). The tutorial shows the same patterns from a user's perspective ([[sources/tutorial]]).

## Exit codes

`ruff check` returns ([[sources/linter]]):
- `0` - no violations found, or all violations fixed.
- `1` - violations found.
- `2` - abnormal termination (invalid config/CLI, or internal error).

Modifiers: `--exit-zero` always exits `0` except on abnormal termination, and `--exit-non-zero-on-fix` exits `1` even when all violations were fixed ([[sources/linter]]).

## Relationship to type checking

The linter does not perform type checking; "Ruff is a linter, not a type checker," and tools like Mypy, Pyright, and Pyre remain complementary ([[sources/faq]]).

## Open questions

- The sources do not enumerate which specific rules constitute the recommended `["E", "F", "UP", "B", "SIM", "I"]` baseline beyond their family prefixes ([[sources/linter]]).
