# ─────────────────────────────────────────────────────────────
# Lesson: minimal agent harness
#
# An agent is a loop:
#   1. ask the model what to do
#   2. if the model wants a tool, run it and feed the result back
#   3. if the model is done, return the final answer
#
# The model never executes code. It only DECIDES. This file is
# the code that actually does the calling.
#
# We use a fake LLM so the lesson is deterministic and needs no
# API key. Swap `fake_llm` for a real model call to make this a
# real agent — the loop below doesn't change.
# ─────────────────────────────────────────────────────────────

from dataclasses import dataclass, field
from typing import Any, Callable


# ── 1. The decision type ────────────────────────────────────
# Every turn, the model returns one of these. A harness only ever
# reads `kind` and either `name`+`args` (tool) or `text` (final).
@dataclass
class Decision:
    kind: str                       # "tool" or "final"
    name: str | None = None         # tool name (if kind == "tool")
    args: dict[str, Any] = field(default_factory=dict)
    text: str | None = None         # final text (if kind == "final")


# ── 2. The tools ────────────────────────────────────────────
# A tool is just a function. The model asks for it by name; the
# harness looks it up here and calls it.
def add(a: float, b: float) -> float:
    return a + b


def multiply(a: float, b: float) -> float:
    return a * b


TOOLS: dict[str, Callable[..., Any]] = {
    "add": add,
    "multiply": multiply,
}


# ── 3. The "model" (fake) ───────────────────────────────────
# In a real agent, this would be:
#     response = openai.chat.completions.create(...)
#     return parse_tool_call(response)
# Here it's a scripted list of decisions, so the lesson runs the
# same way every time.
_SCRIPT = [
    Decision(kind="tool", name="add", args={"a": 2, "b": 3}),
    Decision(kind="tool", name="multiply", args={"a": 5, "b": 10}),
    Decision(kind="final", text="The answer is 50."),
]
_step = {"i": 0}


def fake_llm(messages: list[dict]) -> Decision:
    i = _step["i"]
    if i >= len(_SCRIPT):
        return Decision(kind="final", text="(script exhausted)")
    _step["i"] += 1
    return _SCRIPT[i]


# ── 4. The harness ──────────────────────────────────────────
# This is the whole lesson. Everything else is setup.
def run_harness(prompt: str, max_turns: int = 10) -> str:
    messages: list[dict] = [{"role": "user", "content": prompt}]

    for turn in range(1, max_turns + 1):
        print(f"--- turn {turn} ---")

        # 1. Ask the model what to do.
        decision = fake_llm(messages)

        # 2. If it's done, return the final answer.
        if decision.kind == "final":
            print(f"model wants: final answer: {decision.text!r}")
            return decision.text or ""

        # 3. Otherwise it's a tool call. Run the tool.
        print(f"model wants: tool {decision.name!r} with {decision.args}")
        if decision.name not in TOOLS:
            raise ValueError(f"unknown tool: {decision.name}")

        result = TOOLS[decision.name](**decision.args)
        print(f"tool result: {result}")

        # 4. Feed the result back to the model for the next turn.
        messages.append({
            "role": "tool",
            "name": decision.name,
            "content": str(result),
        })

    # Termination guard — real harnesses need this.
    return f"(stopped after {max_turns} turns without a final answer)"


# ── 5. Demo ─────────────────────────────────────────────────
if __name__ == "__main__":
    answer = run_harness("Add 2 and 3, then multiply the result by 10.")
    print("--- final ---")
    print(answer)


# ─────────────────────────────────────────────────────────────
# Exercise:
#   1. Add a "subtract" tool to TOOLS and to the script, and watch
#      the harness call it without any change to run_harness.
#   2. Remove the "final" decision from _SCRIPT and run again.
#      The loop hits max_turns and returns the guard message.
#      This is why real harnesses cap turns.
#   3. Make `add` raise an exception (e.g. `raise ValueError`).
#      Run again. The harness crashes — it doesn't send the error
#      back to the model. Real harnesses catch the exception and
#      append it as a tool message so the model can retry.
# ─────────────────────────────────────────────────────────────