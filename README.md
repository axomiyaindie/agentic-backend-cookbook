<div align="center">

<img src="assets/logo.svg" alt="Agentic Backend Cookbook" width="100%" />

<br />

**Small, runnable lessons for the backend behind AI applications.**
One concept. One runnable file. One exercise. Fifteen minutes.

<br />

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Check Python](https://github.com/axomiyaindie/agentic-backend-cookbook/actions/workflows/check-python.yml/badge.svg)](https://github.com/axomiyaindie/agentic-backend-cookbook/actions/workflows/check-python.yml)
[![Check TypeScript](https://github.com/axomiyaindie/agentic-backend-cookbook/actions/workflows/check-typescript.yml/badge.svg)](https://github.com/axomiyaindie/agentic-backend-cookbook/actions/workflows/check-typescript.yml)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

[Start here](00-roadmap/README.md) &nbsp;|&nbsp; [Lessons](#the-lessons) &nbsp;|&nbsp; [Verify it yourself](#verify-it-yourself) &nbsp;|&nbsp; [Contribute](#contribute) &nbsp;|&nbsp; [Glossary](05-glossary/README.md)

</div>

---

## In 30 seconds

AI assistants can now generate 200 lines of backend code in a few seconds. Understanding those 200 lines still takes you hours.

This repo closes that gap. Every lesson is a tiny, **executable** example of one backend concept, so you can see what "good" looks like before you ship something you did not write.

```text
read the README  ->  run the example  ->  break it on purpose  ->  understand what broke
```

---

## What you will learn

| Question | Lesson |
|---|---|
| How does an HTTP request become a typed function call? | [`01-api-design`](01-api-design/) |
| How do CRUD operations map to verbs and status codes? | [`01-api-design`](01-api-design/) |
| How do MCP tool servers let AI clients discover and call tools? | [`02-mcp-connectors`](02-mcp-connectors/) |
| How does a server decide who is allowed to do what? | [`03-rbac-admin`](03-rbac-admin/) |
| Which database should I pick, and why? | [`04-databases`](04-databases/) |
| What does that word actually mean? | [`05-glossary`](05-glossary/) |
| How do I make an expensive endpoint fast? | [`06-caching`](06-caching/) |
| How do I stop one client from using up all my capacity? | [`07-rate-limiting`](07-rate-limiting/) |
| How do I write the API doc the frontend (or an AI) will actually use? | [`08-documentation`](08-documentation/) |
| How does an AI agent actually call tools in a loop? | [`09-agent-harness`](09-agent-harness/) |
| Which database type fits my data? | [`10-reference/database-types.md`](10-reference/database-types.md) |
| REST, GraphQL, gRPC, or SOAP — which one? | [`10-reference/api-styles.md`](10-reference/api-styles.md) |
| How do I actually write typed models in FastAPI? | [`10-reference/fastapi-types-example.py`](10-reference/fastapi-types-example.py) |
| What does AI-generated backend code get wrong? | [`10-reference/ai-code-pitfalls.md`](10-reference/ai-code-pitfalls.md) |
| How do I move slow work out of the request cycle? | [`11-background-jobs`](11-background-jobs/) |
| How do I stream tokens to the browser as they're produced? | [`12-streaming`](12-streaming/) |
| How do I debug "what happened" across five layers? | [`13-observability`](13-observability/) |
| How do I accept a 500 MB upload without crashing? | [`14-file-uploads`](14-file-uploads/) |
| How do I stop money from vanishing when step 2 fails? | [`15-transactions`](15-transactions/) |
| How do I stop a retried request from charging twice? | [`16-idempotency`](16-idempotency/) |
| How do I push messages from the server to the client in both directions? | [`17-websockets`](17-websockets/) |
| How do I receive untrusted HTTP from a third party safely? | [`18-webhooks`](18-webhooks/) |
| Full-text or vector or hybrid — which search? | [`19-search`](19-search/) |
| How do I get this off my laptop? | [`20-deploy`](20-deploy/) |
| How do I know the code still works after I change it? | [`21-testing`](21-testing/) |

By the end you will be able to read AI-generated backend code and tell, with confidence, whether it is sound or quietly broken.

---

## Why this exists

The backend behind AI applications is the most requested and least explained layer in modern software. Most resources fall into two buckets:

- **Tutorials** walk you step by step, but you only ever build *their* app.
- **Documentation** is accurate, but assumes you already know what to search for.

Neither helps at the moment that matters: an AI hands you a pile of backend code and asks you to trust it.

This repo is the missing middle. It exists to **make backend concepts legible by making them executable.**

> Success condition: a reader can read a lesson, run it, break it, and understand what they broke.
> If a lesson cannot be finished in 15 minutes, it is too big for this repo.

---

## What to expect

**You can count on:**

- **Every lesson is explained.** Each has a README covering what it does and why.
- **Every code lesson runs.** No "trust me, this works."
- **Every code lesson has an exercise** so you do more than read.
- **Every code lesson maps to other languages** (Go, Rust, PHP, Ruby, Java, C#).
- **CI checks that the code compiles** on every push.
- **Thirteen runnable lessons have executed output** shown in their READMEs.
- **Reference docs** answer the "which one should I pick?" questions that don't fit in a 15-minute lesson.

**Do not expect:**

- **Production code.** No hardening, no migrations, no test suites beyond `21-testing/`.
- **Authentication.** Only authorization (RBAC). No passwords, no OAuth.
- **A full app.** No frontend, no deployment beyond a Dockerfile template.
- **Coverage of everything.** This is backend basics, not the whole backend.
- **Performance or scale.** Examples are correct, not tuned.
- **Multi-server behavior.** Caching, rate limiting, background jobs, and WebSockets keep state in process memory. Real systems use Redis or a pub/sub layer.
- **Real model calls.** The agent-harness lesson uses a fake LLM so it runs without an API key.
- **Real embeddings.** The search lesson uses a deterministic hash so it runs without a model. The README shows how to swap in one.
- **CI for databases.** Those lessons need live databases and are marked as not CI-tested.
- **Runnable GraphQL/gRPC/SOAP.** The API styles reference explains them; only REST is taught as a runnable lesson.

If you want a production template, this is the wrong repo. If you want to **understand** what a production template does, you are in the right place.

---

## Who this is for

| This repo is for you if | This repo is not for you if |
|---|---|
| You vibe-code with AI and want to understand the output | You want a copy-paste SaaS starter |
| You are learning backend and want small wins | You need a production deployment guide |
| You teach a class, bootcamp, or study group | You want framework comparisons |
| You review AI-generated PRs and need a mental baseline | You are looking for frontend tutorials |

---

## Learning path

```mermaid
flowchart LR
    A[00 Roadmap] --> B[01 API design]
    B --> C[02 MCP connectors]
    C --> D[03 RBAC admin]
    D --> E[04 Databases]
    E --> F[06 Caching]
    F --> G[07 Rate limiting]
    G --> H[08 Documentation]
    H --> J[09 Agent harness]
    J --> K[10 Reference]
    K --> L[11 Background jobs]
    L --> M[12 Streaming]
    M --> N[13 Observability]
    N --> O[14 File uploads]
    O --> P[15 Transactions]
    P --> Q[16 Idempotency]
    Q --> R[17 WebSockets]
    R --> S[18 Webhooks]
    S --> T[19 Search]
    T --> U[20 Deploy]
    U --> V[21 Testing]
    E --> I[05 Glossary]
    I -. look up any term .-> B
```

Start at **[`00-roadmap/README.md`](00-roadmap/README.md)**. It tells you which lesson to read first and why, and doubles as a safety net: if an AI generates backend code you do not understand, the roadmap points you to the lesson that explains it.

---

## The lessons

Click any folder or file to open it on GitHub.

### [`00-roadmap/`](00-roadmap/) - Start here

Suggested reading order, plus a "vibe coding" safety net.

| File | What it is |
|---|---|
| [`00-roadmap/README.md`](00-roadmap/README.md) | Reading order and safety net |

### [`01-api-design/`](01-api-design/) - HTTP, typed requests, CRUD

How a request becomes a typed function, and how Create / Read / Update / Delete map to HTTP verbs. No server needed. Both examples run with `npx tsx`.

| File | What it is |
|---|---|
| [`01-api-design/README.md`](01-api-design/README.md) | Section overview and language policy |
| [`01-api-design/01-http-typescript/README.md`](01-api-design/01-http-typescript/README.md) | Describing a request and response as a type |
| [`01-api-design/01-http-typescript/example.ts`](01-api-design/01-http-typescript/example.ts) | Typed request/response with no server, just functions |
| [`01-api-design/02-crud-model/README.md`](01-api-design/02-crud-model/README.md) | How CRUD maps to HTTP verbs and status codes |
| [`01-api-design/02-crud-model/example.ts`](01-api-design/02-crud-model/example.ts) | In-memory CRUD: create, read, update, delete |

### [`02-mcp-connectors/`](02-mcp-connectors/) - MCP tool servers

**MCP** (Model Context Protocol) is how AI clients discover and call tools. The example is a single-file server exposing one tool: the whole protocol surface in 65 lines.

| File | What it is |
|---|---|
| [`02-mcp-connectors/README.md`](02-mcp-connectors/README.md) | What MCP is, and where real servers live |
| [`02-mcp-connectors/01-minimal-mcp-server/README.md`](02-mcp-connectors/01-minimal-mcp-server/README.md) | Walkthrough of the smallest possible MCP server |
| [`02-mcp-connectors/01-minimal-mcp-server/server.ts`](02-mcp-connectors/01-minimal-mcp-server/server.ts) | `tools/list` and `tools/call`: the whole protocol |
| [`02-mcp-connectors/01-minimal-mcp-server/package.json`](02-mcp-connectors/01-minimal-mcp-server/package.json) | `tsx` and `typescript` |

**Verified output:**

```text
tools/list -> [ { name: "add_numbers", inputSchema: {...}, ... } ]
tools/call add_numbers({a:2,b:3}) -> { sum: 5 }
```

### [`03-rbac-admin/`](03-rbac-admin/) - Role-based access control

How the server knows *this* user is allowed to do *that*. Demonstrates 200 (allowed), 403 (denied), and 401 (not logged in).

| File | What it is |
|---|---|
| [`03-rbac-admin/README.md`](03-rbac-admin/README.md) | What RBAC is, plus an "admin panel" note |
| [`03-rbac-admin/01-fastapi-rbac/README.md`](03-rbac-admin/01-fastapi-rbac/README.md) | Step-by-step walkthrough with expected results |
| [`03-rbac-admin/01-fastapi-rbac/main.py`](03-rbac-admin/01-fastapi-rbac/main.py) | `login` -> `get_current_role` -> `require_role("admin")` |
| [`03-rbac-admin/01-fastapi-rbac/requirements.txt`](03-rbac-admin/01-fastapi-rbac/requirements.txt) | `fastapi` and `uvicorn` |

**Verified output (executed):**

```text
admin -> GET /admin/users  -> 200 OK
user  -> GET /admin/users  -> 403 {"detail":"insufficient role"}   <- the point
none  -> GET /me           -> 401 {"detail":"missing token"}
```

### [`04-databases/`](04-databases/) - Four engines, one CRUD

The same four operations in Postgres, MySQL, MongoDB, and DynamoDB. Read them side by side to see what changes and what does not.

| File | What it is |
|---|---|
| [`04-databases/README.md`](04-databases/README.md) | Why four engines, not one |
| [`04-databases/01-database-comparison.md`](04-databases/01-database-comparison.md) | Decision table, and what an AI assistant is likely to pick |
| [`04-databases/02-postgres-crud/README.md`](04-databases/02-postgres-crud/README.md) | Postgres setup and parameterised queries |
| [`04-databases/02-postgres-crud/schema.sql`](04-databases/02-postgres-crud/schema.sql) | The `users` table with constraints |
| [`04-databases/02-postgres-crud/crud.py`](04-databases/02-postgres-crud/crud.py) | Postgres CRUD with `RETURNING` |
| [`04-databases/03-mysql-crud/README.md`](04-databases/03-mysql-crud/README.md) | MySQL setup and the `lastrowid` difference |
| [`04-databases/03-mysql-crud/crud.py`](04-databases/03-mysql-crud/crud.py) | MySQL CRUD with `lastrowid` |
| [`04-databases/04-mongodb-crud/README.md`](04-databases/04-mongodb-crud/README.md) | MongoDB setup and the no-schema trade-off |
| [`04-databases/04-mongodb-crud/crud.py`](04-databases/04-mongodb-crud/crud.py) | MongoDB CRUD with `ObjectId` and `$set` |
| [`04-databases/05-dynamodb-crud/README.md`](04-databases/05-dynamodb-crud/README.md) | DynamoDB setup and access-pattern-first design |
| [`04-databases/05-dynamodb-crud/crud.py`](04-databases/05-dynamodb-crud/crud.py) | DynamoDB CRUD with `UpdateExpression` |

**Requires a live database.** Not run in CI. The comparison doc tells you which to pick.

### [`05-glossary/`](05-glossary/) - Every term, defined

Plain-English definitions of every term used in this repo: API, CRUD, RBAC, JWT, MCP, partition key, SQL injection, parameterised query, and more. If a lesson uses a word you do not know, it is here.

| File | What it is |
|---|---|
| [`05-glossary/README.md`](05-glossary/README.md) | A to Z of terms in the cookbook |

### [`06-caching/`](06-caching/) - Make expensive endpoints fast

The cache-aside pattern with TTL, demonstrated with a 2-second fake "expensive operation" that becomes instant on the second call.

| File | What it is |
|---|---|
| [`06-caching/README.md`](06-caching/README.md) | What caching is, the cache-aside flow, and the three hard problems |
| [`06-caching/01-fastapi-cache/README.md`](06-caching/01-fastapi-cache/README.md) | Step-by-step walkthrough with expected elapsed times |
| [`06-caching/01-fastapi-cache/main.py`](06-caching/01-fastapi-cache/main.py) | Hand-written cache with TTL: see the mechanism, not a decorator |
| [`06-caching/01-fastapi-cache/requirements.txt`](06-caching/01-fastapi-cache/requirements.txt) | `fastapi` and `uvicorn` |

**Production note:** the cache lives in process memory. Run two workers and each gets its own cache. Real systems use a shared store such as Redis.

### [`07-rate-limiting/`](07-rate-limiting/) - Survive traffic spikes

The fixed-window algorithm, hand-written so you can see the counter increment. Demonstrates HTTP 429, `Retry-After`, and the `X-RateLimit-*` headers.

| File | What it is |
|---|---|
| [`07-rate-limiting/README.md`](07-rate-limiting/README.md) | Why rate limit, the three algorithms, and why 401 vs 403 matters |
| [`07-rate-limiting/01-fastapi-rate-limit/README.md`](07-rate-limiting/01-fastapi-rate-limit/README.md) | Walkthrough: 5 requests pass, the 6th returns 429 |
| [`07-rate-limiting/01-fastapi-rate-limit/main.py`](07-rate-limiting/01-fastapi-rate-limit/main.py) | Hand-written limiter with `X-RateLimit-*` headers |
| [`07-rate-limiting/01-fastapi-rate-limit/requirements.txt`](07-rate-limiting/01-fastapi-rate-limit/requirements.txt) | `fastapi` and `uvicorn` |

**Production note:** counters live in process memory. Real systems keep them in Redis.

### [`08-documentation/`](08-documentation/) - The contract

A fill-in-the-blanks API spec template, plus a fully worked example that documents the RBAC lesson. Shows 401 vs 403, error shapes, and the summary table readers actually use. This lesson is a writing exercise; no code to run.

| File | What it is |
|---|---|
| [`08-documentation/README.md`](08-documentation/README.md) | Why API docs matter (for humans and AI) |
| [`08-documentation/api-spec-template.md`](08-documentation/api-spec-template.md) | Copy-paste template for documenting one endpoint |
| [`08-documentation/example-spec.md`](08-documentation/example-spec.md) | The RBAC lesson, fully documented |

### [`09-agent-harness/`](09-agent-harness/) - The agent loop

The runtime that sits between the model and your tools. The model never executes code — it only decides what to call. The harness is the loop that actually does the calling.

| File | What it is |
|---|---|
| [`09-agent-harness/README.md`](09-agent-harness/README.md) | What a harness is, and how it differs from MCP |
| [`09-agent-harness/01-minimal-harness/README.md`](09-agent-harness/01-minimal-harness/README.md) | Walkthrough of a 3-turn agent loop |
| [`09-agent-harness/01-minimal-harness/main.py`](09-agent-harness/01-minimal-harness/main.py) | Hand-written harness with a fake LLM, no API key |

**Verified output (executed):**

```text
--- turn 1 --- model wants: tool 'add' with {'a': 2, 'b': 3}
             tool result: 5
--- turn 2 --- model wants: tool 'multiply' with {'a': 5, 'b': 10}
             tool result: 50
--- turn 3 --- model wants: final answer: 'The answer is 50.'
--- final --- The answer is 50.
```

**No `requirements.txt`** — this lesson uses only the Python standard library.

### [`10-reference/`](10-reference/) - Lookup docs

Comparison docs, not runnable lessons. Read these when you need to answer "which one should I pick?" or "what does AI-generated code get wrong?".

| File | What it is |
|---|---|
| [`10-reference/README.md`](10-reference/README.md) | How to use the reference section |
| [`10-reference/database-types.md`](10-reference/database-types.md) | Six database families with real companies and pricing |
| [`10-reference/api-styles.md`](10-reference/api-styles.md) | REST, GraphQL, gRPC, SOAP — when to pick each |
| [`10-reference/fastapi-types-example.py`](10-reference/fastapi-types-example.py) | Runnable Pydantic models: create, response, nested, pagination, patch |
| [`10-reference/ai-code-pitfalls.md`](10-reference/ai-code-pitfalls.md) | Nine patterns AI-generated backend code gets wrong, with the fix for each |

**One file is runnable** (`fastapi-types-example.py`); the rest are read-only reference.

### [`11-background-jobs/`](11-background-jobs/) - Move slow work out of the request

The producer / queue / worker pattern in a single file, using SQLite. Shows retry, dead-letter, and why every job must be idempotent.

| File | What it is |
|---|---|
| [`11-background-jobs/README.md`](11-background-jobs/README.md) | Why jobs exist, the three parts, and the reliability contract |
| [`11-background-jobs/01-minimal-queue/README.md`](11-background-jobs/01-minimal-queue/README.md) | Walkthrough of the states a job moves through |
| [`11-background-jobs/01-minimal-queue/main.py`](11-background-jobs/01-minimal-queue/main.py) | Producer + worker + retry + dead-letter, stdlib only |

**Verified output (executed):**

```text
job 1 (succeed_after_0): status=succeeded, attempts=0
job 2 (succeed_after_1): status=succeeded, attempts=1   <- retried and recovered
job 3 (always_fail):     status=dead,      attempts=3   <- dead-lettered
```

**No `requirements.txt`** — standard library only (SQLite is built in).

### [`12-streaming/`](12-streaming/) - Stream tokens as they are produced

SSE (Server-Sent Events) sends each chunk the moment it is ready. The demo streams 5 words over 5 seconds, and a 30-line HTML page displays them live.

| File | What it is |
|---|---|
| [`12-streaming/README.md`](12-streaming/README.md) | SSE vs WebSocket, and why AI chat uses SSE |
| [`12-streaming/01-fastapi-sse/README.md`](12-streaming/01-fastapi-sse/README.md) | Walkthrough with expected curl output |
| [`12-streaming/01-fastapi-sse/main.py`](12-streaming/01-fastapi-sse/main.py) | `StreamingResponse` + an async generator |
| [`12-streaming/01-fastapi-sse/client.html`](12-streaming/01-fastapi-sse/client.html) | Browser client using `EventSource` |
| [`12-streaming/01-fastapi-sse/requirements.txt`](12-streaming/01-fastapi-sse/requirements.txt) | `fastapi` and `uvicorn` |

**Verified output (executed):** the browser displays `Hello from a streaming server!` one word per second, then `Stream ended or connection lost` (the client's `onerror` for a normal close).

### [`13-observability/`](13-observability/) - One ID across every layer

A middleware generates a correlation ID, logs it with every line, and passes it into a background job so the worker logs the same ID after the HTTP request ends.

| File | What it is |
|---|---|
| [`13-observability/README.md`](13-observability/README.md) | Logs vs metrics vs traces, and why correlation IDs matter |
| [`13-observability/01-fastapi-request-id/README.md`](13-observability/01-fastapi-request-id/README.md) | Walkthrough of the four tests |
| [`13-observability/01-fastapi-request-id/main.py`](13-observability/01-fastapi-request-id/main.py) | Middleware + `ContextVar` + threaded background job |
| [`13-observability/01-fastapi-request-id/requirements.txt`](13-observability/01-fastapi-request-id/requirements.txt) | `fastapi` and `uvicorn` |

**Verified output (executed):**

```text
{"event":"request_start","request_id":"job-trace-456",...}
{"event":"job_enqueued","request_id":"job-trace-456",...}
{"event":"request_end","request_id":"job-trace-456",...}
{"event":"job_running","request_id":"job-trace-456",...}       <- from the thread
{"event":"job_succeeded","request_id":"job-trace-456",...}     <- from the thread
```

### [`14-file-uploads/`](14-file-uploads/) - Don't buffer the whole file

Two endpoints: one reads the whole upload into memory (the anti-pattern), one streams in 1 MB chunks. Same result, 500× less memory.

| File | What it is |
|---|---|
| [`14-file-uploads/README.md`](14-file-uploads/README.md) | Why buffering kills servers, and the three patterns |
| [`14-file-uploads/01-fastapi-upload/README.md`](14-file-uploads/01-fastapi-upload/README.md) | Walkthrough: upload the same file both ways, watch memory |
| [`14-file-uploads/01-fastapi-upload/main.py`](14-file-uploads/01-fastapi-upload/main.py) | `/upload/buffered` vs `/upload/streamed`, side by side |
| [`14-file-uploads/01-fastapi-upload/requirements.txt`](14-file-uploads/01-fastapi-upload/requirements.txt) | `fastapi`, `uvicorn`, `python-multipart` |

**Verified output (executed):**

```text
{"status":"saved","bytes":5242880,"filename":"test-5mb.bin","method":"buffered"}
{"status":"saved","bytes":5242880,"filename":"test-5mb.bin","method":"streamed"}
```

Both succeed; the difference only shows up in memory.

### [`15-transactions/`](15-transactions/) - All or nothing

Two endpoints: one writes without a transaction (money vanishes), one wraps both writes in `BEGIN … COMMIT` (money stays safe). The `?fail=1` flag forces the second write to fail.

| File | What it is |
|---|---|
| [`15-transactions/README.md`](15-transactions/README.md) | What ACID actually means, and why atomicity is the one AI forgets |
| [`15-transactions/01-fastapi-transaction/README.md`](15-transactions/01-fastapi-transaction/README.md) | Walkthrough: trigger the failure on both endpoints, watch the balances |
| [`15-transactions/01-fastapi-transaction/main.py`](15-transactions/01-fastapi-transaction/main.py) | `/transfer/broken` vs `/transfer/safe`, side by side |
| [`15-transactions/01-fastapi-transaction/requirements.txt`](15-transactions/01-fastapi-transaction/requirements.txt) | `fastapi` and `uvicorn` |

**Verified output (executed):**

```text
Baseline:         {"alice":100,"bob":50}
Broken + failure: {"alice": 70,"bob":50}   <- $30 vanished
Safe   + failure: {"alice":100,"bob":50}   <- nothing changed
```

**This is the single most common AI-generated backend bug.**

### [`16-idempotency/`](16-idempotency/) - Retries without double-charging

Transactions make a single operation atomic. Idempotency makes a *retried* operation safe. The `Idempotency-Key` header tells the server "this is the same request as before" — the server returns the stored response instead of running the handler again.

| File | What it is |
|---|---|
| [`16-idempotency/README.md`](16-idempotency/README.md) | The problem, the mechanism, and why AI apps are retry-heavy |
| [`16-idempotency/01-fastapi-idempotency/README.md`](16-idempotency/01-fastapi-idempotency/README.md) | Walkthrough: same key twice, one charge |
| [`16-idempotency/01-fastapi-idempotency/main.py`](16-idempotency/01-fastapi-idempotency/main.py) | `seen_keys` table + header check + stored response |
| [`16-idempotency/01-fastapi-idempotency/requirements.txt`](16-idempotency/01-fastapi-idempotency/requirements.txt) | `fastapi` and `uvicorn` |

**Verified output (executed):**

```text
First charge  (key demo-key-1): charge_id=1
Retry         (key demo-key-1): charge_id=1  <- same, no new charge
GET /charges:                   [{id:1, user:"alice", amount:50}]
New key       (key demo-key-2): charge_id=2
GET /charges:                   [{id:1,...}, {id:2,...}]
No key:                         400 {"detail":"missing Idempotency-Key header"}
```

**Two identical requests, one charge.** That is the whole guarantee.

### [`17-websockets/`](17-websockets/) - Both directions on one connection

SSE is one-way (server → client). WebSocket is two-way. The demo sends a tick every second (server → client) **and** echoes whatever the client types (client → server → client). Both on the same connection.

| File | What it is |
|---|---|
| [`17-websockets/README.md`](17-websockets/README.md) | SSE vs WebSocket, when to pick each |
| [`17-websockets/01-fastapi-websocket/README.md`](17-websockets/01-fastapi-websocket/README.md) | Walkthrough: watch ticks arrive, send a message, get an echo |
| [`17-websockets/01-fastapi-websocket/main.py`](17-websockets/01-fastapi-websocket/main.py) | `@app.websocket` + background tick loop + receive loop |
| [`17-websockets/01-fastapi-websocket/client.html`](17-websockets/01-fastapi-websocket/client.html) | Browser client using `new WebSocket(...)` |
| [`17-websockets/01-fastapi-websocket/requirements.txt`](17-websockets/01-fastapi-websocket/requirements.txt) | `fastapi` and `uvicorn` |

**Verified output (executed):** the browser shows a new `[tick N]` line every second, and typing `hello` produces `[you] hello` followed by `[echo] hello` — both directions working on one connection.

### [`18-webhooks/`](18-webhooks/) - Untrusted HTTP, verified

A webhook is HTTP someone else sends to you. The only thing that proves it came from the expected sender is an HMAC signature over the raw body. Without verification, anyone can POST a "charge succeeded" event to your endpoint.

| File | What it is |
|---|---|
| [`18-webhooks/README.md`](18-webhooks/README.md) | Why the raw body matters, how HMAC verification works |
| [`18-webhooks/01-fastapi-webhook/README.md`](18-webhooks/01-fastapi-webhook/README.md) | Walkthrough: valid signature, wrong signature, duplicate event |
| [`18-webhooks/01-fastapi-webhook/main.py`](18-webhooks/01-fastapi-webhook/main.py) | `await request.body()` + `hmac.compare_digest` + idempotency on event ID |
| [`18-webhooks/01-fastapi-webhook/requirements.txt`](18-webhooks/01-fastapi-webhook/requirements.txt) | `fastapi` and `uvicorn` |

**Verified output (executed):**

```text
Valid signature:   {"status":"ok","event_id":"evt_001","duplicate":false}
Same event again:  {"status":"ok","event_id":"evt_001","duplicate":true}
Wrong signature:   401 {"detail":"invalid signature"}
```

**The 401 proves the receiver rejects forged requests before doing any work.**

### [`19-search/`](19-search/) - Full-text, vector, or both

Three ranking strategies on the same dataset: SQLite FTS5 (keyword match), cosine similarity over fake embeddings (meaning match), and reciprocal rank fusion of both. The demo query `iPhone power problem` shows each one winning in turn.

| File | What it is |
|---|---|
| [`19-search/README.md`](19-search/README.md) | Full-text vs vector vs hybrid, and why production is almost always hybrid |
| [`19-search/01-sqlite-hybrid-search/README.md`](19-search/01-sqlite-hybrid-search/README.md) | Walkthrough: three queries where each method wins |
| [`19-search/01-sqlite-hybrid-search/main.py`](19-search/01-sqlite-hybrid-search/main.py) | FTS5 + fake embeddings + RRF, all in ~200 lines |
| [`19-search/01-sqlite-hybrid-search/requirements.txt`](19-search/01-sqlite-hybrid-search/requirements.txt) | `fastapi` and `uvicorn` |

**Verified output (executed):** for `iPhone power problem`, FTS ranks `Handset has power issues` #1 and `iPhone won't charge` #2; vector ranks `iPhone won't charge` #1 and `Handset has power issues` #4; hybrid puts both at the top — documents each individual method would miss.

**The embeddings are a deterministic hash**, not a real model. The README shows how to swap in `text-embedding-3-small` and change `EMBEDDING_DIM` to 1536.

### [`20-deploy/`](20-deploy/) - Get it off your laptop

Docker and compose templates that deploy any lesson in this repo. Multi-stage build, non-root user, healthcheck, and a full local stack (app + Postgres + Redis) with one command.

| File | What it is |
|---|---|
| [`20-deploy/README.md`](20-deploy/README.md) | The seven concerns of deployment, and why this lesson covers the first three |
| [`20-deploy/01-docker/Dockerfile`](20-deploy/01-docker/Dockerfile) | Multi-stage template: copy into any lesson, change one line |
| [`20-deploy/01-docker/docker-compose.yml`](20-deploy/01-docker/docker-compose.yml) | App + Postgres (with pgvector) + Redis, all local |
| [`20-deploy/01-docker/.dockerignore`](20-deploy/01-docker/.dockerignore) | What not to send to the build context |

**No runnable lesson** — these are templates. The Dockerfile is correct for any lesson's `main.py`, and the compose file brings up a full stack in one command.

### [`21-testing/`](21-testing/) - Prove it still works

Tests for the idempotency lesson. Four behaviors, one test each: first charge succeeds, retry doesn't double-charge, new key does, missing key is rejected. Runs in half a second, catches the bug the whole lesson exists to prevent.

| File | What it is |
|---|---|
| [`21-testing/README.md`](21-testing/README.md) | Unit vs integration vs e2e, what to test, why pytest |
| [`21-testing/01-pytest-example/README.md`](21-testing/01-pytest-example/README.md) | Walkthrough of the four tests and the fixture that isolates them |
| [`21-testing/01-pytest-example/test_idempotency.py`](21-testing/01-pytest-example/test_idempotency.py) | The four tests, using FastAPI's `TestClient` |
| [`21-testing/01-pytest-example/conftest.py`](21-testing/01-pytest-example/conftest.py) | sys.path setup + database reset before each test |
| [`21-testing/01-pytest-example/requirements.txt`](21-testing/01-pytest-example/requirements.txt) | `fastapi`, `uvicorn`, `pytest`, `httpx` |

**Verified output (executed):**

```text
test_idempotency.py::test_first_charge_succeeds PASSED
test_idempotency.py::test_same_key_does_not_double_charge PASSED
test_idempotency.py::test_different_key_creates_new_charge PASSED
test_idempotency.py::test_missing_key_is_rejected PASSED

4 passed in 0.51s
```

---

## Verify it yourself

The fastest proof that the repo works: run the **transaction lesson** and watch the money vanish.

```bash
cd 15-transactions/01-fastapi-transaction
pip install -r requirements.txt
uvicorn main:app --reload --port 8015
```

In a second terminal:

```bash
# Baseline
curl -s http://127.0.0.1:8015/balances
# -> {"alice":100,"bob":50}

# The bug: no transaction, forced failure
curl -s -X POST "http://127.0.0.1:8015/transfer/broken?from_id=alice&to_id=bob&amount=30&fail=1"
curl -s http://127.0.0.1:8015/balances
# -> {"alice":70,"bob":50}   $30 vanished

# The fix: transaction, same failure
curl -s -X POST http://127.0.0.1:8015/reset
curl -s -X POST "http://127.0.0.1:8015/transfer/safe?from_id=alice&to_id=bob&amount=30&fail=1"
curl -s http://127.0.0.1:8015/balances
# -> {"alice":100,"bob":50}  nothing changed
```

**Same failure. Same amount. Different outcome.** That is the whole guarantee.

The other runnable lessons are equally verifiable. In short:

- **RBAC** (`03-`) — admin gets 200, user gets 403, no token gets 401
- **MCP** (`02-`) — `npx tsx server.ts` prints `{ sum: 5 }`
- **Agent harness** (`09-`) — `python main.py` prints a 3-turn loop ending in `The answer is 50.`
- **Background jobs** (`11-`) — `python main.py` retries job 2 and dead-letters job 3
- **Streaming** (`12-`) — browser shows words one per second
- **Observability** (`13-`) — every log line carries the same `request_id`
- **File uploads** (`14-`) — both endpoints save 5 MB; only memory differs
- **Idempotency** (`16-`) — same key twice, one charge
- **WebSockets** (`17-`) — ticks arrive every second, typed message comes back
- **Webhooks** (`18-`) — wrong signature returns 401
- **Search** (`19-`) — hybrid finds documents each individual method misses
- **Testing** (`21-`) — `pytest -v` shows `4 passed`

Each lesson's README has the exact commands.

---

## What you can do with this repo

Free to use for all of these (MIT license):

- **Learn:** read a lesson, run it, break it.
- **Teach:** use it in a class, bootcamp, or study group.
- **Audit:** before accepting AI-generated backend code, check it against [`10-reference/ai-code-pitfalls.md`](10-reference/ai-code-pitfalls.md).
- **Fork:** strip it down and add your own lessons.
- **Translate:** port a lesson to your language (see the "In another language?" table in each lesson README).
- **Contribute:** see below.
- **Star:** the only signal that tells other learners it is worth their time.

**Not for:** copying into production, using as a starter template, or deploying without hardening.

---

## Contribute

See **[`CONTRIBUTING.md`](CONTRIBUTING.md)** for the full recipe format. The short version:

1. **One idea per lesson.** If the README needs "and also...", split it.
2. **Runnable code.** One or two files, with an exercise at the bottom.
3. **README with required sections:** what you will learn, how to run, what to look at, in another language.
4. **No secrets.** No `.env`, API keys, or tokens in examples.

**Good next lessons:**

- WebSockets at scale (Redis pub/sub, sticky sessions)
- Idempotency for webhooks (combining `16-` and `18-`)
- Background job retry with exponential backoff
- Observability with real metrics (Prometheus)
- Deploy to a real provider (Fly.io, Railway, Cloud Run)

**Bad candidates:** frontend topics, framework comparisons, anything that needs a Kubernetes cluster to demonstrate.

PRs welcome. Small PRs preferred. One commit per file or per lesson, no "fix typo" noise.

---

## Repo files at the root

| File | What it is |
|---|---|
| [`README.md`](README.md) | This file |
| [`LICENSE`](LICENSE) | MIT: free to use, fork, teach with |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Recipe format for new lessons |
| [`.gitignore`](.gitignore) | What not to commit |
| [`.github/workflows/check-python.yml`](.github/workflows/check-python.yml) | CI: byte-compiles every `.py` |
| [`.github/workflows/check-typescript.yml`](.github/workflows/check-typescript.yml) | CI: type-checks every `.ts` lesson |

---

## Complete file tree

```
agentic-backend-cookbook/
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── .gitignore
├── .github/
│   └── workflows/
│       ├── check-python.yml
│       └── check-typescript.yml
├── assets/
│   └── logo.svg
├── 00-roadmap/
│   └── README.md
├── 01-api-design/
│   ├── README.md
│   ├── 01-http-typescript/
│   │   ├── README.md
│   │   └── example.ts
│   └── 02-crud-model/
│       ├── README.md
│       └── example.ts
├── 02-mcp-connectors/
│   ├── README.md
│   └── 01-minimal-mcp-server/
│       ├── README.md
│       ├── package.json
│       ├── package-lock.json
│       └── server.ts
├── 03-rbac-admin/
│   ├── README.md
│   └── 01-fastapi-rbac/
│       ├── README.md
│       ├── requirements.txt
│       └── main.py
├── 04-databases/
│   ├── README.md
│   ├── 01-database-comparison.md
│   ├── 02-postgres-crud/
│   │   ├── README.md
│   │   ├── schema.sql
│   │   └── crud.py
│   ├── 03-mysql-crud/
│   │   ├── README.md
│   │   └── crud.py
│   ├── 04-mongodb-crud/
│   │   ├── README.md
│   │   └── crud.py
│   └── 05-dynamodb-crud/
│       ├── README.md
│       └── crud.py
├── 05-glossary/
│   └── README.md
├── 06-caching/
│   ├── README.md
│   └── 01-fastapi-cache/
│       ├── README.md
│       ├── requirements.txt
│       └── main.py
├── 07-rate-limiting/
│   ├── README.md
│   └── 01-fastapi-rate-limit/
│       ├── README.md
│       ├── requirements.txt
│       └── main.py
├── 08-documentation/
│   ├── README.md
│   ├── api-spec-template.md
│   └── example-spec.md
├── 09-agent-harness/
│   ├── README.md
│   └── 01-minimal-harness/
│       ├── README.md
│       └── main.py
├── 10-reference/
│   ├── README.md
│   ├── database-types.md
│   ├── api-styles.md
│   ├── fastapi-types-example.py
│   └── ai-code-pitfalls.md
├── 11-background-jobs/
│   ├── README.md
│   └── 01-minimal-queue/
│       ├── README.md
│       └── main.py
├── 12-streaming/
│   ├── README.md
│   └── 01-fastapi-sse/
│       ├── README.md
│       ├── requirements.txt
│       ├── main.py
│       └── client.html
├── 13-observability/
│   ├── README.md
│   └── 01-fastapi-request-id/
│       ├── README.md
│       ├── requirements.txt
│       └── main.py
├── 14-file-uploads/
│   ├── README.md
│   └── 01-fastapi-upload/
│       ├── README.md
│       ├── requirements.txt
│       └── main.py
├── 15-transactions/
│   ├── README.md
│   └── 01-fastapi-transaction/
│       ├── README.md
│       ├── requirements.txt
│       └── main.py
├── 16-idempotency/
│   ├── README.md
│   └── 01-fastapi-idempotency/
│       ├── README.md
│       ├── requirements.txt
│       └── main.py
├── 17-websockets/
│   ├── README.md
│   └── 01-fastapi-websocket/
│       ├── README.md
│       ├── requirements.txt
│       ├── main.py
│       └── client.html
├── 18-webhooks/
│   ├── README.md
│   └── 01-fastapi-webhook/
│       ├── README.md
│       ├── requirements.txt
│       └── main.py
├── 19-search/
│   ├── README.md
│   └── 01-sqlite-hybrid-search/
│       ├── README.md
│       ├── requirements.txt
│       └── main.py
├── 20-deploy/
│   ├── README.md
│   └── 01-docker/
│       ├── Dockerfile
│       ├── docker-compose.yml
│       └── .dockerignore
└── 21-testing/
    ├── README.md
    └── 01-pytest-example/
        ├── README.md
        ├── conftest.py
        ├── test_idempotency.py
        └── requirements.txt
```

**22 sections · ~100 tracked files · 13 verified runnable lessons**

---

## Stack

| Layer | Language / tool | Why |
|---|---|---|
| API and MCP lessons | **TypeScript / Node** | Types show the concept and are easy to skim |
| RBAC, caching, rate limiting, streaming, observability, file uploads, transactions, idempotency, websockets, webhooks, search | **Python / FastAPI** | Cleanest pattern for each |
| Background jobs | **Python (stdlib + SQLite)** | The loop is plain Python; no deps needed |
| Agent harness | **Python (stdlib only)** | The loop is plain Python; no deps needed |
| Databases | **Postgres, MySQL, MongoDB, DynamoDB** | Same CRUD, four engines |
| Documentation lesson | **Markdown** | The contract is a document, not code |
| Deploy | **Docker + Compose** | The universal deployment packaging |
| Testing | **pytest** | The Python standard |
| Reference docs | **Markdown + one FastAPI file** | Read-only comparison; one runnable Pydantic example |

**These languages are examples, not requirements.** Each code lesson has an "In another language?" table showing Go, Rust, PHP, Ruby, Java, and C# equivalents.

---

## CI: what is tested on every push

| Check | What it does |
|---|---|
| **Check Python** | `python -m py_compile` on every `.py` file, catching syntax errors |
| **Check TypeScript** | `tsc --noEmit` on each lesson, catching type errors |

These are **compile checks**, not behavioral tests. They catch rot as the repo is edited; they do not replace running the examples yourself. The database lessons are **not tested in CI** because that would need four live databases. The testing lesson (`21-testing/`) shows what a *behavioral* test looks like and could be wired into CI in a future PR.

---

<div align="center">

**If this saved you time, star the repo.**
It is the only signal that tells other learners the examples are worth their time.

MIT License. See [`LICENSE`](LICENSE). Use it, fork it, teach with it.

</div>