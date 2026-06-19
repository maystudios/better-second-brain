# Resources and Prompts

Alongside [[Tools]], the [[Model Context Protocol]] defines two more server [[Primitives]]: **resources** for sharing data, and **prompts** for sharing reusable interaction templates.

## Resources

Resources let a server expose data that gives context to a language model — files, database schemas, application-specific information, and the like. Each resource is uniquely identified by a URI (RFC 3986).

They are **application-driven**: the host decides how to fold them into context, whether through UI elements, search and filter, or automatic inclusion. A server supporting resources must declare the `resources` capability, optionally with two flags — `subscribe` (the client can be notified of changes to a single resource) and `listChanged` (the server notifies when the resource list changes). Both are optional; a server can support neither, either, or both.

Clients use `resources/list` (paginated) to enumerate resources and `resources/read` (with a `uri`) to fetch one. **Resource templates** expose parameterized resources via URI templates (RFC 6570), like `file:///{path}`, and are discovered with `resources/templates/list`. Clients can subscribe with `resources/subscribe` and then receive `notifications/resources/updated` when something changes.

A resource definition carries a `uri`, `name`, optional `title`, `description`, `mimeType`, and `size`. Contents are either text (a `text` field) or binary (a base64-encoded `blob`). Resources, templates, and content blocks may also carry annotations — an intended `audience` (`user` and/or `assistant`), a `priority` from 0.0 to 1.0, and a `lastModified` ISO-8601 timestamp.

Common URI schemes include `https://` (web-fetchable), `file://` (filesystem-like, not necessarily a real filesystem), `git://` (version control), and custom schemes that must follow RFC 3986. On the safety side, servers must validate all URIs, apply access controls to sensitive resources, properly encode binary data, and check permissions before operating. Standard JSON-RPC errors apply, with `-32002` for "resource not found" and `-32603` for internal errors.

## Prompts

Prompts let a server provide structured messages and instructions for interacting with a model. Clients can discover them, retrieve their contents, and supply arguments to customize them.

Prompts are **user-controlled**: they are exposed so the user can explicitly choose them, typically through user-initiated commands like slash commands in the UI. A server supporting prompts must declare the `prompts` capability (with optional `listChanged`). Clients enumerate them with `prompts/list` (paginated) and fetch one with `prompts/get`, passing `name` and `arguments` — arguments can even be auto-completed through the completion API. The response includes a `description` and a `messages` array.

A prompt definition includes a `name`, optional `title`, optional `description`, and an optional list of `arguments`. Each message has a `role` (`user` or `assistant`) and `content`, which can be text, image, audio, or an embedded resource — images and audio must be base64-encoded with a valid MIME type, and embedded resources must carry a valid URI plus either text or blob data.

Implementations should validate prompt arguments before processing, handle pagination for large lists, and respect capability negotiation. Because prompt content flows into the model, all inputs and outputs must be carefully validated to prevent injection attacks or unauthorized access.
