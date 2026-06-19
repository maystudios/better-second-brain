# The Formatter (`ruff format`)

The **formatter** is [[concepts/ruff]]'s second half, invoked with `ruff format` ([[sources/formatter]]). It is complementary to the [[concepts/linter]].

## Commands

- `ruff format` - format all files in the current directory ([[sources/formatter]]; [[sources/installation]]).
- `ruff format path/to/code/` - format a directory and subdirectories ([[sources/formatter]]).
- `ruff format path/to/file.py` - format a single file ([[sources/formatter]]).
- `ruff format --check /path` - verify formatting without writing; exits non-zero if files are unformatted ([[sources/formatter]]).

## Black compatibility

The formatter targets Black compatibility as a drop-in replacement ([[sources/formatter]]). It achieves ">99.9% of lines formatted identically" on extensive Black-formatted projects like Django and Zulip, and adheres to Black's stable code style ([[sources/formatter]]). The FAQ restates the >99.9% line-compatibility figure for Django and Zulip ([[sources/faq]]).

### Known deviations from Black

Ruff intentionally diverges from Black in a few places ([[sources/formatter]]):
- It formats expressions inside f-string `{...}`, unlike Black.
- In nested f-strings it alternates quote styles.
- In preview mode, it breaks before the first attribute in long method chains.

## Defaults

Defaults are line-length 88, `quote-style = "double"`, space indentation (`indent-style` supports `"space"` or `"tab"`), indent width 4, and the magic trailing comma respected like Black ([[sources/formatter]]). These are tabulated with their config keys in [[concepts/default-settings]].

## Docstring code formatting

With `docstring-code-format = true`, Ruff formats code embedded in docstrings ([[sources/formatter]]). It recognizes Python doctest format, CommonMark fenced code blocks (info strings `python`, `py`, `python3`, `py3`), and reStructuredText literal blocks plus code-block/sourcecode directives ([[sources/formatter]]). `docstring-code-line-length` controls the line limit for those examples, defaulting to `"dynamic"`, which respects the surrounding code's line length ([[sources/formatter]]; [[sources/settings]]). Code that doesn't parse as valid Python, or that would produce invalid output, is skipped ([[sources/formatter]]).

## Suppression comments

The formatter honors `# fmt: off` / `# fmt: on` (statement-level) and `# fmt: skip` (for case headers, decorators, function/class definitions, or the preceding statement on the same logical line); it also recognizes YAPF's `# yapf: disable` / `# yapf: enable` ([[sources/formatter]]).

## Markdown formatting (preview)

In preview mode the formatter formats fenced code blocks with info strings `python`, `py`, `python3`, `py3`, or `pyi` (which formats as type stubs), and supports Quarto ` ```{python} ` ([[sources/formatter]]). Suppression uses `<!-- fmt:off -->` / `<!-- fmt:on -->` and `<!-- blacken-docs:off/on -->` ([[sources/formatter]]). This preview behavior is gated by [[concepts/preview-mode]].

## Exit codes

Without `--check` ([[sources/formatter]]):
- `0` - success regardless of how many files were formatted.
- `1` - files were formatted and `--exit-non-zero-on-format` was specified.
- `2` - abnormal termination.

With `--check` ([[sources/formatter]]):
- `0` - no files would be formatted.
- `1` - files would be formatted.
- `2` - abnormal termination.

## Imports are not sorted

The formatter does **not** sort imports; to both sort and format, run `ruff check --select I --fix` then `ruff format` ([[sources/formatter]]). See [[concepts/import-sorting]].

## Conflicts with lint rules

A set of lint rules conflict with the formatter and should be disabled; Ruff emits warnings when it detects them. These are enumerated in [[concepts/formatter-lint-conflicts]] ([[sources/formatter]]).

## Open questions

- The method-chain layout change is described as preview-mode behavior ([[sources/formatter]]); the sources do not state whether it has since stabilized.
