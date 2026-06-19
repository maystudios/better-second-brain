# Source: Tools

- **Raw file:** `benchmark/medium/raw/tools.md`
- **Citation / URL:** https://modelcontextprotocol.io/docs/concepts/tools

## Key claims
- MCP allows servers to expose tools that can be invoked by language models. Tools enable models to interact with external systems (querying databases, calling APIs, performing computations).
- Each tool is uniquely identified by a name and includes metadata describing its schema.
- Tools are model-controlled: the language model can discover and invoke tools automatically based on contextual understanding and user prompts.
- For trust & safety/security, there SHOULD always be a human in the loop able to deny tool invocations; applications SHOULD provide UI showing which tools are exposed, visual indicators when tools are invoked, and confirmation prompts.
- Servers supporting tools MUST declare the `tools` capability; `listChanged` indicates whether the server emits notifications when the tool list changes.
- Protocol messages: `tools/list` (supports pagination); `tools/call` (with `name` and `arguments`; response contains a `content` array and an `isError` boolean); `notifications/tools/list_changed`.
- Tool definition fields: `name`, `title` (optional), `description`, `inputSchema` (JSON Schema), `outputSchema` (optional JSON Schema), `annotations` (optional).
- Clients MUST consider tool annotations untrusted unless they come from trusted servers.
- Tool results may contain structured or unstructured content. Unstructured content is returned in `content` and can include: Text Content, Image Content (base64 + mimeType), Audio Content (base64 + mimeType), Resource Links, and Embedded Resources.
- Resource links returned by tools are not guaranteed to appear in the results of a `resources/list` request.
- Structured content is returned as a JSON object in the `structuredContent` field; for backwards compatibility a tool returning structured content SHOULD also return the serialized JSON in a TextContent block.
- If an output schema is provided: servers MUST provide structured results conforming to it; clients SHOULD validate structured results against it.
- Two error-reporting mechanisms: Protocol Errors (standard JSON-RPC, e.g. `-32602` for unknown tool/invalid arguments) and Tool Execution Errors (reported in results with `isError: true`).
- Security: servers MUST validate all tool inputs, implement proper access controls, rate limit invocations, and sanitize outputs. Clients SHOULD prompt for confirmation on sensitive operations, show tool inputs before calling, validate results before passing to the LLM, implement timeouts, and log tool usage for audit.
