# Transports

Source: https://modelcontextprotocol.io/docs/concepts/transports

MCP uses JSON-RPC to encode messages. JSON-RPC messages **MUST** be UTF-8 encoded.

The protocol currently defines two standard transport mechanisms for client-server communication:

1. stdio - communication over standard in and standard out
2. Streamable HTTP

Clients **SHOULD** support stdio whenever possible. It is also possible for clients and servers to implement custom transports.

## stdio

In the **stdio** transport:

- The client launches the MCP server as a subprocess.
- The server reads JSON-RPC messages from its standard input (`stdin`) and sends messages to its standard output (`stdout`).
- Messages are delimited by newlines, and MUST NOT contain embedded newlines.
- The server MAY write UTF-8 strings to its standard error (`stderr`) for logging purposes.
- The server MUST NOT write anything to its `stdout` that is not a valid MCP message.
- The client MUST NOT write anything to the server's `stdin` that is not a valid MCP message.

## Streamable HTTP

> This replaces the HTTP+SSE transport from protocol version 2024-11-05.

In the **Streamable HTTP** transport, the server operates as an independent process that can handle multiple client connections. This transport uses HTTP POST and GET requests. The server can optionally make use of Server-Sent Events (SSE) to stream multiple server messages.

The server MUST provide a single HTTP endpoint path (the **MCP endpoint**) that supports both POST and GET methods, e.g. `https://example.com/mcp`.

### Security Warning

1. Servers MUST validate the `Origin` header on all incoming connections to prevent DNS rebinding attacks
2. When running locally, servers SHOULD bind only to localhost (127.0.0.1) rather than all network interfaces (0.0.0.0)
3. Servers SHOULD implement proper authentication for all connections

### Sending Messages to the Server

- The client MUST use HTTP POST to send JSON-RPC messages to the MCP endpoint.
- The client MUST include an `Accept` header, listing both `application/json` and `text/event-stream`.
- If the input is a JSON-RPC response or notification accepted by the server, the server MUST return HTTP 202 Accepted with no body.
- If the input is a JSON-RPC request, the server MUST either return `Content-Type: text/event-stream` (SSE stream) or `Content-Type: application/json` (one JSON object).

### Session Management

- A server MAY assign a session ID at initialization time, by including it in an `Mcp-Session-Id` header on the HTTP response containing the `InitializeResult`.
- The session ID SHOULD be globally unique and cryptographically secure, and MUST only contain visible ASCII characters (0x21 to 0x7E).
- If returned, clients MUST include `Mcp-Session-Id` on all subsequent HTTP requests.
- The server MAY terminate the session at any time; afterwards it MUST respond with HTTP 404 Not Found to that session ID.
- Clients SHOULD send an HTTP DELETE to the MCP endpoint with the `Mcp-Session-Id` header to explicitly terminate a session.

### Protocol Version Header

If using HTTP, the client MUST include the `MCP-Protocol-Version: <protocol-version>` HTTP header on all subsequent requests. For example: `MCP-Protocol-Version: 2025-06-18`.

For backwards compatibility, if the server does not receive an `MCP-Protocol-Version` header and has no other way to identify the version, the server SHOULD assume protocol version `2025-03-26`.

If the server receives a request with an invalid or unsupported `MCP-Protocol-Version`, it MUST respond with `400 Bad Request`.

### Backwards Compatibility

Clients and servers can maintain backwards compatibility with the deprecated HTTP+SSE transport (from protocol version 2024-11-05). Servers may continue to host both the SSE and POST endpoints of the old transport alongside the new MCP endpoint.

## Custom Transports

Clients and servers MAY implement additional custom transport mechanisms. The protocol is transport-agnostic. Custom transports MUST preserve the JSON-RPC message format and lifecycle requirements defined by MCP.
