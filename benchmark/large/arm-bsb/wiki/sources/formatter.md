# Source: Ruff Formatter

- **Citation / URL:** https://docs.astral.sh/ruff/formatter/
- **Raw file:** `benchmark/large/raw/formatter.md`
- **Type:** Official documentation — formatter reference

## Key claims

### Basic command
```bash
ruff format                   # Format all files in current directory
ruff format path/to/code/     # Format directory and subdirectories
ruff format path/to/file.py   # Format single file
ruff format --check /path     # Verify formatting without writing; non-zero if unformatted
```

### Black compatibility
- Ruff targets Black compatibility as a drop-in replacement.
- The formatter achieves **">99.9% of lines formatted identically"** on extensive Black-formatted projects like Django and Zulip; adheres to Black's stable code style.
- **Known deviations:**
  - F-string expression formatting: unlike Black, Ruff formats expressions within f-string `{...}`.
  - Quote handling in nested f-strings: alternates quote styles.
  - Method chain layout (preview mode): breaks before the first attribute in long method chains.

### Default configuration
- Line length: 88; quote style: `"double"`; indent style: spaces (supports `"space"` or `"tab"`); indent width: 4 spaces; magic trailing comma respected (like Black).

### Configuration keys
```toml
[tool.ruff]
line-length = 100

[tool.ruff.format]
quote-style = "single"
indent-style = "tab"
docstring-code-format = true
docstring-code-line-length = 20
```

### Docstring code formatting
- Enable with `docstring-code-format = true`. Recognizes Python doctest format; CommonMark fenced code blocks (info strings `python`, `py`, `python3`, `py3`); reStructuredText literal blocks and code-block/sourcecode directives.
- `docstring-code-line-length` controls line limits for code examples; default `"dynamic"` respects the surrounding code's line-length limit.
- Code is skipped if it doesn't parse as valid Python or would produce invalid output.

### Format suppression comments
- `# fmt: off` / `# fmt: on`: disable formatting at statement level.
- `# fmt: skip`: suppress formatting for case headers, decorators, function/class definitions, or the preceding statement on the same logical line.
- Also recognizes YAPF's `# yapf: disable` / `# yapf: enable`.

### Markdown code formatting (preview mode)
- Formats fenced code blocks with info strings `python`, `py`, `python3`, `py3`, or `pyi` (pyi formats as type stubs). Supports Quarto ` ```{python} `.
- Suppress with `<!-- fmt:off -->` / `<!-- fmt:on -->`; also `<!-- blacken-docs:off/on -->`.

### Exit codes
- `ruff format` (without `--check`): `0` = success regardless of files formatted; `1` = files formatted and `--exit-non-zero-on-format` specified; `2` = abnormal termination.
- `ruff format --check`: `0` = no files would be formatted; `1` = files would be formatted; `2` = abnormal termination.

### Conflicting lint rules
- Disable via `lint.ignore`: `Q000`, `Q001`, `Q002`, `Q003`, `Q004`; `W191`, `E111`, `E114`, `E117`; `COM812`, `COM819`; `D203`, `D206`, `D300`, `ISC002`.
- Avoid non-default isort settings: `force-single-line`, `force-wrap-aliases`, `lines-after-imports`, `lines-between-types`, `split-on-trailing-comma`.
- `E501` can coexist but may still trigger. `ruff format` emits warnings when incompatible rules are detected.

### Import sorting
- The formatter does **NOT** sort imports. To sort and format:
  ```bash
  ruff check --select I --fix
  ruff format
  ```

## Prose summary

The formatter reference governs `ruff format`. Its central promise is Black compatibility — a drop-in replacement reaching >99.9% identical-line output on Django and Zulip — with an explicit, short list of intentional deviations (f-string internals, nested-f-string quotes, and a preview-mode method-chain layout). It documents the format defaults, docstring-code formatting (recognizing doctest, CommonMark, and reST embeddings), suppression comments (`# fmt: …`, plus YAPF compatibility), preview Markdown formatting, a two-mode exit-code contract, the catalog of lint rules that conflict with the formatter, and the explicit caveat that formatting does not sort imports (use `ruff check --select I --fix`).
