---
type: concept
title: Configuration
---

How Ruff is configured through TOML files, hierarchical discovery, inheritance, and CLI overrides.

- Config in `pyproject.toml` (`[tool.ruff]`), `ruff.toml`, or `.ruff.toml`; same-dir precedence `.ruff.toml` > `ruff.toml` > `pyproject.toml` .
- Discovery walks from the target file's directory upward through parents .
- Hierarchical, closest-config-first (ESLint-like) but does NOT merge across files; CLI args override all config .
- `extend` inherits another config; `target-version` inferred from `requires-python` when unset .
- `ruff.toml` shares pyproject's schema; no INI support; user-level defaults under `~/.config/ruff/` or AppData .

## Sources
- https://docs.astral.sh/ruff/configuration/
- https://docs.astral.sh/ruff/tutorial/
- https://docs.astral.sh/ruff/faq/
