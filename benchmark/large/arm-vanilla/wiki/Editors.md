# Editors

[[Ruff]] integrates with editors through a built-in **language server** (LSP), written in Rust and invoked with `ruff server`. It's a unified backend baked directly into the Ruff CLI - no separate package - and is a direct replacement for the older `ruff-lsp`.

The server became available in beta in v0.4.5 and stabilized in v0.5.3. It surfaces [[Linter|diagnostics]], offers code actions to fix them, and formats via Ruff's built-in [[Formatter]]. It's meant to run *alongside* another Python language server that handles navigation and autocompletion.

> Tip: if you previously used `ruff-lsp`, disable it to avoid conflicts.

## VS Code

Install the Ruff extension (`charliermarsh.ruff`) from the Marketplace; version 2024.32.0 or later is recommended. (Extension versioning is even-for-stable, odd-for-preview - see [[Versioning]].)

## Neovim

With nvim-lspconfig (Neovim 0.10+):

```lua
require('lspconfig').ruff.setup({
  init_options = { settings = {} }
})
```

With `vim.lsp.config` (Neovim 0.11+), in `nvim/lsp/ruff.lua`:

```lua
return {
  cmd = { 'ruff', 'server' },
  filetypes = { 'python' },
  root_markers = { 'pyproject.toml', 'ruff.toml', '.ruff.toml', '.git' },
  init_options = { settings = {} }
}
```

Then `vim.lsp.enable('ruff')`. Plugin alternatives include conform.nvim (`ruff_fix`, `ruff_format`, `ruff_organize_imports`), nvim-lint, and ALE.

## Other editors

- **Vim** - via vim-lsp, command `{server_info->['ruff', 'server']}`, allowlisting `python`.
- **Helix** - add a `[language-server.ruff]` with `command = "ruff"`, `args = ["server"]`, and list it for `python`.
- **Kate** - LSP Client plugin with command `["ruff", "server"]`.
- **Sublime Text** - LSP + LSP-ruff (SublimeLSP).
- **PyCharm** - built-in from 2025.3+ (Python | Tools | Ruff); earlier versions use an External Tool or a third-party plugin.
- **Zed** - built-in, no extension; configure `lsp.ruff.initialization_options.settings`.
- **Emacs** - via Eglot: `(python-base-mode . ("ruff" "server"))`; alternatives include flymake-ruff and Apheleia.
- **TextMate** - the textmate2-ruff-linter bundle.

## See also

- [[Integrations]] - running Ruff in pre-commit and CI
- [[Configuration]] - the settings the language server reads
