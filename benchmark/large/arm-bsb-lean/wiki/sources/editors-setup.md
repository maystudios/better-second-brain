---
type: source
title: "Ruff Editor Setup"
url: https://docs.astral.sh/ruff/editors/setup/
kind: official-docs
---

## Key claims
- VS Code: extension `charliermarsh.ruff` (recommend 2024.32.0+), repo astral-sh/ruff-vscode.
- Neovim: nvim-lspconfig (0.10+) or vim.lsp.config (0.11+) running `ruff server`; plugins conform.nvim, nvim-lint, ALE.
- Other editors: Vim (vim-lsp), Helix, Kate, Sublime (LSP-ruff), Emacs (Eglot/flymake-ruff), Zed (built-in), TextMate.
- PyCharm: built-in from 2025.3+ (Python | Tools | Ruff); earlier via External Tool or third-party plugin.
- All configs invoke the `ruff server` command; disable older `ruff-lsp` to prevent conflicts.
