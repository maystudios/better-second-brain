# Default Settings

This page tabulates the default configuration values for [[concepts/ruff]]. The mechanics of how configuration is loaded and overridden live in [[concepts/configuration]].

## Top-level defaults

| Setting | Default | Sources |
|---------|---------|---------|
| `line-length` | `88` (matches Black) | [[sources/settings]]; [[sources/configuration]]; [[sources/github-astral-sh-ruff]] |
| `indent-width` | `4` | [[sources/settings]]; [[sources/configuration]]; [[sources/github-astral-sh-ruff]] |
| `target-version` | `"py310"` | [[sources/settings]]; [[sources/configuration]]; [[sources/github-astral-sh-ruff]] |
| `respect-gitignore` | `true` | [[sources/settings]] |

The default `exclude` list covers version-control and build/cache directories: `.bzr`, `.direnv`, `.eggs`, `.git`, `.git-rewrite`, `.hg`, `.mypy_cache`, `.nox`, `.pants.d`, `.pytype`, `.ruff_cache`, `.svn`, `.tox`, `.venv`, `__pypackages__`, `_build`, `buck-out`, `dist`, `node_modules`, `venv` ([[sources/settings]]). The configuration page summarizes this list as covering `.git`, `.venv`, `__pycache__`, `build`, `dist`, etc. ([[sources/configuration]]).

The line-length default of 88 is described as matching Black ([[sources/configuration]]), and the 4-space indent is grounded in PEP 8's recommendation ([[sources/settings]]). These defaults are also confirmed in the README's example config ([[sources/github-astral-sh-ruff]]).

## Lint defaults

| Setting | Default | Sources |
|---------|---------|---------|
| `lint.select` | `["E4", "E7", "E9", "F"]` | [[sources/settings]]; [[sources/configuration]] |
| `lint.ignore` | `[]` | [[sources/configuration]] |
| `lint.fixable` | `["ALL"]` | [[sources/configuration]]; [[sources/github-astral-sh-ruff]] |
| `lint.unfixable` | `[]` | [[sources/configuration]] |
| `lint.dummy-variable-rgx` | `"^(_+|(_+[a-zA-Z0-9_]*[a-zA-Z0-9]+?))$"` | [[sources/settings]]; [[sources/configuration]] |

The default `select` enables Pyflakes `F` rules plus a curated subset of pycodestyle `E` rules, deliberately excluding stylistic rules that overlap with the formatter ([[sources/rules]]; [[sources/tutorial]]; [[sources/configuration]]). The full meaning of these codes is covered in [[concepts/rules-and-rule-codes]] and the default-selection rationale in [[concepts/formatter-lint-conflicts]].

## Format defaults

| Setting | Default | Sources |
|---------|---------|---------|
| `format.quote-style` | `"double"` | [[sources/settings]]; [[sources/configuration]]; [[sources/formatter]] |
| `format.indent-style` | `"space"` | [[sources/settings]]; [[sources/configuration]]; [[sources/formatter]] |
| `format.line-ending` | `"auto"` (auto, lf, cr-lf, native) | [[sources/settings]]; [[sources/configuration]] |
| `format.skip-magic-trailing-comma` | `false` | [[sources/configuration]] |
| `format.docstring-code-format` | `false` | [[sources/settings]]; [[sources/configuration]] |
| `format.docstring-code-line-length` | `"dynamic"` | [[sources/settings]]; [[sources/configuration]] |

Double quotes are the default and are grounded in PEP 257 for docstrings/triple-quoted strings ([[sources/settings]]). `indent-style` supports `"space"` or `"tab"` ([[sources/formatter]]). The magic trailing comma is respected by default (equivalent to `skip-magic-trailing-comma = false`), like Black ([[sources/formatter]]; [[sources/configuration]]). Full formatter behavior is in [[concepts/formatter]].

## Cache

The cache is stored in a `.ruff_cache` directory by default ([[sources/settings]]), which is also one of the auto-excluded directories ([[sources/settings]]).

## Open questions

- None beyond the general note that defaults can change between minor versions under Ruff's [[concepts/versioning]] policy, where "adding/removing stable rules from defaults" is classified as a breaking change ([[sources/versioning]]).
