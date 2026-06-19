# Source: The Ruff Linter

- **Citation / URL:** https://docs.astral.sh/ruff/linter/ (includes #rule-selection)
- **Raw file:** `benchmark/large/raw/linter.md`
- **Type:** Official documentation - linter reference

## Key claims

### `ruff check` command
```bash
ruff check                    # Lint files in the current directory
ruff check --fix              # Lint and fix fixable errors
ruff check --watch            # Re-lint on file changes
ruff check path/to/code/      # Lint a specific directory
```

### Rule selection
- `lint.select`, `lint.extend-select`, `lint.ignore`, `lint.extend-ignore`, `lint.per-file-ignores`.
- **Rule code format:** Ruff mirrors Flake8 - a one-to-three-letter prefix plus three digits (e.g., `F401`). Examples: `F`=Pyflakes, `E`=pycodestyle, `ANN`=flake8-annotations, `UP`=pyupgrade, `B`=flake8-bugbear, `SIM`=flake8-simplify, `I`=isort.
- **`ALL`** enables all rules; Ruff auto-disables conflicting rules (like `D203`/`D211`).
- **Precedence:** CLI options override `pyproject.toml`, which overrides inherited config files.
- Recommended baseline: `select = ["E", "F", "UP", "B", "SIM", "I"]`.

### Fixes
- `ruff check --fix`. By default, Ruff applies all "safe" fixes.
- **Safe fixes:** preserve runtime behavior; only remove comments when deleting entire statements.
- **Unsafe fixes:** may change runtime behavior, remove comments, or alter exceptions. Example: `RUF015` replacing `list(...)[0]` with `next(iter(...))` is unsafe (IndexError → StopIteration).
- Display/apply unsafe fixes: `--unsafe-fixes`, `--fix --unsafe-fixes`, or `[tool.ruff] unsafe-fixes = true`.
- Adjust fix safety per rule: `extend-safe-fixes = ["F601"]`, `extend-unsafe-fixes = ["UP034"]`.
- Disable fixes: `fixable = ["ALL"]` with `unfixable = ["F401"]`.

### Error suppression
- Line-level `# noqa`: `# noqa: F841`, multiple codes `# noqa: E741, F841`, or bare `# noqa` (all codes).
- File-level: `# ruff: noqa` or `# ruff: noqa: F841` - must be on their own line. Ruff respects Flake8's `# flake8: noqa`.
- **`RUF100` (`unused-noqa`)** flags suppressions that don't suppress anything; usable with `--fix`.
- `--add-noqa` adds suppression comments.
- **isort action comments:** `# isort: skip_file`, `# isort: on` / `# isort: off`, `# isort: skip`, `# isort: split`.

### Exit codes
- `0`: no violations found, or all violations fixed.
- `1`: violations found.
- `2`: abnormal termination (invalid config/CLI or internal error).
- Modifiers: `--exit-zero` (always exit 0 except abnormal termination); `--exit-non-zero-on-fix` (exit 1 even if all violations fixed).

## Notable quotes

> Safe fixes "preserve runtime behavior; only remove comments when deleting entire statements."

## Prose summary

The linter reference governs `ruff check`. It explains the Flake8-style rule-code grammar, the selection/ignore knobs (`select`, `extend-select`, `ignore`, `extend-ignore`, `per-file-ignores`), and the `ALL` meta-selector with its automatic conflict resolution. Its most substantive content is the **fix-safety model**: safe fixes (default) never change runtime behavior, while unsafe fixes can, illustrated by the `RUF015` IndexError→StopIteration example. It also covers suppression mechanics (`# noqa`, file-level `# ruff: noqa`, `RUF100` for detecting dead suppressions) and a precise exit-code contract with its `--exit-zero` / `--exit-non-zero-on-fix` modifiers.
