---
type: source
title: "Ruff Formatter"
url: https://docs.astral.sh/ruff/formatter/
---

## Key claims
- `ruff format` formats dirs/files; `--check` verifies without writing (non-zero if unformatted).
- Targets Black drop-in compatibility: ">99.9% of lines formatted identically" on projects like Django and Zulip; adheres to Black stable style.
- Known deviations: formats expressions inside f-string `{...}` (Black does not); alternates quotes in nested f-strings; method-chain layout (preview).
- Defaults: line-length 88, `quote-style="double"`, spaces indent width 4, magic trailing comma respected.
- Docstring code formatting via `docstring-code-format=true` (doctest, CommonMark fences, reST blocks); `docstring-code-line-length` default `"dynamic"`; invalid code skipped.
- Suppression `# fmt: off/on/skip` (and YAPF directives); markdown code formatting in preview; does NOT sort imports (use `ruff check --select I --fix`); warns on lint rules conflicting with the formatter.
