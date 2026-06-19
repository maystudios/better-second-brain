---
type: concept
title: Versioning Policy
---

Ruff's pre-1.0 custom versioning scheme governing how breaking and non-breaking changes are released.

- Minor version = breaking changes, patch version = bug fixes; diverges from SemVer until a stable API at 1.0.0 ([[sources/versioning]]).
- Breaking changes (minor): option removal, incompatible config, rule promotions/default changes, stable formatter style changes, EOL Python drops ([[sources/versioning]]).
- Non-breaking (patch): bug fixes, new Python support, unsafe/preview fixes, preview rules, new LSP capabilities ([[sources/versioning]]).
- New rules launch in preview and need ≥1 minor release before stable promotion ([[sources/versioning]], [[sources/preview]]).
- VS Code extension: even minor = stable, odd = preview ([[sources/versioning]], [[sources/editors-setup]]).

## Links
[[concepts/preview-mode]] · [[concepts/fix-safety]] · [[concepts/editor-integration]] · [[sources/versioning]] · [[sources/preview]] · [[sources/editors-setup]]
