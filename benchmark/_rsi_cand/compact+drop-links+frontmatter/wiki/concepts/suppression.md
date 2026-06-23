---
type: concept
title: Error Suppression
---

Mechanisms for silencing specific lint violations or disabling formatting on selected code.

- Line-level `# noqa` or `# noqa: CODE`; file-level `# ruff: noqa[: CODE]` on its own line .
- Respects Flake8's `# flake8: noqa`; `RUF100` flags noqa comments that suppress nothing .
- Bulk-add suppressions via `--add-noqa` (optionally scoped with `--select`) .
- Formatter suppression: `# fmt: off`/`on`/`skip` plus YAPF directives .
- isort action comments (`# isort: skip_file`, `on`/`off`, `skip`, `split`) control import sorting .

## Sources
- https://docs.astral.sh/ruff/linter/
- https://docs.astral.sh/ruff/tutorial/
- https://docs.astral.sh/ruff/formatter/
