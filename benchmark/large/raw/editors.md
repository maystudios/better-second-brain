# Ruff Editor Integration Overview

Source: https://docs.astral.sh/ruff/editors/

## Ruff Language Server

Editor integration via built-in Language Server (LSP), written in Rust, invoked via `ruff server`. Unified backend integrated directly into the Ruff CLI.

### Version History
- Available in beta starting with Ruff v0.4.5
- Stabilized in Ruff v0.5.3

### LSP Capabilities
- Surfacing Ruff diagnostics
- Code actions to fix issues
- Code formatting via Ruff's built-in formatter

Designed to work alongside another Python language server for navigation/autocompletion.

## Legacy Alternative

Native `ruff server` is a direct replacement for `ruff-lsp`, the previous language server implementation.
