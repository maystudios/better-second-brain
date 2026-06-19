# Ruff Wiki — Index (Map of Content)

A research-gated (BSB) wiki on **Ruff**, the Astral Python linter & formatter, built from 15 raw source documents. Every non-trivial claim in the concept pages is grounded in and cites a `[[sources/<slug>]]` page; uncertainties are flagged under each page's "## Open questions".

## Start here

- [[concepts/ruff]] — the hub: what Ruff is, who maintains it, scope, adoption.

## Core capabilities

- [[concepts/linter]] — `ruff check`, rule selection, exit codes.
  - [[concepts/fix-safety]] — safe vs. unsafe automatic fixes.
  - [[concepts/error-suppression]] — `# noqa`, file-level suppression, `RUF100`.
- [[concepts/formatter]] — `ruff format`, Black compatibility, docstring formatting.
  - [[concepts/formatter-lint-conflicts]] — lint rules that conflict with the formatter.
- [[concepts/import-sorting]] — isort-compatible `I` rules.
- [[concepts/rules-and-rule-codes]] — rule code grammar, family prefixes, status markers.

## Setup & configuration

- [[concepts/installation]] — install channels (uv, pip, Docker, etc.).
- [[concepts/configuration]] — config files, discovery, hierarchy, CLI overrides.
- [[concepts/default-settings]] — default values tabulated.
- [[concepts/python-version-support]] — supported Python versions.

## Tooling & lifecycle

- [[concepts/editor-integration]] — `ruff server` LSP and per-editor setup.
- [[concepts/integrations]] — pre-commit, GitHub Actions, GitLab, Docker.
- [[concepts/preview-mode]] — opt-in unstable features.
- [[concepts/versioning]] — custom (non-SemVer) versioning policy.

## Cross-cutting

- [[concepts/performance]] — the speed claims and anecdotes.
- [[concepts/tool-replacement]] — what Ruff replaces, and what it does not.

## Sources (one page per raw file)

- [[sources/ruff-overview]] — docs landing page
- [[sources/github-astral-sh-ruff]] — GitHub README
- [[sources/installation]] — installation guide
- [[sources/tutorial]] — tutorial
- [[sources/configuration]] — configuration reference
- [[sources/linter]] — linter reference
- [[sources/formatter]] — formatter reference
- [[sources/rules]] — rules reference
- [[sources/settings]] — settings reference
- [[sources/preview]] — preview mode
- [[sources/versioning]] — versioning policy
- [[sources/editors]] — editor overview
- [[sources/editors-setup]] — per-editor setup
- [[sources/integrations]] — CI/CD integrations
- [[sources/faq]] — FAQ
