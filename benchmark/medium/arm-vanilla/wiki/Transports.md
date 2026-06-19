# Transports

The **transport layer** is the outer layer of the [[Model Context Protocol]] (see [[Architecture]]) - it carries the data-layer messages between client and server. MCP encodes all messages as JSON-RPC, and those messages must be UTF-8 encoded. The protocol itself is transport-agnostic, but it defines two standard transports, and clients should support stdio whenever possible.

## stdio

In the **stdio** transport the client launches the [[Architecture|MCP Server]] as a subprocess and communicates over standard streams. The server reads JSON-RPC messages from `stdin` and writes them to `stdout`. Messages are newline-delimited and must not contain embedded newlines. The server may write free-form UTF-8 to `stderr` for logging, but it must never write anything to `stdout` that isn't a valid MCP message - and likewise the client must never write non-MCP data to the server's `stdin`. Because it's just two local processes talking over pipes, stdio has no network overhead and is ideal for local servers.

## Streamable HTTP

The **Streamable HTTP** transport (which replaces the older HTTP+SSE transport from protocol version 2024-11-05) runs the server as an independent process that can handle many client connections. It uses HTTP POST and GET against a single **MCP endpoint** path that supports both methods, for example `https://example.com/mcp`, and can optionally use Server-Sent Events to stream multiple server messages.

Clients send messages via HTTP POST and must include an `Accept` header listing both `application/json` and `text/event-stream`. If the client's message is a response or notification the server accepts, the server returns `202 Accepted` with no body. If it's a request, the server replies either with an SSE stream (`Content-Type: text/event-stream`) or a single JSON object (`Content-Type: application/json`).

### Sessions and versioning

A server may assign a session at initialization by returning an `Mcp-Session-Id` header on the `InitializeResult` response. That ID should be globally unique, cryptographically secure, and made of visible ASCII (0x21-0x7E); if it's returned, clients must echo it on every later request. A server may terminate a session at any time and then respond `404 Not Found` to that ID, and clients should send an HTTP `DELETE` with the session header to end a session explicitly.

Over HTTP, clients must also send an `MCP-Protocol-Version` header (e.g. `2025-06-18`) on subsequent requests. If a server gets no such header and can't otherwise tell, it should assume `2025-03-26`; if the version is invalid or unsupported, it must respond `400 Bad Request`.

## Security and custom transports

Streamable HTTP servers must validate the `Origin` header on incoming connections to prevent DNS-rebinding attacks, should bind only to localhost (127.0.0.1) rather than all interfaces when running locally, and should authenticate all connections. The transport layer is where authorization lives, and MCP recommends OAuth for obtaining tokens (bearer tokens, API keys, and custom headers are all supported).

Finally, clients and servers may implement **custom transports** of their own. Anything they build must preserve the JSON-RPC message format and the lifecycle requirements the protocol defines.
