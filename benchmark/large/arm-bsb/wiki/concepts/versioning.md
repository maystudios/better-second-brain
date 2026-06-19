# Versioning Policy

[[concepts/ruff]] uses a custom versioning scheme that diverges from semantic versioning: "Ruff uses a custom versioning scheme that uses the minor version number for breaking changes and the patch version number for bug fixes" ([[sources/versioning]]). The project lacks a stable API; once stability is achieved, standard SemVer will apply ([[sources/versioning]]).

## Pre-1.0.0 meaning

`0.x` versioning indicates an unstable API, with breaking changes distributed across **minor** versions rather than major versions ([[sources/versioning]]). (As fetched, the latest release was 0.15.18 — see [[concepts/ruff]] and [[sources/github-astral-sh-ruff]].)

## Breaking changes (minor bumps)

Classified as breaking ([[sources/versioning]]): deprecated option/feature removal; backwards-incompatible configuration changes (may occur pre-1.0.0); promoting a new file type to stable; dropping end-of-life Python version support; for the linter — promoting a rule to stable, modifying a stable rule's behavior, adding/removing stable rules from defaults, promoting safe fixes to stable, and rule deprecations; for the formatter — stable style modifications; for the language server — capability removal or deprecated-setting removal.

Note that "adding/removing stable rules from defaults" being breaking is why the [[concepts/default-settings]] can shift between minor versions.

## Non-breaking changes (patch bumps)

Classified as non-breaking ([[sources/versioning]]): bug fixes (including behavioral corrections); backwards-compatible config additions; new Python version support; new preview file-type support; feature/option deprecations; for the linter — unsafe fixes, preview safe fixes, preview scope expansions, and preview rule additions/behavior changes; for the formatter — style changes that prevent invalid syntax/semantics/comment loss, plus preview style changes; for the language server — new capabilities, new settings, and setting deprecations.

## Rule and fix stabilization

New rules launch in [[concepts/preview-mode]] and require "at least one minor release before being promoted to stable" ([[sources/versioning]]). Fix applicability progresses through **Display → Unsafe → Safe** levels ([[sources/versioning]]) — the foundation of the [[concepts/fix-safety]] model.

## VS Code extension versioning

The VS Code extension uses a separate convention: even minor versions denote stable releases and odd numbers indicate preview releases ([[sources/versioning]]). See [[concepts/editor-integration]].

## Open questions

- The policy notes that backwards-incompatible configuration changes "may occur pre-1.0.0" ([[sources/versioning]]) but does not enumerate which config keys are at risk.
