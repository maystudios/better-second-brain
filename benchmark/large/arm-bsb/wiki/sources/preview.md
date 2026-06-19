# Source: Ruff Preview Mode

- **Citation / URL:** https://docs.astral.sh/ruff/preview/
- **Raw file:** `benchmark/large/raw/preview.md`
- **Type:** Official documentation — preview mode

## Key claims

- "Preview mode enables a collection of unstable features such as new lint rules and fixes, formatter style changes, interface updates, and more." It is an opt-in mechanism for community feedback before general release.
- **Enabling:** CLI flags `ruff check --preview` / `ruff format --preview`; or config `[tool.ruff.lint] preview = true` and `[tool.ruff.format] preview = true`. Preview can be configured **independently** for linting and formatting.
- **Rule selection behavior:** preview rules require preview mode to be active. A preview rule `HYP001` would NOT be enabled by `extend-select = ["HYP001"]`, `extend-select = ["HYP"]`, or `select = ["ALL"]` alone. Enabling preview mode alongside any of these selections WOULD activate it.
- **Explicit preview rules:** `explicit-preview-rules = true` requires each preview rule to be individually named; with it enabled, only `--select ALL,HYP001` activates that specific rule.
- **Deprecated rules:** "When preview mode is enabled, deprecated rules will be disabled." Explicitly selecting a deprecated rule raises an error; they remain excluded from category/prefix selections.

## Notable quotes

> "Preview mode enables a collection of unstable features such as new lint rules and fixes, formatter style changes, interface updates, and more."

> "When preview mode is enabled, deprecated rules will be disabled."

## Prose summary

Preview mode is Ruff's opt-in channel for unstable features (new rules/fixes, formatter style changes, interface updates) gathered for community feedback ahead of stabilization. It can be enabled per-tool (lint vs. format) via flag or config. The page clarifies a subtle gating rule: simply selecting a preview rule's code or prefix — even via `ALL` — does not enable it; preview mode itself must be on. The stricter `explicit-preview-rules` setting demands each preview rule be named individually. When preview is on, deprecated rules are disabled, and explicitly selecting one errors.
