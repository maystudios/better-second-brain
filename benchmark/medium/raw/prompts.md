# Prompts

Source: https://modelcontextprotocol.io/docs/concepts/prompts

The Model Context Protocol (MCP) provides a standardized way for servers to expose prompt templates to clients. Prompts allow servers to provide structured messages and instructions for interacting with language models. Clients can discover available prompts, retrieve their contents, and provide arguments to customize them.

## User Interaction Model

Prompts are designed to be **user-controlled**, meaning they are exposed from servers to clients with the intention of the user being able to explicitly select them for use. Typically, prompts would be triggered through user-initiated commands in the user interface, for example as slash commands.

## Capabilities

Servers that support prompts **MUST** declare the `prompts` capability during initialization:

```json
{ "capabilities": { "prompts": { "listChanged": true } } }
```

`listChanged` indicates whether the server will emit notifications when the list of available prompts changes.

## Protocol Messages

### Listing Prompts

Clients send a `prompts/list` request. Supports pagination.

### Getting a Prompt

Clients send a `prompts/get` request with `name` and `arguments`. Arguments may be auto-completed through the completion API. The response includes a `description` and a `messages` array.

### List Changed Notification

```json
{ "jsonrpc": "2.0", "method": "notifications/prompts/list_changed" }
```

## Data Types

### Prompt

A prompt definition includes:

- `name`: Unique identifier for the prompt
- `title`: Optional human-readable name for display purposes.
- `description`: Optional human-readable description
- `arguments`: Optional list of arguments for customization

### PromptMessage

Messages in a prompt can contain:

- `role`: Either "user" or "assistant" to indicate the speaker
- `content`: One of: Text Content, Image Content, Audio Content, or Embedded Resources.

#### Text Content
`{ "type": "text", "text": "..." }`

#### Image Content
`{ "type": "image", "data": "base64...", "mimeType": "image/png" }` - image data MUST be base64-encoded with a valid MIME type.

#### Audio Content
`{ "type": "audio", "data": "base64...", "mimeType": "audio/wav" }` - audio data MUST be base64-encoded with a valid MIME type.

#### Embedded Resources
`{ "type": "resource", "resource": { "uri": "...", "mimeType": "...", "text": "..." } }`. Resources can contain either text or binary (blob) data and MUST include a valid resource URI, appropriate MIME type, and either text content or base64-encoded blob data.

## Error Handling

Servers SHOULD return standard JSON-RPC errors:

- Invalid prompt name: `-32602` (Invalid params)
- Missing required arguments: `-32602` (Invalid params)
- Internal errors: `-32603` (Internal error)

## Implementation Considerations

1. Servers SHOULD validate prompt arguments before processing
2. Clients SHOULD handle pagination for large prompt lists
3. Both parties SHOULD respect capability negotiation

## Security

Implementations MUST carefully validate all prompt inputs and outputs to prevent injection attacks or unauthorized access to resources.
