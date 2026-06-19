# Versioning

[[Ruff]] uses a **custom versioning scheme** that diverges from semantic versioning: the minor version number carries breaking changes, and the patch number carries bug fixes. The project has no stable public API yet; once it reaches stability, standard SemVer will take over. The current `0.x` line signals that breaking changes are spread across minor releases rather than major ones.

## What counts as a breaking change (minor bump)

- Removing a deprecated option or feature
- Backwards-incompatible configuration changes (allowed pre-1.0.0)
- Promoting a new file type to stable
- Dropping support for an end-of-life Python version
- **[[Linter]]:** promoting a rule to stable, changing a stable rule's behavior, adding/removing stable rules from the defaults, promoting a safe fix to stable, or deprecating a rule
- **[[Formatter]]:** modifying the stable style
- **[[Editors|Language server]]:** removing a capability or a deprecated setting

## What counts as non-breaking (patch bump)

- Bug fixes, including behavioral corrections
- Backwards-compatible configuration additions
- Supporting a new Python version
- New [[Preview|preview]] file-type support
- Feature/option deprecations
- **Linter:** unsafe fixes, preview safe fixes, preview scope expansions, preview rule additions or changes
- **Formatter:** style changes that prevent invalid syntax/semantics/comment loss, and preview style changes
- **Language server:** new capabilities, new settings, setting deprecations

## How rules and fixes graduate

New rules launch in [[Preview|preview mode]] and must spend **at least one minor release** there before being promoted to stable. Fix applicability climbs through three levels: **Display → Unsafe → Safe** (see fix safety in the [[Linter]] page).

## VS Code extension versioning

The [[Editors|VS Code extension]] uses its own convention: even minor versions are stable releases, odd minor versions are previews.

## See also

- [[Preview]] - the channel where features start
- [[Integrations]] - pinning versions in CI and Docker
