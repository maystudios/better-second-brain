# uv Tools (uvx and uv tool)

uv can install and execute command-line Python tools, a capability the sources describe as "similar to pipx" ([[sources/github-astral-sh-uv]]; [[sources/docs-astral-sh-uv]]).

## Running tools temporarily with uvx

- `uvx` invokes a tool without installing it into a persistent environment ([[sources/docs-astral-sh-uv-guides-tools]]).
- `uvx` is an alias "exactly equivalent to: `uv tool run`" ([[sources/docs-astral-sh-uv-guides-tools]]).
- Usage: `uvx ruff`; arguments follow the tool name, e.g. `uvx pycowsay hello from uv` ([[sources/docs-astral-sh-uv-guides-tools]]; the `uvx pycowsay` example also appears in [[sources/docs-astral-sh-uv]]).
- Tools run by `uvx` are installed into "temporary, isolated environments" ([[sources/docs-astral-sh-uv-guides-tools]]).

## Installing tools persistently

- `uv tool install ruff` installs a tool persistently ([[sources/docs-astral-sh-uv-guides-tools]]; also shown in [[sources/docs-astral-sh-uv]]).
- After installation, executables are available directly without the uv prefix, e.g. `ruff --version` ([[sources/docs-astral-sh-uv-guides-tools]]).
- `uv tool install` places executables in a `bin` directory added to `PATH` for repeated access, whereas `uvx` creates temporary, isolated environments per invocation ([[sources/docs-astral-sh-uv-guides-tools]]).
- Unlike `uv pip install`, installing a tool does not expose its modules to the current Python environment; this isolation prevents dependency conflicts ([[sources/docs-astral-sh-uv-guides-tools]]).

## Selecting versions

- With `uvx`, use `@`: `uvx ruff@0.3.0 check`, `uvx ruff@latest check` ([[sources/docs-astral-sh-uv-guides-tools]]).
- With `uv tool install`, use constraints: `uv tool install 'ruff==0.3.0'`, `uv tool install 'ruff>0.2.0,<0.3.0'` ([[sources/docs-astral-sh-uv-guides-tools]]).

## Different command vs. package names

- Use `--from` when the command name differs from the package name: `uvx --from httpie http` ([[sources/docs-astral-sh-uv-guides-tools]]).

## Selecting Python versions

- `uvx --python 3.10 ruff`, `uv tool install --python 3.10 ruff`, `uv tool upgrade --python 3.10 ruff` ([[sources/docs-astral-sh-uv-guides-tools]]).

## Upgrading tools

- `uv tool upgrade ruff`, `uv tool upgrade --all` ([[sources/docs-astral-sh-uv-guides-tools]]).
- Upgrades respect existing version constraints; to change constraints, reinstall the tool ([[sources/docs-astral-sh-uv-guides-tools]]).

## Managing tool environments

- If the tools directory isn't on PATH: `uv tool update-shell` ([[sources/docs-astral-sh-uv-guides-tools]]).
- Legacy setuptools scripts (`.ps1`, `.cmd`, `.bat`) are accessible via `$(uv tool dir)\<tool-name>\Scripts` ([[sources/docs-astral-sh-uv-guides-tools]]).

## Open questions

- The sources state `uvx` is "exactly equivalent to `uv tool run`" ([[sources/docs-astral-sh-uv-guides-tools]]); whether `uvx` is a separate installed binary (the uninstall step removes a `uvx` binary, see [[uv-installation]] and [[sources/docs-astral-sh-uv-getting-started-installation]]) or purely an alias is not fully reconciled across the raw sources.
