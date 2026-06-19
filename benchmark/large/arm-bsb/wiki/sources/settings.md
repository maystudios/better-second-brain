# Source: Ruff Settings Reference

- **Citation / URL:** https://docs.astral.sh/ruff/settings/
- **Raw file:** `benchmark/large/raw/settings.md`
- **Type:** Official documentation - settings reference

## Key claims

### Top-level settings
| Setting | Default |
|---------|---------|
| `line-length` | `88` |
| `indent-width` | `4` |
| `target-version` | `"py310"` |
| `respect-gitignore` | `true` |
| `exclude` | `[".bzr", ".direnv", ".eggs", ".git", ".git-rewrite", ".hg", ".mypy_cache", ".nox", ".pants.d", ".pytype", ".ruff_cache", ".svn", ".tox", ".venv", "__pypackages__", "_build", "buck-out", "dist", "node_modules", "venv"]` |

### Format settings
| Setting | Default |
|---------|---------|
| `format.quote-style` | `"double"` |
| `format.indent-style` | `"space"` |
| `format.line-ending` | `"auto"` (auto, lf, cr-lf, native) |
| `format.docstring-code-format` | `false` |
| `format.docstring-code-line-length` | `"dynamic"` |

### Lint settings
| Setting | Default |
|---------|---------|
| `lint.select` | `["E4", "E7", "E9", "F"]` |
| `lint.dummy-variable-rgx` | `"^(_+|(_+[a-zA-Z0-9_]*[a-zA-Z0-9]+?))$"` |

### Behavioral defaults
- PEP 8 recommends 4-space indentation; this is Ruff's default.
- Double quotes are preferred (PEP 257) for docstrings/triple-quoted strings.
- Cache stored in the `.ruff_cache` directory by default.
- Common dev directories are excluded automatically.

## Prose summary

This page tabulates Ruff's default settings. It confirms the canonical root defaults (line-length 88, indent-width 4, target-version py310, respect-gitignore true) and provides the full default `exclude` list of version-control and build/cache directories. It restates the format defaults (double quotes, space indent, auto line-ending, docstring-code formatting off) and the lint defaults (the `["E4", "E7", "E9", "F"]` selection and the dummy-variable regex), and grounds several defaults in PEP 8 / PEP 257 rationale plus the `.ruff_cache` location.
