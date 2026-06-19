# Installing uv

The sources describe several installation methods. uv can be installed without requiring Rust or Python ([[sources/docs-astral-sh-uv]]).

## Standalone installer

- macOS/Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh` ([[sources/github-astral-sh-uv]]; [[sources/docs-astral-sh-uv]]; [[sources/docs-astral-sh-uv-getting-started-installation]]).
- macOS/Linux alternative with wget: `wget -qO- https://astral.sh/uv/install.sh | sh` ([[sources/docs-astral-sh-uv-getting-started-installation]]).
- Windows: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"` ([[sources/github-astral-sh-uv]]; [[sources/docs-astral-sh-uv]]; [[sources/docs-astral-sh-uv-getting-started-installation]]).
- A specific version can be pinned in the URL, e.g. `.../uv/0.11.22/install.sh` (macOS/Linux) or `.../uv/0.11.22/install.ps1` (Windows) ([[sources/docs-astral-sh-uv-getting-started-installation]]).

## Via PyPI

- `pip install uv` or `pipx install uv` ([[sources/github-astral-sh-uv]]; [[sources/docs-astral-sh-uv-getting-started-installation]]).

## Via package managers

- `brew install uv` (Homebrew), `sudo port install uv` (MacPorts), `winget install --id=astral-sh.uv -e` (WinGet), `scoop install main/uv` (Scoop), `cargo install --locked uv` (Cargo) ([[sources/docs-astral-sh-uv-getting-started-installation]]).

## Docker and GitHub Releases

- Docker image: `ghcr.io/astral-sh/uv` ([[sources/docs-astral-sh-uv-getting-started-installation]]).
- GitHub Releases: https://github.com/astral-sh/uv/releases ([[sources/docs-astral-sh-uv-getting-started-installation]]).

## Upgrading

- Self-update: `uv self update` ([[sources/github-astral-sh-uv]]; [[sources/docs-astral-sh-uv-getting-started-installation]]).
- For other installation methods, use that method's own upgrade command, e.g. `pip install --upgrade uv` ([[sources/docs-astral-sh-uv-getting-started-installation]]).

## Shell autocompletion

- Generated via `uv generate-shell-completion <shell>` for Bash, Zsh, and Fish (added to the respective shell config) ([[sources/docs-astral-sh-uv-getting-started-installation]]).

## Uninstallation

- Clean up data: `uv cache clean`, `rm -r "$(uv python dir)"`, `rm -r "$(uv tool dir)"` ([[sources/docs-astral-sh-uv-getting-started-installation]]).
- Remove binaries on macOS/Linux: `rm ~/.local/bin/uv ~/.local/bin/uvx`; on Windows remove `uv.exe`, `uvx.exe`, and `uvw.exe` from `$HOME\.local\bin\` ([[sources/docs-astral-sh-uv-getting-started-installation]]).

## Open questions

- `0.11.22` appears only as an example pinned version in the installation guide ([[sources/docs-astral-sh-uv-getting-started-installation]]); the raw sources do not state the current/latest uv release version.
- The macOS/Linux binary-removal command lists `uv` and `uvx`, while the Windows command additionally lists `uvw.exe` ([[sources/docs-astral-sh-uv-getting-started-installation]]); the sources do not explain what `uvw` is.
