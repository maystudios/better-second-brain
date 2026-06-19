# Answers — arm-bsb (Ruff)

1: Ruff is an extremely fast Python linter and code formatter written in **Rust**, designed to replace a fragmented set of traditional Python quality tools with a single unified solution. It is maintained by **Astral** (described as "the company behind the uv package manager and ty type checker") and distributed under the MIT License. [[sources/ruff-overview]] https://docs.astral.sh/ruff/ ; [[sources/github-astral-sh-ruff]] https://github.com/astral-sh/ruff

2: Ruff consolidates/replaces: Flake8 (plus dozens of plugins; core checkers Pyflakes/pycodestyle and 40+/50+ Flake8 plugins re-implemented natively, e.g. flake8-bugbear, flake8-comprehensions, flake8-docstrings, flake8-django), Black, isort, pydocstyle, pyupgrade (most rules), autoflake, plus pandas-vet, pep8-naming, yesqa, and eradicate. [[sources/ruff-overview]] https://docs.astral.sh/ruff/ ; [[sources/github-astral-sh-ruff]] https://github.com/astral-sh/ruff ; [[sources/faq]] https://docs.astral.sh/ruff/faq/

3: The default `lint.select` is `["E4", "E7", "E9", "F"]` — Pyflakes `F` rules plus a curated subset of pycodestyle `E` rules (deliberately excluding stylistic rules that overlap with the formatter). [[sources/settings]] https://docs.astral.sh/ruff/settings/ ; [[sources/configuration]] https://docs.astral.sh/ruff/configuration/

4: Default `line-length` = `88` (matches Black) and default `indent-width` = `4` (per PEP 8). [[sources/settings]] https://docs.astral.sh/ruff/settings/ ; [[sources/configuration]] https://docs.astral.sh/ruff/configuration/ ; [[sources/github-astral-sh-ruff]] https://github.com/astral-sh/ruff

5: (inferred) The wiki lists both pairs as the rule-selection keys (`lint.select`, `lint.extend-select`, `lint.ignore`, `lint.extend-ignore`) but does not state the semantics in one sentence. Based on the `extend-` naming and the tutorial's framing of "adding rule sets via `extend-select`" (e.g. `["UP"]`), `select`/`ignore` set/replace the active rule list, whereas `extend-select`/`extend-ignore` add rules on top of the existing (default or inherited) selection rather than replacing it. [[sources/linter]] https://docs.astral.sh/ruff/linter/ ; [[sources/tutorial]] https://docs.astral.sh/ruff/tutorial/

6: The three config file formats are `pyproject.toml` (under the `[tool.ruff]` section), `ruff.toml`, and `.ruff.toml` (the latter two omit the `[tool.ruff]` prefix). When more than one exists in the same directory, precedence is `.ruff.toml` > `ruff.toml` > `pyproject.toml`. [[sources/configuration]] https://docs.astral.sh/ruff/configuration/

7: No — by default `ruff check --fix` applies only "safe" fixes. To enable unsafe fixes: `ruff check --fix --unsafe-fixes` on the CLI (or `ruff check --unsafe-fixes` to display them), or set `[tool.ruff] unsafe-fixes = true` in config. [[sources/linter]] https://docs.astral.sh/ruff/linter/

8: The formatter defaults are `quote-style = "double"` and `indent-style = "space"`. Ruff targets Black compatibility as a drop-in replacement, achieving ">99.9% of lines formatted identically" on large Black-formatted projects like Django and Zulip. [[sources/settings]] https://docs.astral.sh/ruff/settings/ ; [[sources/formatter]] https://docs.astral.sh/ruff/formatter/ ; [[sources/faq]] https://docs.astral.sh/ruff/faq/

9: Enable docstring code formatting with `docstring-code-format = true` (in `[tool.ruff.format]`). The `docstring-code-line-length` setting defaults to `"dynamic"` (it respects the surrounding code's line length). [[sources/formatter]] https://docs.astral.sh/ruff/formatter/ ; [[sources/settings]] https://docs.astral.sh/ruff/settings/

10: F = Pyflakes; E/W = pycodestyle; I = isort; UP = pyupgrade; B = flake8-bugbear; SIM = flake8-simplify; S = flake8-bandit; RUF = Ruff-specific. [[sources/rules]] https://docs.astral.sh/ruff/rules/ ; [[sources/linter]] https://docs.astral.sh/ruff/linter/

11: No — Ruff does not follow standard SemVer. It uses a custom scheme where the **minor** version number is used for breaking changes and the **patch** version number for bug fixes. (`0.x` indicates an unstable API; once stability is reached, standard SemVer will apply.) [[sources/versioning]] https://docs.astral.sh/ruff/versioning/

12: A preview-only rule (e.g. HYP001) is activated only when preview mode itself is active (`ruff check --preview`, or `[tool.ruff.lint] preview = true`). Selecting it explicitly via `extend-select = ["HYP001"]`, `extend-select = ["HYP"]`, or `select = ["ALL"]` alone does NOT enable it; enabling preview mode alongside any of those selections does. (With `explicit-preview-rules = true`, the rule must be named individually, e.g. `--select ALL,HYP001`.) [[sources/preview]] https://docs.astral.sh/ruff/preview/

13: The built-in language server is run with `ruff server`. It was available in beta starting with Ruff **v0.4.5** and was stabilized in **v0.5.3**. The official VS Code extension ID is **`charliermarsh.ruff`** (recommended 2024.32.0+; repo github.com/astral-sh/ruff-vscode). [[sources/editors]] https://docs.astral.sh/ruff/editors/ ; [[sources/editors-setup]] https://docs.astral.sh/ruff/editors/setup/

14: No — according to these docs Ruff is a linter, not a type checker, and cannot replace mypy/pyright. Type checkers such as Mypy, Pyright, and Pyre catch type errors Ruff misses and are described as complementary. [[sources/faq]] https://docs.astral.sh/ruff/faq/
