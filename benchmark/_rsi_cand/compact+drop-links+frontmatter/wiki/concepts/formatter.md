---
type: concept
title: The Formatter (ruff format)
---

Ruff's code formatter, invoked with `ruff format`, designed as a near drop-in replacement for Black.

- Targets Black compatibility: >99.9% of lines formatted identically on Django/Zulip; adheres to Black stable style .
- Defaults: line-length 88, `quote-style="double"`, 4-space indent, magic trailing comma respected .
- Known deviations from Black: formats f-string expressions, alternates nested-f-string quotes, preview method-chain layout .
- Does NOT sort imports; sort separately via `ruff check --select I --fix` then `ruff format` .
- `--check` verifies without writing; warns when lint rules conflict with the formatter .
- Optional docstring code formatting (`docstring-code-format=true`) over doctest/CommonMark/reST blocks .

## Sources
- https://docs.astral.sh/ruff/formatter/
- https://docs.astral.sh/ruff/faq/
- https://docs.astral.sh/ruff/settings/
