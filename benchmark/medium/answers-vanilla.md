# Answers (arm-vanilla wiki)

Topic: Model Context Protocol (MCP)

1. A USB-C port for AI applications. Just as USB-C provides one standardized plug for many devices, MCP gives one standardized way to wire an AI application into the outside world. (Source: wiki "Model Context Protocol" page; documentation at modelcontextprotocol.io)

2. The three core server primitives are: Tools - executable functions an AI application can invoke to perform actions (file operations, API calls, database queries); Resources - data sources that provide contextual information (file contents, database records, API responses); and Prompts - reusable templates that help structure interactions with the model (system prompts, few-shot examples). (Source: wiki "Primitives" page)

3. JSON-RPC 2.0. (Source: wiki "Architecture" page - the data layer is "a JSON-RPC 2.0 based protocol")

4. `-32002` ("resource not found"). (Source: wiki "Resources and Prompts" page)

5. The session identifier is carried in the `Mcp-Session-Id` header. A client must treat an HTTP `404 Not Found` response to that session ID as the signal to start a new session. (Source: wiki "Transports" page)

6. It should assume protocol version `2025-03-26`. (Source: wiki "Transports" page)

7. PyPI package name: `mcp`. Recommended install with the CLI extra: `uv add "mcp[cli]"` (or `pip install "mcp[cli]"`). (Source: wiki "Ecosystem and SDKs" page)

8. The most recent MCP specification version is `2025-11-25`, released November 25, 2025. (Source: wiki "Ecosystem and SDKs" / "Model Context Protocol" pages)

9. On the main branch, the v2 TypeScript SDK is in development and pre-alpha; v1.x remains the recommended version for production use (and will keep getting bug and security fixes for at least six months after v2 ships). (Source: wiki "Ecosystem and SDKs" page)

10. the wiki does not say. (The wiki states Slack and Brave Search are older servers that now live in the separate `servers-archived` repository, not actively maintained reference servers; no single reference server provides built-in Slack messaging and Brave web search.)
