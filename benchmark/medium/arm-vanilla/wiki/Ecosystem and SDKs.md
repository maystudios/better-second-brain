# Ecosystem and SDKs

Beyond the protocol itself, the [[Model Context Protocol]] is supported by a small ecosystem of projects: the formal specification, language SDKs, development tools, and a collection of reference servers to learn from.

## The specification

The protocol is defined in the `modelcontextprotocol/modelcontextprotocol` repository, which hosts the formal **specification**, the **protocol schema** (defined in TypeScript first, then published as JSON Schema for wider compatibility), and the official documentation (built with Mintlify and hosted at modelcontextprotocol.io). The latest version is **2025-11-25**, released November 25, 2025. The project is authored by David Soria Parra (@dsp) and Justin Spahr-Summers (@jspahrsummers) and is MIT-licensed.

The broader scope of MCP includes the spec, the SDKs, development tools such as the **MCP Inspector**, and the reference server implementations described below.

## SDKs

Official SDKs exist for many languages — C#, Go, Java, Python, TypeScript, and others — so developers can build both [[Architecture|clients]] and [[Architecture|servers]] without implementing the wire protocol by hand.

### Python SDK

The Python SDK ships as the PyPI package `mcp`, installed with `uv add "mcp[cli]"` or `pip install "mcp[cli]"`. Its high-level **FastMCP** API lets you declare [[Tools]], [[Resources]], and [[Prompts]] with simple decorators:

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
```

It supports stdio, SSE, and Streamable HTTP transports, structured output via Pydantic models / TypedDicts / dataclasses, context management for logging and progress, OAuth 2.1 resource-server authentication, and lifespan functions for setup and cleanup. You can run a server with `uv run mcp dev server.py`, install it into Claude Desktop with `uv run mcp install server.py`, or just `python server.py`. License: MIT.

### TypeScript SDK

The TypeScript SDK runs on Node.js, Bun, and Deno, with split packages for the server (`@modelcontextprotocol/server`) and client (`@modelcontextprotocol/client`), plus optional middleware for Node HTTP, Express, and Hono. A minimal stdio server registers a tool and connects a transport:

```typescript
const server = new McpServer({ name: 'greeting-server', version: '1.0.0' });
server.registerTool('greet',
  { description: 'Greet someone by name', inputSchema: z.object({ name: z.string() }) },
  async ({ name }) => ({ content: [{ type: 'text', text: `Hello, ${name}!` }] })
);
```

It supports tools, resources, and prompts; stdio and HTTP/Streamable HTTP transports; Standard Schema validation (Zod, Valibot, ArkType); and authentication helpers. Note the versioning: the `main` branch holds **v2**, which is in development and **pre-alpha**, so **v1.x remains the recommended version for production** and will keep getting bug and security fixes for at least six months after v2 ships. License: Apache 2.0 for new contributions, MIT for existing code.

## Reference servers

The `modelcontextprotocol/servers` repository, maintained by Anthropic, collects reference implementations that show how LLMs can gain secure, controlled access to tools and data. The actively maintained set includes:

- **Everything** — a comprehensive test server with prompts, resources, and tools
- **Fetch** — web content retrieval and conversion for LLMs
- **Filesystem** — file operations with configurable access restrictions
- **Git** — repository reading, searching, and manipulation
- **Memory** — a persistent knowledge-graph memory system
- **Sequential Thinking** — problem-solving through reflective thought sequences
- **Time** — time and timezone conversion

TypeScript servers run via `npx` (e.g. `npx -y @modelcontextprotocol/server-memory`) and Python servers via `uvx` or pip (e.g. `uvx mcp-server-git`). They are wired into clients like Claude Desktop through JSON configuration:

```json
{ "mcpServers": { "filesystem": {
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/files"] } } }
```

These reference servers are meant for education rather than production, and thirteen older ones (AWS KB Retrieval, Brave Search, GitHub, Slack, SQLite, and more) now live in a separate `servers-archived` repository.
