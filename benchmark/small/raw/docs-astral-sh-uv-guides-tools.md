# Using Tools with uv

Source: https://docs.astral.sh/uv/guides/tools/

## Running Tools Temporarily

The `uvx` command invokes a tool without installing it into a persistent environment. According to the documentation, `uvx` is an alias that is "exactly equivalent to: `uv tool run`"

Basic usage:
```bash
uvx ruff
```

Pass arguments after the tool name:
```bash
uvx pycowsay hello from uv
```

Tools are installed into "temporary, isolated environments when using `uvx`"

## Installing Tools Persistently

For frequently-used tools, install them to a persistent environment:

```bash
uv tool install ruff
```

Once installed, executables become available directly without the uv prefix:

```bash
ruff --version
```

### Key Difference Between uvx and uv tool install

- **uvx**: Creates temporary, isolated environments for each invocation
- **uv tool install**: Places executables in a `bin` directory added to `PATH` for repeated access

Unlike `uv pip install`, installing a tool does not expose its modules to the current Python environment. This isolation prevents dependency conflicts.

## Requesting Specific Versions

Use the `@` syntax with `uvx`:

```bash
uvx ruff@0.3.0 check
uvx ruff@latest check
```

With `uv tool install`, specify versions as package constraints:

```bash
uv tool install 'ruff==0.3.0'
uv tool install 'ruff>0.2.0,<0.3.0'
```

## Commands with Different Package Names

Use the `--from` option when the command name differs from the package name:

```bash
uvx --from httpie http
```

## Selecting Python Versions

Specify which Python interpreter to use:

```bash
uvx --python 3.10 ruff
uv tool install --python 3.10 ruff
uv tool upgrade --python 3.10 ruff
```

## Upgrading Tools

```bash
uv tool upgrade ruff
uv tool upgrade --all
```

Upgrades respect existing version constraints. To change constraints, reinstall the tool.

## Managing Tool Environments

If the tools directory isn't on your PATH, run:

```bash
uv tool update-shell
```

Legacy setuptools scripts (`.ps1`, `.cmd`, `.bat` extensions) are accessible via `$(uv tool dir)\<tool-name>\Scripts`
