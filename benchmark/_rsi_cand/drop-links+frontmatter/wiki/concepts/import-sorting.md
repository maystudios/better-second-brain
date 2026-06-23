---
type: concept
title: Import Sorting (isort)
---

Ruff's native isort-equivalent import sorting, exposed through the `I` rule category.

- Targets isort's "black" profile for compatibility ([[sources/faq]], [[sources/rules]]).
- The formatter does not sort imports; run `ruff check --select I --fix` then `ruff format` ([[sources/formatter]], [[sources/faq]]).
- Differs from isort: groups non-aliased same-module imports on one line; recognizes extra stdlib modules like `_string`, `idlelib` ([[sources/faq]]).
- isort action comments (`# isort: skip_file`, `on`/`off`, `skip`, `split`) control behavior ([[sources/linter]]).
- Avoid non-default isort settings that conflict with the formatter (e.g. `force-single-line`) ([[sources/formatter]]).
