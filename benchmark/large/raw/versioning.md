# Ruff Versioning Policy

Source: https://docs.astral.sh/ruff/versioning/

## Overview

Ruff uses a custom versioning scheme that diverges from semantic versioning: "Ruff uses a custom versioning scheme that uses the minor version number for breaking changes and the patch version number for bug fixes." The project lacks a stable API; once stability is achieved, standard SemVer will apply.

## Breaking Changes (Minor Version Bumps)

- Deprecated option/feature removal
- Backwards-incompatible configuration changes (may occur pre-1.0.0)
- New file type promotion to stable
- End-of-life Python version support drops
- Linter: rule promotion to stable; stable rule behavior modifications; adding/removing stable rules from defaults; safe fix promotions to stable; rule deprecations
- Formatter: stable style modifications
- Language server: capability removal or deprecated setting removal

## Non-Breaking Changes (Patch Version Bumps)

- Bug fixes (including behavioral corrections)
- Backwards-compatible configuration additions
- New Python version support
- New preview file type support
- Feature/option deprecations
- Linter: unsafe fixes, preview safe fixes, preview scope expansions, preview rule additions/behavior changes
- Formatter: style changes preventing invalid syntax/semantics/comment loss; preview style changes
- Language server: new capability support, new settings, setting deprecations

## Rule and Fix Stabilization

New rules launch in preview mode and require "at least one minor release before being promoted to stable." Fix applicability progresses through Display -> Unsafe -> Safe levels.

## Pre-1.0.0 Status

`0.x` versioning indicates an unstable API with breaking changes distributed across minor versions rather than major versions.

## VS Code Extension Versioning

Even minor versions denote stable releases; odd numbers indicate preview releases.
