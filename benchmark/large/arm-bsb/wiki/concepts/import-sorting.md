# Import Sorting (isort compatibility)

[[concepts/ruff]] provides import sorting through its [[concepts/linter|linter]], under the `I` (isort) rule prefix ([[sources/rules]]; [[sources/linter]]). It is **not** part of the [[concepts/formatter]]: "the formatter does NOT sort imports" ([[sources/formatter]]).

## How to sort and format together

Because sorting lives in the linter, the documented two-step workflow is ([[sources/formatter]]):
```bash
ruff check --select I --fix
ruff format
```

## Compatibility with isort

Ruff's import sorting targets isort's "black" profile ([[sources/faq]]). Documented differences from isort ([[sources/faq]]):
- Ruff groups non-aliased imports from the same module on single lines, whereas isort splits at aliased boundaries.
- Ruff recognizes additional standard-library modules that isort misses, e.g. `_string` and `idlelib`.

## Action comments

Ruff honors isort action comments to control sorting: `# isort: skip_file`, `# isort: on` / `# isort: off`, `# isort: skip`, and `# isort: split` ([[sources/linter]]). These are part of the broader [[concepts/error-suppression]] surface.

## Interaction with the formatter

When combining sorting with formatting, certain non-default isort settings should be avoided because they conflict with the formatter: `force-single-line`, `force-wrap-aliases`, `lines-after-imports`, `lines-between-types`, and `split-on-trailing-comma` ([[sources/formatter]]). See [[concepts/formatter-lint-conflicts]].

## Open questions

- The sources describe Ruff's sorting as targeting isort's "black" profile ([[sources/faq]]) but do not state whether other isort profiles are emulated.
