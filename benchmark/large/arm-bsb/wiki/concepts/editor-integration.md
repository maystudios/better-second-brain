# Editor Integration

[[concepts/ruff]] provides editor integration through a built-in **Language Server (LSP)**, written in Rust and invoked via `ruff server` ([[sources/editors]]). It is a unified backend integrated directly into the Ruff CLI ([[sources/editors]]), and first-party editor integrations (VS Code and others) are listed among Ruff's headline features ([[sources/ruff-overview]]; [[sources/github-astral-sh-ruff]]).

## The language server

The server was available in beta starting with Ruff **v0.4.5** and was stabilized in **v0.5.3** ([[sources/editors]]). Its capabilities are: surfacing Ruff diagnostics, code actions to fix issues, and code formatting via Ruff's built-in formatter ([[sources/editors]]). It is designed to run alongside another Python language server that handles navigation and autocompletion ([[sources/editors]]).

The native `ruff server` is a direct replacement for the older standalone `ruff-lsp` implementation ([[sources/editors]]), and the setup guide repeatedly cautions users to disable the legacy `ruff-lsp` to prevent conflicts ([[sources/editors-setup]]).

## Per-editor setup

Most editors connect through the same `ruff server` command ([[sources/editors-setup]]):
- **VS Code** - the `charliermarsh.ruff` extension (recommended 2024.32.0+), repo `github.com/astral-sh/ruff-vscode` ([[sources/editors-setup]]).
- **Neovim** - nvim-lspconfig (0.10+) or native `vim.lsp.config` (0.11+); plugin alternatives conform.nvim (`ruff_fix`, `ruff_format`, `ruff_organize_imports`), nvim-lint, and ALE ([[sources/editors-setup]]).
- **Vim** - vim-lsp ([[sources/editors-setup]]).
- **Helix**, **Kate**, **Sublime Text** (LSP + LSP-ruff), **Zed** (built-in, no extension), **Emacs** (Eglot, plus flymake-ruff / emacs-ruff-format / Apheleia), and **TextMate** (textmate2-ruff-linter) ([[sources/editors-setup]]).
- **PyCharm** - built-in via Python | Tools | Ruff in 2025.3+; earlier versions use an External Tool or a third-party plugin ([[sources/editors-setup]]).

## Extension versioning

The VS Code extension follows its own scheme - even minor versions are stable, odd minor versions are preview - distinct from the core tool's [[concepts/versioning]] policy ([[sources/versioning]]).

## Open questions

- The recommended VS Code extension version is given as "2024.32.0 or later" ([[sources/editors-setup]]); the sources do not state a minimum supported version.
