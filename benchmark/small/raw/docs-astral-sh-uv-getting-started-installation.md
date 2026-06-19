# uv Installation Guide

Source: https://docs.astral.sh/uv/getting-started/installation/

## Installation Methods

**Standalone Installer (macOS/Linux):**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Alternative with wget:
```bash
wget -qO- https://astral.sh/uv/install.sh | sh
```

Specific version:
```bash
curl -LsSf https://astral.sh/uv/0.11.22/install.sh | sh
```

**Standalone Installer (Windows):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Specific version:
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/0.11.22/install.ps1 | iex"
```

**PyPI Installation:**
```bash
pipx install uv
# or
pip install uv
```

**Package Managers:**
```bash
brew install uv                    # Homebrew
sudo port install uv               # MacPorts
winget install --id=astral-sh.uv -e  # WinGet
scoop install main/uv              # Scoop
cargo install --locked uv          # Cargo
```

**Docker:**
Access the image at `ghcr.io/astral-sh/uv`

**GitHub Releases:**
Download directly from https://github.com/astral-sh/uv/releases

## Upgrading

```bash
uv self update
```

For other installation methods, use the package manager's upgrade command (e.g., `pip install --upgrade uv`).

## Shell Autocompletion

**uv completion:**
```bash
# Bash
echo 'eval "$(uv generate-shell-completion bash)"' >> ~/.bashrc

# Zsh
echo 'eval "$(uv generate-shell-completion zsh)"' >> ~/.zshrc

# Fish
echo 'uv generate-shell-completion fish | source' > ~/.config/fish/completions/uv.fish
```

## Uninstallation

Clean up data:
```bash
uv cache clean
rm -r "$(uv python dir)"
rm -r "$(uv tool dir)"
```

Remove binaries (macOS/Linux):
```bash
rm ~/.local/bin/uv ~/.local/bin/uvx
```

Remove binaries (Windows):
```powershell
rm $HOME\.local\bin\uv.exe
rm $HOME\.local\bin\uvx.exe
rm $HOME\.local\bin\uvw.exe
```
