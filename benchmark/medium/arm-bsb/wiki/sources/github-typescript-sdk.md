# Source: GitHub — modelcontextprotocol/typescript-sdk

- **Raw file:** `benchmark/medium/raw/github-typescript-sdk.md`
- **Citation / URL:** https://github.com/modelcontextprotocol/typescript-sdk

## Key claims
- The MCP TypeScript SDK enables building standardized context providers for LLMs. It runs on Node.js, Bun, and Deno runtimes and includes server and client libraries.
- Core packages via npm: `@modelcontextprotocol/server` and `@modelcontextprotocol/client`.
- Optional middleware packages: `@modelcontextprotocol/node` (Node.js HTTP transport), `@modelcontextprotocol/express` (Express integration), `@modelcontextprotocol/hono` (Hono integration).
- A stdio server example uses `McpServer` and `StdioServerTransport` from `@modelcontextprotocol/server`, with `zod/v4`, registering a tool via `server.registerTool(...)` and connecting via `server.connect(transport)`.
- Key features: split packages for servers and clients; support for tools, resources, and prompts; multiple transport options (stdio, HTTP, Streamable HTTP); Standard Schema compatibility (Zod, Valibot, ArkType); authentication helpers.
- Status: the `main` branch contains v2 of the SDK, currently in development and pre-alpha. v1.x remains the recommended version for production use and receives bug fixes and security updates for at least 6 months after v2 ships.
- License: Apache 2.0 for new contributions; existing code under MIT.
