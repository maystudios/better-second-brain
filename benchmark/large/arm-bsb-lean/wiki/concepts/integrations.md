---
type: concept
title: CI & Tooling Integrations
---

How Ruff plugs into pre-commit, CI pipelines, and containerized workflows.

- pre-commit via `astral-sh/ruff-pre-commit` (rev v0.15.18), hooks `ruff-check`/`ruff-format`; with `--fix`, run check before format ([[sources/integrations]], [[sources/tutorial]]).
- GitHub Actions: `astral-sh/ruff-action@v3` with `version`/`args`/`src` options ([[sources/integrations]]).
- GitLab CI/CD: alpine image plus `--output-format=gitlab` code-quality report; `ruff format --diff` ([[sources/integrations]]).
- Docker tags follow `ruff:{version}-{base}` (alpine, debian-slim, etc.) ([[sources/integrations]], [[sources/installation]]).
- mdformat-ruff formats Python code blocks inside Markdown ([[sources/integrations]]).

## Links
[[concepts/installation]] · [[concepts/editor-integration]] · [[concepts/cli-commands]] · [[sources/integrations]] · [[sources/tutorial]] · [[sources/installation]]
