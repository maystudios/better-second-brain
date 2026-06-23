---
type: concept
title: Configuration
---

How Ruff is configured through TOML files, hierarchical discovery, inheritance, and CLI overrides.

- Config in `pyproject.toml` (`[tool.ruff]`), `ruff.toml`, or `.ruff.toml`; same-dir precedence `.ruff.toml` > `ruff.toml` > `pyproject.toml` ([[sources/configuration]], [[sources/tutorial]]).
- Discovery walks from the target file's directory upward through parents ([[sources/tutorial]], [[sources/configuration]]).
- Hierarchical, closest-config-first (ESLint-like) but does NOT merge across files; CLI args override all config ([[sources/configuration]]).
- `extend` inherits another config; `target-version` inferred from `requires-python` when unset ([[sources/configuration]], [[sources/tutorial]]).
- `ruff.toml` shares pyproject's schema; no INI support; user-level defaults under `~/.config/ruff/` or AppData ([[sources/faq]], [[sources/configuration]]).
