✅ FILE 7 pushed: `e0cb0d8..812e154`, 47 insertions, 36 lines verified.

---

## FILE 8 of 27

**Path:**
```
D:\agentic-backend-cookbook\02-mcp-connectors\01-minimal-mcp-server\README.md
```

**Open it:**
```powershell
code D:\agentic-backend-cookbook\02-mcp-connectors\01-minimal-mcp-server\README.md
```

**Paste this:**
```
# Minimal MCP server

One file. One tool. Shows the whole protocol surface you actually need.

## What you'll learn
- How a tool is declared (name, description, JSON schema, handler)
- How an MCP client discovers and calls it

## How to run
```bash
npm install
npx tsx server.ts
```

This example **doesn't** connect to a real AI. It prints the tool
list and a sample call result, so you can see the shapes.

## What to look at
- `server.ts` — read top to bottom. The comments label each of the
  four pieces: the tool type, the tool list, the `tools/list` handler,
  and the `tools/call` handler.

---

## In another language?

The protocol is JSON-RPC 2.0. A minimal server in any language needs
only two message handlers:

| Message | What you do |
|---|---|
| `tools/list` | return `[{name, description, inputSchema}, ...]` |
| `tools/call` | find the tool by `name`, run it with `arguments`, return result |

| Language | Smallest viable approach |
|---|---|
| Go | read JSON from stdin, write JSON to stdout, `switch` on method |
| Rust | same, using `serde_json` + `std::io` |
| PHP | same, using `json_decode` / `json_encode` on STDIN/STDOUT |
| Ruby | same, using `JSON.parse` / `puts JSON.generate` |
| Java | same, using Jackson + `System.in` / `System.out` |
| C# | same, using `System.Text.Json` + `Console.In` / `Console.Out` |

The official SDKs add transports (stdio, HTTP+SSE), auth, and typed
tool definitions — but the **minimum** MCP server is two `switch`
cases. That's the point of this lesson.
```