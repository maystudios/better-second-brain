---
type: concept
title: Error Suppression
---

Mechanisms for silencing specific lint violations or disabling formatting on selected code.

- Line-level `# noqa` or `# noqa: CODE`; file-level `# ruff: noqa[: CODE]` on its own line ([[sources/linter]], [[sources/tutorial]]).
- Respects Flake8's `# flake8: noqa`; `RUF100` flags noqa comments that suppress nothing ([[sources/linter]]).
- Bulk-add suppressions via `--add-noqa` (optionally scoped with `--select`) ([[sources/linter]], [[sources/tutorial]]).
- Formatter suppression: `# fmt: off`/`on`/`skip` plus YAPF directives ([[sources/formatter]]).
- isort action comments (`# isort: skip_file`, `on`/`off`, `skip`, `split`) control import sorting ([[sources/linter]]).
