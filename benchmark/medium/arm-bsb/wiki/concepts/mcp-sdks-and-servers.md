# MCP SDKs and Reference Servers

MCP's scope includes SDKs for different programming languages and reference server implementations ([[sources/architecture]]). The reference servers repository states that SDKs are available across multiple languages including C#, Go, Java, Python, and TypeScript ([[sources/github-servers]]).

## Python SDK

The official MCP Python SDK enables developers to build MCP clients and servers, exposing context to language models through resources, tools, and prompts ([[sources/github-python-sdk]]). Its PyPI package name is `mcp`, installable via `uv add "mcp[cli]"` or `pip install "mcp[cli]"` ([[sources/github-python-sdk]]). The quick start uses FastMCP with `@mcp.tool()` and `@mcp.resource(...)` decorators ([[sources/github-python-sdk]]). Stated features include multiple transports (Stdio, SSE, Streamable HTTP), structured output (Pydantic models, TypedDicts, dataclasses), context management, an OAuth 2.1 resource server implementation, and lifespan-based lifecycle support ([[sources/github-python-sdk]]). The SDK is MIT licensed ([[sources/github-python-sdk]]).

## TypeScript SDK

The MCP TypeScript SDK builds standardized context providers for LLMs and runs on Node.js, Bun, and Deno ([[sources/github-typescript-sdk]]). Core packages are `@modelcontextprotocol/server` and `@modelcontextprotocol/client`, with optional middleware packages for Node.js HTTP, Express, and Hono ([[sources/github-typescript-sdk]]). It supports tools, resources, and prompts; multiple transports (stdio, HTTP, Streamable HTTP); Standard Schema compatibility (Zod, Valibot, ArkType); and authentication helpers ([[sources/github-typescript-sdk]]). The `main` branch contains v2, currently in development and pre-alpha, while v1.x remains recommended for production and receives bug/security fixes for at least 6 months after v2 ships ([[sources/github-typescript-sdk]]). License is Apache 2.0 for new contributions; existing code is under MIT ([[sources/github-typescript-sdk]]).

## Reference servers

The `modelcontextprotocol/servers` repository, maintained by Anthropic, houses reference implementations demonstrating secure, controlled LLM access to tools and data ([[sources/github-servers]]). Actively maintained servers include Everything, Fetch, Filesystem, Git, Memory, Sequential Thinking, and Time ([[sources/github-servers]]). TypeScript servers run via npx (e.g. `npx -y @modelcontextprotocol/server-memory`) and Python servers via uvx or pip (e.g. `uvx mcp-server-git`) ([[sources/github-servers]]). Servers are configured in Claude Desktop or other clients through JSON (`mcpServers` with `command` and `args`) ([[sources/github-servers]]). Thirteen legacy servers (e.g. AWS KB Retrieval, Brave Search, GitHub, Slack, SQLite) were moved to a separate `servers-archived` repository ([[sources/github-servers]]). Repository languages are TypeScript (~70.4%), Python (~18.3%), and JavaScript (~10.2%); licensing is Apache 2.0 for new contributions with existing code under MIT ([[sources/github-servers]]).

The development tools in scope also include the MCP Inspector ([[sources/architecture]]).

## Related concepts

- [[concepts/model-context-protocol]]
- [[concepts/mcp-primitives]]
- [[concepts/mcp-transports]]

## Open questions

- The reference servers repository states the servers are intended for educational purposes and "not production use" ([[sources/github-servers]]); the raw sources do not specify what production-grade alternatives exist, so that is left unknown.
- The Python SDK README does not state a specific minimum Python version in its readable text ([[sources/github-python-sdk]]), so the minimum supported Python version is unknown from these sources.
- Licensing is described two ways across repos — MIT for `modelcontextprotocol/modelcontextprotocol` ([[sources/github-modelcontextprotocol]]) and the Python SDK ([[sources/github-python-sdk]]), versus "Apache 2.0 for new contributions; existing code under MIT" for `servers` and the TypeScript SDK ([[sources/github-servers]], [[sources/github-typescript-sdk]]). The raw sources do not explain this difference.
