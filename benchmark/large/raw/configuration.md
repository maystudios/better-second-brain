# Ruff Configuration

Source: https://docs.astral.sh/ruff/configuration/

## Configuration Files

- `pyproject.toml` - uses `[tool.ruff]` section header
- `ruff.toml` - omits `[tool.ruff]` prefix
- `.ruff.toml` - omits `[tool.ruff]` prefix

Precedence in same directory: `.ruff.toml` > `ruff.toml` > `pyproject.toml`

## Default Configuration

Root settings:
- `line-length = 88` (matches Black)
- `indent-width = 4`
- `target-version = "py310"`
- `exclude` list covering `.git`, `.venv`, `__pycache__`, `build`, `dist`, etc.

Lint `[tool.ruff.lint]`:
- `select = ["E4", "E7", "E9", "F"]`
- `ignore = []`
- `fixable = ["ALL"]`
- `unfixable = []`
- `dummy-variable-rgx = "^(_+|(_+[a-zA-Z0-9_]*[a-zA-Z0-9]+?))$"`

Format `[tool.ruff.format]`:
- `quote-style = "double"`
- `indent-style = "space"`
- `skip-magic-trailing-comma = false`
- `line-ending = "auto"`
- `docstring-code-format = false`
- `docstring-code-line-length = "dynamic"`

## Hierarchical Configuration

Closest-configuration-first approach (similar to ESLint). The closest config file applies to each file. Unlike ESLint, Ruff does NOT merge settings across config files.

- `pyproject.toml` files without `[tool.ruff]` are ignored
- `--config` with a direct file path applies to all analyzed files
- If no config found, Ruff checks `${config_dir}/ruff/pyproject.toml` (user-level)
- CLI arguments override all configuration files

## Configuration Inheritance with `extend`

```toml
[tool.ruff]
extend = "../pyproject.toml"
line-length = 100
```

## Python Version Inference

When `target-version` unspecified, Ruff infers from `requires-python` in `pyproject.toml`.

## Python File Discovery

Default inclusions: `*.py`, `*.pyi`, `*.ipynb`, `pyproject.toml`, `*.pyw` (preview only).

Respects `.gitignore`, `.git/info/exclude`, global gitignore (via `respect-gitignore`). Files passed directly bypass exclusions unless `force-exclude` enabled. Use `extend-include` / `include`.

```toml
[tool.ruff]
include = ["pyproject.toml", "src/**/*.py", "scripts/**/*.py"]
```
Warning: paths in `include` must match files, not directories.

Tool-specific exclusions:
```toml
[tool.ruff.format]
exclude = ["*.pyi"]
```

## Jupyter Notebook Handling

By default Ruff lints and formats Jupyter Notebooks (v0.6.0+). Per-file ignores:
```toml
[tool.ruff.lint.per-file-ignores]
"*.ipynb" = ["T20"]
```
E402 detects imports at cell top in notebooks, not file top.

## CLI --config Flag

```bash
ruff check path/to/directory --config path/to/ruff.toml
ruff check path/to/file --config "lint.dummy-variable-rgx = '__.*'"
```
Dedicated flags (e.g., `--line-length`) override `--config`.
```bash
ruff format path/to/file --line-length=90 --config "line-length=100"
# Result: line-length = 90
```

## Top-Level Commands

check, rule, config, linter, clean, format, server, analyze, version, help

## Key CLI Options

Rule selection: `--select`, `--ignore`, `--extend-select`, `--per-file-ignores`, `--fixable`/`--unfixable`
File selection: `--exclude`, `--extend-exclude`, `--respect-gitignore`, `--force-exclude`
Linting: `--fix`, `--unsafe-fixes`, `--show-fixes`, `--diff`, `--statistics`
Formatting: `--check`, `--diff`
Other: `--target-version`, `--preview`, `--isolated`, `--output-format` (json, junit, github, etc.)

## Shell Autocompletion

`ruff generate-shell-completion bash|zsh|fish|elvish|powershell`
