# Model Context Protocol (MCP)

The **Model Context Protocol (MCP)** is an open-source standard for connecting AI applications to external systems. Using MCP, assistants like Claude or ChatGPT can reach out to data sources (local files, databases), tools (search engines, calculators), and workflows (specialized prompts), which lets them pull in the information they need and actually take action.

A common way to picture it is as a *USB-C port for AI applications*. Just as USB-C gives you one standardized plug for many devices, MCP gives you one standardized way to wire an AI application into the outside world. Build an integration once, and it works across the broad ecosystem of clients and servers that speak the protocol.

## Why it matters

The benefits depend on where you sit:

- **Developers** spend less time and deal with less complexity when building or integrating AI applications.
- **AI applications and agents** gain access to a whole ecosystem of data sources, tools, and apps, which expands what they can do.
- **End-users** get more capable assistants that can read their data and act on their behalf when needed.

Concretely, MCP makes it possible for an agent to read your Google Calendar and Notion, for Claude Code to generate a web app from a Figma design, for enterprise chatbots to query many databases at once, or for a model to model a 3D object in Blender and send it to a printer.

## The shape of the system

MCP follows a client–server design. See [[Architecture]] for the full picture, but in short: an [[Architecture|MCP Host]] (the AI application) spins up one [[Architecture|MCP Client]] per connection, and each client talks to one [[Architecture|MCP Server]] that provides context.

Servers expose three core building blocks — the [[Primitives]] of MCP:

- [[Tools]] — executable functions the model can call to do things.
- [[Resources]] — data the server shares as context.
- [[Prompts]] — reusable templates for structuring interactions.

Underneath, messages travel over a chosen [[Transports|transport]] (local stdio or remote Streamable HTTP) and are encoded as JSON-RPC.

## Getting started

The MCP world is split into a few projects: the formal **specification**, language **SDKs**, development tools like the MCP Inspector, and a set of reference **servers**. See the [[Ecosystem and SDKs]] page for how to build your own client or server, which SDKs exist, and which reference servers are available to learn from.

The protocol is stewarded as an open standard (latest spec version **2025-11-25**), authored by David Soria Parra and Justin Spahr-Summers, with documentation at modelcontextprotocol.io.
