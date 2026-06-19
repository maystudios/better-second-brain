# uv (overview)

uv is described as "an extremely fast Python package and project manager, written in Rust" ([[sources/github-astral-sh-uv]]; [[sources/docs-astral-sh-uv]]).

It is positioned as a single tool that replaces pip, pip-tools, pipx, poetry, pyenv, twine, and virtualenv ([[sources/github-astral-sh-uv]]); the documentation landing page lists the same set plus "additional package management tools" ([[sources/docs-astral-sh-uv]]).

## Performance claim

uv is claimed to be "10-100x faster" than pip ([[sources/github-astral-sh-uv]]; [[sources/docs-astral-sh-uv]]).

## Capabilities (as listed by the sources)

- Comprehensive project management with universal lockfile support ([[sources/github-astral-sh-uv]]; [[sources/docs-astral-sh-uv]]). See [[uv-projects-and-lockfiles]].
- Script execution with inline dependency metadata ([[sources/github-astral-sh-uv]]; [[sources/docs-astral-sh-uv]]).
- Python version installation and management ([[sources/github-astral-sh-uv]]; [[sources/docs-astral-sh-uv]]).
- Tool installation and execution, "similar to pipx" ([[sources/github-astral-sh-uv]]; [[sources/docs-astral-sh-uv]]). See [[uv-tools]].
- A pip-compatible interface for performance improvements ([[sources/github-astral-sh-uv]]; [[sources/docs-astral-sh-uv]]).
- Cargo-style workspace support ([[sources/github-astral-sh-uv]]; [[sources/docs-astral-sh-uv]]).
- A global cache for dependency deduplication / efficient disk usage ([[sources/github-astral-sh-uv]]; [[sources/docs-astral-sh-uv]]).
- Cross-platform support: macOS, Linux, and Windows ([[sources/github-astral-sh-uv]]; [[sources/docs-astral-sh-uv]]).
- Installation without requiring Rust or Python ([[sources/docs-astral-sh-uv]]).

## Maintainer and licensing

uv is developed by Astral, described as the creators of Ruff and other Python tooling ([[sources/github-astral-sh-uv]]). It is dual-licensed under the Apache License 2.0 or the MIT license ([[sources/github-astral-sh-uv]]).

## Open questions

- The exact "10-100x faster than pip" figure is presented as a project/marketing claim in the sources; no benchmark methodology is provided in the raw material, so the conditions under which it holds are unknown.
- The full list of tools uv replaces is given as a closed list on GitHub ([[sources/github-astral-sh-uv]]) but extended with "additional package management tools" in the docs ([[sources/docs-astral-sh-uv]]); the sources do not enumerate what those additional tools are.
