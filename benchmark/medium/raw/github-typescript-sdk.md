# modelcontextprotocol/typescript-sdk (GitHub)

Source: https://github.com/modelcontextprotocol/typescript-sdk

The Model Context Protocol (MCP) TypeScript SDK enables building standardized context providers for LLMs. It runs on Node.js, Bun, and Deno runtimes and includes server and client libraries.

## Installation

Core packages via npm:

```bash
npm install @modelcontextprotocol/server
npm install @modelcontextprotocol/client
```

Optional middleware packages:

- `@modelcontextprotocol/node` - Node.js HTTP transport
- `@modelcontextprotocol/express` - Express integration
- `@modelcontextprotocol/hono` - Hono integration

## Creating a Server (stdio example)

```typescript
import { McpServer } from '@modelcontextprotocol/server';
import { StdioServerTransport } from '@modelcontextprotocol/server/stdio';
import * as z from 'zod/v4';

const server = new McpServer({ name: 'greeting-server', version: '1.0.0' });

server.registerTool(
    'greet',
    {
        description: 'Greet someone by name',
        inputSchema: z.object({ name: z.string() })
    },
    async ({ name }) => ({
        content: [{ type: 'text', text: `Hello, ${name}!` }]
    })
);

async function main() {
    const transport = new StdioServerTransport();
    await server.connect(transport);
}

main();
```

## Key Features

- Split packages for servers and clients
- Support for tools, resources, and prompts
- Multiple transport options (stdio, HTTP, Streamable HTTP)
- Standard Schema compatibility (Zod, Valibot, ArkType)
- Authentication helpers

## Status

- The `main` branch contains **v2** of the SDK, currently in development, **pre-alpha**.
- **v1.x remains the recommended version for production use.** v1.x receives bug fixes and security updates for at least 6 months after v2 ships.

## License

Apache 2.0 for new contributions; existing code under MIT.
