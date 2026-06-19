# Architecture overview

Source: https://modelcontextprotocol.io/docs/concepts/architecture

This overview of the Model Context Protocol (MCP) discusses its scope and core concepts, and provides an example demonstrating each core concept.

## Scope

The Model Context Protocol includes the following projects:

- **MCP Specification**: A specification of MCP that outlines the implementation requirements for clients and servers.
- **MCP SDKs**: SDKs for different programming languages that implement MCP.
- **MCP Development Tools**: Tools for developing MCP servers and clients, including the MCP Inspector (https://github.com/modelcontextprotocol/inspector)
- **MCP Reference Server Implementations**: Reference implementations of MCP servers (https://github.com/modelcontextprotocol/servers).

> MCP focuses solely on the protocol for context exchange-it does not dictate how AI applications use LLMs or manage the provided context.

## Concepts of MCP

### Participants

MCP follows a client-server architecture where an MCP host - an AI application like Claude Code or Claude Desktop - establishes connections to one or more MCP servers. The MCP host accomplishes this by creating one MCP client for each MCP server. Each MCP client maintains a dedicated connection with its corresponding MCP server.

Local MCP servers that use the STDIO transport typically serve a single MCP client, whereas remote MCP servers that use the Streamable HTTP transport will typically serve many MCP clients.

The key participants in the MCP architecture are:

- **MCP Host**: The AI application that coordinates and manages one or multiple MCP clients
- **MCP Client**: A component that maintains a connection to an MCP server and obtains context from an MCP server for the MCP host to use
- **MCP Server**: A program that provides context to MCP clients

**For example**: Visual Studio Code acts as an MCP host. When Visual Studio Code establishes a connection to an MCP server, such as the Sentry MCP server, the Visual Studio Code runtime instantiates an MCP client object that maintains the connection to the Sentry MCP server.

MCP servers can execute locally or remotely. A server using STDIO runs locally ("local" MCP server); the Sentry MCP server runs on the Sentry platform and uses the Streamable HTTP transport ("remote" MCP server).

### Layers

MCP consists of two layers:

- **Data layer**: Defines the JSON-RPC based protocol for client-server communication, including lifecycle management, and core primitives, such as tools, resources, prompts and notifications.
- **Transport layer**: Defines the communication mechanisms and channels that enable data exchange between clients and servers, including transport-specific connection establishment, message framing, and authorization.

Conceptually the data layer is the inner layer, while the transport layer is the outer layer.

#### Data layer

The data layer implements a JSON-RPC 2.0 based exchange protocol that defines the message structure and semantics. This layer includes:

- **Lifecycle management**: Handles connection initialization, capability negotiation, and connection termination between clients and servers
- **Server features**: Tools for AI actions, resources for context data, and prompts for interaction templates
- **Client features**: Sampling from the host LLM, eliciting input from the user, and logging messages to the client
- **Utility features**: Notifications for real-time updates and progress tracking for long-running operations

#### Transport layer

The transport layer manages communication channels and authentication between clients and servers. MCP supports two transport mechanisms:

- **Stdio transport**: Uses standard input/output streams for direct process communication between local processes on the same machine, providing optimal performance with no network overhead.
- **Streamable HTTP transport**: Uses HTTP POST for client-to-server messages with optional Server-Sent Events for streaming capabilities. Supports bearer tokens, API keys, and custom headers. MCP recommends using OAuth to obtain authentication tokens.

### Data Layer Protocol

MCP uses JSON-RPC 2.0 as its underlying RPC protocol. Notifications can be used when no response is required.

#### Lifecycle management

MCP is a stateful protocol that requires lifecycle management. The purpose of lifecycle management is to negotiate the capabilities that both client and server support.

#### Primitives

MCP defines three core primitives that *servers* can expose:

- **Tools**: Executable functions that AI applications can invoke to perform actions (e.g., file operations, API calls, database queries)
- **Resources**: Data sources that provide contextual information to AI applications (e.g., file contents, database records, API responses)
- **Prompts**: Reusable templates that help structure interactions with language models (e.g., system prompts, few-shot examples)

Each primitive type has associated methods for discovery (`*/list`), retrieval (`*/get`), and in some cases, execution (`tools/call`). Clients use `*/list` methods to discover available primitives.

MCP also defines primitives that *clients* can expose:

- **Sampling**: Allows servers to request language model completions from the client's AI application via `sampling/createMessage`.
- **Elicitation**: Allows servers to request additional information from users via `elicitation/create`.
- **Logging**: Enables servers to send log messages to clients for debugging and monitoring.

Cross-cutting utility primitives:

- **Tasks (Experimental)**: Durable execution wrappers that enable deferred result retrieval and status tracking for MCP requests.

#### Notifications

The protocol supports real-time notifications. Notifications are sent as JSON-RPC 2.0 notification messages (without expecting a response).

## Example (Data Layer)

### Initialization (Lifecycle Management)

The client sends an `initialize` request to establish the connection and negotiate supported features. Example uses `"protocolVersion": "2025-06-18"`.

After successful initialization, the client sends:

```json
{ "jsonrpc": "2.0", "method": "notifications/initialized" }
```

- **Protocol Version Negotiation**: The `protocolVersion` field (e.g., "2025-06-18") ensures compatible versions. If a mutually compatible version is not negotiated, the connection should be terminated.
- **Capability Discovery**: `"tools": {"listChanged": true}` means the server supports tools AND can send `tools/list_changed` notifications.

### Tool Discovery

`tools/list` request (no parameters). Each tool object includes: `name`, `title`, `description`, `inputSchema` (JSON Schema).

### Tool Execution

`tools/call` with `name` and `arguments`. Responses return a `content` array of content objects.

### Real-time Updates (Notifications)

```json
{ "jsonrpc": "2.0", "method": "notifications/tools/list_changed" }
```

Notifications have no `id` field (JSON-RPC 2.0 notification semantics). Only sent by servers that declared `"listChanged": true`.
