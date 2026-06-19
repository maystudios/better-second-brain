# Installing Ruff

Source: https://docs.astral.sh/ruff/installation/

## Quick Start with uvx

```bash
uvx ruff check   # Lint all files in the current directory
uvx ruff format  # Format all files in the current directory
```

## Package Manager Installations

### uv (Recommended)
```bash
uv tool install ruff@latest
uv add --dev ruff
```

### pip
```bash
pip install ruff
```

### pipx
```bash
pipx install ruff
```

## Standalone Installers (v0.5.0+)

### macOS and Linux
```bash
curl -LsSf https://astral.sh/ruff/install.sh | sh
curl -LsSf https://astral.sh/ruff/0.5.0/install.sh | sh  # specific version
```

### Windows
```powershell
powershell -c "irm https://astral.sh/ruff/install.ps1 | iex"
powershell -c "irm https://astral.sh/ruff/0.5.0/install.ps1 | iex"  # specific version
```

## System Package Managers

- Homebrew: `brew install ruff`
- Conda: `conda install -c conda-forge ruff`
- Arch Linux: `pacman -S ruff`
- Alpine Linux: `apk add ruff`
- openSUSE Tumbleweed: `sudo zypper install python3-ruff`
- pkgx: `pkgx install ruff`

## Docker

```bash
docker run -v .:/io --rm ghcr.io/astral-sh/ruff check
docker run -v .:/io --rm ghcr.io/astral-sh/ruff:0.3.0 check
docker run -v .:/io:Z --rm ghcr.io/astral-sh/ruff check  # Podman/SELinux
```

## Basic Usage

```bash
ruff check   # Lint all files in the current directory
ruff format  # Format all files in the current directory
```
