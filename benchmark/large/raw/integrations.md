# Ruff Integrations

Source: https://docs.astral.sh/ruff/integrations/

## pre-commit

```yaml
- repo: https://github.com/astral-sh/ruff-pre-commit
  rev: v0.15.18
  hooks:
    - id: ruff-check
    - id: ruff-format
```

With automatic fixes:
```yaml
    - id: ruff-check
      args: [ --fix ]
    - id: ruff-format
```

Hook ordering: when using `--fix`, position `ruff-check` before `ruff-format` and other formatting tools.

## GitHub Actions (ruff-action)

`.github/workflows/ruff.yml`:
```yaml
- uses: astral-sh/ruff-action@v3
```
Options via `with:`: `version` (default latest), `args` (default `"check"`), `src` (default `[".", "src"]`).

```yaml
- uses: astral-sh/ruff-action@v3
  with:
    version: 0.8.0
    args: check --select B
    src: "./src"
```

## GitLab CI/CD

Image `ghcr.io/astral-sh/ruff:0.15.18-alpine`.
```yaml
script:
  - ruff check --output-format=gitlab --output-file=code-quality-report.json
```
```yaml
script:
  - ruff format --diff
```

## Docker

Tags: `ruff:latest`, `ruff:{major}.{minor}.{patch}`, `ruff:alpine`, `ruff:debian-slim`, `ruff:bookworm-slim`, `ruff:debian`. Format `ruff:{version}-{base}` (e.g., `ruff:0.6.6-alpine`).

## Additional

mdformat-ruff plugin: format Python code blocks within Markdown using Ruff.
