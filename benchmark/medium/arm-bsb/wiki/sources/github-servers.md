# Source: GitHub - modelcontextprotocol/servers

- **Raw file:** `benchmark/medium/raw/github-servers.md`
- **Citation / URL:** https://github.com/modelcontextprotocol/servers

## Key claims
- This repository houses reference implementations for MCP, maintained by Anthropic, demonstrating how LLMs can gain secure, controlled access to tools and data sources through MCP.
- Actively maintained reference servers: Everything (test server with prompts, resources, tools), Fetch (web content retrieval/conversion for LLMs), Filesystem (file operations with configurable access restrictions), Git (repository reading/searching/manipulation), Memory (persistent knowledge-graph-based memory), Sequential Thinking (problem-solving via reflective thought sequences), Time (time and timezone conversion).
- TypeScript servers run via npx, e.g. `npx -y @modelcontextprotocol/server-memory`.
- Python servers run via uvx or pip, e.g. `uvx mcp-server-git` or `pip install mcp-server-git` then `python -m mcp_server_git`.
- Servers are configured in Claude Desktop or other MCP clients via JSON configuration (an `mcpServers` block specifying `command` and `args`).
- Thirteen legacy servers (AWS KB Retrieval, Brave Search, GitHub, Slack, SQLite, etc.) were moved to the separate `servers-archived` repository.
- Languages: TypeScript (~70.4%), Python (~18.3%), JavaScript (~10.2%).
- License: Apache 2.0 for new contributions; existing code under MIT.
- Status: reference implementations intended for educational purposes, not production use.
- SDKs available across multiple languages: C#, Go, Java, Python, TypeScript, and others.
