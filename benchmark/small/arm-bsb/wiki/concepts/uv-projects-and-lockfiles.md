# uv Projects and Lockfiles

uv provides project management with universal/cross-platform lockfile support ([[sources/docs-astral-sh-uv]]; [[sources/github-astral-sh-uv]]).

## Creating a project

- `uv init hello-world` creates a named project; `uv init` initializes the current directory ([[sources/docs-astral-sh-uv-guides-projects]]; quick-start command also noted in [[sources/docs-astral-sh-uv]]).
- `uv init` creates `.git/`, `.gitignore`, `.python-version`, `README.md`, `main.py`, and `pyproject.toml` ([[sources/docs-astral-sh-uv-guides-projects]]).

## Project files

- `pyproject.toml` contains project metadata and dependencies ([[sources/docs-astral-sh-uv-guides-projects]]).
- `.python-version` specifies the project's default Python version for virtual environment creation ([[sources/docs-astral-sh-uv-guides-projects]]).
- `.venv` is the isolated virtual environment directory where dependencies are installed; it appears after commands such as `uv run` or `uv sync` ([[sources/docs-astral-sh-uv-guides-projects]]).
- `uv.lock` appears after those same commands and is "A cross-platform lockfile that contains exact information about your project's dependencies" ([[sources/docs-astral-sh-uv-guides-projects]]).

## The lockfile (`uv.lock`)

- It "should be checked into version control, allowing for consistent and reproducible installations across machines" ([[sources/docs-astral-sh-uv-guides-projects]]).
- It is human-readable TOML but "should not be edited manually" ([[sources/docs-astral-sh-uv-guides-projects]]).

## Managing dependencies

- Add: `uv add requests`, `uv add 'requests==2.31.0'`, `uv add git+https://github.com/psf/requests`, `uv add -r requirements.txt -c constraints.txt` ([[sources/docs-astral-sh-uv-guides-projects]]).
- Remove: `uv remove requests` ([[sources/docs-astral-sh-uv-guides-projects]]).
- Upgrade a single package: `uv lock --upgrade-package requests` ([[sources/docs-astral-sh-uv-guides-projects]]).

## Running and syncing

- Run in the project environment: `uv run main.py`, `uv run -- flask run -p 3000` ([[sources/docs-astral-sh-uv-guides-projects]]).
- Manually sync then activate: `uv sync`, then `source .venv/bin/activate` (macOS/Linux) or `.venv\Scripts\activate` (Windows) ([[sources/docs-astral-sh-uv-guides-projects]]).

## Versioning and building

- `uv version` reports the project version (e.g., `hello-world 0.7.0`), with `--short` and `--output-format json` variants ([[sources/docs-astral-sh-uv-guides-projects]]).
- `uv build` produces source and binary distributions, e.g. a `.whl` and `.tar.gz` in `dist/` ([[sources/docs-astral-sh-uv-guides-projects]]).

## Workspaces

uv advertises Cargo-style workspace support for scalable project structures ([[sources/github-astral-sh-uv]]; [[sources/docs-astral-sh-uv]]).

## Open questions

- The sources advertise "Cargo-style workspaces" ([[sources/github-astral-sh-uv]]; [[sources/docs-astral-sh-uv]]) but the projects guide in the raw material does not actually demonstrate workspace configuration, so the concrete mechanics are not covered here.
- The example `pyproject.toml` shows an empty `dependencies = []`; the raw sources do not detail how `uv add` rewrites this table beyond the command examples above.
