---
type: concept
title: The Formatter (ruff format)
---

Ruff's code formatter, invoked with `ruff format`, designed as a near drop-in replacement for Black.

- Targets Black compatibility: >99.9% of lines formatted identically on Django/Zulip; adheres to Black stable style ([[sources/formatter]], [[sources/faq]]).
- Defaults: line-length 88, `quote-style="double"`, 4-space indent, magic trailing comma respected ([[sources/formatter]], [[sources/settings]]).
- Known deviations from Black: formats f-string expressions, alternates nested-f-string quotes, preview method-chain layout ([[sources/formatter]]).
- Does NOT sort imports; sort separately via `ruff check --select I --fix` then `ruff format` ([[sources/formatter]], [[sources/faq]]).
- `--check` verifies without writing; warns when lint rules conflict with the formatter ([[sources/formatter]]).
- Optional docstring code formatting (`docstring-code-format=true`) over doctest/CommonMark/reST blocks ([[sources/formatter]], [[sources/settings]]).

## Links
[[concepts/linter]] · [[concepts/configuration]] · [[concepts/suppression]] · [[concepts/preview-mode]] · [[sources/formatter]] · [[sources/faq]] · [[sources/settings]]
