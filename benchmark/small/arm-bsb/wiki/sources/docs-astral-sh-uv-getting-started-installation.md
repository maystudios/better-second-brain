# Source: docs-astral-sh-uv-getting-started-installation

- **Citation / URL:** https://docs.astral.sh/uv/getting-started/installation/
- **Title:** uv Installation Guide
- **Raw file:** `benchmark/small/raw/docs-astral-sh-uv-getting-started-installation.md`

## Key claims

### Installation methods
- Standalone installer (macOS/Linux): `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Alternative with wget: `wget -qO- https://astral.sh/uv/install.sh | sh`
- Specific version (macOS/Linux): `curl -LsSf https://astral.sh/uv/0.11.22/install.sh | sh`
- Standalone installer (Windows): `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
- Specific version (Windows): `...irm https://astral.sh/uv/0.11.22/install.ps1 | iex`
- PyPI: `pipx install uv` or `pip install uv`
- Package managers:
  - `brew install uv` (Homebrew)
  - `sudo port install uv` (MacPorts)
  - `winget install --id=astral-sh.uv -e` (WinGet)
  - `scoop install main/uv` (Scoop)
  - `cargo install --locked uv` (Cargo)
- Docker image: `ghcr.io/astral-sh/uv`
- GitHub Releases: https://github.com/astral-sh/uv/releases

### Upgrading
- `uv self update`
- For other installation methods, use that method's upgrade command (e.g., `pip install --upgrade uv`).

### Shell autocompletion
- Bash: `echo 'eval "$(uv generate-shell-completion bash)"' >> ~/.bashrc`
- Zsh: `echo 'eval "$(uv generate-shell-completion zsh)"' >> ~/.zshrc`
- Fish: `echo 'uv generate-shell-completion fish | source' > ~/.config/fish/completions/uv.fish`

### Uninstallation
- Clean up data: `uv cache clean`, `rm -r "$(uv python dir)"`, `rm -r "$(uv tool dir)"`
- Remove binaries (macOS/Linux): `rm ~/.local/bin/uv ~/.local/bin/uvx`
- Remove binaries (Windows): `rm $HOME\.local\bin\uv.exe`, `...uvx.exe`, `...uvw.exe`
