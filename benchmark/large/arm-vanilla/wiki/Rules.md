# Rules

[[Ruff]] ships over **900 lint rules** drawn from Pyflakes, pycodestyle, isort, and native reimplementations of 50+ popular Flake8 plugins. The [[Linter]] decides which of these run via `select`/`ignore`; this page is the map of what's available.

## Prefix-to-plugin map

Each rule code is a prefix plus three digits (e.g. `F401`). The prefix tells you which tool the rule came from:

| Prefix | Plugin / Source |
|--------|-----------------|
| F | Pyflakes |
| E, W | pycodestyle |
| C90 | mccabe |
| I | isort |
| N | pep8-naming |
| D | pydocstyle |
| UP | pyupgrade |
| ANN | flake8-annotations |
| ASYNC | flake8-async |
| S | flake8-bandit |
| B | flake8-bugbear |
| A | flake8-builtins |
| COM | flake8-commas |
| C4 | flake8-comprehensions |
| SIM | flake8-simplify |
| PTH | flake8-use-pathlib |
| PD | pandas-vet |
| PL | Pylint |
| NPY | NumPy-specific |
| RUF | Ruff-specific |
| AIR | Airflow |
| ERA | eradicate |
| FAST | FastAPI |
| YTT | flake8-2020 |
| BLE | flake8-blind-except |
| FBT | flake8-boolean-trap |
| CPY | flake8-copyright |
| DTZ | flake8-datetimez |
| T10 | flake8-debugger |
| DJ | flake8-django |
| EM | flake8-errmsg |
| EXE | flake8-executable |
| FIX | flake8-fixme |
| FA | flake8-future-annotations |
| INT | flake8-gettext |
| ISC | flake8-implicit-str-concat |
| ICN | flake8-import-conventions |
| LOG | flake8-logging |
| G | flake8-logging-format |
| INP | flake8-no-pep420 |
| PIE | flake8-pie |
| T20 | flake8-print |
| PYI | flake8-pyi |
| PT | flake8-pytest-style |
| Q | flake8-quotes |
| RSE | flake8-raise |
| RET | flake8-return |
| SLF | flake8-self |
| SLOT | flake8-slots |
| TID | flake8-tidy-imports |
| TD | flake8-todos |
| TC | flake8-type-checking |
| ARG | flake8-unused-arguments |
| FLY | flynt |
| PERF | Perflint |
| PGH | pygrep-hooks |
| DOC | pydoclint |
| FURB | refurb |
| TRY | tryceratops |

## Status markers

In the rule reference, each rule may carry a marker:

- 🧪 **Preview** - unstable, still in evaluation (requires [[Preview|preview mode]])
- ⚠️ **Deprecated** - scheduled for removal
- ❌ **Removed** - no longer active
- 🛠️ **Automatic fix available** - supports `--fix` (see [[Linter]])

Rules with no marker are stable and production-ready.

## The default set

By default Ruff enables Pyflakes' `F` rules plus a curated subset of `E` rules, excluding stylistic rules that overlap with the [[Formatter]]. To turn on more, use prefixes in `select`/`extend-select` - see the [[Tutorial]] and [[Configuration]] for examples.
