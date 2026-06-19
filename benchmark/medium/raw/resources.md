# Resources

Source: https://modelcontextprotocol.io/docs/concepts/resources

The Model Context Protocol (MCP) provides a standardized way for servers to expose resources to clients. Resources allow servers to share data that provides context to language models, such as files, database schemas, or application-specific information. Each resource is uniquely identified by a URI (RFC 3986).

## User Interaction Model

Resources in MCP are designed to be **application-driven**, with host applications determining how to incorporate context based on their needs. Applications could expose resources through UI elements, allow search/filter, or implement automatic context inclusion.

## Capabilities

Servers that support resources **MUST** declare the `resources` capability:

```json
{ "capabilities": { "resources": { "subscribe": true, "listChanged": true } } }
```

Two optional features:

- `subscribe`: whether the client can subscribe to be notified of changes to individual resources.
- `listChanged`: whether the server will emit notifications when the list of available resources changes.

Both are optional—servers can support neither, either, or both.

## Protocol Messages

### Listing Resources

Clients send a `resources/list` request. Supports pagination.

### Reading Resources

Clients send a `resources/read` request with a `uri` parameter.

### Resource Templates

Resource templates allow servers to expose parameterized resources using URI templates (RFC 6570). Discovered via `resources/templates/list`. Example template object includes `uriTemplate` (e.g. `file:///{path}`), `name`, `title`, `description`, `mimeType`.

### List Changed Notification

```json
{ "jsonrpc": "2.0", "method": "notifications/resources/list_changed" }
```

### Subscriptions

Clients subscribe via `resources/subscribe` (with `uri`). Updates arrive as:

```json
{ "jsonrpc": "2.0", "method": "notifications/resources/updated", "params": { "uri": "file:///project/src/main.rs" } }
```

## Data Types

### Resource

A resource definition includes:

- `uri`: Unique identifier for the resource
- `name`: The name of the resource.
- `title`: Optional human-readable name for display purposes.
- `description`: Optional description
- `mimeType`: Optional MIME type
- `size`: Optional size in bytes

### Resource Contents

Resources can contain either text or binary data. Binary content uses a base64-encoded `blob` field; text uses a `text` field.

### Annotations

Resources, resource templates and content blocks support optional annotations:

- **`audience`**: An array indicating the intended audience(s). Valid values are `"user"` and `"assistant"`.
- **`priority`**: A number from 0.0 to 1.0 indicating importance. 1 means "most important", 0 means "least important".
- **`lastModified`**: An ISO 8601 formatted timestamp (e.g., `"2025-01-12T15:00:58Z"`).

## Common URI Schemes

- `https://` — a resource available on the web. Use only when the client can fetch directly from the web on its own.
- `file://` — resources that behave like a filesystem (need not map to an actual physical filesystem). May use XDG MIME types like `inode/directory`.
- `git://` — Git version control integration.
- **Custom URI Schemes** — MUST be in accordance with RFC3986.

## Error Handling

Servers SHOULD return standard JSON-RPC errors:

- Resource not found: `-32002`
- Internal errors: `-32603`

## Security Considerations

1. Servers MUST validate all resource URIs
2. Access controls SHOULD be implemented for sensitive resources
3. Binary data MUST be properly encoded
4. Resource permissions SHOULD be checked before operations
