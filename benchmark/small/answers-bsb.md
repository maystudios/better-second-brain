# Answers — uv (Astral Python package & project manager)

1. uv is written in **Rust**. Astral describes uv as "an extremely fast Python package and project manager, written in Rust."
   Source: [[sources/github-astral-sh-uv]] (https://github.com/astral-sh/uv); [[sources/docs-astral-sh-uv]] (https://docs.astral.sh/uv/)

2. The standalone installer command for Windows is:
   `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
   Source: [[sources/docs-astral-sh-uv-getting-started-installation]] (https://docs.astral.sh/uv/getting-started/installation/); also [[sources/github-astral-sh-uv]] (https://github.com/astral-sh/uv); [[sources/docs-astral-sh-uv]] (https://docs.astral.sh/uv/)

3. `uvx` is documented as being exactly equivalent to **`uv tool run`**.
   Source: [[sources/docs-astral-sh-uv-guides-tools]] (https://docs.astral.sh/uv/guides/tools/)

4. uv aims to replace **pip, pip-tools, pipx, poetry, pyenv, twine, and virtualenv** (the docs landing page adds "additional package management tools"). The claimed speed improvement is being **10-100x faster than pip**.
   Source: [[sources/github-astral-sh-uv]] (https://github.com/astral-sh/uv); [[sources/docs-astral-sh-uv]] (https://docs.astral.sh/uv/)

5. The pinned/specific version used in the installation page's standalone-installer example is **0.11.22** (e.g., `https://astral.sh/uv/0.11.22/install.ps1`).
   Source: [[sources/docs-astral-sh-uv-getting-started-installation]] (https://docs.astral.sh/uv/getting-started/installation/)

6. the wiki does not say
