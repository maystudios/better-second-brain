# Tools

Beyond [[projects]], [[index|uv]] can run and install **command-line Python programs** - things like `ruff`, `black`, or `httpie`. This is the role pipx traditionally filled, and uv covers it with the `uvx` and `uv tool` commands.

## Running a tool once: `uvx`

`uvx` runs a tool in a temporary, isolated environment without permanently installing anything. It's an exact alias for `uv tool run`:

```bash
uvx ruff
uvx pycowsay hello from uv
```

Arguments after the tool name are passed straight through to the tool.

## Installing a tool persistently

For tools you reach for often, install them so their executables stay on your `PATH`:

```bash
uv tool install ruff
ruff --version
```

The difference between the two:

- **`uvx`** - spins up a fresh temporary, isolated environment for each invocation.
- **`uv tool install`** - places the executable in a `bin` directory that's added to your `PATH` for repeated use.

Importantly, installing a tool does **not** expose its modules to your current Python environment (unlike `uv pip install`). That isolation is deliberate - it keeps tool dependencies from clashing with your project's.

## Picking versions

With `uvx`, use the `@` syntax:

```bash
uvx ruff@0.3.0 check
uvx ruff@latest check
```

With `uv tool install`, express the version as a normal constraint:

```bash
uv tool install 'ruff==0.3.0'
uv tool install 'ruff>0.2.0,<0.3.0'
```

## When the command name differs from the package

Some packages ship a command with a different name (for example, the `httpie` package provides the `http` command). Use `--from`:

```bash
uvx --from httpie http
```

## Choosing a Python interpreter

```bash
uvx --python 3.10 ruff
uv tool install --python 3.10 ruff
```

See [[scripts-and-python]] for more on managing Python versions.

## Upgrading tools

```bash
uv tool upgrade ruff
uv tool upgrade --all
```

Upgrades respect the version constraints you set at install time; to change them, reinstall the tool. If the tools directory isn't on your `PATH`, run `uv tool update-shell`.

Back to the [[index|overview]], or see [[installation]] to get uv first.
