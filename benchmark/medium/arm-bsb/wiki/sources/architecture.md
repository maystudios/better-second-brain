# Source: Architecture overview

- **Raw file:** `benchmark/medium/raw/architecture.md`
- **Citation / URL:** https://modelcontextprotocol.io/docs/concepts/architecture

## Key claims
- MCP focuses solely on the protocol for context exchange; it does not dictate how AI applications use LLMs or manage the provided context.
- MCP scope includes four projects: MCP Specification, MCP SDKs, MCP Development Tools (including the MCP Inspector, https://github.com/modelcontextprotocol/inspector), and MCP Reference Server Implementations (https://github.com/modelcontextprotocol/servers).
- MCP follows a client-server architecture. An MCP host (an AI application like Claude Code or Claude Desktop) establishes connections to one or more MCP servers by creating one MCP client per server; each client maintains a dedicated connection to its server.
- Participants: MCP Host (coordinates/manages one or multiple clients), MCP Client (maintains a connection and obtains context for the host), MCP Server (provides context to clients).
- Local MCP servers using STDIO transport typically serve a single client; remote MCP servers using Streamable HTTP typically serve many clients.
- Example: Visual Studio Code acts as an MCP host; connecting to the Sentry MCP server instantiates a client object. A STDIO server runs locally; the Sentry MCP server runs remotely via Streamable HTTP.
- MCP consists of two layers: a data layer (inner) and a transport layer (outer).
- Data layer: JSON-RPC 2.0 based exchange protocol covering lifecycle management, server features (tools, resources, prompts), client features (sampling, elicitation, logging), and utility features (notifications, progress tracking).
- Transport layer: defines communication mechanisms/channels, connection establishment, message framing, and authorization. Two transports: Stdio and Streamable HTTP.
- Stdio transport: standard input/output streams for local processes on the same machine; optimal performance, no network overhead.
- Streamable HTTP transport: HTTP POST for client-to-server messages with optional Server-Sent Events for streaming; supports bearer tokens, API keys, and custom headers; MCP recommends OAuth to obtain authentication tokens.
- MCP is a stateful protocol requiring lifecycle management to negotiate capabilities both client and server support.
- Three core server primitives: Tools (executable functions), Resources (data sources for context), Prompts (reusable templates). Each has methods for discovery (`*/list`), retrieval (`*/get`), and sometimes execution (`tools/call`).
- Three client primitives: Sampling (`sampling/createMessage`), Elicitation (`elicitation/create`), Logging.
- Cross-cutting utility primitive: Tasks (Experimental) - durable execution wrappers enabling deferred result retrieval and status tracking.
- Notifications are JSON-RPC 2.0 notification messages sent without expecting a response.
- Initialization: client sends an `initialize` request to negotiate features, then sends `{ "jsonrpc": "2.0", "method": "notifications/initialized" }`. Example uses `"protocolVersion": "2025-06-18"`.
- Protocol version negotiation: if no mutually compatible version is negotiated, the connection should be terminated.
- Capability example: `"tools": {"listChanged": true}` means the server supports tools and can send `tools/list_changed` notifications.
- Tool discovery via `tools/list` (no parameters); each tool object includes `name`, `title`, `description`, `inputSchema` (JSON Schema).
- Tool execution via `tools/call` with `name` and `arguments`; responses return a `content` array.
- `notifications/tools/list_changed` notifications have no `id` field and are only sent by servers that declared `"listChanged": true`.
