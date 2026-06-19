# Ruff Editor Setup

Source: https://docs.astral.sh/ruff/editors/setup/

## VS Code

Ruff extension from the VS Code Marketplace:
- Extension ID: `charliermarsh.ruff`
- Recommended version: 2024.32.0 or later
- Repository: github.com/astral-sh/ruff-vscode

## Neovim

nvim-lspconfig (Neovim 0.10+):
```lua
require('lspconfig').ruff.setup({
  init_options = { settings = {} }
})
```

vim.lsp.config (Neovim 0.11+), in `nvim/lsp/ruff.lua`:
```lua
return {
  cmd = { 'ruff', 'server' },
  filetypes = { 'python' },
  root_markers = { 'pyproject.toml', 'ruff.toml', '.ruff.toml', '.git' },
  init_options = { settings = {} }
}
```
Enable: `vim.lsp.enable('ruff')`

Plugin alternatives: conform.nvim (`ruff_fix`, `ruff_format`, `ruff_organize_imports`), nvim-lint, ALE.

## Vim

vim-lsp plugin; cmd `{server_info->['ruff', 'server']}`, allowlist `['python']`.

## Helix
```toml
[language-server.ruff]
command = "ruff"
args = ["server"]

[[language]]
name = "python"
language-servers = ["ruff"]
```

## Kate
LSP Client plugin; command `["ruff", "server"]`.

## Sublime Text
LSP (SublimeLSP) + LSP-ruff (SublimeLSP).

## PyCharm
- 2025.3+: built-in via Python | Tools | Ruff
- Earlier: External Tool or third-party Ruff plugin

## Zed
Built-in support (no extension). Configure `lsp.ruff.initialization_options.settings`.

## Emacs
Via Eglot: `(python-base-mode . ("ruff" "server"))`. Alternatives: flymake-ruff, emacs-ruff-format, Apheleia.

## TextMate
textmate2-ruff-linter bundle.

Note: Disable older `ruff-lsp` to prevent conflicts.
