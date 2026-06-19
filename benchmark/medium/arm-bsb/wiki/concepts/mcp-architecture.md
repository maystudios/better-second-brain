# MCP Architecture

MCP follows a client-server architecture in which an MCP host - an AI application such as Claude Code or Claude Desktop - establishes connections to one or more MCP servers by creating one MCP client per server, with each client maintaining a dedicated connection to its server ([[sources/architecture]]).

## Participants

- **MCP Host**: the AI application that coordinates and manages one or multiple MCP clients ([[sources/architecture]]).
- **MCP Client**: a component that maintains a connection to an MCP server and obtains context from it for the host to use ([[sources/architecture]]).
- **MCP Server**: a program that provides context to MCP clients ([[sources/architecture]]).

As an example, Visual Studio Code acts as an MCP host; when it connects to the Sentry MCP server, its runtime instantiates an MCP client object that maintains the connection ([[sources/architecture]]). Servers can run locally or remotely: local servers using STDIO typically serve a single client, while remote servers using Streamable HTTP typically serve many clients ([[sources/architecture]]).

## Layers

MCP consists of two layers, with the data layer as the inner layer and the transport layer as the outer layer ([[sources/architecture]]):

- **Data layer**: a JSON-RPC 2.0 based exchange protocol covering lifecycle management, server features (tools, resources, prompts), client features (sampling, elicitation, logging), and utility features such as notifications and progress tracking ([[sources/architecture]]).
- **Transport layer**: defines communication mechanisms/channels, connection establishment, message framing, and authorization ([[sources/architecture]]). See [[concepts/mcp-transports]].

## Lifecycle management

MCP is a stateful protocol that requires lifecycle management in order to negotiate the capabilities that both client and server support ([[sources/architecture]]). The client sends an `initialize` request to establish the connection and negotiate supported features, then sends a `notifications/initialized` notification ([[sources/architecture]]). If a mutually compatible protocol version is not negotiated, the connection should be terminated ([[sources/architecture]]).

Capabilities are declared per primitive; for example `"tools": {"listChanged": true}` means the server supports tools and can send `tools/list_changed` notifications ([[sources/architecture]]). Notifications are JSON-RPC 2.0 messages sent without expecting a response, and a `list_changed` notification (which has no `id` field) is only sent by servers that declared `"listChanged": true` ([[sources/architecture]]).

## Related concepts

- [[concepts/model-context-protocol]]
- [[concepts/mcp-primitives]]
- [[concepts/mcp-transports]]

## Open questions

- The architecture source lists "Tasks (Experimental)" as a cross-cutting utility primitive for durable execution and deferred result retrieval, but the raw sources provide no further detail (e.g. method names or message shapes), so its full behavior is unknown ([[sources/architecture]]).
