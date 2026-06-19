# Ruff Formatter

Source: https://docs.astral.sh/ruff/formatter/

## Basic Command

```bash
ruff format                   # Format all files in current directory
ruff format path/to/code/     # Format directory and subdirectories
ruff format path/to/file.py   # Format single file
ruff format --check /path     # Verify formatting without writing; non-zero if unformatted
```

## Black Compatibility

Ruff targets Black compatibility as a drop-in replacement. The formatter achieves ">99.9% of lines formatted identically" on extensive Black-formatted projects like Django and Zulip. Adheres to Black's stable code style.

### Known Deviations
- F-string expression formatting: unlike Black, Ruff formats expressions within f-string `{...}`
- Quote handling in nested f-strings: alternates quote styles
- Method chain layout (preview mode): breaks before the first attribute in long method chains

## Default Configuration

- Line length: 88 characters
- Quote style: `"double"` (via `quote-style`)
- Indent style: spaces (`indent-style`; supports `"space"` or `"tab"`)
- Indent width: 4 spaces
- Magic trailing comma respected (like Black)

## Configuration Keys

```toml
[tool.ruff]
line-length = 100

[tool.ruff.format]
quote-style = "single"
indent-style = "tab"
docstring-code-format = true
docstring-code-line-length = 20
```

## Docstring Code Formatting

Enable with `docstring-code-format = true`. Recognizes:
- Python doctest format
- CommonMark fenced code blocks (info strings: `python`, `py`, `python3`, `py3`)
- reStructuredText literal blocks and code-block/sourcecode directives

`docstring-code-line-length` controls line limits for code examples. Default `"dynamic"` respects surrounding code's line length limit.

Code is skipped if it doesn't parse as valid Python or would produce invalid output.

## Format Suppression Comments

- `# fmt: off` and `# fmt: on`: disable formatting at statement level
- `# fmt: skip`: suppress formatting for case headers, decorators, function/class definitions, or preceding statement on same logical line
- Also recognizes YAPF's `# yapf: disable` / `# yapf: enable`

```python
# fmt: off
not_formatted = 3
# fmt: on

x = 1  # fmt: skip
```

## Markdown Code Formatting (preview mode)

Formats fenced code blocks with info strings: `python`, `py`, `python3`, `py3`, or `pyi` (pyi formats as type stubs). Supports Quarto ` ```{python} `. Suppress with `<!-- fmt:off -->` / `<!-- fmt:on -->`; also `<!-- blacken-docs:off/on -->`.

## Exit Codes

`ruff format` (without `--check`):
- `0`: success regardless of files formatted
- `1`: files formatted and `--exit-non-zero-on-format` was specified
- `2`: abnormal termination

`ruff format --check`:
- `0`: no files would be formatted
- `1`: files would be formatted
- `2`: abnormal termination

## Conflicting Lint Rules

Disable via `lint.ignore`: `Q000`, `Q001`, `Q002`, `Q003`, `Q004`; `W191`, `E111`, `E114`, `E117`; `COM812`, `COM819`; `D203`, `D206`, `D300`, `ISC002`. Avoid non-default isort settings: `force-single-line`, `force-wrap-aliases`, `lines-after-imports`, `lines-between-types`, `split-on-trailing-comma`. `E501` can coexist but may still trigger. `ruff format` emits warnings when incompatible rules detected.

## Import Sorting

The formatter does NOT sort imports. To sort and format:
```bash
ruff check --select I --fix
ruff format
```
