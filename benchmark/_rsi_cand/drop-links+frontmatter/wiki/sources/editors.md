---
type: source
title: "Ruff Editor Integration Overview"
url: https://docs.astral.sh/ruff/editors/
---

## Key claims
- Editor integration via a built-in Language Server (LSP) written in Rust, invoked with `ruff server`; unified backend in the Ruff CLI.
- Available in beta from Ruff v0.4.5; stabilized in v0.5.3.
- LSP capabilities: surface diagnostics, code actions to fix issues, formatting via Ruff's formatter.
- Designed to run alongside another Python language server for navigation/autocompletion.
- Native `ruff server` is a direct replacement for the previous `ruff-lsp` implementation.
