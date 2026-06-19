# Source: Ruff Editor Setup

- **Citation / URL:** https://docs.astral.sh/ruff/editors/setup/
- **Raw file:** `benchmark/large/raw/editors-setup.md`
- **Type:** Official documentation — per-editor setup

## Key claims

- **VS Code:** Ruff extension from the Marketplace; Extension ID `charliermarsh.ruff`; recommended version 2024.32.0 or later; repository `github.com/astral-sh/ruff-vscode`.
- **Neovim:**
  - nvim-lspconfig (Neovim 0.10+): `require('lspconfig').ruff.setup({ init_options = { settings = {} } })`.
  - vim.lsp.config (Neovim 0.11+), in `nvim/lsp/ruff.lua`, with `cmd = { 'ruff', 'server' }`, `filetypes = { 'python' }`, `root_markers = { 'pyproject.toml', 'ruff.toml', '.ruff.toml', '.git' }`; enable via `vim.lsp.enable('ruff')`.
  - Plugin alternatives: conform.nvim (`ruff_fix`, `ruff_format`, `ruff_organize_imports`), nvim-lint, ALE.
- **Vim:** vim-lsp plugin; cmd `{server_info->['ruff', 'server']}`, allowlist `['python']`.
- **Helix:** `[language-server.ruff]` with `command = "ruff"`, `args = ["server"]`; `[[language]]` python uses `language-servers = ["ruff"]`.
- **Kate:** LSP Client plugin; command `["ruff", "server"]`.
- **Sublime Text:** LSP (SublimeLSP) + LSP-ruff (SublimeLSP).
- **PyCharm:** 2025.3+ built-in via Python | Tools | Ruff; earlier versions use External Tool or a third-party Ruff plugin.
- **Zed:** built-in support (no extension); configure `lsp.ruff.initialization_options.settings`.
- **Emacs:** via Eglot `(python-base-mode . ("ruff" "server"))`; alternatives flymake-ruff, emacs-ruff-format, Apheleia.
- **TextMate:** textmate2-ruff-linter bundle.
- Note: disable older `ruff-lsp` to prevent conflicts.

## Prose summary

This is the per-editor cookbook. Nearly every modern editor connects to Ruff through the same `ruff server` LSP command — VS Code (via the `charliermarsh.ruff` extension), Neovim (lspconfig or native `vim.lsp.config`, plus conform.nvim/nvim-lint/ALE), Vim, Helix, Kate, Sublime, Zed, and Emacs (Eglot). PyCharm gains native support in 2025.3+ and otherwise relies on an External Tool or third-party plugin. The page repeats the overview's caution to disable the legacy `ruff-lsp` to avoid conflicts.
