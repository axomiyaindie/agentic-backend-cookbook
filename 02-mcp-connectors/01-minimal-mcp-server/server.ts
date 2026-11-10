// ─────────────────────────────────────────────────────────────
// Lesson: minimal MCP server
//
// MCP (Model Context Protocol) lets an AI client discover and
// call "tools" you expose. A tool is just:
//   - name
//   - description  (the AI reads this)
//   - inputSchema  (JSON Schema — what arguments are allowed)
//   - handler      (the function that runs)
//
// This file doesn't depend on any MCP library. It shows the
// data shapes so you can recognise them in real code later.
// ─────────────────────────────────────────────────────────────

type Tool = {
  name: string;
  description: string;
  inputSchema: Record<string, unknown>;
  handler: (args: Record<string, unknown>) => unknown;
};

// 1. Declare a tool. The AI sees `name`, `description`, `inputSchema`.
const tools: Tool[] = [
  {
    name: "add_numbers",
    description: "Add two numbers and return their sum.",
    inputSchema: {
      type: "object",
      properties: {
        a: { type: "number" },
        b: { type: "number" },
      },
      required: ["a", "b"],
    },
    handler: ({ a, b }) => ({
      sum: Number(a) + Number(b),
    }),
  },
];

// 2. What the AI client sees when it asks "tools/list".
function listTools() {
  return tools.map(({ name, description, inputSchema }) => ({
    name,
    description,
    inputSchema,
  }));
}

// 3. What happens when the AI calls "tools/call".
function callTool(name: string, args: Record<string, unknown>) {
  const tool = tools.find((t) => t.name === name);
  if (!tool) throw new Error(`unknown tool: ${name}`);
  return tool.handler(args);
}

// 4. Demo — this is what the AI sees and does.
console.log("tools/list →", JSON.stringify(listTools(), null, 2));
console.log("tools/call add_numbers({a:2,b:3}) →",
  callTool("add_numbers", { a: 2, b: 3 }));

// ─────────────────────────────────────────────────────────────
// Exercise: add a `get_weather` tool with inputSchema { city: string }.
// Then add `required: ["city"]`. Then delete `city` from a call
// and see what happens — in real MCP, the client validates the
// schema before your handler ever runs.
// ─────────────────────────────────────────────────────────────