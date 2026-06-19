# Formatter

The formatter is the `ruff format` half of [[Ruff]]. It rewrites Python source into a consistent style, aiming to be a drop-in replacement for **Black**.

## The command

```bash
ruff format                   # Format all files in current directory
ruff format path/to/code/     # A directory and its subdirectories
ruff format path/to/file.py   # A single file
ruff format --check /path     # Verify only; non-zero exit if unformatted
```

## Black compatibility

Ruff targets Black's stable code style and reports formatting >99.9% of lines identically on large Black-formatted projects like Django and Zulip. A few deliberate deviations exist:

- **F-strings** - unlike Black, Ruff formats expressions inside `{...}`.
- **Nested f-string quotes** - Ruff alternates quote styles to keep them valid.
- **Method chains** (preview mode) - breaks before the first attribute in long chains.

## Defaults and configuration

The defaults mirror Black: 88-character lines, double quotes, 4-space indentation, and a respected magic trailing comma. Keys live under `[tool.ruff.format]` (with `line-length` at the top level). See [[Configuration]] for the complete settings table.

```toml
[tool.ruff]
line-length = 100

[tool.ruff.format]
quote-style = "single"
indent-style = "tab"
docstring-code-format = true
docstring-code-line-length = 20
```

## Docstring code formatting

With `docstring-code-format = true`, Ruff also formats code examples embedded in docstrings - Python doctests, CommonMark fenced blocks (info strings `python`, `py`, `python3`, `py3`), and reStructuredText literal/`code-block` directives. The `docstring-code-line-length` key controls their line limit; the default `"dynamic"` follows the surrounding code's limit. Code that doesn't parse as valid Python is left untouched.

## Suppressing formatting

```python
# fmt: off
not_formatted = 3
# fmt: on

x = 1  # fmt: skip
```

`# fmt: skip` works on case headers, decorators, function/class definitions, or a preceding statement on the same logical line. YAPF's `# yapf: disable`/`# yapf: enable` are also recognized.

In **preview mode**, the formatter can format fenced Python blocks inside Markdown (info strings `python`, `py`, `python3`, `py3`, or `pyi` for type stubs, plus Quarto ` ```{python} `), suppressed with `<!-- fmt:off -->`/`<!-- fmt:on -->`.

## Import sorting

The formatter does **not** sort imports - that's a [[Linter]] job. To do both, run the isort rule first, then format:

```bash
ruff check --select I --fix
ruff format
```

## Exit codes

For `ruff format` (no `--check`): `0` always means success, `1` only if files were formatted and `--exit-non-zero-on-format` was passed, `2` is abnormal termination. With `--check`: `0` means nothing would change, `1` means something would, `2` is abnormal termination.

## Avoiding lint/format conflicts

Some lint rules fight the formatter. Ruff emits a warning when it detects them; disable them via `lint.ignore`: the quote rules `Q000`-`Q004`, the tab/indent rules `W191`, `E111`, `E114`, `E117`, the comma rules `COM812`/`COM819`, and `D203`, `D206`, `D300`, `ISC002`. Also avoid non-default isort settings like `force-single-line` and `split-on-trailing-comma`. `E501` (line length) can coexist but may still fire.

## See also

- [[Linter]] - the companion `ruff check` command
- [[Configuration]] - full format settings and defaults
- [[Preview]] - how preview-mode style changes are gated
