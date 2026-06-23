---
type: concept
title: Editor Integration
---

Ruff's built-in Rust language server (`ruff server`) and its setup across editors.

- LSP written in Rust, invoked via `ruff server`, unified into the Ruff CLI .
- Beta from v0.4.5, stabilized in v0.5.3; direct replacement for legacy `ruff-lsp` .
- Capabilities: diagnostics, code actions to fix, and formatting; runs alongside another Python LS for navigation .
- VS Code extension `charliermarsh.ruff` (2024.32.0+); Neovim, Helix, Sublime, Emacs, Zed, PyCharm (built-in 2025.3+) .
- Disable older `ruff-lsp` to avoid conflicts .

## Sources
- https://docs.astral.sh/ruff/editors/
- https://docs.astral.sh/ruff/editors/setup/
- https://docs.astral.sh/ruff/versioning/
