# uv — Overview

**uv** is an extremely fast Python package and project manager, written in Rust and developed by [Astral](https://astral.sh) (the team behind the Ruff linter). Its central idea is consolidation: instead of juggling a handful of separate tools, you use one binary that handles installing packages, managing virtual environments, locking dependencies, running scripts, and installing command-line tools.

In practice, uv aims to replace `pip`, `pip-tools`, `pipx`, `poetry`, `pyenv`, `twine`, and `virtualenv`. Because it's compiled to a native binary, it's claimed to be **10–100x faster than pip**, and it installs without needing Rust or Python already present on your system. A shared global cache deduplicates downloaded packages across all your projects, keeping disk usage low.

## What uv does

uv groups its functionality into a few main areas:

- **[[installation|Installation]]** — getting uv onto macOS, Linux, or Windows, plus upgrading and uninstalling.
- **[[projects|Projects]]** — managing an application or library with a `pyproject.toml`, a `uv.lock` lockfile, and an isolated `.venv`.
- **[[tools|Tools]]** — running and installing command-line Python programs (the `uvx` / `uv tool` interface, a pipx replacement).
- **[[scripts-and-python|Scripts & Python Versions]]** — single-file scripts with inline dependencies, and installing/switching Python versions.

## Why people use it

The appeal is speed plus simplicity. One tool, one mental model. You can `uv init` a project, `uv add` a dependency, and `uv run` your code, and uv quietly creates the virtual environment, resolves dependencies, writes a cross-platform lockfile, and keeps everything in sync — all far faster than the traditional pip-and-virtualenv dance.

uv is open source and dual-licensed under Apache 2.0 or MIT. The source lives at [github.com/astral-sh/uv](https://github.com/astral-sh/uv) and the docs at [docs.astral.sh/uv](https://docs.astral.sh/uv/).

See also: [[installation]] · [[projects]] · [[tools]] · [[scripts-and-python]]
