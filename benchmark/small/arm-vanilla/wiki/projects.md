# Projects

Project management is the heart of [[index|uv]]. A uv project is a directory with a `pyproject.toml` describing your dependencies, a `uv.lock` lockfile pinning exact versions, and an isolated `.venv` virtual environment that uv manages for you.

## Creating a project

```bash
uv init hello-world
cd hello-world
```
You can also run `uv init` inside an existing empty directory. Either way, uv scaffolds a small starting layout:

```
├── .git/
├── .gitignore
├── .python-version
├── README.md
├── main.py
└── pyproject.toml
```

The first time you run a project command, uv fills in the rest - creating `.venv/` and writing `uv.lock`.

## Key files

- **`pyproject.toml`** - project metadata (name, version, description) and the dependency list. This is the file you edit (directly or via `uv add`).
- **`.python-version`** - the default Python version used when uv creates the project's virtual environment. See [[scripts-and-python]] for more on Python version management.
- **`.venv/`** - the isolated environment where dependencies are installed.
- **`uv.lock`** - a cross-platform lockfile with the exact resolved versions of every dependency. It's human-readable TOML but **should not be edited by hand**, and it **should be checked into version control** so installs are reproducible across machines.

## Managing dependencies

```bash
uv add requests
uv add 'requests==2.31.0'
uv add git+https://github.com/psf/requests
uv add -r requirements.txt -c constraints.txt
uv remove requests
```

To bump a single locked package:

```bash
uv lock --upgrade-package requests
```

## Running code

`uv run` executes a command inside the project environment, syncing dependencies first so you never run against a stale environment:

```bash
uv run main.py
uv run -- flask run -p 3000
```

If you'd rather activate the environment yourself:

```bash
uv sync
source .venv/bin/activate   # macOS/Linux
.venv\Scripts\activate      # Windows
```

## Versioning and building

Check or print the project version:

```bash
uv version            # hello-world 0.7.0
uv version --short    # 0.7.0
```

And produce distributable artifacts (a wheel and a source tarball) into `dist/`:

```bash
uv build
```

Related: [[tools]] for command-line programs, [[scripts-and-python]] for one-off scripts, and [[installation]] to get uv set up.
