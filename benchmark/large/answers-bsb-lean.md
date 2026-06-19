# Answers - arm-bsb-lean (Ruff)

1: Ruff is an extremely fast Python linter and code formatter written in Rust. It is maintained by Astral (the makers of the uv package manager and the ty type checker) and is MIT-licensed. [[sources/ruff-overview]] https://docs.astral.sh/ruff/ ; [[sources/github-astral-sh-ruff]] https://github.com/astral-sh/ruff

2: Ruff aims to replace/consolidate a stack of standalone tools into one binary: Flake8 (and its plugins), Black, isort, pydocstyle, pyupgrade, and autoflake. It also reimplements 50+ Flake8 plugins natively plus tools like pandas-vet and pep8-naming. [[sources/ruff-overview]] https://docs.astral.sh/ruff/ ; [[sources/faq]] https://docs.astral.sh/ruff/faq/

3: The default `lint.select` is `["E4","E7","E9","F"]` - the Pyflakes `F` rules plus a curated subset of pycodestyle `E` rules (deliberately omitting stylistic rules that overlap the formatter). [[sources/settings]] https://docs.astral.sh/ruff/settings/ ; [[sources/configuration]] https://docs.astral.sh/ruff/configuration/

4: Default `line-length=88` (matching Black) and default `indent-width=4`. [[sources/settings]] https://docs.astral.sh/ruff/settings/ ; [[sources/github-astral-sh-ruff]] https://github.com/astral-sh/ruff

5: `select`/`ignore` set the rule selection outright (replacing the defaults), whereas `extend-select`/`extend-ignore` add to (extend) the existing selection/ignore lists rather than replacing them. (inferred - the wiki documents both `select`/`ignore` and `extend-select`/`extend-ignore` as selection settings and uses `extend-select` to *add* rule categories like `["UP"]` or `["D"]`, implying extend variants augment rather than replace.) [[sources/linter]] https://docs.astral.sh/ruff/linter/ ; [[sources/tutorial]] https://docs.astral.sh/ruff/tutorial/

6: The three config formats are `pyproject.toml` (under the `[tool.ruff]` header), `ruff.toml`, and `.ruff.toml`. When multiple exist in the same directory the precedence is `.ruff.toml` > `ruff.toml` > `pyproject.toml`. [[sources/configuration]] https://docs.astral.sh/ruff/configuration/

7: No - by default `ruff check --fix` applies only safe fixes. To enable unsafe fixes you pass the `--unsafe-fixes` flag (per-rule adjustment is also possible via `extend-safe-fixes`/`extend-unsafe-fixes`). [[sources/linter]] https://docs.astral.sh/ruff/linter/ ; [[sources/tutorial]] https://docs.astral.sh/ruff/tutorial/

8: Formatter defaults are `quote-style="double"` and `indent-style="space"` (4-space indent width). Ruff targets Black drop-in compatibility, formatting >99.9% of lines identically to Black on real-world projects like Django and Zulip, adhering to Black's stable style. [[sources/formatter]] https://docs.astral.sh/ruff/formatter/ ; [[sources/settings]] https://docs.astral.sh/ruff/settings/

9: Enable docstring code formatting by setting `docstring-code-format=true` (it formats code in doctest examples, CommonMark fenced blocks, and reST literal blocks; invalid code is skipped). `docstring-code-line-length` defaults to `"dynamic"`. [[sources/formatter]] https://docs.astral.sh/ruff/formatter/ ; [[sources/settings]] https://docs.astral.sh/ruff/settings/

10: F = Pyflakes; E/W = pycodestyle; I = isort; UP = pyupgrade; B = flake8-bugbear; SIM = flake8-simplify; S = flake8-bandit (bandit); RUF = Ruff-specific rules. [[sources/rules]] https://docs.astral.sh/ruff/rules/ ; [[sources/linter]] https://docs.astral.sh/ruff/linter/

11: Ruff does not follow standard SemVer (it diverges until a stable API at 1.0.0). In its pre-1.0 custom scheme, a minor version bump signals breaking changes (e.g. option removal, incompatible config changes, rule promotions/default changes, stable formatter style changes, EOL Python drops), while a patch version bump signals non-breaking changes/bug fixes (e.g. bug fixes, new Python support, new unsafe/preview fixes, new preview rules, new LSP capabilities). [[sources/versioning]] https://docs.astral.sh/ruff/versioning/

12: A preview-only rule (e.g. HYP001) is activated only when preview mode is on (via the `--preview` CLI flag or `preview=true` in `[tool.ruff.lint]`/`[tool.ruff.format]`). Selecting it explicitly or via `select=["ALL"]` does NOT enable it without preview mode active. If `explicit-preview-rules=true`, each preview rule must be named individually (e.g. `--select ALL,HYP001`). [[sources/preview]] https://docs.astral.sh/ruff/preview/ ; [[sources/rules]] https://docs.astral.sh/ruff/rules/

13: The built-in language server is run with the `ruff server` command. It was available in beta from Ruff v0.4.5 and was stabilized in v0.5.3. The official VS Code extension ID is `charliermarsh.ruff` (recommended 2024.32.0+). [[sources/editors]] https://docs.astral.sh/ruff/editors/ ; [[sources/editors-setup]] https://docs.astral.sh/ruff/editors/setup/

14: No. According to these docs, "Ruff is a linter, not a type checker" - it is complementary to (not a replacement for) Mypy/Pyright/Pyre. [[sources/faq]] https://docs.astral.sh/ruff/faq/
