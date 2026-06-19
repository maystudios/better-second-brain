# Performance

Ruff's defining marketing claim is speed. The headline figure, repeated in both the docs landing page and the README, is that Ruff is **10-100x faster** than existing linters (Flake8) and formatters (Black) ([[sources/ruff-overview]]; [[sources/github-astral-sh-ruff]]). This figure is attributed to benchmarking on the CPython codebase ([[sources/ruff-overview]]; [[sources/github-astral-sh-ruff]]), with the overview adding that the benchmark was run "from scratch" ([[sources/ruff-overview]]).

## Concrete anecdote

The most specific data point in the corpus comes from the README: one maintainer noted analysis in **0.4 seconds versus 2.5 minutes with Pylint** on a 250k-line codebase ([[sources/github-astral-sh-ruff]]).

## Why it is fast

The sources attribute the speed primarily to the implementation language - Ruff is written in Rust ([[sources/ruff-overview]]; [[sources/github-astral-sh-ruff]]) - and to **built-in caching** that skips re-analyzing unchanged files ([[sources/ruff-overview]]; [[sources/github-astral-sh-ruff]]). The cache lives in a `.ruff_cache` directory by default ([[sources/settings]]). The consolidation argument is that Ruff runs "tens to hundreds of times faster than individual tools" while doing the work of many ([[sources/ruff-overview]]).

Speed also underpins the [[concepts/editor-integration]] story: the language server is itself written in Rust ([[sources/editors]]).

## Open questions

- The "10-100x" range is broad and the sources do not specify which workloads land at the low versus high end, nor the benchmark methodology beyond "CPython codebase … from scratch" ([[sources/ruff-overview]]; [[sources/github-astral-sh-ruff]]).
- The 0.4s-vs-2.5-minute Pylint comparison is reported as a single maintainer's observation rather than a reproducible published benchmark ([[sources/github-astral-sh-ruff]]).
