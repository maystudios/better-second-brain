# Answers — arm-vanilla

1. Ruff is an extremely fast Python linter and code formatter. It is written in Rust and is maintained by Astral (the same company behind the `uv` package manager and the `ty` type checker). (Ruff.md)

2. A single install of Ruff stands in for Flake8 (plus dozens of its plugins), Black, isort, pydocstyle, pyupgrade, and autoflake. It also natively reimplements 50+ popular Flake8 plugins. (Ruff.md, Rules.md)

3. The default `lint.select` is `["E4", "E7", "E9", "F"]` — i.e. Pyflakes' `F` rules plus a curated subset of `E` (pycodestyle) rules, excluding stylistic rules that overlap with the formatter. (Configuration.md, Rules.md)

4. Default `line-length` is `88` (matches Black) and default `indent-width` is `4`. (Configuration.md)

5. `select`/`ignore` set the rule list outright, while `extend-select`/`extend-ignore` add to / remove from an inherited set rather than replacing it. `extend-select` adds rules to an inherited set; `extend-ignore` removes rules from an inherited set. (Linter.md)

6. The three config file formats are `pyproject.toml` (settings under a `[tool.ruff]` header), `ruff.toml` (same schema, no prefix), and `.ruff.toml` (same schema, no prefix). When several sit in one directory, precedence is `.ruff.toml` > `ruff.toml` > `pyproject.toml`. (Configuration.md)

7. No. By default `ruff check --fix` applies only safe fixes (which preserve runtime behavior). To enable unsafe fixes, pass `--unsafe-fixes` (e.g. `ruff check --fix --unsafe-fixes`; `ruff check --unsafe-fixes` alone just displays them). You can also reclassify fix safety per rule via `extend-safe-fixes`/`extend-unsafe-fixes`. (Linter.md)

8. The formatter defaults are `quote-style = "double"` and `indent-style = "space"`. Ruff targets Black's stable code style and reports formatting >99.9% of lines identically on large Black-formatted projects (e.g. Django and Zulip). (Configuration.md, Formatter.md)

9. Enable docstring code formatting by setting `docstring-code-format = true` under `[tool.ruff.format]`. The `docstring-code-line-length` key defaults to `"dynamic"`, which follows the surrounding code's line limit. (Configuration.md, Formatter.md)

10. F = Pyflakes; E/W = pycodestyle; I = isort; UP = pyupgrade; B = flake8-bugbear; SIM = flake8-simplify; S = flake8-bandit; RUF = Ruff-specific. (Rules.md)

11. No, Ruff does not follow standard SemVer — it uses a custom versioning scheme. The minor version number carries breaking changes, and the patch number carries bug fixes (the current `0.x` line spreads breaking changes across minor releases rather than major ones). There is no stable public API yet; once it reaches stability, standard SemVer will take over. (Versioning.md)

12. A preview-only rule like HYP001 is activated only when preview mode is on. Simply naming it is not enough — `extend-select = ["HYP001"]`, `extend-select = ["HYP"]`, and `select = ["ALL"]` do NOT enable it on their own. Each of those plus `preview = true` activates it. So no, selecting it explicitly or via `select = ["ALL"]` does not enable it without preview mode. (With `explicit-preview-rules = true`, you must name each preview rule individually, e.g. `--select ALL,HYP001`.) (Preview.md)

13. The built-in language server is run with `ruff server`. It became available in beta in v0.4.5 and stabilized in v0.5.3. The official VS Code extension ID is `charliermarsh.ruff` (version 2024.32.0 or later recommended). (Editors.md)

14. No. According to these docs Ruff is a linter and code formatter; the docs describe Astral's separate `ty` tool as the type checker, and nowhere state that Ruff is a type checker or a replacement for mypy/pyright. (inferred — the wiki does not directly address replacing mypy/pyright, but it consistently presents Ruff only as a linter/formatter and names `ty` as the type checker) (Ruff.md)
