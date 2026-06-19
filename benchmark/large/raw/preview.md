# Ruff Preview Mode

Source: https://docs.astral.sh/ruff/preview/

## Overview

"Preview mode enables a collection of unstable features such as new lint rules and fixes, formatter style changes, interface updates, and more." It is an opt-in mechanism for community feedback before general release.

## Enabling Preview Mode

CLI flag:
```bash
ruff check --preview
ruff format --preview
```

Configuration:
```toml
[tool.ruff.lint]
preview = true

[tool.ruff.format]
preview = true
```

Preview can be configured independently for linting and formatting.

## Rule Selection Behavior

Preview rules require preview mode to be active. A preview rule `HYP001` would NOT be enabled by:
- `extend-select = ["HYP001"]`
- `extend-select = ["HYP"]`
- `select = ["ALL"]`

Enabling preview mode alongside any of these selections WOULD activate the preview rule.

## Explicit Preview Rules

`explicit-preview-rules` requires each preview rule to be individually named:
```toml
[tool.ruff.lint]
preview = true
explicit-preview-rules = true
```
With this enabled, only `--select ALL,HYP001` activates that specific rule.

## Deprecated Rules

"When preview mode is enabled, deprecated rules will be disabled." Explicitly selecting a deprecated rule raises an error; they remain excluded from category/prefix selections.
