# Source: docs-astral-sh-uv

- **Citation / URL:** https://docs.astral.sh/uv/
- **Title:** uv Documentation Landing Page
- **Raw file:** `benchmark/small/raw/docs-astral-sh-uv.md`

## Key claims

- uv is "An extremely fast Python package and project manager, written in Rust."
- uv serves as a single tool to replace: pip, pip-tools, pipx, poetry, pyenv, twine, virtualenv, and "additional package management tools."
- Listed capabilities:
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
- Installation (macOS/Linux): `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Installation (Windows): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
- Quick-start command examples:
  - Projects: `uv init`, `uv add`, `uv run`, `uv lock`, `uv sync`
  - Scripts: `uv add --script` and `uv run` for single-file Python scripts
  - Tools: `uvx pycowsay` and `uv tool install ruff`
  - Python versions: `uv python install`
- Users are directed to a "first steps" guide or project/script guides for detailed setup.
