---
type: concept
title: CI & Tooling Integrations
---

How Ruff plugs into pre-commit, CI pipelines, and containerized workflows.

- pre-commit via `astral-sh/ruff-pre-commit` (rev v0.15.18), hooks `ruff-check`/`ruff-format`; with `--fix`, run check before format .
- GitHub Actions: `astral-sh/ruff-action@v3` with `version`/`args`/`src` options .
- GitLab CI/CD: alpine image plus `--output-format=gitlab` code-quality report; `ruff format --diff` .
- Docker tags follow `ruff:{version}-{base}` (alpine, debian-slim, etc.) .
- mdformat-ruff formats Python code blocks inside Markdown .

## Sources
- https://docs.astral.sh/ruff/integrations/
- https://docs.astral.sh/ruff/tutorial/
- https://docs.astral.sh/ruff/installation/
