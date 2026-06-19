# Tool Replacement & Compatibility

A central premise of [[concepts/ruff]] is that it consolidates many separate Python tools into one. This page records exactly what the sources claim Ruff replaces - and the stated limits of those claims.

## What Ruff consolidates

The overview lists Ruff as consolidating Flake8 (plus dozens of plugins), Black, isort, pydocstyle, pyupgrade, and autoflake ([[sources/ruff-overview]]). The FAQ states Ruff can replace Black, isort, yesqa, eradicate, and most pyupgrade rules, and re-implements 50+ popular Flake8 plugins natively (flake8-bugbear, flake8-comprehensions, flake8-docstrings, flake8-django, etc.) ([[sources/faq]]). The README groups the replaced tooling as core checkers (Pyflakes, pycodestyle), 40+ Flake8 plugins, and tool equivalents (isort, Black, pyupgrade, pydocstyle, autoflake, pandas-vet, pep8-naming) ([[sources/github-astral-sh-ruff]]).

## Flake8 compatibility

Ruff is a drop-in Flake8 replacement when used without plugins, alongside Black, on Python 3 code; it implements all Pyflakes rules plus a subset of pycodestyle rules ([[sources/faq]]). The rule-code grammar itself mirrors Flake8 ([[sources/linter]]), as do the suppression comments ([[concepts/error-suppression]]; [[sources/linter]]).

## Black compatibility

There are two distinct Black-compatibility claims:
1. The **linter** is compatible with Black out-of-the-box, "as long as the line-length setting is consistent between the two" ([[sources/faq]]). This is why the default rule selection avoids stylistic rules that conflict with formatters ([[concepts/formatter-lint-conflicts]]).
2. The **formatter** aims to reproduce Black's output, reaching ">99.9% of lines formatted identically" on Django and Zulip ([[sources/formatter]]; [[sources/faq]]), with a small list of intentional deviations ([[concepts/formatter]]).

## isort compatibility

Ruff's import sorting targets isort's "black" profile, with documented behavioral differences; see [[concepts/import-sorting]] ([[sources/faq]]).

## What Ruff is NOT

Ruff is **a linter, not a type checker**; type checkers (Mypy, Pyright, Pyre) catch errors Ruff misses and are complementary ([[sources/faq]]). It also does not sort imports as part of formatting - that is a linter (`I`) responsibility ([[sources/formatter]]).

## Open questions

- The set of replaced tools is phrased slightly differently in each source (overview vs. README vs. FAQ); the union above is faithful to all three, but the sources do not give a single authoritative list ([[sources/ruff-overview]]; [[sources/github-astral-sh-ruff]]; [[sources/faq]]).
- "Most pyupgrade rules" ([[sources/faq]]) is not quantified - the sources do not say which pyupgrade behaviors are unsupported.
