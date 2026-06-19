# Ruff: Python Linter & Formatter (Overview)

Source: https://docs.astral.sh/ruff/

## Overview

Ruff is an extremely fast Python linter and code formatter written in Rust, designed to replace multiple traditional tools with a unified solution.

## Core Tagline

An extremely fast Python linter and code formatter, written in Rust.

## Performance Claims

- 10-100x faster than existing linters (Flake8) and formatters (Black)
- Benchmarked on the CPython codebase from scratch

## Key Features

- Exceptional speed compared to legacy tools
- Installable via pip
- `pyproject.toml` support
- Python 3.14 compatibility
- Feature parity with Flake8, isort, and Black
- Built-in caching to skip re-analyzing unchanged files
- Automatic error correction (e.g., removing unused imports)
- Over 900 built-in rules including native implementations of popular Flake8 plugins
- First-party editor integrations for VS Code and others
- Monorepo-friendly with hierarchical configuration

## What It Replaces

Ruff consolidates the functionality of:
- Flake8 (plus dozens of plugins)
- Black
- isort
- pydocstyle
- pyupgrade
- autoflake

All while executing tens to hundreds of times faster than individual tools.

## Adoption

Apache Airflow, Apache Superset, FastAPI, Hugging Face, Pandas, and SciPy.
