---
type: source
title: "Ruff Versioning Policy"
url: https://docs.astral.sh/ruff/versioning/
---

## Key claims
- Custom scheme: minor version = breaking changes, patch version = bug fixes (diverges from SemVer); no stable API until 1.0.0.
- Breaking (minor bump): option removal, incompatible config changes, file-type promotion to stable, EOL Python drops, rule promotion/default changes, stable formatter style changes.
- Non-breaking (patch bump): bug fixes, backwards-compatible config additions, new Python support, unsafe/preview fixes, preview rules, new LSP capabilities.
- New rules launch in preview and need at least one minor release before promotion to stable; fix applicability progresses Display → Unsafe → Safe.
- `0.x` indicates unstable API with breaking changes across minor versions; VS Code extension even minor = stable, odd = preview.
