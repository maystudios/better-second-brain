# Source: GitHub — modelcontextprotocol/python-sdk

- **Raw file:** `benchmark/medium/raw/github-python-sdk.md`
- **Citation / URL:** https://github.com/modelcontextprotocol/python-sdk

## Key claims
- The official MCP Python SDK enables developers to build MCP clients and servers, providing a standardized way to expose context to language models through resources, tools, and prompts.
- PyPI package name: `mcp`. Install via uv (recommended): `uv add "mcp[cli]"`, or via pip: `pip install "mcp[cli]"`.
- The README does not state a specific minimum Python version number in its readable text (it links to the Python downloads page via a version badge).
- Quick start uses FastMCP: `from mcp.server.fastmcp import FastMCP`, with `@mcp.tool()` and `@mcp.resource("greeting://{name}")` decorators; example runs `mcp.run(transport="streamable-http")`.
- Core concepts: Resources expose data (similar to GET endpoints), Tools perform actions with side effects (like POST endpoints), Prompts define reusable interaction templates.
- Key features: multiple transports (Stdio, SSE, Streamable HTTP); structured output (Pydantic models, TypedDicts, dataclasses); context management (logging, progress reporting, resource reading); authentication (OAuth 2.1 resource server implementation available); lifecycle support (lifespan functions).
- Running a server: development mode `uv run mcp dev server.py`; install in Claude Desktop `uv run mcp install server.py`; direct execution `python server.py`.
- License: MIT. PyPI package: `mcp`.
