# Error Suppression

[[concepts/linter|Linter]] violations can be suppressed at the line level, the file level, or removed automatically. The suppression syntax mirrors Flake8's ([[sources/linter]]).

## Line-level `# noqa`

A trailing `# noqa` comment suppresses violations on that line ([[sources/linter]]; [[sources/tutorial]]):
```python
x = 1  # noqa: F841
i = 1  # noqa: E741, F841
x = 1  # noqa
```
A bare `# noqa` suppresses all codes on the line; a coded form like `# noqa: F841` suppresses only the listed codes ([[sources/linter]]). The tutorial shows the same pattern, e.g. `from typing import Iterable  # noqa: UP035` ([[sources/tutorial]]).

## File-level suppression

File-level comments must be on their own line ([[sources/linter]]):
```python
# ruff: noqa
# ruff: noqa: F841
```
The tutorial shows `# ruff: noqa: UP035` placed above an import to suppress a code for the whole file ([[sources/tutorial]]). Ruff also respects Flake8's `# flake8: noqa` ([[sources/linter]]).

## Detecting and adding suppressions

- **`RUF100` (`unused-noqa`)** flags suppression comments that don't actually suppress anything; it can be combined with `--fix` to remove them ([[sources/linter]]).
- `ruff check /path/to/file.py --add-noqa` adds suppression comments automatically ([[sources/linter]]). The tutorial demonstrates targeting a specific rule when bulk-adding noqa to an existing codebase: `ruff check --select UP035 --add-noqa .` ([[sources/tutorial]]).

## isort action comments

For import-sorting (`I`) behavior, Ruff recognizes isort action comments: `# isort: skip_file`, `# isort: on` / `# isort: off`, `# isort: skip`, and `# isort: split` ([[sources/linter]]). Import sorting itself is described in [[concepts/import-sorting]].

## Open questions

- None; the suppression syntax is fully specified by the linter reference and corroborated by the tutorial ([[sources/linter]]; [[sources/tutorial]]).
