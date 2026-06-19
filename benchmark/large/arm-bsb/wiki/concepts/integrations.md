# CI/CD Integrations

Beyond [[concepts/editor-integration|editors]], [[concepts/ruff]] integrates into continuous-integration pipelines via pre-commit, GitHub Actions, GitLab CI/CD, and Docker images ([[sources/integrations]]).

## pre-commit

Ruff publishes hooks at `astral-sh/ruff-pre-commit` ([[sources/integrations]]; [[sources/tutorial]]):
```yaml
- repo: https://github.com/astral-sh/ruff-pre-commit
  rev: v0.15.18
  hooks:
    - id: ruff-check
    - id: ruff-format
```
For auto-fixing, `ruff-check` takes `args: [ --fix ]` ([[sources/integrations]]). A key ordering rule: when using `--fix`, position `ruff-check` before `ruff-format` and other formatting tools ([[sources/integrations]]) — consistent with the [[concepts/import-sorting]] and [[concepts/formatter]] workflow where linting/sorting precedes formatting.

## GitHub Actions

The `astral-sh/ruff-action@v3` action runs Ruff in CI ([[sources/integrations]]). It exposes inputs via `with:`: `version` (default latest), `args` (default `"check"`), and `src` (default `[".", "src"]`) ([[sources/integrations]]). Example overriding all three: `version: 0.8.0`, `args: check --select B`, `src: "./src"` ([[sources/integrations]]).

## GitLab CI/CD

Uses the alpine Docker image `ghcr.io/astral-sh/ruff:0.15.18-alpine` ([[sources/integrations]]). It can emit a GitLab code-quality report via `ruff check --output-format=gitlab --output-file=code-quality-report.json` ([[sources/integrations]]); the `--output-format` option is part of Ruff's CLI surface ([[sources/configuration]]). Formatting checks use `ruff format --diff` ([[sources/integrations]]).

## Docker

Ruff publishes a tag taxonomy: `ruff:latest`, `ruff:{major}.{minor}.{patch}`, `ruff:alpine`, `ruff:debian-slim`, `ruff:bookworm-slim`, `ruff:debian`, and the combined form `ruff:{version}-{base}` (e.g. `ruff:0.6.6-alpine`) ([[sources/integrations]]). Local Docker usage is covered in [[concepts/installation]] ([[sources/installation]]).

## Other

The `mdformat-ruff` plugin formats Python code blocks within Markdown using Ruff ([[sources/integrations]]).

## Open questions

- The `rev: v0.15.18` pre-commit revision ([[sources/integrations]]; [[sources/tutorial]]) and the `0.15.18-alpine` GitLab image ([[sources/integrations]]) are version-pinned snapshots; the sources do not indicate the current recommended pin beyond these.
