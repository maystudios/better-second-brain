# Source: Ruff Tutorial

- **Citation / URL:** https://docs.astral.sh/ruff/tutorial/
- **Raw file:** `benchmark/large/raw/tutorial.md`
- **Type:** Official documentation — tutorial

## Key claims

- Getting started workflow with uv:
  ```bash
  uv init --lib numbers
  uv add --dev ruff
  uv run ruff check
  uv run ruff check --fix
  uv run ruff format
  ```
- "Ruff highlights problems like unused imports; many are fixable with `--fix`."
- **Config discovery:** Ruff searches `pyproject.toml`, `ruff.toml`, or `.ruff.toml`, starting from the target file's directory and moving up through parent directories.
- `pyproject.toml` uses `[tool.ruff]` / `[tool.ruff.lint]`; `ruff.toml` omits the `tool.ruff` prefix.
- **Default rule selection:** Ruff enables Flake8's `F` rules plus a subset of `E` rules, "deliberately omitting stylistic rules that overlap with formatters."
- Adding rule sets via `extend-select` (e.g., `["UP"]`, or `["UP", "D"]` with `[tool.ruff.lint.pydocstyle] convention = "google"`).
- **Ignoring errors:** single line `# noqa: UP035`; whole file `# ruff: noqa: UP035`.
- Adding rules to existing codebases: `uv run ruff check --select UP035 --add-noqa .`
- **pre-commit integration** with `astral-sh/ruff-pre-commit`, `rev: v0.15.18`, hooks `ruff-check` and `ruff-format`.

## Key defaults (quoted)

- Line length: **88 characters**.
- Default rule set focuses on errors and common issues, avoiding formatter overlap.
- **Over 900 lint rules across 50+ plugins.**
- `--fix` flag automatically corrects fixable violations.

## Prose summary

The tutorial walks a new user from an empty `uv` library project through linting, auto-fixing, and formatting. It introduces the upward config-discovery algorithm, the convention that the default rule set deliberately avoids stylistic rules that would conflict with the formatter, and the mechanics of extending rule selection and suppressing violations (`# noqa`, `# ruff: noqa`, `--add-noqa`). It pins the same line-length (88), rule count (900+ across 50+ plugins), and pre-commit revision (v0.15.18) seen elsewhere in the corpus.
