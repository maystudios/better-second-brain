---
type: concept
title: Installation & Distribution
---

How Ruff is installed and distributed across package managers, standalone installers, and containers.

- Recommended via uv (`uv tool install ruff@latest`, `uv add --dev ruff`); also pip and pipx .
- Run without installing using `uvx ruff check` / `uvx ruff format` .
- Standalone installers (v0.5.0+): curl script (macOS/Linux), PowerShell `irm ... | iex` (Windows), version-pinnable .
- System packages: Homebrew, Conda, Arch, Alpine, openSUSE, pkgx; Docker via `ghcr.io/astral-sh/ruff` .
- Ships pre-built PyPI wheels, so no Rust toolchain is required to install .

## Sources
- https://docs.astral.sh/ruff/installation/
- https://github.com/astral-sh/ruff
- https://docs.astral.sh/ruff/faq/
