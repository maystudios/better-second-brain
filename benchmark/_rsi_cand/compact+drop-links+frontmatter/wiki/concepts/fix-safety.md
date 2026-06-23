---
type: concept
title: Fix Safety
---

Ruff's classification of automatic fixes as safe or unsafe based on whether they can change runtime behavior.

- Safe fixes preserve runtime behavior and only remove comments when deleting whole statements .
- Unsafe fixes may change behavior, e.g. `RUF015` rewriting `list(...)[0]`→`next(iter(...))` swaps IndexError for StopIteration .
- `ruff check --fix` applies safe fixes by default; `--unsafe-fixes` opts into unsafe ones .
- Per-rule overrides via `extend-safe-fixes`/`extend-unsafe-fixes`; `fixable`/`unfixable` gate which rules fix .
- Fix applicability matures through Display → Unsafe → Safe across releases .

## Sources
- https://docs.astral.sh/ruff/linter/
- https://docs.astral.sh/ruff/tutorial/
- https://docs.astral.sh/ruff/configuration/
- https://docs.astral.sh/ruff/versioning/
