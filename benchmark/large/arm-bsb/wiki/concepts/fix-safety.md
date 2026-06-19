# Fix Safety

When [[concepts/linter|the linter]] applies automatic fixes, each fix carries an **applicability level**. By default, `ruff check --fix` applies all "safe" fixes ([[sources/linter]]).

## Safe vs. unsafe fixes

- **Safe fixes** preserve runtime behavior and only remove comments when deleting entire statements ([[sources/linter]]).
- **Unsafe fixes** may change runtime behavior, remove comments, or alter exceptions ([[sources/linter]]).

The canonical example of an unsafe fix is `RUF015`, which replaces `list(...)[0]` with `next(iter(...))`; this is unsafe because it changes the raised exception from `IndexError` to `StopIteration` ([[sources/linter]]).

## Controlling fix safety

Unsafe fixes can be displayed or applied explicitly ([[sources/linter]]):
- `ruff check --unsafe-fixes` displays them.
- `ruff check --fix --unsafe-fixes` applies them.
- `[tool.ruff] unsafe-fixes = true` enables them via config.

Fix safety can be overridden per rule with `extend-safe-fixes` and `extend-unsafe-fixes`, e.g. `extend-safe-fixes = ["F601"]` and `extend-unsafe-fixes = ["UP034"]` ([[sources/linter]]).

Whether a rule is fixable at all is controlled by `fixable` / `unfixable`; the default is `fixable = ["ALL"]` ([[sources/configuration]]; [[sources/github-astral-sh-ruff]]), and a rule can be excluded with e.g. `unfixable = ["F401"]` ([[sources/linter]]). Rules that support `--fix` are marked with the 🛠️ "automatic fix available" status marker in the rule catalog ([[sources/rules]]).

## Stabilization ladder

Fix applicability is not static across releases. Under Ruff's [[concepts/versioning]] policy, fix applicability "progresses through Display → Unsafe → Safe levels" ([[sources/versioning]]), and promoting a safe fix to stable is classified as a breaking (minor-version) change ([[sources/versioning]]).

## Open questions

- The sources give only one concrete unsafe-fix example (`RUF015`) and one safe/unsafe override example each ([[sources/linter]]); they do not provide a full list of which rules ship safe versus unsafe fixes by default.
