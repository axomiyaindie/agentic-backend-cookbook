# Roadmap

22 sections. You don't have to read them in order. Pick the track that
matches what you're doing right now, then come back for the rest.

- **New to backend?** → [Track 1: Start from zero](#track-1-start-from-zero)
- **Reviewing AI-generated code?** → [Track 2: Audit AI code](#track-2-audit-ai-code)
- **Building an AI app?** → [Track 3: Build an AI app](#track-3-build-an-ai-app)
- **Making it production-ready?** → [Track 4: Harden and ship](#track-4-harden-and-ship)
- **Just curious about a topic?** → [Jump to the section](#all-sections-at-a-glance)

Every section is a folder with a README, a runnable example, and an
exercise. Terms in **bold** are defined in [`05-glossary/`](../05-glossary/).

---

## Track 1: Start from zero

You've never built a backend, or you've only written frontend. Read these
in order. About 3 hours total.

| Order | Section | What you'll learn |
|---|---|---|
| 1 | [`01-api-design/`](../01-api-design/) | How a request becomes a typed function; CRUD and HTTP verbs |
| 2 | [`03-rbac-admin/`](../03-rbac-admin/) | How a server decides who is allowed to do what |
| 3 | [`04-databases/`](../04-databases/) | The same CRUD in Postgres, MySQL, MongoDB, DynamoDB — read the comparison first |
| 4 | [`05-glossary/`](../05-glossary/) | Look up any term you hit along the way |
| 5 | [`06-caching/`](../06-caching/) | How to make an expensive endpoint fast |
| 6 | [`07-rate-limiting/`](../07-rate-limiting/) | How to stop one client from using up all capacity |
| 7 | [`15-transactions/`](../15-transactions/) | All-or-nothing writes — the single most common AI bug |

After this track, you can read most FastAPI code and explain what it does.

---

## Track 2: Audit AI code

An AI assistant just generated 200 lines of backend code. You need to
decide whether to ship it. Read these 3 first. About 45 minutes.

| Order | Section | What you'll check |
|---|---|---|
| 1 | [`10-reference/ai-code-pitfalls.md`](../10-reference/ai-code-pitfalls.md) | Nine patterns to look for — the checklist |
| 2 | [`15-transactions/`](../15-transactions/) | "Two writes in a row" without a transaction → money vanishes |
| 3 | [`16-idempotency/`](../16-idempotency/) | Retried requests → charged twice |

Then read whichever of these matches what the AI wrote:

| If the AI generated… | Read |
|---|---|
| An endpoint that takes input | [`01-api-design/`](../01-api-design/) and [`10-reference/fastapi-types-example.py`](../10-reference/fastapi-types-example.py) |
| Anything with auth | [`03-rbac-admin/`](../03-rbac-admin/) |
| A tool call | [`02-mcp-connectors/`](../02-mcp-connectors/) and [`09-agent-harness/`](../09-agent-harness/) |
| A database write | [`04-databases/`](../04-databases/) |
| A cache | [`06-caching/`](../06-caching/) |
| A rate limit | [`07-rate-limiting/`](../07-rate-limiting/) |
| A webhook receiver | [`18-webhooks/`](../18-webhooks/) |
| File upload handling | [`14-file-uploads/`](../14-file-uploads/) |
| A search feature | [`19-search/`](../19-search/) |
| Anything async or real-time | [`12-streaming/`](../12-streaming/) or [`17-websockets/`](../17-websockets/) |
| An API doc | [`08-documentation/`](../08-documentation/) |
| No tests | [`21-testing/`](../21-testing/) |

---

## Track 3: Build an AI app

You're building an AI app and want to understand the backend layers.
About 4 hours.

| Order | Section | What you'll learn |
|---|---|---|
| 1 | [`01-api-design/`](../01-api-design/) | The HTTP layer |
| 2 | [`03-rbac-admin/`](../03-rbac-admin/) | Who's allowed to do what |
| 3 | [`10-reference/api-styles.md`](../10-reference/api-styles.md) | REST vs GraphQL vs gRPC vs SOAP |
| 4 | [`12-streaming/`](../12-streaming/) | Streaming tokens to the browser (SSE) |
| 5 | [`02-mcp-connectors/`](../02-mcp-connectors/) | Exposing tools to the model |
| 6 | [`09-agent-harness/`](../09-agent-harness/) | The loop that calls those tools |
| 7 | [`19-search/`](../19-search/) | The "retrieve" half of RAG |
| 8 | [`06-caching/`](../06-caching/) | Cache expensive model calls |
| 9 | [`11-background-jobs/`](../11-background-jobs/) | Long-running work outside the request |
| 10 | [`13-observability/`](../13-observability/) | Correlation IDs across the whole stack |

That's the full stack behind a typical AI chat app.

---

## Track 4: Harden and ship

The app works locally. Now make it survive production. About 2 hours.

| Order | Section | What you'll learn |
|---|---|---|
| 1 | [`15-transactions/`](../15-transactions/) | Atomic writes |
| 2 | [`16-idempotency/`](../16-idempotency/) | Safe retries |
| 3 | [`07-rate-limiting/`](../07-rate-limiting/) | Abuse defense |
| 4 | [`13-observability/`](../13-observability/) | Debugging across layers |
| 5 | [`18-webhooks/`](../18-webhooks/) | Verifying inbound requests |
| 6 | [`21-testing/`](../21-testing/) | Proving it still works after edits |
| 7 | [`20-deploy/`](../20-deploy/) | Dockerfile, compose, environment |

After this track, the repo reads as a checklist of "things I've handled."

---

## All sections at a glance

| # | Section | One-line summary | Runnable? |
|---|---|---|---|
| 00 | [`00-roadmap/`](../00-roadmap/) | You are here | — |
| 01 | [`01-api-design/`](../01-api-design/) | Typed requests, CRUD, HTTP verbs | ✅ |
| 02 | [`02-mcp-connectors/`](../02-mcp-connectors/) | MCP tool servers | ✅ |
| 03 | [`03-rbac-admin/`](../03-rbac-admin/) | Role-based access control | ✅ |
| 04 | [`04-databases/`](../04-databases/) | Postgres, MySQL, MongoDB, DynamoDB | needs DB |
| 05 | [`05-glossary/`](../05-glossary/) | Every term, defined | — |
| 06 | [`06-caching/`](../06-caching/) | Cache-aside with TTL | ✅ |
| 07 | [`07-rate-limiting/`](../07-rate-limiting/) | Fixed-window, 429, Retry-After | ✅ |
| 08 | [`08-documentation/`](../08-documentation/) | API spec template + worked example | — |
| 09 | [`09-agent-harness/`](../09-agent-harness/) | The agent loop | ✅ |
| 10 | [`10-reference/`](../10-reference/) | Database types, API styles, AI code pitfalls | 1 file |
| 11 | [`11-background-jobs/`](../11-background-jobs/) | Queue, worker, retry, dead-letter | ✅ |
| 12 | [`12-streaming/`](../12-streaming/) | SSE — stream tokens to the browser | ✅ |
| 13 | [`13-observability/`](../13-observability/) | Correlation IDs across layers | ✅ |
| 14 | [`14-file-uploads/`](../14-file-uploads/) | Buffered vs streamed, 500 MB safe | ✅ |
| 15 | [`15-transactions/`](../15-transactions/) | BEGIN/COMMIT/ROLLBACK, money vanishes | ✅ |
| 16 | [`16-idempotency/`](../16-idempotency/) | Idempotency-Key, same request twice | ✅ |
| 17 | [`17-websockets/`](../17-websockets/) | Bidirectional, ticks + echo | ✅ |
| 18 | [`18-webhooks/`](../18-webhooks/) | HMAC verification, raw body | ✅ |
| 19 | [`19-search/`](../19-search/) | FTS + vector + RRF hybrid | ✅ |
| 20 | [`20-deploy/`](../20-deploy/) | Dockerfile, compose, .dockerignore | — |
| 21 | [`21-testing/`](../21-testing/) | pytest, TestClient, fixtures | ✅ |

---

## "Vibe coding" safety net

If you're building with an AI assistant and it produces backend code you
don't understand, check it against this table. If the answer is "no" to
any of these, that's what to fix first.

| Does the code… | Read |
|---|---|
| Define types for its request and response? | [`01-api-design/01-http-typescript/`](../01-api-design/01-http-typescript/) |
| Validate input at runtime (not just compile time)? | [`10-reference/fastapi-types-example.py`](../10-reference/fastapi-types-example.py) |
| Check *who* is allowed to do *what*, with 401 vs 403 correct? | [`03-rbac-admin/`](../03-rbac-admin/) and [`08-documentation/example-spec.md`](../08-documentation/example-spec.md) |
| Use parameterised queries (not string concatenation)? | [`04-databases/02-postgres-crud/`](../04-databases/02-postgres-crud/) |
| Wrap multi-step writes in a transaction? | [`15-transactions/`](../15-transactions/) |
| Handle retries without double-charging? | [`16-idempotency/`](../16-idempotency/) |
| Stream uploads instead of buffering them in memory? | [`14-file-uploads/`](../14-file-uploads/) |
| Verify webhook signatures before trusting the body? | [`18-webhooks/`](../18-webhooks/) |
| Log a correlation ID on every line? | [`13-observability/`](../13-observability/) |
| Return 429 and `Retry-After` on rate-limit violations? | [`07-rate-limiting/`](../07-rate-limiting/) |
| Cache expensive results with a TTL? | [`06-caching/`](../06-caching/) |
| Run a test that proves the behavior? | [`21-testing/`](../21-testing/) |
| Expose tools over a standard protocol? | [`02-mcp-connectors/`](../02-mcp-connectors/) |
| Have a loop that terminates when the model says "done"? | [`09-agent-harness/`](../09-agent-harness/) |

If the AI wrote something not covered by any of these — a new endpoint, a
new service, a new protocol — the section that matches it will show you
what "correct" looks like. If nothing matches, that's a sign it's time to
read [`10-reference/ai-code-pitfalls.md`](../10-reference/ai-code-pitfalls.md)
and ask whether the AI is doing something the repo doesn't cover.

---

## How to read any lesson

Every section follows the same shape (see [`CONTRIBUTING.md`](../CONTRIBUTING.md)):

1. **Read the section's `README.md` first.** It explains what the concept
   is, why it matters, and what the lesson demonstrates.
2. **Read the runnable file's comments.** They're numbered — 1, 2, 3 — so
   you read the mechanism in order.
3. **Run it.** The `## How to run` section has copy-pasteable commands.
4. **Do the exercise at the bottom of the file.** It asks you to change
   one thing and observe the result. That's where the learning happens.

If a section doesn't make sense after step 4, open an issue. The lesson
isn't finished until you can finish it.

---

## What's missing

The repo deliberately does not cover:

- **Real authentication** — only authorization (RBAC). No passwords, no
  JWT signing, no OAuth.
- **Password hashing** — the RBAC lesson compares plaintext for clarity.
- **Migrations** — schemas are created inline.
- **Distributed systems** — single server only. No Kafka, no multi-region.
- **Cloud deployment walkthroughs** — the Dockerfile template is the
  boundary.

If a term or concept is missing from [`05-glossary/`](../05-glossary/),
or a lesson you want doesn't exist, open an issue. `CONTRIBUTING.md` has
the format a new lesson needs to follow.