# Configuration

[[Ruff]] is configured from a single TOML file shared by both the [[Linter]] and the [[Formatter]]. There is no INI support.

## Config files and precedence

Three filenames are recognized:

- `pyproject.toml` — settings under a `[tool.ruff]` header
- `ruff.toml` — same schema, no `[tool.ruff]` prefix
- `.ruff.toml` — same schema, no prefix

When several sit in one directory, precedence is `.ruff.toml` > `ruff.toml` > `pyproject.toml`. If no config is found, Ruff falls back to a user-level file (`~/.config/ruff/ruff.toml` on Linux/macOS, `~\AppData\Roaming\ruff\ruff.toml` on Windows). CLI arguments override everything.

## Default settings

Top-level:

| Setting | Default |
|---------|---------|
| `line-length` | `88` (matches Black) |
| `indent-width` | `4` |
| `target-version` | `"py310"` |
| `respect-gitignore` | `true` |

The default `exclude` list covers the usual suspects: `.git`, `.venv`, `__pycache__`, `.mypy_cache`, `.ruff_cache`, `build`, `dist`, `node_modules`, and more.

Lint `[tool.ruff.lint]`:

```toml
select = ["E4", "E7", "E9", "F"]
ignore = []
fixable = ["ALL"]
unfixable = []
dummy-variable-rgx = "^(_+|(_+[a-zA-Z0-9_]*[a-zA-Z0-9]+?))$"
```

Format `[tool.ruff.format]`:

```toml
quote-style = "double"
indent-style = "space"
line-ending = "auto"           # auto, lf, cr-lf, native
skip-magic-trailing-comma = false
docstring-code-format = false
docstring-code-line-length = "dynamic"
```

(PEP 8's 4-space indent and PEP 257's double-quote preference are the reasons behind these defaults. The cache lives in `.ruff_cache`.)

## Hierarchical configuration

Ruff uses a **closest-configuration-first** approach, similar to ESLint: the nearest config file applies to each file. Unlike ESLint, Ruff does **not** merge settings across files — the closest one wins outright. A `pyproject.toml` without a `[tool.ruff]` section is simply ignored. This is what makes Ruff monorepo-friendly.

To share a base explicitly, use `extend`:

```toml
[tool.ruff]
extend = "../pyproject.toml"
line-length = 100
```

## Python version and file discovery

If `target-version` is unset, Ruff infers it from `requires-python` in `pyproject.toml`. By default it discovers `*.py`, `*.pyi`, `*.ipynb`, `pyproject.toml`, and (in preview) `*.pyw`, while respecting `.gitignore`, `.git/info/exclude`, and global gitignore. Files passed directly bypass exclusions unless `force-exclude` is set. Note that paths in `include` must match files, not directories:

```toml
[tool.ruff]
include = ["pyproject.toml", "src/**/*.py", "scripts/**/*.py"]
```

## Jupyter notebooks

Since v0.6.0 Ruff lints and formats notebooks by default. `E402` (import placement) is measured per-cell rather than per-file. Per-file ignores work as usual:

```toml
[tool.ruff.lint.per-file-ignores]
"*.ipynb" = ["T20"]
```

## The `--config` flag

You can point at a file or pass an inline override:

```bash
ruff check path/to/directory --config path/to/ruff.toml
ruff check path/to/file --config "lint.dummy-variable-rgx = '__.*'"
```

Dedicated flags win over `--config`:

```bash
ruff format path/to/file --line-length=90 --config "line-length=100"
# Result: line-length = 90
```

## Top-level commands and key options

The CLI exposes `check`, `format`, `rule`, `config`, `linter`, `clean`, `server`, `analyze`, `version`, and `help`. Common options include rule selection (`--select`, `--ignore`, `--extend-select`, `--per-file-ignores`), file selection (`--exclude`, `--force-exclude`, `--respect-gitignore`), linting (`--fix`, `--unsafe-fixes`, `--show-fixes`, `--diff`, `--statistics`), and output (`--output-format` for json, junit, github, etc.). Shell completion is generated with `ruff generate-shell-completion bash|zsh|fish|elvish|powershell`.

## See also

- [[Linter]] and [[Formatter]] — the commands these settings control
- [[Rules]] — what `select`/`ignore` refer to
- [[Preview]] — the `preview` flag and how unstable features are gated
