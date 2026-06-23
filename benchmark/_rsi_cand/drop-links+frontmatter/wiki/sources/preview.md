---
type: source
title: "Ruff Preview Mode"
url: https://docs.astral.sh/ruff/preview/
---

## Key claims
- Preview mode opt-in enables unstable features: new lint rules/fixes, formatter style changes, interface updates, for community feedback pre-release.
- Enable via `--preview` CLI flag or `[tool.ruff.lint]`/`[tool.ruff.format]` `preview=true`; configurable independently for lint vs format.
- Preview rules require preview mode active; not enabled by `extend-select`/`select=["ALL"]` alone unless preview is on.
- `explicit-preview-rules=true` requires each preview rule be named individually (e.g. `--select ALL,HYP001`).
- When preview mode is enabled, deprecated rules are disabled; explicitly selecting a deprecated rule raises an error.
