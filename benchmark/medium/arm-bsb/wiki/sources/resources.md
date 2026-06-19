# Source: Resources

- **Raw file:** `benchmark/medium/raw/resources.md`
- **Citation / URL:** https://modelcontextprotocol.io/docs/concepts/resources

## Key claims
- MCP provides a standardized way for servers to expose resources to clients. Resources let servers share data that provides context to language models (files, database schemas, application-specific information).
- Each resource is uniquely identified by a URI (RFC 3986).
- Resources are application-driven: host applications determine how to incorporate context (UI elements, search/filter, automatic context inclusion).
- Servers supporting resources MUST declare the `resources` capability. Two optional features: `subscribe` (client can subscribe to changes of individual resources) and `listChanged` (server emits notifications when the resource list changes). Servers may support neither, either, or both.
- Protocol messages: `resources/list` (supports pagination); `resources/read` (with a `uri` parameter).
- Resource templates expose parameterized resources using URI templates (RFC 6570), discovered via `resources/templates/list`. A template object includes `uriTemplate` (e.g. `file:///{path}`), `name`, `title`, `description`, `mimeType`.
- List changed notification: `notifications/resources/list_changed`.
- Subscriptions: clients subscribe via `resources/subscribe` (with `uri`); updates arrive as `notifications/resources/updated` with the `uri` in params.
- Resource definition fields: `uri`, `name`, `title` (optional), `description` (optional), `mimeType` (optional), `size` (optional, bytes).
- Resource contents can be text (`text` field) or binary (base64-encoded `blob` field).
- Annotations supported on resources, templates, and content blocks: `audience` (array; valid values `"user"`, `"assistant"`), `priority` (0.0-1.0; 1 = most important), `lastModified` (ISO 8601 timestamp).
- Common URI schemes: `https://` (web; only when client can fetch directly), `file://` (filesystem-like; may use XDG MIME types like `inode/directory`), `git://` (Git integration), and custom schemes (MUST conform to RFC 3986).
- Error handling: resource not found `-32002`; internal errors `-32603`.
- Security: servers MUST validate all resource URIs; access controls SHOULD be implemented for sensitive resources; binary data MUST be properly encoded; resource permissions SHOULD be checked before operations.
