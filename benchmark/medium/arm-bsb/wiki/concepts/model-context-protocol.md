# Model Context Protocol (MCP)

MCP (Model Context Protocol) is an open-source standard for connecting AI applications to external systems ([[sources/introduction]]). It focuses solely on the protocol for context exchange and does not dictate how AI applications use LLMs or manage the provided context ([[sources/architecture]]).

Using MCP, AI applications like Claude or ChatGPT can connect to data sources (e.g. local files, databases), tools (e.g. search engines, calculators), and workflows (e.g. specialized prompts) ([[sources/introduction]]). The introduction analogizes MCP to "a USB-C port for AI applications" — a standardized way to connect AI applications to external systems ([[sources/introduction]]).

## Why it matters

Stated benefits differ by ecosystem role: developers see reduced development time and complexity; AI applications/agents gain access to an ecosystem of data sources, tools, and apps; and end-users get more capable AI applications/agents ([[sources/introduction]]).

## Ecosystem support

MCP is described as an open protocol supported across a wide range of clients and servers, with named supporting tools including Claude, ChatGPT, Visual Studio Code, Cursor, and MCPJam ([[sources/introduction]]).

## Scope and projects

MCP's scope includes four projects: the MCP Specification, MCP SDKs, MCP Development Tools (including the MCP Inspector), and MCP Reference Server Implementations ([[sources/architecture]]). The specification and protocol schema (defined in TypeScript first, then published as JSON Schema for wider compatibility) live in the `modelcontextprotocol/modelcontextprotocol` GitHub repository under the MIT license ([[sources/github-modelcontextprotocol]]).

## Versioning

The `modelcontextprotocol/modelcontextprotocol` repository lists a latest version of 2025-11-25, released November 25, 2025 ([[sources/github-modelcontextprotocol]]). The architecture example for initialization uses `"protocolVersion": "2025-06-18"` ([[sources/architecture]]), and the transports documentation references protocol versions `2025-06-18`, a fallback assumption of `2025-03-26`, and a deprecated HTTP+SSE transport from `2024-11-05` ([[sources/transports]]).

## Related concepts

- [[concepts/mcp-architecture]] — participants, layers, and lifecycle
- [[concepts/mcp-primitives]] — tools, resources, prompts, and client primitives
- [[concepts/mcp-transports]] — stdio and Streamable HTTP
- [[concepts/mcp-sdks-and-servers]] — SDKs and reference servers

## Open questions

- The introduction says MCP is supported by "many others" beyond the named clients/servers, but the raw sources do not enumerate the full list ([[sources/introduction]]). The complete set of supporting clients/servers is therefore unknown from these sources.
- The relationship between the dated "latest version" (2025-11-25, [[sources/github-modelcontextprotocol]]) and the protocol versions used in examples (2025-06-18, 2025-03-26, [[sources/architecture]], [[sources/transports]]) is not explained in the raw sources, so which version is current/authoritative is unclear.
