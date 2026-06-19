# Architecture

The [[Model Context Protocol]] focuses solely on the protocol for context exchange. It deliberately does not dictate how an AI application uses its LLM or manages the context it receives - it just standardizes how that context moves around.

## Participants

MCP uses a client-server architecture with three roles:

- **[[Architecture|MCP Host]]** - the AI application (Claude Code, Claude Desktop, VS Code) that coordinates one or more clients.
- **[[Architecture|MCP Client]]** - a component inside the host that maintains a connection to a single server and obtains context from it.
- **[[Architecture|MCP Server]]** - a program that provides context to clients.

The host creates one client per server, and each client keeps a dedicated connection to its server. For example, Visual Studio Code acts as a host; when it connects to the Sentry MCP server, its runtime instantiates a client object that manages that connection. Servers can run locally (over stdio) or remotely (the Sentry server runs on Sentry's platform over Streamable HTTP). Local stdio servers typically serve a single client, while remote HTTP servers usually serve many.

## Two layers

MCP is organized into two layers:

- **Data layer** (the inner layer) - a JSON-RPC 2.0 based protocol defining message structure and semantics, including lifecycle management and the core [[Primitives]].
- **Transport layer** (the outer layer) - the communication channels and authorization that carry the data. See [[Transports]] for the details.

### Data layer

The data layer covers:

- **Lifecycle management** - connection initialization, capability negotiation, and termination.
- **Server features** - [[Tools]], [[Resources]], and [[Prompts]].
- **Client features** - sampling, elicitation, and logging (see [[Primitives]]).
- **Utility features** - notifications and progress tracking.

## Lifecycle and JSON-RPC

MCP is a **stateful** protocol that requires lifecycle management. The point of that lifecycle is to negotiate which capabilities both sides support. A session opens with the client sending an `initialize` request that names a `protocolVersion` (for example, `2025-06-18`) and lists its capabilities; if no mutually compatible version can be agreed on, the connection is terminated. The client then sends a `notifications/initialized` message to confirm it is ready.

Capability flags travel in this handshake. For instance, a server declaring `"tools": { "listChanged": true }` is saying both that it supports tools and that it will emit `tools/list_changed` notifications when its tool list changes.

After initialization, the model can discover tools with `tools/list` and invoke them with `tools/call`, which returns a `content` array. The protocol also supports real-time **notifications** - JSON-RPC messages sent without an `id` and expecting no response - which is how servers push updates like `notifications/tools/list_changed`.
