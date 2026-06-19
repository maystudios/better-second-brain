---
type: concept
title: Fix Safety
---

Ruff's classification of automatic fixes as safe or unsafe based on whether they can change runtime behavior.

- Safe fixes preserve runtime behavior and only remove comments when deleting whole statements ([[sources/linter]]).
- Unsafe fixes may change behavior, e.g. `RUF015` rewriting `list(...)[0]`→`next(iter(...))` swaps IndexError for StopIteration ([[sources/linter]]).
- `ruff check --fix` applies safe fixes by default; `--unsafe-fixes` opts into unsafe ones ([[sources/linter]], [[sources/tutorial]]).
- Per-rule overrides via `extend-safe-fixes`/`extend-unsafe-fixes`; `fixable`/`unfixable` gate which rules fix ([[sources/linter]], [[sources/configuration]]).
- Fix applicability matures through Display → Unsafe → Safe across releases ([[sources/versioning]]).

## Links
[[concepts/linter]] · [[concepts/rules-and-plugins]] · [[concepts/versioning]] · [[sources/linter]] · [[sources/versioning]] · [[sources/configuration]]
