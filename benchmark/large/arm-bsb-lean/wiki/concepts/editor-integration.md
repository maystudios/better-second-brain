---
type: concept
title: Editor Integration
---

Ruff's built-in Rust language server (`ruff server`) and its setup across editors.

- LSP written in Rust, invoked via `ruff server`, unified into the Ruff CLI ([[sources/editors]], [[sources/editors-setup]]).
- Beta from v0.4.5, stabilized in v0.5.3; direct replacement for legacy `ruff-lsp` ([[sources/editors]], [[sources/versioning]]).
- Capabilities: diagnostics, code actions to fix, and formatting; runs alongside another Python LS for navigation ([[sources/editors]]).
- VS Code extension `charliermarsh.ruff` (2024.32.0+); Neovim, Helix, Sublime, Emacs, Zed, PyCharm (built-in 2025.3+) ([[sources/editors-setup]]).
- Disable older `ruff-lsp` to avoid conflicts ([[sources/editors-setup]], [[sources/editors]]).

## Links
[[concepts/ruff]] · [[concepts/versioning]] · [[concepts/integrations]] · [[sources/editors]] · [[sources/editors-setup]] · [[sources/versioning]]
