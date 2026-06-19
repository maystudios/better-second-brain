# Ruff

**Ruff** is an extremely fast Python linter and code formatter written in Rust ([[sources/ruff-overview]]; [[sources/github-astral-sh-ruff]]). Its design goal is to replace a fragmented set of traditional Python quality tools with a single unified solution ([[sources/ruff-overview]]). The project is maintained by **Astral**, described as "the company behind the uv package manager and ty type checker" ([[sources/github-astral-sh-ruff]]), and is distributed under the **MIT License** ([[sources/github-astral-sh-ruff]]).

The recurring tagline across the docs and README is: "An extremely fast Python linter and code formatter, written in Rust" ([[sources/ruff-overview]]; [[sources/github-astral-sh-ruff]]).

## What it consolidates

Ruff is positioned as a consolidation of multiple tools: Flake8 (plus dozens of plugins), Black, isort, pydocstyle, pyupgrade, and autoflake ([[sources/ruff-overview]]). The [[concepts/tool-replacement]] page covers the precise replacement claims and their stated limits; in summary, Ruff offers feature parity with Flake8, isort, and Black ([[sources/ruff-overview]]; [[sources/github-astral-sh-ruff]]) and re-implements 50+ popular Flake8 plugins natively ([[sources/faq]]).

Two capabilities are split into the linter and the formatter:
- The [[concepts/linter]] runs via `ruff check` and surfaces/fixes rule violations ([[sources/linter]]).
- The [[concepts/formatter]] runs via `ruff format` and reformats code targeting Black compatibility ([[sources/formatter]]).

## Speed

Ruff's headline claim is being **10-100x faster** than existing linters (Flake8) and formatters (Black), benchmarked on the CPython codebase ([[sources/ruff-overview]]; [[sources/github-astral-sh-ruff]]). See [[concepts/performance]] for the supporting anecdotes, including a maintainer's report of 0.4 seconds versus 2.5 minutes with Pylint on a 250k-line codebase ([[sources/github-astral-sh-ruff]]).

## Scope and rules

Ruff ships **over 900 built-in rules**, including native implementations of popular Flake8 plugins ([[sources/ruff-overview]]; [[sources/github-astral-sh-ruff]]); the tutorial frames this as "over 900 lint rules across 50+ plugins" ([[sources/tutorial]]). The rule families are catalogued in [[concepts/rules-and-rule-codes]]. It also includes built-in caching to skip re-analyzing unchanged files ([[sources/ruff-overview]]; [[sources/github-astral-sh-ruff]]), with the cache stored in a `.ruff_cache` directory by default ([[sources/settings]]).

## Ecosystem position

Ruff is **a linter, not a type checker**; type checkers such as Mypy, Pyright, and Pyre catch type errors Ruff misses and are described as complementary ([[sources/faq]]). It lints code for Python 3.7 through 3.13 and does not support Python 2 ([[sources/faq]]), while advertising **Python 3.14 compatibility** as a feature ([[sources/ruff-overview]]; [[sources/github-astral-sh-ruff]]) - see [[concepts/python-version-support]] for how these two figures relate. Installation options are covered in [[concepts/installation]], configuration in [[concepts/configuration]], CI/editor wiring in [[concepts/integrations]] and [[concepts/editor-integration]], and release policy in [[concepts/versioning]] and [[concepts/preview-mode]].

## Adoption

Named adopters across the corpus include FastAPI, Pandas, SciPy, Hugging Face / Hugging Face Transformers, Apache Airflow, Apache Superset, and "100+ organizations" ([[sources/ruff-overview]]; [[sources/github-astral-sh-ruff]]).

## Repository facts (as fetched)

As fetched, the GitHub repository reported 48.1k stars, 2.2k forks, and 1.7k open issues, with a latest release of **0.15.18 (June 18, 2026)** and a language breakdown of Rust 96.5% / Python 2.5% / TypeScript 0.9% ([[sources/github-astral-sh-ruff]]).

## Open questions

- The exact total rule count is given only as "over 900" / "900+" across sources ([[sources/ruff-overview]]; [[sources/github-astral-sh-ruff]]; [[sources/tutorial]]); no precise number is stated.
- The plugin count is given inconsistently as "40+ Flake8 plugins" ([[sources/github-astral-sh-ruff]]), "50+ plugins" ([[sources/tutorial]]), and "50+ popular Flake8 plugins" ([[sources/faq]]). The sources do not reconcile these figures.
- Repository statistics are explicitly labeled "as fetched" ([[sources/github-astral-sh-ruff]]); they are point-in-time and not authoritative going forward.
