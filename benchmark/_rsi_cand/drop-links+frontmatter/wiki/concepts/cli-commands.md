---
type: concept
title: CLI Commands & Exit Codes
---

Ruff's command-line surface, key flags, and process exit semantics.

- Top-level commands: check, rule, config, linter, clean, format, server, analyze, version, help ([[sources/configuration]]).
- `ruff check` and `ruff format` accept path args; `--config` takes a file or inline key=value, overridden by dedicated flags ([[sources/configuration]], [[sources/linter]]).
- Linter exit codes: 0 clean/fixed, 1 violations, 2 abnormal; `--exit-zero`, `--exit-non-zero-on-fix` ([[sources/linter]]).
- Formatter exit codes: `--check` returns 1 if files would change, 2 on abnormal termination ([[sources/formatter]]).
- `--output-format` supports json, junit, github, gitlab, etc.; shell completion via `generate-shell-completion` ([[sources/configuration]], [[sources/integrations]]).
