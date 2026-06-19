# Tools

Source: https://modelcontextprotocol.io/docs/concepts/tools

The Model Context Protocol (MCP) allows servers to expose tools that can be invoked by language models. Tools enable models to interact with external systems, such as querying databases, calling APIs, or performing computations. Each tool is uniquely identified by a name and includes metadata describing its schema.

## User Interaction Model

Tools in MCP are designed to be **model-controlled**, meaning that the language model can discover and invoke tools automatically based on its contextual understanding and the user's prompts.

> For trust & safety and security, there SHOULD always be a human in the loop with the ability to deny tool invocations. Applications SHOULD provide UI that makes clear which tools are exposed, insert visual indicators when tools are invoked, and present confirmation prompts.

## Capabilities

Servers that support tools **MUST** declare the `tools` capability:

```json
{ "capabilities": { "tools": { "listChanged": true } } }
```

`listChanged` indicates whether the server will emit notifications when the list of available tools changes.

## Protocol Messages

### Listing Tools

Clients send a `tools/list` request. Supports pagination.

### Calling Tools

Clients send a `tools/call` request with `name` and `arguments`. The response contains a `content` array and `isError` boolean.

### List Changed Notification

```json
{ "jsonrpc": "2.0", "method": "notifications/tools/list_changed" }
```

## Data Types

### Tool

A tool definition includes:

- `name`: Unique identifier for the tool
- `title`: Optional human-readable name for display purposes.
- `description`: Human-readable description of functionality
- `inputSchema`: JSON Schema defining expected parameters
- `outputSchema`: Optional JSON Schema defining expected output structure
- `annotations`: optional properties describing tool behavior

> For trust & safety and security, clients MUST consider tool annotations to be untrusted unless they come from trusted servers.

### Tool Result

Tool results may contain **structured** or **unstructured** content. Unstructured content is returned in the `content` field and can contain multiple content items of different types:

- **Text Content**: `{ "type": "text", "text": "..." }`
- **Image Content**: `{ "type": "image", "data": "base64...", "mimeType": "image/png" }`
- **Audio Content**: `{ "type": "audio", "data": "base64...", "mimeType": "audio/wav" }`
- **Resource Links**: `{ "type": "resource_link", "uri": "...", ... }`. Resource links returned by tools are not guaranteed to appear in the results of a `resources/list` request.
- **Embedded Resources**: `{ "type": "resource", "resource": { ... } }`.

#### Structured Content

Structured content is returned as a JSON object in the `structuredContent` field of a result. For backwards compatibility, a tool that returns structured content SHOULD also return the serialized JSON in a TextContent block.

#### Output Schema

If an output schema is provided:

- Servers MUST provide structured results that conform to this schema.
- Clients SHOULD validate structured results against this schema.

## Error Handling

Tools use two error reporting mechanisms:

1. **Protocol Errors**: Standard JSON-RPC errors for unknown tools, invalid arguments, server errors. Example: `{ "code": -32602, "message": "Unknown tool: invalid_tool_name" }`.
2. **Tool Execution Errors**: Reported in tool results with `isError: true` (API failures, invalid input data, business logic errors).

## Security Considerations

1. Servers MUST: validate all tool inputs, implement proper access controls, rate limit tool invocations, sanitize tool outputs.
2. Clients SHOULD: prompt for user confirmation on sensitive operations; show tool inputs to the user before calling the server; validate tool results before passing to LLM; implement timeouts for tool calls; log tool usage for audit purposes.
