# Source: Transports

- **Raw file:** `benchmark/medium/raw/transports.md`
- **Citation / URL:** https://modelcontextprotocol.io/docs/concepts/transports

## Key claims
- MCP uses JSON-RPC to encode messages; JSON-RPC messages MUST be UTF-8 encoded.
- Two standard transport mechanisms are defined: stdio and Streamable HTTP. Clients SHOULD support stdio whenever possible. Clients and servers MAY implement custom transports.
- stdio transport: the client launches the MCP server as a subprocess; the server reads JSON-RPC from `stdin` and writes to `stdout`; messages are newline-delimited and MUST NOT contain embedded newlines; the server MAY write UTF-8 logging to `stderr`; the server MUST NOT write non-MCP messages to `stdout`, and the client MUST NOT write non-MCP messages to the server's `stdin`.
- Streamable HTTP replaces the HTTP+SSE transport from protocol version 2024-11-05. The server is an independent process handling multiple client connections, using HTTP POST and GET, optionally using SSE to stream multiple server messages.
- The server MUST provide a single HTTP endpoint path (the MCP endpoint) supporting both POST and GET, e.g. `https://example.com/mcp`.
- Security: servers MUST validate the `Origin` header to prevent DNS rebinding attacks; when running locally servers SHOULD bind only to localhost (127.0.0.1) rather than 0.0.0.0; servers SHOULD implement proper authentication.
- Sending messages: the client MUST use HTTP POST and MUST include an `Accept` header listing both `application/json` and `text/event-stream`. A JSON-RPC response/notification accepted by the server returns HTTP 202 Accepted with no body. A JSON-RPC request returns either `text/event-stream` (SSE) or `application/json`.
- Session management: a server MAY assign a session ID at initialization via an `Mcp-Session-Id` header on the `InitializeResult` response. The session ID SHOULD be globally unique and cryptographically secure and MUST contain only visible ASCII (0x21-0x7E). If returned, clients MUST include `Mcp-Session-Id` on subsequent requests. The server MAY terminate a session at any time, then MUST respond HTTP 404 to that session ID. Clients SHOULD send HTTP DELETE with the `Mcp-Session-Id` header to explicitly terminate a session.
- Protocol version header: over HTTP the client MUST include `MCP-Protocol-Version: <version>` on subsequent requests (example `2025-06-18`). If absent and the version cannot otherwise be identified, the server SHOULD assume `2025-03-26`. An invalid/unsupported version MUST yield `400 Bad Request`.
- Backwards compatibility: servers may continue to host both the old SSE and POST endpoints alongside the new MCP endpoint.
- Custom transports MUST preserve the JSON-RPC message format and lifecycle requirements defined by MCP; the protocol is transport-agnostic.
