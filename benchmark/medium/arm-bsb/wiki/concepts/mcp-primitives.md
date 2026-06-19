# MCP Primitives

MCP defines core primitives exposed by servers and additional primitives exposed by clients ([[sources/architecture]]). Each server primitive type has associated methods for discovery (`*/list`), retrieval (`*/get`), and in some cases execution (`tools/call`); clients use `*/list` methods to discover available primitives ([[sources/architecture]]).

## Server primitives

### Tools
Tools are executable functions that AI applications can invoke to perform actions such as file operations, API calls, or database queries ([[sources/architecture]]). They are **model-controlled**: the language model can discover and invoke tools automatically based on contextual understanding and the user's prompts ([[sources/tools]]). For trust & safety, there SHOULD always be a human in the loop able to deny tool invocations ([[sources/tools]]).

A tool definition includes `name`, optional `title`, `description`, `inputSchema` (JSON Schema), optional `outputSchema`, and optional `annotations`; clients MUST treat annotations as untrusted unless they come from trusted servers ([[sources/tools]]). Servers supporting tools MUST declare the `tools` capability ([[sources/tools]]). Tools are listed via `tools/list` and invoked via `tools/call` with `name` and `arguments`; the response contains a `content` array and an `isError` boolean ([[sources/tools]]). Errors are reported either as protocol errors (standard JSON-RPC, e.g. `-32602`) or as tool execution errors (`isError: true`) ([[sources/tools]]).

### Resources
Resources are data sources that provide contextual information to AI applications, e.g. file contents, database records, or API responses ([[sources/architecture]]). Each resource is uniquely identified by a URI (RFC 3986) ([[sources/resources]]). Resources are **application-driven**: host applications determine how to incorporate context ([[sources/resources]]).

Servers supporting resources MUST declare the `resources` capability, optionally with `subscribe` and/or `listChanged` features ([[sources/resources]]). Resources are listed via `resources/list` and read via `resources/read` (with a `uri`) ([[sources/resources]]). Resource templates expose parameterized resources via URI templates (RFC 6570), discovered through `resources/templates/list` ([[sources/resources]]). Contents may be text or base64-encoded binary (`blob`) ([[sources/resources]]). Common URI schemes include `https://`, `file://`, `git://`, and custom schemes conforming to RFC 3986 ([[sources/resources]]).

### Prompts
Prompts are reusable templates that help structure interactions with language models, such as system prompts or few-shot examples ([[sources/architecture]]). They are **user-controlled**: exposed so the user can explicitly select them, typically via user-initiated commands such as slash commands ([[sources/prompts]]). Servers supporting prompts MUST declare the `prompts` capability during initialization ([[sources/prompts]]). Prompts are listed via `prompts/list` and retrieved via `prompts/get` (with `name` and `arguments`); the response includes a `description` and a `messages` array ([[sources/prompts]]). A PromptMessage has a `role` ("user" or "assistant") and content of type Text, Image, Audio, or Embedded Resource ([[sources/prompts]]).

## Client primitives

Clients can expose three primitives: Sampling (servers request language-model completions via `sampling/createMessage`), Elicitation (servers request additional information from users via `elicitation/create`), and Logging (servers send log messages to clients) ([[sources/architecture]]).

## Content types and notifications

Tool results and prompt messages share content types including Text, Image (base64 + mimeType), and Audio (base64 + mimeType) ([[sources/tools]], [[sources/prompts]]). Tool results may additionally include Resource Links and Embedded Resources, and may be structured (returned in `structuredContent`) or unstructured ([[sources/tools]]). Each primitive supports a `notifications/<primitive>/list_changed` message when the server declares `listChanged` ([[sources/tools]], [[sources/resources]], [[sources/prompts]]).

## Security

Across primitives, servers MUST validate inputs and URIs and implement access controls; clients SHOULD seek user confirmation for sensitive operations and validate results before passing them to the LLM ([[sources/tools]], [[sources/resources]], [[sources/prompts]]).

## Related concepts

- [[concepts/model-context-protocol]]
- [[concepts/mcp-architecture]]

## Open questions

- The SDK sources describe Resources as "similar to GET endpoints" and Tools as "like POST endpoints" ([[sources/github-python-sdk]]), an analogy the protocol concept docs ([[sources/tools]], [[sources/resources]]) do not use; whether this is an exact semantic mapping or just an SDK-level convenience is not stated in the raw sources.
