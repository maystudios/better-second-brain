# Answers — Model Context Protocol (MCP)

1. MCP is analogized to "a USB-C port for AI applications" — a standardized way to connect AI applications to external systems.
   Source: [[sources/introduction]] — https://modelcontextprotocol.io/introduction

2. The three core server primitives are: **Tools** — executable functions an AI application can invoke to perform actions (e.g. file operations, API calls, database queries); **Resources** — data sources that provide contextual information (e.g. file contents, database records, API responses); and **Prompts** — reusable templates that help structure interactions with language models (e.g. system prompts or few-shot examples).
   Source: [[sources/architecture]] — https://modelcontextprotocol.io/docs/concepts/architecture

3. The MCP data layer uses **JSON-RPC 2.0** to encode messages.
   Source: [[sources/architecture]] — https://modelcontextprotocol.io/docs/concepts/architecture

4. The wiki does not say. (It documents tool protocol errors using standard JSON-RPC codes such as -32602 for invalid params, but does not state a specific JSON-RPC error code for a resource that is not found.)
   the wiki does not say

5. The session identifier is carried in the **`Mcp-Session-Id`** HTTP header; a client must treat an **HTTP 404** response (returned for a session ID the server has terminated) as a signal to start a new session.
   Source: [[sources/transports]] — https://modelcontextprotocol.io/docs/concepts/transports

6. If no `MCP-Protocol-Version` header is received and the version cannot otherwise be identified, the server should assume protocol version **`2025-03-26`**.
   Source: [[sources/transports]] — https://modelcontextprotocol.io/docs/concepts/transports

7. The PyPI package name is **`mcp`**. The recommended install command including the CLI extra is **`uv add "mcp[cli]"`** (or, via pip, `pip install "mcp[cli]"`).
   Source: [[sources/github-python-sdk]] — https://github.com/modelcontextprotocol/python-sdk

8. The most recent MCP specification version is **2025-11-25**, released **November 25, 2025**.
   Source: [[sources/github-modelcontextprotocol]] — https://github.com/modelcontextprotocol/modelcontextprotocol

9. The `main` branch contains **v2**, which is currently in development and pre-alpha. **v1.x** remains recommended for production use (and receives bug/security fixes for at least 6 months after v2 ships).
   Source: [[sources/github-typescript-sdk]] — https://github.com/modelcontextprotocol/typescript-sdk

10. the wiki does not say
    (The wiki states that Slack and Brave Search are among thirteen legacy servers that were moved to the separate `servers-archived` repository, not actively maintained reference servers. The actively maintained servers are Everything, Fetch, Filesystem, Git, Memory, Sequential Thinking, and Time. Source: [[sources/github-servers]] — https://github.com/modelcontextprotocol/servers.)
