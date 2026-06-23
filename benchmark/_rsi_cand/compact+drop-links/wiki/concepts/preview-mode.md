---
type: concept
title: Preview Mode
---

An opt-in channel that enables unstable features for community feedback before stable release.

- Enables new lint rules/fixes, formatter style changes, and interface updates pre-release .
- Activated by `--preview` or `preview=true`, configurable independently for lint vs format .
- Preview rules require preview mode on; not enabled by `extend-select`/`select=["ALL"]` alone .
- `explicit-preview-rules=true` requires naming each preview rule individually .
- With preview enabled, deprecated rules are disabled and explicitly selecting one errors .

## Sources
- https://docs.astral.sh/ruff/preview/
- https://docs.astral.sh/ruff/formatter/
- https://docs.astral.sh/ruff/rules/
