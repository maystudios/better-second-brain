# Working on Projects with uv

Source: https://docs.astral.sh/uv/guides/projects/

## Creating a New Project

Initialize a project using `uv init`:

```bash
$ uv init hello-world
$ cd hello-world
```

Or initialize in the current directory:

```bash
$ mkdir hello-world
$ cd hello-world
$ uv init
```

## Project Structure

uv creates the following files and directories:

```
├── .git/
├── .gitignore
├── .python-version
├── README.md
├── main.py
└── pyproject.toml
```

After running project commands like `uv run` or `uv sync`, additional files appear:

```
.
├── .git/
├── .venv/
│   ├── bin
│   ├── lib
│   └── pyvenv.cfg
├── .gitignore
├── .python-version
├── README.md
├── main.py
├── pyproject.toml
└── uv.lock
```

### `pyproject.toml`

Contains project metadata and dependencies:

```toml
[project]
name = "hello-world"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
dependencies = []
```

### `.python-version`

Specifies the project's default Python version for virtual environment creation.

### `.venv`

The isolated virtual environment directory where dependencies are installed.

### `uv.lock`

"A cross-platform lockfile that contains exact information about your project's dependencies"
and "should be checked into version control, allowing for consistent and reproducible
installations across machines." It's human-readable TOML but "should not be edited manually."

## Managing Dependencies

Add packages with `uv add`:

```bash
$ uv add requests
$ uv add 'requests==2.31.0'
$ uv add git+https://github.com/psf/requests
$ uv add -r requirements.txt -c constraints.txt
```

Remove packages:

```bash
$ uv remove requests
```

Upgrade packages:

```bash
$ uv lock --upgrade-package requests
```

## Viewing Your Version

```bash
$ uv version
hello-world 0.7.0

$ uv version --short
0.7.0

$ uv version --output-format json
{
    "package_name": "hello-world",
    "version": "0.7.0",
    "commit_info": null
}
```

## Running Commands

Execute scripts and commands in your project environment:

```bash
$ uv run main.py
$ uv run -- flask run -p 3000
$ uv run example.py
```

Or manually sync and activate the environment:

```bash
$ uv sync
$ source .venv/bin/activate  # macOS/Linux
$ .venv\Scripts\activate     # Windows
```

## Building Distributions

Build source and binary distributions:

```bash
$ uv build
$ ls dist/
hello-world-0.1.0-py3-none-any.whl
hello-world-0.1.0.tar.gz
```
