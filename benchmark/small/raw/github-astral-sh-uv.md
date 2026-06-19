# uv: Python Package and Project Manager

Source: https://github.com/astral-sh/uv

## What is uv?

uv is "an extremely fast Python package and project manager, written in Rust." It consolidates functionality from multiple Python tools into a single, high-performance utility.

## Key Highlights

uv replaces numerous tools including pip, pip-tools, pipx, poetry, pyenv, twine, and virtualenv. The project delivers substantial performance improvements—claimed to be 10-100x faster than pip. It offers comprehensive project management with universal lockfiles, script execution with inline dependency declarations, Python version installation and management, and tool execution similar to pipx. The tool supports Cargo-style workspaces and maintains a global cache for efficient disk usage.

## Installation

**macOS and Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Via PyPI:**
```bash
pip install uv
# or
pipx install uv
```

Self-updates are available: `uv self update`

## Core Features

- **Projects**: Dependency management with lockfiles and workspaces
- **Scripts**: Single-file scripts with inline metadata for dependencies
- **Tools**: Installation and execution of command-line Python packages
- **Python Management**: Installation and version switching
- **Pip Interface**: Drop-in replacement for pip/pip-tools with enhanced features
- **Workspace Support**: Scalable project structures
- **Cross-Platform**: macOS, Linux, and Windows support

## Maintainer

uv is developed by Astral, creators of Ruff and other Python tooling.

## Licensing

Dual-licensed under Apache License 2.0 or MIT license.
