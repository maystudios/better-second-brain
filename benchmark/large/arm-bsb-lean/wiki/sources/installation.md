---
type: source
title: "Installing Ruff"
url: https://docs.astral.sh/ruff/installation/
kind: official-docs
---

## Key claims
- Quick start without install: `uvx ruff check` / `uvx ruff format`.
- Package managers: uv (`uv tool install ruff@latest`, `uv add --dev ruff`) recommended; also pip, pipx.
- Standalone installers (v0.5.0+): curl `astral.sh/ruff/install.sh` (macOS/Linux); PowerShell `irm astral.sh/ruff/install.ps1 | iex` (Windows); version-pinnable.
- System packages: Homebrew, Conda (conda-forge), Arch (pacman), Alpine (apk), openSUSE (zypper), pkgx.
- Docker: `ghcr.io/astral-sh/ruff` with `-v .:/io`; `:Z` mount suffix for Podman/SELinux.
- Basic usage: `ruff check` lints, `ruff format` formats the current directory.
