# Reference

Comparison docs, not runnable lessons. Read these when you need to
answer "which one should I pick?" or "what does this word mean?" — not
when you want to code.

The lessons in `00`–`09` teach one concept each, with runnable code. The
files here are the **lookup layer** that sits behind those lessons.

## What's here

| File | Answers |
|---|---|
| [`database-types.md`](database-types.md) | Relational vs document vs key-value vs graph vs time-series vs vector — what each is actually for, with real companies using each |
| [`api-styles.md`](api-styles.md) | REST vs GraphQL vs gRPC vs SOAP — what each is, when to pick it, and what a real request looks like |
| [`fastapi-types-example.py`](fastapi-types-example.py) | Pydantic request/response models in FastAPI — the runnable counterpart to the API styles doc |

## How to use this section

**If you're choosing a database for a new project:**
Read `database-types.md` top to bottom. It gives you the decision heuristics
first, then the real-world examples, so you can see what the choice looks
like at scale.

**If you're choosing an API style:**
Read `api-styles.md`. It starts with REST (the default), then explains when
GraphQL, gRPC, or SOAP is actually the right answer — and when it isn't.

**If you're writing FastAPI code:**
Run `fastapi-types-example.py` and read the comments. It shows how Pydantic
models map to the API styles doc — the same concepts, in runnable form.

## Why these are reference and not lessons

A lesson teaches one thing you can do in 15 minutes. These files answer
questions that take longer to internalize:

- "Which database should I use?" has no 15-minute answer — it depends on
  access patterns, scale, consistency needs, and team familiarity.
- "REST vs GraphQL" is a design decision, not a syntax you can learn by
  running a file.

The reference docs give you the vocabulary. The lessons (`04-databases`,
`01-api-design`) give you the practice. Use both.

---

## In another language?

These docs are language-agnostic. The database types and API styles are
the same whether you write Python, Go, TypeScript, or Java. Where a file
shows code (the FastAPI example), it includes an "In another language?"
table like every other lesson.