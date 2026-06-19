# Source: Prompts

- **Raw file:** `benchmark/medium/raw/prompts.md`
- **Citation / URL:** https://modelcontextprotocol.io/docs/concepts/prompts

## Key claims
- MCP provides a standardized way for servers to expose prompt templates to clients. Prompts provide structured messages and instructions for interacting with language models. Clients can discover prompts, retrieve their contents, and provide arguments to customize them.
- Prompts are user-controlled: exposed from servers to clients with the intention that the user explicitly selects them, typically through user-initiated commands such as slash commands.
- Servers supporting prompts MUST declare the `prompts` capability during initialization; `listChanged` indicates whether the server emits notifications when the prompt list changes.
- Protocol messages: `prompts/list` (supports pagination); `prompts/get` (with `name` and `arguments`; arguments may be auto-completed through the completion API; response includes a `description` and a `messages` array); `notifications/prompts/list_changed`.
- Prompt definition fields: `name`, `title` (optional), `description` (optional), `arguments` (optional list).
- PromptMessage: `role` ("user" or "assistant") and `content` (one of Text, Image, Audio, or Embedded Resources). Image/Audio data MUST be base64-encoded with a valid MIME type. Embedded resources MUST include a valid resource URI, appropriate MIME type, and either text or base64-encoded blob data.
- Error handling: invalid prompt name `-32602`; missing required arguments `-32602`; internal errors `-32603`.
- Implementation considerations: servers SHOULD validate prompt arguments before processing; clients SHOULD handle pagination for large prompt lists; both parties SHOULD respect capability negotiation.
- Security: implementations MUST carefully validate all prompt inputs and outputs to prevent injection attacks or unauthorized access to resources.
