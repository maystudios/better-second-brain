# Ruff Settings Reference

Source: https://docs.astral.sh/ruff/settings/

## Top-Level Settings

| Setting | Default |
|---------|---------|
| `line-length` | `88` |
| `indent-width` | `4` |
| `target-version` | `"py310"` |
| `respect-gitignore` | `true` |
| `exclude` | `[".bzr", ".direnv", ".eggs", ".git", ".git-rewrite", ".hg", ".mypy_cache", ".nox", ".pants.d", ".pytype", ".ruff_cache", ".svn", ".tox", ".venv", "__pypackages__", "_build", "buck-out", "dist", "node_modules", "venv"]` |

## Format Settings

| Setting | Default |
|---------|---------|
| `format.quote-style` | `"double"` |
| `format.indent-style` | `"space"` |
| `format.line-ending` | `"auto"` (auto, lf, cr-lf, native) |
| `format.docstring-code-format` | `false` |
| `format.docstring-code-line-length` | `"dynamic"` |

## Lint Settings

| Setting | Default |
|---------|---------|
| `lint.select` | `["E4", "E7", "E9", "F"]` |
| `lint.dummy-variable-rgx` | `"^(_+|(_+[a-zA-Z0-9_]*[a-zA-Z0-9]+?))$"` |

## Behavioral Defaults

- PEP 8 recommends 4-space indentation; Ruff default
- Double quotes preferred (PEP 257) for docstrings/triple-quoted strings
- Cache stored in `.ruff_cache` directory by default
- Common dev directories excluded automatically
