# Source: Installing Ruff

- **Citation / URL:** https://docs.astral.sh/ruff/installation/
- **Raw file:** `benchmark/large/raw/installation.md`
- **Type:** Official documentation — installation guide

## Key claims

- Quick start via `uvx`: `uvx ruff check` lints all files in the current directory; `uvx ruff format` formats them.
- **uv (recommended):** `uv tool install ruff@latest` or `uv add --dev ruff`.
- **pip:** `pip install ruff`.
- **pipx:** `pipx install ruff`.
- **Standalone installers (v0.5.0+):**
  - macOS/Linux: `curl -LsSf https://astral.sh/ruff/install.sh | sh` (or a versioned path `.../0.5.0/install.sh`).
  - Windows: `powershell -c "irm https://astral.sh/ruff/install.ps1 | iex"` (or versioned).
- **System package managers:** Homebrew (`brew install ruff`), Conda (`conda install -c conda-forge ruff`), Arch (`pacman -S ruff`), Alpine (`apk add ruff`), openSUSE Tumbleweed (`sudo zypper install python3-ruff`), pkgx (`pkgx install ruff`).
- **Docker:** `docker run -v .:/io --rm ghcr.io/astral-sh/ruff check`; versioned tag form `ghcr.io/astral-sh/ruff:0.3.0 check`; Podman/SELinux variant uses `-v .:/io:Z`.

## Basic usage

```bash
ruff check   # Lint all files in the current directory
ruff format  # Format all files in the current directory
```

## Prose summary

This page enumerates every supported way to install Ruff. The recommended path is Astral's own `uv` toolchain, but the tool is broadly available across Python package managers (pip, pipx), OS package managers (Homebrew, Conda, pacman, apk, zypper, pkgx), standalone shell/PowerShell installers (introduced at v0.5.0, supporting version pinning), and Docker images on GHCR. Notably it documents `uvx ruff …` as a zero-install run path and confirms the two core subcommands (`check`, `format`) operate on the current directory by default.
