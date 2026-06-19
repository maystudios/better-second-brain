---
type: concept
title: Installation & Distribution
---

How Ruff is installed and distributed across package managers, standalone installers, and containers.

- Recommended via uv (`uv tool install ruff@latest`, `uv add --dev ruff`); also pip and pipx ([[sources/installation]], [[sources/github-astral-sh-ruff]]).
- Run without installing using `uvx ruff check` / `uvx ruff format` ([[sources/installation]]).
- Standalone installers (v0.5.0+): curl script (macOS/Linux), PowerShell `irm ... | iex` (Windows), version-pinnable ([[sources/installation]], [[sources/github-astral-sh-ruff]]).
- System packages: Homebrew, Conda, Arch, Alpine, openSUSE, pkgx; Docker via `ghcr.io/astral-sh/ruff` ([[sources/installation]]).
- Ships pre-built PyPI wheels, so no Rust toolchain is required to install ([[sources/faq]]).

## Links
[[concepts/ruff]] · [[concepts/integrations]] · [[concepts/cli-commands]] · [[sources/installation]] · [[sources/github-astral-sh-ruff]] · [[sources/faq]]
