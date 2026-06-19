# Installation

[[concepts/ruff]] can be installed through many channels. The two core subcommands operate on the current directory by default: `ruff check` lints all files and `ruff format` formats all files in the current directory ([[sources/installation]]).

## Zero-install run (uvx)

Ruff can be run without a persistent install using Astral's `uvx`: `uvx ruff check` lints and `uvx ruff format` formats the current directory ([[sources/installation]]).

## Package managers

- **uv (recommended):** `uv tool install ruff@latest` or `uv add --dev ruff` ([[sources/installation]]; [[sources/github-astral-sh-ruff]]).
- **pip:** `pip install ruff` ([[sources/installation]]; [[sources/github-astral-sh-ruff]]).
- **pipx:** `pipx install ruff` ([[sources/installation]]; [[sources/github-astral-sh-ruff]]).

Because Ruff ships as pre-built wheels on PyPI, installing it requires no Rust toolchain ([[sources/faq]]).

## System package managers

Homebrew (`brew install ruff`), Conda (`conda install -c conda-forge ruff`), Arch (`pacman -S ruff`), Alpine (`apk add ruff`), openSUSE Tumbleweed (`sudo zypper install python3-ruff`), and pkgx (`pkgx install ruff`) are all documented ([[sources/installation]]).

## Standalone installers (v0.5.0+)

Standalone shell/PowerShell installers were introduced at **v0.5.0** ([[sources/installation]]):
- macOS/Linux: `curl -LsSf https://astral.sh/ruff/install.sh | sh`, with a versioned path form `.../0.5.0/install.sh` for pinning ([[sources/installation]]).
- Windows: `powershell -c "irm https://astral.sh/ruff/install.ps1 | iex"`, also version-pinnable ([[sources/installation]]).

The README additionally lists the macOS/Linux `curl` installer among its installation methods ([[sources/github-astral-sh-ruff]]).

## Docker

Ruff publishes images on GHCR: `docker run -v .:/io --rm ghcr.io/astral-sh/ruff check`, a versioned form `ghcr.io/astral-sh/ruff:0.3.0 check`, and a Podman/SELinux variant using `-v .:/io:Z` ([[sources/installation]]). The full Docker tag taxonomy used in CI is documented under [[concepts/integrations]] ([[sources/integrations]]).

## Open questions

- The installation page lists standalone installers "v0.5.0+" ([[sources/installation]]); it does not state which install channels existed before that version.
