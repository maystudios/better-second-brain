# The Ruff Linter

Source: https://docs.astral.sh/ruff/linter/ (includes #rule-selection)

## ruff check Command

```bash
ruff check                    # Lint files in the current directory
ruff check --fix              # Lint and fix fixable errors
ruff check --watch            # Re-lint on file changes
ruff check path/to/code/      # Lint specific directory
```

## Rule Selection

- `lint.select`: Enable specific rules
- `lint.extend-select`: Add rules to an inherited set
- `lint.ignore`: Disable specific rules
- `lint.extend-ignore`: Remove rules from an inherited set
- `lint.per-file-ignores`: Ignore rules for files matching patterns

### Rule Code Format

Ruff mirrors Flake8: one-to-three letter prefix plus three digits (e.g., `F401`).
- `F` = Pyflakes
- `E` = pycodestyle
- `ANN` = flake8-annotations
- `UP` = pyupgrade
- `B` = flake8-bugbear
- `SIM` = flake8-simplify
- `I` = isort

```toml
[tool.ruff.lint]
select = ["E", "F"]
ignore = ["F401"]
```

### Special Cases

- `ALL` enables all rules; Ruff auto-disables conflicting rules (like `D203`/`D211`).
- Precedence: CLI options override `pyproject.toml`, which overrides inherited config files.

### Recommended Baseline

```toml
[tool.ruff.lint]
select = ["E", "F", "UP", "B", "SIM", "I"]
```

## Fixes

```bash
ruff check --fix
```
By default, Ruff applies all "safe" fixes.

### Fix Safety

- Safe fixes: preserve runtime behavior; only remove comments when deleting entire statements
- Unsafe fixes: may change runtime behavior, remove comments, or alter exceptions
- Example: `RUF015` replacing `list(...)[0]` with `next(iter(...))` is unsafe (IndexError -> StopIteration)

```bash
ruff check --unsafe-fixes          # Display unsafe fixes
ruff check --fix --unsafe-fixes    # Apply unsafe fixes
```
```toml
[tool.ruff]
unsafe-fixes = true
```

### Adjusting Fix Safety Per Rule
```toml
[tool.ruff.lint]
extend-safe-fixes = ["F601"]
extend-unsafe-fixes = ["UP034"]
```

### Disabling Fixes
```toml
[tool.ruff.lint]
fixable = ["ALL"]
unfixable = ["F401"]
```

## Error Suppression

### Line-Level noqa
```python
x = 1  # noqa: F841
i = 1  # noqa: E741, F841
x = 1  # noqa
```

### File-Level
```python
# ruff: noqa
# ruff: noqa: F841
```
File-level comments must be on their own line. Ruff respects Flake8's `# flake8: noqa`.

### Detecting Unused Suppressions
`RUF100` (`unused-noqa`) flags suppressions that don't suppress anything.
```bash
ruff check /path/to/file.py --extend-select RUF100
ruff check /path/to/file.py --extend-select RUF100 --fix
```

### Adding Suppression Comments
```bash
ruff check /path/to/file.py --add-noqa
```

### isort Action Comments
`# isort: skip_file`, `# isort: on` / `# isort: off`, `# isort: skip`, `# isort: split`

## Exit Codes

- `0`: No violations found, or all violations fixed
- `1`: Violations found
- `2`: Abnormal termination (invalid config, invalid CLI, or internal error)

### Modifiers
- `--exit-zero`: Always exit with status `0` (except abnormal termination)
- `--exit-non-zero-on-fix`: Exit with status `1` even if all violations fixed
