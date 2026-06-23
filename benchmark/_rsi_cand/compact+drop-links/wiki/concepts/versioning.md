---
type: concept
title: Versioning Policy
---

Ruff's pre-1.0 custom versioning scheme governing how breaking and non-breaking changes are released.

- Minor version = breaking changes, patch version = bug fixes; diverges from SemVer until a stable API at 1.0.0 .
- Breaking changes (minor): option removal, incompatible config, rule promotions/default changes, stable formatter style changes, EOL Python drops .
- Non-breaking (patch): bug fixes, new Python support, unsafe/preview fixes, preview rules, new LSP capabilities .
- New rules launch in preview and need ≥1 minor release before stable promotion .
- VS Code extension: even minor = stable, odd = preview .

## Sources
- https://docs.astral.sh/ruff/versioning/
- https://docs.astral.sh/ruff/preview/
- https://docs.astral.sh/ruff/editors/setup/
