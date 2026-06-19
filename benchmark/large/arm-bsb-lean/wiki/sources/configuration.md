---
type: source
title: "Ruff Configuration"
url: https://docs.astral.sh/ruff/configuration/
kind: official-docs
---

## Key claims
- Config files: `pyproject.toml` (`[tool.ruff]` header), `ruff.toml`, `.ruff.toml`; same-dir precedence `.ruff.toml` > `ruff.toml` > `pyproject.toml`.
- Hierarchical, closest-config-first (ESLint-like) but does NOT merge settings across files; CLI args override all config.
- `extend` inherits another config file; `target-version` inferred from `requires-python` when unspecified.
- File discovery: `*.py`, `*.pyi`, `*.ipynb`, `pyproject.toml`, `*.pyw` (preview); respects `.gitignore`/global gitignore; `include`/`extend-include`/`force-exclude`.
- Jupyter notebooks linted+formatted by default (v0.6.0+); `E402` checks cell-top in notebooks not file-top.
- `--config` takes a file path or inline key=value; dedicated flags (e.g. `--line-length`) override `--config`; top-level commands include check, rule, config, linter, clean, format, server, analyze, version, help.
