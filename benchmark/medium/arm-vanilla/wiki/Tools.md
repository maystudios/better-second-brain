# Tools

**Tools** are one of the three server [[Primitives]] in the [[Model Context Protocol]]. They let servers expose functions that a language model can invoke to interact with external systems - querying databases, calling APIs, performing computations, and so on. Each tool has a unique name and metadata describing its schema.

## Model-controlled, human-supervised

Tools are designed to be **model-controlled**: the model discovers and invokes them automatically based on the conversation and the user's prompts. Because that gives the model real reach into external systems, the spec is firm that there *should* always be a human in the loop with the ability to deny an invocation. Applications should make clear which tools are exposed, show visual indicators when a tool runs, and present confirmation prompts before sensitive actions.

## Capability and discovery

A server that supports tools must declare the `tools` capability, optionally with `listChanged` to signal that it will emit notifications when its tool list changes. Clients discover tools with `tools/list` (which supports pagination) and invoke them with `tools/call`, passing `name` and `arguments`. The response carries a `content` array plus an `isError` boolean.

## What a tool looks like

A tool definition includes:

- `name` - unique identifier
- `title` - optional human-readable display name
- `description` - what the tool does
- `inputSchema` - JSON Schema for the expected parameters
- `outputSchema` - optional JSON Schema for the output structure
- `annotations` - optional properties describing behavior (clients must treat these as untrusted unless they come from a trusted server)

## Results and errors

Tool results can be **unstructured** (a `content` array of text, image, audio, resource-link, or embedded-resource items) or **structured** (a JSON object in `structuredContent` that conforms to the tool's output schema). For backward compatibility, structured results should also be serialized into a text block.

There are two error channels. **Protocol errors** are standard JSON-RPC errors for things like an unknown tool or invalid arguments (e.g. `-32602`). **Tool execution errors** - API failures, bad input, business-logic problems - are reported inside the result with `isError: true`, so the model can see and reason about them.

## Safety

Servers must validate all inputs, enforce access controls, rate-limit invocations, and sanitize outputs. Clients should confirm sensitive operations with the user, show inputs before calling, validate results before handing them to the LLM, set timeouts, and log usage for audit. For how tools fit alongside data and templates, see [[Resources]] and [[Prompts]].
