# Preview Mode

**Preview mode** is [[concepts/ruff]]'s opt-in channel for unstable features. It "enables a collection of unstable features such as new lint rules and fixes, formatter style changes, interface updates, and more," and exists to gather community feedback before general release ([[sources/preview]]).

## Enabling

Preview mode can be turned on per tool ([[sources/preview]]):
```bash
ruff check --preview
ruff format --preview
```
```toml
[tool.ruff.lint]
preview = true

[tool.ruff.format]
preview = true
```
It can be configured independently for linting and formatting ([[sources/preview]]).

## Gating of preview rules

Selecting a preview rule's code or prefix is not sufficient to enable it — preview mode itself must be active. A preview rule `HYP001` would NOT be enabled by `extend-select = ["HYP001"]`, `extend-select = ["HYP"]`, or `select = ["ALL"]` alone; enabling preview mode alongside any of these WOULD activate it ([[sources/preview]]).

The stricter `explicit-preview-rules = true` requires each preview rule to be named individually, so that only `--select ALL,HYP001` activates that specific rule ([[sources/preview]]).

## Deprecated rules under preview

"When preview mode is enabled, deprecated rules will be disabled." Explicitly selecting a deprecated rule raises an error, and deprecated rules are excluded from category/prefix selections ([[sources/preview]]). Deprecated and preview status are both surfaced as markers in the rule catalog ([[concepts/rules-and-rule-codes]]; [[sources/rules]]).

## Preview-only behaviors elsewhere

Several documented behaviors are explicitly preview-gated:
- The [[concepts/formatter]]'s method-chain layout change and its Markdown code-block formatting are preview-mode features ([[sources/formatter]]).
- `*.pyw` is a preview-only default inclusion for file discovery ([[sources/configuration]]).

## Relationship to versioning

Preview is tightly coupled to the [[concepts/versioning]] lifecycle: new rules launch in preview and require "at least one minor release before being promoted to stable," and preview-only changes are non-breaking patch-level changes ([[sources/versioning]]).

## Open questions

- `HYP001` / `HYP` are used as illustrative placeholders in the source ([[sources/preview]]); they are not stated to be real rule codes.
