```
# Minimal agent harness

A hand-written agent loop with a **fake LLM**. No API key, no external
dependencies, no framework. Just the loop, so you can see exactly what
an agent framework does underneath.

## What you'll learn
- What an agent loop actually is: decide, execute, feed back, repeat
- Why the LLM never runs code itself — it only asks for it
- What stops the loop (the `final` decision)
- Where the hard problems live (termination, errors, approval)

## How to run
```bash
python main.py
```

That's it. No `pip install`, no `requirements.txt`. The script uses only
the Python standard library.

## What to look at
- `main.py` — read `run_harness` first. It's the whole loop.
- Then read `fake_llm` — it stands in for a real model. Each call
  advances the script one step, so you can see the loop without needing
  an API key.

## Walkthrough — what you'll see

Run `python main.py`. Output looks roughly like:

```text
--- turn 1 ---
model wants: tool 'add' with {'a': 2, 'b': 3}
tool result: 5
--- turn 2 ---
model wants: tool 'multiply' with {'a': 5, 'b': 10}
tool result: 50
--- turn 3 ---
model wants: final answer: "The answer is 50."
--- final ---
The answer is 50.
```

Three turns. The model asked for two tools, the harness ran them, fed
the results back, and the model finally said "done." The harness never
decided *what* to do — it just did what the model asked, one step at a
time.

## What each line is

| Line | Who produced it | What it means |
|---|---|---|
| `--- turn N ---` | Harness | The loop ran again |
| `model wants: tool ...` | Harness, reading the fake LLM's output | The model's decision for this turn |
| `tool result: ...` | Harness, after calling the tool | The tool actually ran |
| `model wants: final answer` | Harness | The model decided to stop |
| `--- final ---` | Harness | The loop ended |

The **decision** always comes from the model. The **execution** always
comes from the harness. That separation is the whole point.

## The loop in five lines

```python
while True:
    decision = model.decide(messages)
    if decision.kind == "final":
        return decision.text
    result = tools[decision.name](**decision.args)
    messages.append({"role": "tool", "content": str(result)})
```

That's it. Every agent framework — Microsoft Agent Framework, OpenAI
Agents SDK, LangGraph, everything — is a wrapper around this shape. They
add features, but the shape is the same.

## Why use a fake LLM instead of a real one?

Because the lesson is about the **loop**, not the model. A real LLM adds:

- An API key you have to configure
- Non-determinism (the lesson wouldn't produce the same output each run)
- Cost (a few cents per run)
- Latency (a few seconds per run)

A fake LLM that returns scripted decisions makes the loop **deterministic
and inspectable**. The printed output is the same every time, so the
reader can follow along without guessing.

Once you understand the loop with a fake LLM, swapping in a real one is
a mechanical change: replace `fake_llm` with a call to `openai.chat.completions.create`
that returns a tool-call decision in the same shape. The harness code
doesn't change.

## What this example deliberately skips

- **Termination guard.** If the fake LLM never says `final`, the loop
  runs forever. Real harnesses cap the turn count.
- **Tool errors.** If a tool throws, this example crashes. Real harnesses
  send the error back to the model as a message.
- **Approval.** Some tools (delete, pay, send) should require human
  confirmation. This one runs everything immediately.
- **Memory.** Every message is kept in a list. Long sessions would
  exhaust the context window; real harnesses summarize or truncate.

Each of those is a lesson's worth of work. The point here is to see the
loop clearly, without the extras.

---

## In another language?

The five-line loop translates directly:

| Language | The loop |
|---|---|
| Go | `for { d := model.Decide(msgs); if d.Final { return d.Text }; runTool(d); msgs = append(msgs, d) }` |
| Rust | `loop { match model.decide(&msgs)? { Decision::Final(t) => return Ok(t), Decision::Tool(tc) => run(tc) } }` |
| PHP | `while (true) { $d = askModel(); if ($d['final']) return $d['text']; runTool($d); }` |
| Ruby | `loop do; d = ask_model; return d[:text] if d[:final]; run_tool(d); end` |
| Java | `while (true) { var d = model.decide(msgs); if (d.isFinal()) return d.text(); run(d); }` |
| C# | `while (true) { var d = model.Decide(msgs); if (d.IsFinal) return d.Text; Run(d); }` |

Every harness in every language is this loop with more or fewer safety
checks. Once you can read the loop, you can read the harness.
```