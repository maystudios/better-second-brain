# modelcontextprotocol/python-sdk (GitHub)

Source: https://github.com/modelcontextprotocol/python-sdk

The official Model Context Protocol (MCP) Python SDK enables developers to build MCP clients and servers. It provides a standardized way to expose context to language models through resources, tools, and prompts.

## Installation

- **PyPI Package Name:** `mcp`
- Install via uv (recommended): `uv add "mcp[cli]"`
- Or via pip: `pip install "mcp[cli]"`

(The README links to the Python downloads page via a Python version badge but does not state a specific minimum version number in the readable text.)

## Quick Start with FastMCP

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Demo", json_response=True)

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
```

## Core Concepts

- **Resources** expose data (similar to GET endpoints)
- **Tools** perform actions with side effects (like POST endpoints)
- **Prompts** define reusable interaction templates

## Key Features

- **Multiple Transports:** Stdio, SSE, and Streamable HTTP support
- **Structured Output:** Return Pydantic models, TypedDicts, or dataclasses
- **Context Management:** Access logging, progress reporting, and resource reading
- **Authentication:** OAuth 2.1 resource server implementation available
- **Lifecycle Support:** Initialize and cleanup resources with lifespan functions

## Running Your Server

- Development mode: `uv run mcp dev server.py`
- Install in Claude Desktop: `uv run mcp install server.py`
- Direct execution: `python server.py`

## Repository Info

- **GitHub:** modelcontextprotocol/python-sdk
- **License:** MIT
- **PyPI Package:** `mcp`
