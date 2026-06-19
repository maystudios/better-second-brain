# MCP Transports

The transport layer defines the communication mechanisms and channels that enable data exchange between clients and servers, including connection establishment, message framing, and authorization ([[sources/architecture]]). MCP uses JSON-RPC to encode messages, and JSON-RPC messages MUST be UTF-8 encoded ([[sources/transports]]). Two standard transports are defined — stdio and Streamable HTTP — and clients SHOULD support stdio whenever possible ([[sources/transports]]).

## stdio

In the stdio transport the client launches the MCP server as a subprocess; the server reads JSON-RPC messages from `stdin` and writes them to `stdout`, with messages newline-delimited and containing no embedded newlines ([[sources/transports]]). The server MAY write UTF-8 logging to `stderr`, but MUST NOT write non-MCP messages to `stdout`, and the client MUST NOT write non-MCP messages to the server's `stdin` ([[sources/transports]]). stdio is used by local servers and offers optimal performance with no network overhead ([[sources/architecture]]).

## Streamable HTTP

Streamable HTTP replaces the HTTP+SSE transport from protocol version 2024-11-05 ([[sources/transports]]). The server is an independent process handling multiple client connections, using HTTP POST and GET, optionally using Server-Sent Events (SSE) to stream multiple server messages ([[sources/transports]]). It must expose a single MCP endpoint path supporting both POST and GET, e.g. `https://example.com/mcp` ([[sources/transports]]).

The client MUST use HTTP POST and MUST include an `Accept` header listing both `application/json` and `text/event-stream` ([[sources/transports]]). A JSON-RPC response/notification accepted by the server returns HTTP 202 with no body, while a JSON-RPC request returns either an SSE stream or a single JSON object ([[sources/transports]]). For authentication, Streamable HTTP supports bearer tokens, API keys, and custom headers, and MCP recommends using OAuth to obtain authentication tokens ([[sources/architecture]]).

### Session management

A server MAY assign a session ID at initialization via an `Mcp-Session-Id` header on the `InitializeResult` response; the ID SHOULD be globally unique and cryptographically secure and MUST contain only visible ASCII (0x21–0x7E) ([[sources/transports]]). If returned, clients MUST include `Mcp-Session-Id` on subsequent requests; the server MAY terminate a session at any time (then responding HTTP 404 to that ID), and clients SHOULD send an HTTP DELETE to end a session ([[sources/transports]]).

### Protocol version header

Over HTTP, the client MUST include an `MCP-Protocol-Version` header on subsequent requests (example `2025-06-18`); if absent and otherwise unidentifiable, the server SHOULD assume `2025-03-26`, and an invalid/unsupported version MUST yield `400 Bad Request` ([[sources/transports]]).

## Security

Servers MUST validate the `Origin` header to prevent DNS rebinding attacks, SHOULD bind only to localhost (127.0.0.1) when running locally rather than 0.0.0.0, and SHOULD implement proper authentication ([[sources/transports]]).

## Custom transports

Clients and servers MAY implement custom transports; the protocol is transport-agnostic, but custom transports MUST preserve the JSON-RPC message format and lifecycle requirements defined by MCP ([[sources/transports]]).

## Related concepts

- [[concepts/mcp-architecture]]
- [[concepts/model-context-protocol]]

## Open questions

- The architecture source names "SSE" as a supported transport in the Python SDK feature list ([[sources/github-python-sdk]]), while the transports source describes HTTP+SSE as the deprecated transport replaced by Streamable HTTP ([[sources/transports]]). The raw sources do not reconcile whether the SDK's "SSE" support refers to the deprecated transport, to SSE-within-Streamable-HTTP, or to both, so this is left flagged.
