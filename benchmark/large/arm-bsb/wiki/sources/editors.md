# Source: Ruff Editor Integration Overview

- **Citation / URL:** https://docs.astral.sh/ruff/editors/
- **Raw file:** `benchmark/large/raw/editors.md`
- **Type:** Official documentation - editor integration overview

## Key claims

- Editor integration is provided via a built-in **Language Server (LSP)**, written in Rust, invoked via `ruff server`. It is a unified backend integrated directly into the Ruff CLI.
- **Version history:** available in beta starting with Ruff **v0.4.5**; stabilized in Ruff **v0.5.3**.
- **LSP capabilities:** surfacing Ruff diagnostics; code actions to fix issues; code formatting via Ruff's built-in formatter.
- Designed to work alongside another Python language server for navigation/autocompletion.
- **Legacy alternative:** native `ruff server` is a direct replacement for `ruff-lsp`, the previous language server implementation.

## Prose summary

Ruff ships its own LSP server as part of the CLI (`ruff server`), beta from v0.4.5 and stable from v0.5.3. The server surfaces diagnostics, offers fix code-actions, and formats using Ruff's formatter, while being intended to run alongside a separate Python language server that handles navigation and autocompletion. It supersedes the older standalone `ruff-lsp` implementation.
