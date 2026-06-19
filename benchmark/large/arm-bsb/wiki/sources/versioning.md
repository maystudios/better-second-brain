# Source: Ruff Versioning Policy

- **Citation / URL:** https://docs.astral.sh/ruff/versioning/
- **Raw file:** `benchmark/large/raw/versioning.md`
- **Type:** Official documentation - versioning policy

## Key claims

- "Ruff uses a custom versioning scheme that uses the minor version number for breaking changes and the patch version number for bug fixes." The project lacks a stable API; once stability is achieved, standard SemVer will apply.
- **Breaking changes (minor version bumps):** deprecated option/feature removal; backwards-incompatible configuration changes (may occur pre-1.0.0); new file type promotion to stable; end-of-life Python version support drops; linter rule promotion to stable, stable-rule behavior modifications, adding/removing stable rules from defaults, safe-fix promotions to stable, rule deprecations; formatter stable-style modifications; language-server capability removal or deprecated-setting removal.
- **Non-breaking changes (patch version bumps):** bug fixes (including behavioral corrections); backwards-compatible config additions; new Python version support; new preview file-type support; feature/option deprecations; linter unsafe fixes, preview safe fixes, preview scope expansions, preview rule additions/behavior changes; formatter style changes preventing invalid syntax/semantics/comment loss plus preview style changes; language-server new capabilities/settings and setting deprecations.
- **Rule and fix stabilization:** new rules launch in preview mode and require "at least one minor release before being promoted to stable." Fix applicability progresses through Display → Unsafe → Safe levels.
- **Pre-1.0.0 status:** `0.x` versioning indicates an unstable API with breaking changes distributed across minor versions rather than major versions.
- **VS Code extension versioning:** even minor versions denote stable releases; odd numbers indicate preview releases.

## Notable quotes

> "Ruff uses a custom versioning scheme that uses the minor version number for breaking changes and the patch version number for bug fixes."

## Prose summary

Ruff deliberately diverges from SemVer while pre-1.0: minor bumps carry breaking changes, patch bumps carry bug fixes. The page exhaustively classifies what counts as breaking (e.g., promoting a rule to stable, changing a stable rule's behavior, dropping EOL Python support) versus non-breaking (bug fixes, additive config, preview-only changes, unsafe fixes). It ties into the preview lifecycle: rules start in preview and need at least one minor release before stabilizing, and fixes climb the Display→Unsafe→Safe applicability ladder. It also notes the separate VS Code extension convention where even/odd minor versions distinguish stable from preview releases.
