# Preview

Preview mode is [[Ruff]]'s opt-in channel for unstable features — new lint rules and fixes, formatter style changes, and interface updates — released early so the community can give feedback before they become stable. It can be turned on independently for the [[Linter]] and the [[Formatter]].

## Enabling it

```bash
ruff check --preview
ruff format --preview
```

Or in [[Configuration|config]]:

```toml
[tool.ruff.lint]
preview = true

[tool.ruff.format]
preview = true
```

## How preview rules are selected

A preview rule only runs when preview mode is active. Simply naming it isn't enough — given a hypothetical preview rule `HYP001`, none of these enable it on their own:

- `extend-select = ["HYP001"]`
- `extend-select = ["HYP"]`
- `select = ["ALL"]`

Each of those **plus** `preview = true` would activate it. (This is why a preview-marked rule in the [[Rules]] catalog won't fire under a plain `select = ["ALL"]`.)

For maximum control, `explicit-preview-rules` requires every preview rule to be named individually:

```toml
[tool.ruff.lint]
preview = true
explicit-preview-rules = true
```

With that set, only something like `--select ALL,HYP001` enables the specific rule.

## Deprecated rules under preview

When preview mode is on, deprecated rules are disabled. Explicitly selecting a deprecated rule raises an error, and they stay excluded from category/prefix selections.

## See also

- [[Versioning]] — how preview features graduate to stable
- [[Rules]] — the 🧪 preview marker in the catalog
