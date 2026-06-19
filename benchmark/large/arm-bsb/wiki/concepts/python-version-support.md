# Python Version Support

Two distinct version-related facts appear across the [[concepts/ruff]] sources, and they concern different things.

## Versions Ruff can lint/target

Ruff can lint code for **Python 3.7 through 3.13** and "does not support Python 2" ([[sources/faq]]). The default lint target is `target-version = "py310"` ([[sources/settings]]; [[sources/configuration]]; [[sources/github-astral-sh-ruff]]). When `target-version` is unspecified, Ruff infers it from `requires-python` in `pyproject.toml` ([[sources/configuration]]); this is shown in the tutorial via `[project] requires-python = ">=3.10"` ([[sources/tutorial]]).

## "Python 3.14 compatibility"

Separately, the overview and README advertise **Python 3.14 compatibility** as a feature ([[sources/ruff-overview]]; [[sources/github-astral-sh-ruff]]). The sources do not explicitly state whether this means Ruff runs on a 3.14 interpreter, can lint 3.14 code, or both.

## Runtime requirements

Ruff is installable on any Python 3.7+ environment and requires no Rust installation, since it ships as pre-built wheels on PyPI ([[sources/faq]]). Installation channels are covered in [[concepts/installation]].

## Versioning interaction

Dropping end-of-life Python version support is classified as a breaking change (minor version bump), while adding new Python version support is non-breaking (patch bump) under Ruff's [[concepts/versioning]] policy ([[sources/versioning]]).

## Open questions

- There is a tension between the FAQ's stated lint range of **3.7-3.13** ([[sources/faq]]) and the advertised **Python 3.14 compatibility** ([[sources/ruff-overview]]; [[sources/github-astral-sh-ruff]]). The sources do not reconcile whether 3.14 refers to the interpreter Ruff runs under, the code it can analyze, or both - and the FAQ's "3.7 through 3.13" may simply predate the 3.14 claim.
