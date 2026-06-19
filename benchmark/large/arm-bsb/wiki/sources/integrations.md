# Source: Ruff Integrations

- **Citation / URL:** https://docs.astral.sh/ruff/integrations/
- **Raw file:** `benchmark/large/raw/integrations.md`
- **Type:** Official documentation - CI/CD and tooling integrations

## Key claims

### pre-commit
```yaml
- repo: https://github.com/astral-sh/ruff-pre-commit
  rev: v0.15.18
  hooks:
    - id: ruff-check
    - id: ruff-format
```
- With automatic fixes, `ruff-check` takes `args: [ --fix ]`.
- **Hook ordering:** when using `--fix`, position `ruff-check` before `ruff-format` and other formatting tools.

### GitHub Actions (ruff-action)
- `.github/workflows/ruff.yml` uses `astral-sh/ruff-action@v3`.
- Options via `with:`: `version` (default latest), `args` (default `"check"`), `src` (default `[".", "src"]`).
- Example: `version: 0.8.0`, `args: check --select B`, `src: "./src"`.

### GitLab CI/CD
- Image `ghcr.io/astral-sh/ruff:0.15.18-alpine`.
- `ruff check --output-format=gitlab --output-file=code-quality-report.json`.
- `ruff format --diff`.

### Docker
- Tags: `ruff:latest`, `ruff:{major}.{minor}.{patch}`, `ruff:alpine`, `ruff:debian-slim`, `ruff:bookworm-slim`, `ruff:debian`.
- Format `ruff:{version}-{base}` (e.g., `ruff:0.6.6-alpine`).

### Additional
- mdformat-ruff plugin: format Python code blocks within Markdown using Ruff.

## Prose summary

This page covers automating Ruff in CI/CD pipelines. The pre-commit hooks (`ruff-check`, `ruff-format` from `astral-sh/ruff-pre-commit`) carry an important ordering rule when auto-fixing: run `ruff-check --fix` before `ruff-format`. For GitHub Actions, `astral-sh/ruff-action@v3` exposes `version`/`args`/`src` inputs. GitLab integration leverages the alpine Docker image and a `--output-format=gitlab` code-quality report. The page documents the Docker tag taxonomy and notes the `mdformat-ruff` plugin for formatting Python inside Markdown.
