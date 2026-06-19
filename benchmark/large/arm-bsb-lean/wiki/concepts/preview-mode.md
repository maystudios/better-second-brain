---
type: concept
title: Preview Mode
---

An opt-in channel that enables unstable features for community feedback before stable release.

- Enables new lint rules/fixes, formatter style changes, and interface updates pre-release ([[sources/preview]]).
- Activated by `--preview` or `preview=true`, configurable independently for lint vs format ([[sources/preview]], [[sources/formatter]]).
- Preview rules require preview mode on; not enabled by `extend-select`/`select=["ALL"]` alone ([[sources/preview]], [[sources/rules]]).
- `explicit-preview-rules=true` requires naming each preview rule individually ([[sources/preview]]).
- With preview enabled, deprecated rules are disabled and explicitly selecting one errors ([[sources/preview]]).

## Links
[[concepts/rules-and-plugins]] · [[concepts/formatter]] · [[concepts/versioning]] · [[sources/preview]] · [[sources/rules]] · [[sources/formatter]]
