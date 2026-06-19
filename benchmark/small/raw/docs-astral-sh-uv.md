# uv Documentation Landing Page

Source: https://docs.astral.sh/uv/

## Overview

**uv** is described as "An extremely fast Python package and project manager, written in Rust."

## What It Replaces

uv serves as a single tool to replace: `pip`, `pip-tools`, `pipx`, `poetry`, `pyenv`, `twine`, `virtualenv`, and additional package management tools.

## Key Features

The documentation highlights these capabilities:

- "10-100x faster" than pip
- Comprehensive project management with universal lockfile support
- Script execution with inline dependency metadata
- Python version installation and management
- Tool installation and execution (similar to pipx)
- Pip-compatible interface for performance improvements
- Cargo-style workspace support
- Global cache for dependency deduplication
- Cross-platform support (macOS, Linux, Windows)
- Installation without requiring Rust or Python

## Installation

**macOS and Linux:**
```bash
$ curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
PS> powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## Quick Start Examples

The landing page demonstrates:

- **Projects**: `uv init`, `uv add`, `uv run`, `uv lock`, `uv sync`
- **Scripts**: `uv add --script` and `uv run` for single-file Python scripts
- **Tools**: `uvx pycowsay` and `uv tool install ruff`
- **Python versions**: Installing multiple versions with `uv python install`

## Next Steps

Users are directed to the "first steps" guide or project/script guides for detailed setup instructions.
