# Integrations

Beyond the [[Editors|editor]] experience, [[Ruff]] is built to run in version control hooks and CI pipelines, where its speed makes it nearly free to enforce on every commit.

## pre-commit

```yaml
- repo: https://github.com/astral-sh/ruff-pre-commit
  rev: v0.15.18
  hooks:
    - id: ruff-check
    - id: ruff-format
```

To auto-fix during the hook:

```yaml
    - id: ruff-check
      args: [ --fix ]
    - id: ruff-format
```

When `--fix` is on, position `ruff-check` **before** `ruff-format` (and before other formatters) so import sorting and fixes happen before the final layout pass - the same ordering recommended in the [[Linter]] and [[Formatter]] pages.

## GitHub Actions

```yaml
# .github/workflows/ruff.yml
- uses: astral-sh/ruff-action@v3
  with:
    version: 0.8.0          # default: latest
    args: check --select B  # default: "check"
    src: "./src"            # default: [".", "src"]
```

## GitLab CI/CD

Use the Alpine image and emit a Code Quality report:

```yaml
script:
  - ruff check --output-format=gitlab --output-file=code-quality-report.json
```

```yaml
script:
  - ruff format --diff
```

The `--output-format` option (and others) is covered in [[Configuration]].

## Docker

Images are published as `ghcr.io/astral-sh/ruff`. Tags include `ruff:latest`, versioned `ruff:{major}.{minor}.{patch}`, and base variants `ruff:alpine`, `ruff:debian-slim`, `ruff:bookworm-slim`, `ruff:debian`. Combine them as `ruff:{version}-{base}`, e.g. `ruff:0.6.6-alpine`. See [[Installation]] for `docker run` examples.

## Markdown

The `mdformat-ruff` plugin formats Python code blocks embedded in Markdown using Ruff.

## See also

- [[Preview]] - opting in to experimental rules and styles
- [[Versioning]] - what a version bump means for your pipeline
