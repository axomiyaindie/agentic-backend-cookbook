```
# Agent harness

**Agent harness** = the runtime loop that decides when the model wants a
tool, executes that tool, feeds the result back, and decides when to stop.

## The one idea to take away

The model never executes code. It only **decides** what to call and with
what arguments. The harness is the code that actually does the calling.

```
                    ┌──────────────────────────┐
                    │  LLM (just text in/out)  │
                    └────────────┬─────────────┘
                                 │
                    "call add(a=2, b=3)"
                                 │
                                 ▼
   ┌──────────────────────────────────────────────────┐
   │  HARNESS (this lesson)                           │
   │  1. read the model's decision                    │
   │  2. if it's a tool call → execute the tool       │
   │  3. feed the result back to the model            │
   │  4. repeat until the model says "final answer"   │
   └──────────────────────────────────────────────────┘
```

That loop is the entire difference between "a chat completion" and "an
agent." Everything else — memory, approval gates, budgets, tracing —
wraps around this loop.

## How this is different from MCP

Both involve tools. The difference is **who runs them**:

| | `02-mcp-connectors` | `09-agent-harness` (this) |
|---|---|---|
| What it is | A **protocol** for exposing tools | A **runtime** for calling tools |
| Who decides | The AI client decides what to call | The harness loops until done |
| Unit | One tool definition | The full multi-step loop |
| Example | `server.ts` exposes `add_numbers` | `main.py` loops until `final` |

MCP is the *interface*. The harness is the *engine* that drives it.

## Why this matters

When an AI assistant generates "an agent," it usually produces:

- a `while` loop that calls the model
- a `switch` on the model's decision
- a call to some tool function
- a break when the model returns a final answer

That `while` loop is the harness. If you can read it, you can tell whether
the agent will actually stop, whether it can be tricked into calling
tools forever, and whether errors are handled. If you can't read it,
you're shipping a loop you don't understand.

## Lesson

`01-minimal-harness/` — a hand-written harness with a fake LLM. No API
key, no dependencies, ~70 lines. You watch the loop run, see each tool
call, and see the loop end with a final answer.

## Where this fits in real code

- **Microsoft Agent Framework** — `HarnessAgent` is a pre-wired loop with
  todo tracking, context compaction, tool approval, and OpenTelemetry,
  all toggleable.
- **OpenAI Agents SDK** — `Runner.run(agent, input)` runs the loop for you.
- **LangGraph** — the loop is an explicit graph of nodes and edges.
- **Hand-written** — a `while True:` loop, a `switch`, and a dict of tools.

Real frameworks add a lot, but the mechanism in this lesson is the seed
of all of them.

## What a harness has to solve (and this lesson does not)

Once you understand the loop, the hard parts become visible:

- **Termination** — what stops the model from looping forever? (Max turns,
  or a required `final` decision.)
- **Tool errors** — if the tool throws, do you send the error back to the
  model, retry, or crash?
- **Approval** — some tools (delete, send email, charge card) should
  require human confirmation before running.
- **Context growth** — every turn adds to the message history. Long
  sessions need compaction or summarization.
- **Observability** — you need to log every decision and tool call so you
  can debug why the agent did what it did.

The minimal harness teaches the loop. Each of those is a lesson's worth of
work on top of it.

---

## In another language?

The loop is the same everywhere. Every language has a `while`, a `switch`,
and a dictionary of functions:

| Language | Minimal harness pattern |
|---|---|
| Go | `for { d := callModel(); switch d.Kind { case Tool: execute(d); case Final: break } }` |
| Rust | `loop { match call_model()? { Decision::Tool(t) => run(t), Decision::Final(f) => break f } }` |
| PHP | `while (true) { $d = askModel(); if ($d['kind'] === 'tool') ... else break; }` |
| Ruby | `loop do; d = ask_model; break d[:final] if d[:final]; execute(d[:tool]) end` |
| Java | `while (true) { var d = callModel(); if (d.isFinal()) break; execute(d); }` |
| C# | `while (true) { var d = CallModel(); if (d.IsFinal) break; Execute(d); }` |

If you understand the loop, you can read a harness in any language in
under five minutes.
```