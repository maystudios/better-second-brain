# Installation

Getting [[index|uv]] installed is deliberately easy, and notably it does **not** require Rust or an existing Python — uv ships as a self-contained binary.

## Standalone installer (recommended)

The fastest path is the official install script, which drops the `uv` and `uvx` binaries into `~/.local/bin`.

**macOS and Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
(`wget -qO- https://astral.sh/uv/install.sh | sh` works too if you prefer wget.)

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

You can pin a specific version by putting it in the URL, e.g. `https://astral.sh/uv/0.11.22/install.sh`.

## Other install methods

uv is also available from PyPI and from most package managers:

```bash
pip install uv          # or: pipx install uv
brew install uv         # Homebrew
sudo port install uv    # MacPorts
scoop install main/uv   # Scoop
cargo install --locked uv
```
```powershell
winget install --id=astral-sh.uv -e   # WinGet
```

There's also a Docker image at `ghcr.io/astral-sh/uv`, and raw binaries on the [GitHub releases page](https://github.com/astral-sh/uv/releases).

## Upgrading

If you used the standalone installer, uv can update itself:

```bash
uv self update
```

If you installed via a package manager, upgrade through that manager instead (e.g. `pip install --upgrade uv`).

## Shell autocompletion

uv can generate completions for your shell:

```bash
echo 'eval "$(uv generate-shell-completion bash)"' >> ~/.bashrc   # Bash
echo 'eval "$(uv generate-shell-completion zsh)"'  >> ~/.zshrc    # Zsh
echo 'uv generate-shell-completion fish | source' > ~/.config/fish/completions/uv.fish  # Fish
```

## Uninstalling

To remove cached data and managed directories, then delete the binaries:

```bash
uv cache clean
rm -r "$(uv python dir)"
rm -r "$(uv tool dir)"
rm ~/.local/bin/uv ~/.local/bin/uvx          # macOS/Linux
```

On Windows, remove `uv.exe`, `uvx.exe`, and `uvw.exe` from `$HOME\.local\bin`.

Next: once installed, head to [[projects]] to start a project, or [[tools]] to run command-line programs.
