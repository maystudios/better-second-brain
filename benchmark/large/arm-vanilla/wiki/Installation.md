# Installation

[[Ruff]] ships as pre-built wheels and standalone binaries, so installing it never requires a Rust toolchain. It runs on any Python 3.7+ environment.

## The quickest path: uvx

If you have `uv`, you can run Ruff without installing it at all:

```bash
uvx ruff check   # Lint all files in the current directory
uvx ruff format  # Format all files in the current directory
```

## Package managers

```bash
uv tool install ruff@latest   # recommended
uv add --dev ruff             # as a project dev dependency
pip install ruff
pipx install ruff
```

System package managers are also supported: Homebrew (`brew install ruff`), Conda (`conda install -c conda-forge ruff`), Arch (`pacman -S ruff`), Alpine (`apk add ruff`), openSUSE, and pkgx.

## Standalone installers (v0.5.0+)

```bash
# macOS / Linux
curl -LsSf https://astral.sh/ruff/install.sh | sh
curl -LsSf https://astral.sh/ruff/0.5.0/install.sh | sh   # pin a version
```

```powershell
# Windows
powershell -c "irm https://astral.sh/ruff/install.ps1 | iex"
```

## Docker

```bash
docker run -v .:/io --rm ghcr.io/astral-sh/ruff check
docker run -v .:/io --rm ghcr.io/astral-sh/ruff:0.3.0 check
docker run -v .:/io:Z --rm ghcr.io/astral-sh/ruff check   # Podman/SELinux
```

The full set of image tags is covered under [[Integrations]].

## First commands

Once installed, the two entry points are the [[Linter]] and the [[Formatter]]:

```bash
ruff check   # Lint all files in the current directory
ruff format  # Format all files in the current directory
```

For a guided first project, continue to the [[Tutorial]].
