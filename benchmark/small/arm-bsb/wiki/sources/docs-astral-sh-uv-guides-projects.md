# Source: docs-astral-sh-uv-guides-projects

- **Citation / URL:** https://docs.astral.sh/uv/guides/projects/
- **Title:** Working on Projects with uv
- **Raw file:** `benchmark/small/raw/docs-astral-sh-uv-guides-projects.md`

## Key claims

### Creating a project
- Initialize a named project: `uv init hello-world` then `cd hello-world`.
- Or initialize in the current directory with `uv init`.

### Project structure
- `uv init` creates: `.git/`, `.gitignore`, `.python-version`, `README.md`, `main.py`, `pyproject.toml`.
- After commands like `uv run` or `uv sync`, additional items appear: `.venv/` (with `bin`, `lib`, `pyvenv.cfg`) and `uv.lock`.
- `pyproject.toml` contains project metadata and dependencies (example shows `[project]` table with name, version, description, readme, dependencies).
- `.python-version` specifies the project's default Python version for virtual environment creation.
- `.venv` is the isolated virtual environment directory where dependencies are installed.
- `uv.lock` is "A cross-platform lockfile that contains exact information about your project's dependencies" and "should be checked into version control, allowing for consistent and reproducible installations across machines." It is human-readable TOML but "should not be edited manually."

### Managing dependencies
- Add packages: `uv add requests`, `uv add 'requests==2.31.0'`, `uv add git+https://github.com/psf/requests`, `uv add -r requirements.txt -c constraints.txt`.
- Remove packages: `uv remove requests`.
- Upgrade a package: `uv lock --upgrade-package requests`.

### Viewing version
- `uv version` (e.g., outputs `hello-world 0.7.0`), `uv version --short`, `uv version --output-format json`.

### Running commands
- `uv run main.py`, `uv run -- flask run -p 3000`, `uv run example.py`.
- Or manually: `uv sync`, then `source .venv/bin/activate` (macOS/Linux) or `.venv\Scripts\activate` (Windows).

### Building distributions
- `uv build` produces source and binary distributions (e.g., `hello-world-0.1.0-py3-none-any.whl` and `hello-world-0.1.0.tar.gz` in `dist/`).
