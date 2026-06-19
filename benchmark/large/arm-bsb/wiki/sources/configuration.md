# Source: Ruff Configuration

- **Citation / URL:** https://docs.astral.sh/ruff/configuration/
- **Raw file:** `benchmark/large/raw/configuration.md`
- **Type:** Official documentation — configuration reference

## Key claims

### Configuration files
- `pyproject.toml` uses the `[tool.ruff]` section header.
- `ruff.toml` and `.ruff.toml` omit the `[tool.ruff]` prefix.
- **Precedence in the same directory:** `.ruff.toml` > `ruff.toml` > `pyproject.toml`.

### Default configuration
- Root: `line-length = 88` (matches Black), `indent-width = 4`, `target-version = "py310"`, plus an `exclude` list covering `.git`, `.venv`, `__pycache__`, `build`, `dist`, etc.
- Lint `[tool.ruff.lint]`: `select = ["E4", "E7", "E9", "F"]`, `ignore = []`, `fixable = ["ALL"]`, `unfixable = []`, `dummy-variable-rgx = "^(_+|(_+[a-zA-Z0-9_]*[a-zA-Z0-9]+?))$"`.
- Format `[tool.ruff.format]`: `quote-style = "double"`, `indent-style = "space"`, `skip-magic-trailing-comma = false`, `line-ending = "auto"`, `docstring-code-format = false`, `docstring-code-line-length = "dynamic"`.

### Hierarchical configuration
- "Closest-configuration-first" approach (similar to ESLint); the closest config file applies to each file. **Unlike ESLint, Ruff does NOT merge settings across config files.**
- `pyproject.toml` files without `[tool.ruff]` are ignored.
- `--config` with a direct file path applies to all analyzed files.
- If no config is found, Ruff checks `${config_dir}/ruff/pyproject.toml` (user-level).
- **CLI arguments override all configuration files.**

### Configuration inheritance with `extend`
```toml
[tool.ruff]
extend = "../pyproject.toml"
line-length = 100
```

### Python version inference
- When `target-version` is unspecified, Ruff infers it from `requires-python` in `pyproject.toml`.

### File discovery
- Default inclusions: `*.py`, `*.pyi`, `*.ipynb`, `pyproject.toml`, and `*.pyw` (preview only).
- Respects `.gitignore`, `.git/info/exclude`, and the global gitignore (via `respect-gitignore`). Files passed directly bypass exclusions unless `force-exclude` is enabled. Use `extend-include` / `include`.
- Warning: paths in `include` must match **files, not directories**.
- Tool-specific exclusion example: `[tool.ruff.format] exclude = ["*.pyi"]`.

### Jupyter Notebook handling
- By default Ruff lints and formats Jupyter Notebooks (v0.6.0+). Per-file ignores via `[tool.ruff.lint.per-file-ignores] "*.ipynb" = ["T20"]`.
- E402 detects imports at the top of a **cell** in notebooks, not the top of the file.

### CLI `--config` flag
- `ruff check path/to/directory --config path/to/ruff.toml`.
- Inline TOML override: `--config "lint.dummy-variable-rgx = '__.*'"`.
- Dedicated flags (e.g., `--line-length`) override `--config`. Example: `--line-length=90 --config "line-length=100"` resolves to 90.

### Top-level commands
`check`, `rule`, `config`, `linter`, `clean`, `format`, `server`, `analyze`, `version`, `help`.

### Key CLI options
- Rule selection: `--select`, `--ignore`, `--extend-select`, `--per-file-ignores`, `--fixable`/`--unfixable`.
- File selection: `--exclude`, `--extend-exclude`, `--respect-gitignore`, `--force-exclude`.
- Linting: `--fix`, `--unsafe-fixes`, `--show-fixes`, `--diff`, `--statistics`.
- Formatting: `--check`, `--diff`.
- Other: `--target-version`, `--preview`, `--isolated`, `--output-format` (json, junit, github, etc.).

### Shell autocompletion
`ruff generate-shell-completion bash|zsh|fish|elvish|powershell`.

## Prose summary

This is the densest reference page in the corpus. It defines Ruff's three config-file formats and their same-directory precedence, the full set of root/lint/format defaults, and the hierarchical "closest config wins, no merging" model that distinguishes Ruff from ESLint. It documents config inheritance (`extend`), Python-version inference from `requires-python`, the file-discovery and gitignore-respecting rules, Jupyter notebook behavior (including the cell-scoped E402 nuance), the `--config` precedence ladder (dedicated flags > `--config` > files), the ten top-level commands, and the catalog of CLI options.
