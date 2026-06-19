# modelcontextprotocol/servers (GitHub)

Source: https://github.com/modelcontextprotocol/servers

This GitHub repository houses reference implementations for the Model Context Protocol (MCP), maintained by Anthropic. The project demonstrates how LLMs can gain secure, controlled access to tools and data sources through MCP.

## Reference Servers (actively maintained)

- **Everything** — Comprehensive test server featuring prompts, resources, and tools
- **Fetch** — Web content retrieval and conversion optimized for LLM processing
- **Filesystem** — File operations with configurable access restrictions
- **Git** — Repository reading, searching, and manipulation capabilities
- **Memory** — Persistent knowledge graph-based memory system
- **Sequential Thinking** — Problem-solving through reflective thought sequences
- **Time** — Time and timezone conversion tools

## Using the Servers

### TypeScript Servers (via npx)

```bash
npx -y @modelcontextprotocol/server-memory
```

### Python Servers (via uvx or pip)

```bash
uvx mcp-server-git
# or
pip install mcp-server-git
python -m mcp_server_git
```

## Integration with Clients

Configure servers in Claude Desktop or other MCP clients through JSON configuration. Example:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/files"]
    }
  }
}
```

## Archived Servers

Thirteen legacy servers (AWS KB Retrieval, Brave Search, GitHub, Slack, SQLite, etc.) have been moved to the separate `servers-archived` repository.

## Key Details

- **Languages**: TypeScript (~70.4%), Python (~18.3%), JavaScript (~10.2%)
- **License**: Apache 2.0 for new contributions; existing code under MIT
- **Status**: Reference implementations intended for educational purposes, not production use
- **SDKs Available**: Multiple language implementations across C#, Go, Java, Python, TypeScript, and others
