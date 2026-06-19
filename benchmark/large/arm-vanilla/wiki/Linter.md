# Linter

The linter is the `ruff check` half of [[Ruff]]. It scans Python files for problems - unused imports, undefined names, style violations, likely bugs - and can fix many of them automatically. It's designed as a drop-in Flake8 replacement that also absorbs dozens of Flake8 plugins.

## The command

```bash
ruff check                 # Lint files in the current directory
ruff check --fix           # Lint and fix fixable errors
ruff check --watch         # Re-lint on file changes
ruff check path/to/code/   # Lint a specific directory
```

## Selecting rules

Which rules run is controlled by a handful of [[Configuration|config]] keys:

- `lint.select` - enable specific rules
- `lint.extend-select` - add rules to an inherited set
- `lint.ignore` - disable specific rules
- `lint.extend-ignore` - remove rules from an inherited set
- `lint.per-file-ignores` - ignore rules for files matching a pattern

Rule codes follow Flake8's convention: a one-to-three letter prefix plus three digits, like `F401` (Pyflakes) or `UP032` (pyupgrade). The full prefix-to-plugin map is in [[Rules]].

```toml
[tool.ruff.lint]
select = ["E", "F"]
ignore = ["F401"]
```

A reasonable starting baseline:

```toml
[tool.ruff.lint]
select = ["E", "F", "UP", "B", "SIM", "I"]
```

`ALL` enables every rule at once (Ruff auto-disables conflicting ones like `D203`/`D211`). Precedence runs CLI > `pyproject.toml` > inherited config files.

## Fixes and fix safety

```bash
ruff check --fix
```

By default Ruff applies all **safe** fixes - ones that preserve runtime behavior and only remove comments when deleting an entire statement. **Unsafe** fixes may change behavior, remove comments, or alter exceptions. For example, `RUF015` rewriting `list(...)[0]` to `next(iter(...))` is unsafe because it changes an `IndexError` into a `StopIteration`.

```bash
ruff check --unsafe-fixes          # Display unsafe fixes
ruff check --fix --unsafe-fixes    # Apply them
```

You can reclassify safety per rule, or restrict which rules are fixable:

```toml
[tool.ruff.lint]
extend-safe-fixes = ["F601"]
extend-unsafe-fixes = ["UP034"]
fixable = ["ALL"]
unfixable = ["F401"]
```

## Suppressing violations

Line-level:

```python
x = 1  # noqa: F841
i = 1  # noqa: E741, F841
x = 1  # noqa
```

File-level (must be on its own line; Flake8's `# flake8: noqa` is also respected):

```python
# ruff: noqa
# ruff: noqa: F841
```

The `RUF100` rule (`unused-noqa`) flags suppressions that no longer suppress anything - useful for keeping `noqa` comments honest:

```bash
ruff check /path/to/file.py --extend-select RUF100 --fix
```

You can also bulk-add suppressions with `--add-noqa`. Ruff additionally honors isort action comments like `# isort: skip` and `# isort: off`/`# isort: on`.

## Exit codes

- `0` - no violations, or all violations fixed
- `1` - violations found
- `2` - abnormal termination (bad config, bad CLI, internal error)

Modifiers: `--exit-zero` always returns `0` (except on abnormal termination), and `--exit-non-zero-on-fix` returns `1` even when everything was fixed - handy for CI gates.

## See also

- [[Formatter]] - the companion `ruff format` command (note: the formatter does **not** sort imports)
- [[Rules]] - the catalog of what the linter can check
- [[Tutorial]] - a worked example of fixing and suppressing
