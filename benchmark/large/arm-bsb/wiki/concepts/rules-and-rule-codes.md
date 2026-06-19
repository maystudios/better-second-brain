# Rules and Rule Codes

[[concepts/ruff]] ships **over 900 built-in rules** ([[sources/ruff-overview]]; [[sources/github-astral-sh-ruff]]; [[sources/tutorial]]; [[sources/rules]]), organized into families identified by a rule code.

## Rule code format

Ruff mirrors Flake8's convention: a rule code is a one-to-three-letter prefix plus three digits, e.g. `F401` ([[sources/linter]]). The prefix identifies the originating tool or plugin ([[sources/rules]]; [[sources/linter]]).

## Family prefix map

The rules reference maps each prefix to its source ([[sources/rules]]). Core checkers and a selection of common families:

| Prefix | Plugin/Source |
|--------|---------------|
| F | Pyflakes |
| E, W | pycodestyle |
| C90 | mccabe |
| I | isort |
| N | pep8-naming |
| D | pydocstyle |
| UP | pyupgrade |
| ANN | flake8-annotations |
| S | flake8-bandit |
| B | flake8-bugbear |
| A | flake8-builtins |
| C4 | flake8-comprehensions |
| SIM | flake8-simplify |
| PL | Pylint |
| RUF | Ruff-specific |
| AIR | Airflow |
| FAST | FastAPI |
| NPY | NumPy-specific |
| PD | pandas-vet |

The full table — over 60 prefixes spanning core checkers, 40+ re-implemented Flake8 plugins, framework-specific sets (Airflow, FastAPI, Django, NumPy, pandas), and Ruff's own `RUF` rules — is preserved verbatim in [[sources/rules]]. The linter reference repeats a shorter subset of these prefixes ([[sources/linter]]).

## Status markers

The rule catalog annotates rules with status markers ([[sources/rules]]):
- 🧪 **Preview** — unstable rules still in evaluation (see [[concepts/preview-mode]]).
- ⚠️ **Deprecated** — scheduled for future removal.
- ❌ **Removed** — no longer active.
- 🛠️ **Automatic fix available** — supports `--fix` (see [[concepts/fix-safety]]).

Rules without markers are stable / production-ready ([[sources/rules]]).

## Selection and defaults

Rules are enabled/disabled with `select`, `extend-select`, `ignore`, `extend-ignore`, and `per-file-ignores` ([[sources/linter]]), and the `ALL` meta-selector enables everything while auto-disabling conflicting rules ([[sources/linter]]). The default selection is `["E4", "E7", "E9", "F"]` ([[sources/settings]]; [[sources/configuration]]) — Pyflakes `F` rules plus a curated subset of pycodestyle `E` rules, excluding stylistic rules that overlap with formatters ([[sources/rules]]; [[sources/tutorial]]). This relationship is detailed in [[concepts/default-settings]] and [[concepts/formatter-lint-conflicts]].

## Open questions

- The plugin count varies across sources between "40+ Flake8 plugins" ([[sources/github-astral-sh-ruff]]) and "50+ plugins" ([[sources/tutorial]]; [[sources/faq]]); the exact figure is unresolved.
- The total rule count is consistently given only as "over 900" / "900+" with no precise number ([[sources/rules]]; [[sources/ruff-overview]]).
