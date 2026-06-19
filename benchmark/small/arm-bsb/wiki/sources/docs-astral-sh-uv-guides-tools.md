# Source: docs-astral-sh-uv-guides-tools

- **Citation / URL:** https://docs.astral.sh/uv/guides/tools/
- **Title:** Using Tools with uv
- **Raw file:** `benchmark/small/raw/docs-astral-sh-uv-guides-tools.md`

## Key claims

### Running tools temporarily
- `uvx` invokes a tool without installing it into a persistent environment.
- `uvx` is an alias that is "exactly equivalent to: `uv tool run`".
- Basic usage: `uvx ruff`; with arguments: `uvx pycowsay hello from uv`.
- Tools are installed into "temporary, isolated environments when using `uvx`".

### Installing tools persistently
- For frequently-used tools: `uv tool install ruff`.
- Once installed, executables are available directly without the uv prefix, e.g., `ruff --version`.

### Difference between uvx and uv tool install
- **uvx**: creates temporary, isolated environments for each invocation.
- **uv tool install**: places executables in a `bin` directory added to `PATH` for repeated access.
- Unlike `uv pip install`, installing a tool does not expose its modules to the current Python environment; this isolation prevents dependency conflicts.

### Requesting specific versions
- With `uvx` using `@` syntax: `uvx ruff@0.3.0 check`, `uvx ruff@latest check`.
- With `uv tool install` using constraints: `uv tool install 'ruff==0.3.0'`, `uv tool install 'ruff>0.2.0,<0.3.0'`.

### Commands with different package names
- Use `--from` when command name differs from package name: `uvx --from httpie http`.

### Selecting Python versions
- `uvx --python 3.10 ruff`, `uv tool install --python 3.10 ruff`, `uv tool upgrade --python 3.10 ruff`.

### Upgrading tools
- `uv tool upgrade ruff`, `uv tool upgrade --all`.
- Upgrades respect existing version constraints; to change constraints, reinstall the tool.

### Managing tool environments
- If the tools directory isn't on PATH: `uv tool update-shell`.
- Legacy setuptools scripts (`.ps1`, `.cmd`, `.bat`) are accessible via `$(uv tool dir)\<tool-name>\Scripts`.
