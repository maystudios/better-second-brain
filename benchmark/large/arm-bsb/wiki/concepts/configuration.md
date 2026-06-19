# Configuration

[[concepts/ruff]] is configured through TOML files, with a hierarchical discovery model. This page covers config files, discovery, defaults, and CLI overrides. Rule-specific selection lives in [[concepts/rules-and-rule-codes]]; the default values themselves are tabulated in [[concepts/default-settings]].

## Configuration files

Ruff reads configuration from three file types ([[sources/configuration]]; [[sources/github-astral-sh-ruff]]; [[sources/tutorial]]):
- `pyproject.toml`, using the `[tool.ruff]` section header ([[sources/configuration]]).
- `ruff.toml`, which omits the `[tool.ruff]` prefix ([[sources/configuration]]; [[sources/tutorial]]).
- `.ruff.toml`, which also omits the prefix ([[sources/configuration]]).

When more than one exists in the **same directory**, precedence is `.ruff.toml` > `ruff.toml` > `pyproject.toml` ([[sources/configuration]]). The FAQ confirms `ruff.toml` is a drop-in alternative to `pyproject.toml` with an identical schema, and that there is **no INI file support** ([[sources/faq]]).

## Discovery and hierarchy

Ruff searches for configuration starting from the target file's directory and moving up through parent directories ([[sources/tutorial]]). It uses a "closest-configuration-first" approach similar to ESLint, where the closest config file applies to each file - but **unlike ESLint, Ruff does NOT merge settings across config files** ([[sources/configuration]]). This hierarchical model is what makes Ruff "monorepo-friendly" ([[sources/ruff-overview]]; [[sources/github-astral-sh-ruff]]).

Additional discovery rules ([[sources/configuration]]):
- `pyproject.toml` files without a `[tool.ruff]` section are ignored.
- `--config` with a direct file path applies to all analyzed files.
- If no config is found, Ruff checks a user-level `${config_dir}/ruff/pyproject.toml`.

The FAQ gives concrete user-level config locations: `~/.config/ruff/ruff.toml` on Linux/macOS and `~\AppData\Roaming\ruff\ruff.toml` on Windows ([[sources/faq]]).

## Inheritance with `extend`

A config can inherit from another via `extend`, then override specific keys ([[sources/configuration]]):
```toml
[tool.ruff]
extend = "../pyproject.toml"
line-length = 100
```

## Python version inference

When `target-version` is unspecified, Ruff infers it from `requires-python` in `pyproject.toml` ([[sources/configuration]]). See [[concepts/python-version-support]].

## File discovery and exclusions

Default inclusions are `*.py`, `*.pyi`, `*.ipynb`, `pyproject.toml`, and `*.pyw` (preview only) ([[sources/configuration]]). Ruff respects `.gitignore`, `.git/info/exclude`, and the global gitignore via `respect-gitignore` ([[sources/configuration]]), which defaults to `true` ([[sources/settings]]). Files passed directly bypass exclusions unless `force-exclude` is enabled ([[sources/configuration]]). The `include` setting must match files, not directories ([[sources/configuration]]). Tool-specific exclusions are possible, e.g. `[tool.ruff.format] exclude = ["*.pyi"]` ([[sources/configuration]]).

## Jupyter notebooks

By default Ruff lints and formats Jupyter Notebooks (v0.6.0+) ([[sources/configuration]]), with built-in support and nbQA integration noted in the FAQ ([[sources/faq]]). Per-file ignores use `[tool.ruff.lint.per-file-ignores] "*.ipynb" = ["T20"]` ([[sources/configuration]]). Notably, E402 detects imports at the top of a **cell** in notebooks, not the top of the file ([[sources/configuration]]).

## CLI overrides

**CLI arguments override all configuration files** ([[sources/configuration]]); the linter reference restates this as CLI > `pyproject.toml` > inherited config files ([[sources/linter]]). The `--config` flag accepts either a file path or an inline TOML string, e.g. `--config "lint.dummy-variable-rgx = '__.*'"` ([[sources/configuration]]). Dedicated flags outrank `--config`: combining `--line-length=90 --config "line-length=100"` resolves to 90 ([[sources/configuration]]).

The ten top-level commands are `check`, `rule`, `config`, `linter`, `clean`, `format`, `server`, `analyze`, `version`, and `help` ([[sources/configuration]]). Shell autocompletion is generated via `ruff generate-shell-completion bash|zsh|fish|elvish|powershell` ([[sources/configuration]]).

## Open questions

- The user-level fallback path is described two ways: `${config_dir}/ruff/pyproject.toml` ([[sources/configuration]]) versus `~/.config/ruff/ruff.toml` / `~\AppData\Roaming\ruff\ruff.toml` ([[sources/faq]]). The sources do not reconcile whether the user-level file is named `pyproject.toml` or `ruff.toml`.
