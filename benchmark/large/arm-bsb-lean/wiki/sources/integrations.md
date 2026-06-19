---
type: source
title: "Ruff Integrations"
url: https://docs.astral.sh/ruff/integrations/
kind: official-docs
---

## Key claims
- pre-commit via `astral-sh/ruff-pre-commit` (rev v0.15.18), hooks `ruff-check`/`ruff-format`; with `--fix`, put `ruff-check` before `ruff-format`.
- GitHub Actions: `astral-sh/ruff-action@v3`; `with:` options `version` (default latest), `args` (default `"check"`), `src` (default `[".","src"]`).
- GitLab CI/CD: image `ghcr.io/astral-sh/ruff:0.15.18-alpine`; `--output-format=gitlab` produces a code-quality report; `ruff format --diff`.
- Docker tags: `ruff:latest`, `ruff:{version}`, `ruff:alpine`/`debian-slim`/`bookworm-slim`/`debian`; pattern `ruff:{version}-{base}`.
- mdformat-ruff plugin formats Python code blocks inside Markdown using Ruff.
