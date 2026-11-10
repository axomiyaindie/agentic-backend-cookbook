# MCP connectors

**MCP** = Model Context Protocol. It's how AI clients (Claude Desktop,
IDEs, agents) call your tools over a standard interface instead of
you hand-rolling endpoints for each AI product.

## The one idea to take away

An MCP **server** exposes a list of **tools**. Each tool has:
- a name
- a description (the AI reads this to decide when to call it)
- an input schema (JSON Schema)
- a handler function

The AI client sends `tools/list` to discover them, then `tools/call`
to invoke one.

## Lesson
`01-minimal-mcp-server/` — a single-file MCP server exposing one tool.

## Where this fits in real code
- `ragen-mcp` (TypeScript, FastMCP + Hono) — real-world example
- `ai-mcp` (TypeScript monorepo) — server + client + gateway
- `Butterbase` (open-source BaaS) — MCP embedded at `/mcp`

---

## In another language?

MCP is a **protocol**, not a library. The wire format is JSON-RPC 2.0.
Any language that can read JSON and call a function can host an MCP
server. Official and community SDKs exist for:

| Language | SDK |
|---|---|
| TypeScript | `@modelcontextprotocol/sdk` (official) |
| Python | `mcp` (official) |
| Go | `mark3labs/mcp-go` (community) |
| Rust | `rmcp` (community) |
| Java | `modelcontextprotocol/java-sdk` (official) |
| C# | `modelcontextprotocol/csharp-sdk` (official) |
| Ruby | `ruby-mcp` (community) |
| PHP | `mcp/php-sdk` (community) |

If your language has none, you can still build a server: implement
`tools/list` and `tools/call` over stdin/stdout or HTTP+SSE. That's
the whole protocol surface for a tool-only server.