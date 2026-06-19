# Formatter / Lint Rule Conflicts

Some [[concepts/linter|lint]] rules conflict with the [[concepts/formatter]] because they enforce stylistic choices the formatter already handles. Ruff emits warnings when it detects incompatible rules ([[sources/formatter]]).

## Rules to disable via `lint.ignore`

The formatter reference lists these conflicting rules to disable ([[sources/formatter]]):
- Quotes: `Q000`, `Q001`, `Q002`, `Q003`, `Q004`.
- Whitespace/tabs: `W191`, `E111`, `E114`, `E117`.
- Commas: `COM812`, `COM819`.
- Docstrings/implicit concat: `D203`, `D206`, `D300`, `ISC002`.

`E501` (line too long) can coexist with the formatter but may still trigger ([[sources/formatter]]).

## isort settings to avoid

When pairing [[concepts/import-sorting|import sorting]] with the formatter, avoid these non-default isort settings ([[sources/formatter]]): `force-single-line`, `force-wrap-aliases`, `lines-after-imports`, `lines-between-types`, `split-on-trailing-comma`.

## Why the defaults already avoid most conflicts

This conflict surface is the reason Ruff's default rule selection deliberately omits stylistic rules that overlap with formatters. The default `select` of `["E4", "E7", "E9", "F"]` enables Pyflakes `F` plus a curated subset of pycodestyle `E` rules, excluding stylistic ones that overlap with Black / `ruff format` ([[sources/rules]]; [[sources/tutorial]]; [[sources/configuration]]; [[sources/settings]]). See [[concepts/default-settings]] and [[concepts/rules-and-rule-codes]].

The linter's own conflict handling is related but distinct: when `ALL` is selected, Ruff auto-disables internally conflicting rules such as `D203`/`D211` ([[sources/linter]]).

## Open questions

- The sources do not state the precise warning text Ruff emits, only that warnings are emitted when incompatible rules are detected ([[sources/formatter]]).
