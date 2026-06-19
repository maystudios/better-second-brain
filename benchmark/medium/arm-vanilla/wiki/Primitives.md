# Primitives

Primitives are the core building blocks that MCP participants expose to one another. They are defined in the data layer (see [[Architecture]]) and discovered through capability negotiation during the lifecycle handshake.

## Server primitives

Servers can expose three primitives, each with associated methods for discovery (`*/list`), retrieval (`*/get`), and sometimes execution (`tools/call`). Clients use the `*/list` methods to find out what a server offers.

- **[[Tools]]** — executable functions an AI application can invoke to perform actions, such as file operations, API calls, or database queries.
- **[[Resources]]** — data sources that provide contextual information, such as file contents, database records, or API responses.
- **[[Prompts]]** — reusable templates that help structure interactions with the model, such as system prompts or few-shot examples.

A useful way to think about the difference: tools are model-controlled (the model decides when to call them), resources are application-driven (the host decides how to use them), and prompts are user-controlled (the user explicitly picks them, often as slash commands).

## Client primitives

MCP also defines primitives that *clients* expose back to servers:

- **Sampling** — lets a server request a language-model completion from the client's AI application via `sampling/createMessage`.
- **Elicitation** — lets a server request additional input from the user via `elicitation/create`.
- **Logging** — lets a server send log messages to the client for debugging and monitoring.

## Cross-cutting utilities

- **Notifications** — JSON-RPC 2.0 messages sent without expecting a response, used for real-time updates such as list-changed events.
- **Tasks (experimental)** — durable execution wrappers that enable deferred result retrieval and status tracking for long-running MCP requests.

Together these primitives let the [[Architecture|MCP Server]] and [[Architecture|MCP Client]] hold a rich, two-way conversation rather than a one-directional request flow.
