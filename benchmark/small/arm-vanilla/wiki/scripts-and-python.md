# Scripts & Python Versions

Alongside [[projects]] and [[tools]], [[index|uv]] handles two more everyday needs: running **single-file scripts** with their own dependencies, and **installing and switching Python versions**.

## Single-file scripts with inline dependencies

Not every bit of Python deserves a full project. uv lets a standalone `.py` file declare its own dependencies as inline metadata, so the script is self-contained and runnable anywhere uv is installed.

You attach a dependency to a script with `uv add --script`, and then run it with `uv run`:

```bash
uv add --script example.py requests
uv run example.py
```

When you run such a script, uv reads its inline metadata, sets up a temporary environment with exactly those dependencies, and executes it — no manual virtual environment, no leftover state. This makes scripts easy to share: the dependency list travels with the file itself.

## Installing and managing Python versions

uv can install Python interpreters for you, replacing the need for a separate tool like pyenv:

```bash
uv python install 3.10 3.11 3.12
```

Once installed, uv uses these interpreters automatically. Within a [[projects|project]], the `.python-version` file records which version to use when creating the `.venv`. You can also point individual [[tools|tool]] runs or script runs at a specific interpreter:

```bash
uvx --python 3.10 ruff
```

To find where uv keeps its managed interpreters, `uv python dir` prints the path (handy when uninstalling — see [[installation]]).

## How it fits together

These features round out uv's "one tool" promise: [[projects]] for applications and libraries, [[tools]] for command-line programs, and scripts plus Python management here for quick, self-contained work. Together they cover most of what you'd otherwise need pip, virtualenv, pipx, and pyenv to do.

Back to the [[index|overview]].
