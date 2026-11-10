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

[Setup](SETUP.md) &nbsp;|&nbsp; [Lessons](#lessons) &nbsp;|&nbsp; [Contribute](CONTRIBUTING.md) &nbsp;|&nbsp; [Glossary](05-glossary/README.md)

</div>

---

## What this is

AI assistants can now generate 200 lines of backend code in a few seconds. Understanding those 200 lines still takes you hours.

This repo closes that gap. Every section is a folder of **runnable, one-concept lessons** with a README, a runnable file, and an exercise. Thirteen of the lessons have executed output shown in their README — not "trust me, this works."

**New here?** Read [`SETUP.md`](SETUP.md) first (5 minutes), then start with [`00-roadmap/README.md`](00-roadmap/README.md).

**Reviewing AI-generated code?** Start with [`10-reference/ai-code-pitfalls.md`](10-reference/ai-code-pitfalls.md) — nine patterns to check before you ship.

---

## Lessons

Every section is a folder. Click any link to open it. Inside each folder, the `README.md` explains what it is, how to run it, and what to look at.

### 00 — Roadmap

| Path | What it is |
|---|---|
| [`00-roadmap/README.md`](00-roadmap/README.md) | Reading order + "vibe coding" safety net |

### 01 — API design

| Path | What it is |
|---|---|
| [`01-api-design/README.md`](01-api-design/README.md) | Section overview + language policy |
| [`01-api-design/01-http-typescript/README.md`](01-api-design/01-http-typescript/README.md) | Request/response as a TypeScript type |
| [`01-api-design/01-http-typescript/example.ts`](01-api-design/01-http-typescript/example.ts) | Runnable typed example |
| [`01-api-design/02-crud-model/README.md`](01-api-design/02-crud-model/README.md) | How CRUD maps to HTTP verbs |
| [`01-api-design/02-crud-model/example.ts`](01-api-design/02-crud-model/example.ts) | Runnable in-memory CRUD |

### 02 — MCP tool servers

| Path | What it is |
|---|---|
| [`02-mcp-connectors/README.md`](02-mcp-connectors/README.md) | What MCP is |
| [`02-mcp-connectors/01-minimal-mcp-server/README.md`](02-mcp-connectors/01-minimal-mcp-server/README.md) | Walkthrough |
| [`02-mcp-connectors/01-minimal-mcp-server/server.ts`](02-mcp-connectors/01-minimal-mcp-server/server.ts) | Runnable: `tools/list` + `tools/call` |
| [`02-mcp-connectors/01-minimal-mcp-server/package.json`](02-mcp-connectors/01-minimal-mcp-server/package.json) | Dependencies |

### 03 — Role-based access control

| Path | What it is |
|---|---|
| [`03-rbac-admin/README.md`](03-rbac-admin/README.md) | What RBAC is |
| [`03-rbac-admin/01-fastapi-rbac/README.md`](03-rbac-admin/01-fastapi-rbac/README.md) | Walkthrough: 200/403/401 |
| [`03-rbac-admin/01-fastapi-rbac/main.py`](03-rbac-admin/01-fastapi-rbac/main.py) | Runnable: `login` → `require_role("admin")` |
| [`03-rbac-admin/01-fastapi-rbac/requirements.txt`](03-rbac-admin/01-fastapi-rbac/requirements.txt) | Dependencies |

### 04 — Databases

| Path | What it is |
|---|---|
| [`04-databases/README.md`](04-databases/README.md) | Why four engines |
| [`04-databases/01-database-comparison.md`](04-databases/01-database-comparison.md) | Decision table |
| [`04-databases/02-postgres-crud/README.md`](04-databases/02-postgres-crud/README.md) | Postgres setup |
| [`04-databases/02-postgres-crud/schema.sql`](04-databases/02-postgres-crud/schema.sql) | The `users` table |
| [`04-databases/02-postgres-crud/crud.py`](04-databases/02-postgres-crud/crud.py) | Postgres CRUD |
| [`04-databases/03-mysql-crud/README.md`](04-databases/03-mysql-crud/README.md) | MySQL setup |
| [`04-databases/03-mysql-crud/crud.py`](04-databases/03-mysql-crud/crud.py) | MySQL CRUD |
| [`04-databases/04-mongodb-crud/README.md`](04-databases/04-mongodb-crud/README.md) | MongoDB setup |
| [`04-databases/04-mongodb-crud/crud.py`](04-databases/04-mongodb-crud/crud.py) | MongoDB CRUD |
| [`04-databases/05-dynamodb-crud/README.md`](04-databases/05-dynamodb-crud/README.md) | DynamoDB setup |
| [`04-databases/05-dynamodb-crud/crud.py`](04-databases/05-dynamodb-crud/crud.py) | DynamoDB CRUD |

### 05 — Glossary

| Path | What it is |
|---|---|
| [`05-glossary/README.md`](05-glossary/README.md) | Every term, defined |

### 06 — Caching

| Path | What it is |
|---|---|
| [`06-caching/README.md`](06-caching/README.md) | What caching is |
| [`06-caching/01-fastapi-cache/README.md`](06-caching/01-fastapi-cache/README.md) | Walkthrough |
| [`06-caching/01-fastapi-cache/main.py`](06-caching/01-fastapi-cache/main.py) | Runnable: cache-aside with TTL |
| [`06-caching/01-fastapi-cache/requirements.txt`](06-caching/01-fastapi-cache/requirements.txt) | Dependencies |

### 07 — Rate limiting

| Path | What it is |
|---|---|
| [`07-rate-limiting/README.md`](07-rate-limiting/README.md) | Why rate limit |
| [`07-rate-limiting/01-fastapi-rate-limit/README.md`](07-rate-limiting/01-fastapi-rate-limit/README.md) | Walkthrough |
| [`07-rate-limiting/01-fastapi-rate-limit/main.py`](07-rate-limiting/01-fastapi-rate-limit/main.py) | Runnable: 429 + headers |
| [`07-rate-limiting/01-fastapi-rate-limit/requirements.txt`](07-rate-limiting/01-fastapi-rate-limit/requirements.txt) | Dependencies |

### 08 — Documentation

| Path | What it is |
|---|---|
| [`08-documentation/README.md`](08-documentation/README.md) | Why API docs matter |
| [`08-documentation/api-spec-template.md`](08-documentation/api-spec-template.md) | Copy-paste template |
| [`08-documentation/example-spec.md`](08-documentation/example-spec.md) | Worked example (RBAC) |

### 09 — Agent harness

| Path | What it is |
|---|---|
| [`09-agent-harness/README.md`](09-agent-harness/README.md) | What a harness is |
| [`09-agent-harness/01-minimal-harness/README.md`](09-agent-harness/01-minimal-harness/README.md) | Walkthrough |
| [`09-agent-harness/01-minimal-harness/main.py`](09-agent-harness/01-minimal-harness/main.py) | Runnable: 3-turn loop |

### 10 — Reference docs

| Path | What it is |
|---|---|
| [`10-reference/README.md`](10-reference/README.md) | How to use this section |
| [`10-reference/database-types.md`](10-reference/database-types.md) | Six database families, pricing, real companies |
| [`10-reference/api-styles.md`](10-reference/api-styles.md) | REST vs GraphQL vs gRPC vs SOAP |
| [`10-reference/fastapi-types-example.py`](10-reference/fastapi-types-example.py) | Runnable: Pydantic models |
| [`10-reference/ai-code-pitfalls.md`](10-reference/ai-code-pitfalls.md) | Nine patterns AI code gets wrong |

### 11 — Background jobs

| Path | What it is |
|---|---|
| [`11-background-jobs/README.md`](11-background-jobs/README.md) | Producer/queue/worker, reliability |
| [`11-background-jobs/01-minimal-queue/README.md`](11-background-jobs/01-minimal-queue/README.md) | Walkthrough |
| [`11-background-jobs/01-minimal-queue/main.py`](11-background-jobs/01-minimal-queue/main.py) | Runnable: retry + dead-letter |

### 12 — Streaming (SSE)

| Path | What it is |
|---|---|
| [`12-streaming/README.md`](12-streaming/README.md) | SSE vs WebSocket |
| [`12-streaming/01-fastapi-sse/README.md`](12-streaming/01-fastapi-sse/README.md) | Walkthrough |
| [`12-streaming/01-fastapi-sse/main.py`](12-streaming/01-fastapi-sse/main.py) | Runnable: `StreamingResponse` |
| [`12-streaming/01-fastapi-sse/client.html`](12-streaming/01-fastapi-sse/client.html) | Browser client |
| [`12-streaming/01-fastapi-sse/requirements.txt`](12-streaming/01-fastapi-sse/requirements.txt) | Dependencies |

### 13 — Observability

| Path | What it is |
|---|---|
| [`13-observability/README.md`](13-observability/README.md) | Logs, metrics, traces |
| [`13-observability/01-fastapi-request-id/README.md`](13-observability/01-fastapi-request-id/README.md) | Walkthrough |
| [`13-observability/01-fastapi-request-id/main.py`](13-observability/01-fastapi-request-id/main.py) | Runnable: correlation ID across thread |
| [`13-observability/01-fastapi-request-id/requirements.txt`](13-observability/01-fastapi-request-id/requirements.txt) | Dependencies |

### 14 — File uploads

| Path | What it is |
|---|---|
| [`14-file-uploads/README.md`](14-file-uploads/README.md) | Buffered vs streamed |
| [`14-file-uploads/01-fastapi-upload/README.md`](14-file-uploads/01-fastapi-upload/README.md) | Walkthrough |
| [`14-file-uploads/01-fastapi-upload/main.py`](14-file-uploads/01-fastapi-upload/main.py) | Runnable: both patterns side by side |
| [`14-file-uploads/01-fastapi-upload/requirements.txt`](14-file-uploads/01-fastapi-upload/requirements.txt) | Dependencies |

### 15 — Transactions

| Path | What it is |
|---|---|
| [`15-transactions/README.md`](15-transactions/README.md) | What ACID means |
| [`15-transactions/01-fastapi-transaction/README.md`](15-transactions/01-fastapi-transaction/README.md) | Walkthrough: money vanishes |
| [`15-transactions/01-fastapi-transaction/main.py`](15-transactions/01-fastapi-transaction/main.py) | Runnable: broken vs safe |
| [`15-transactions/01-fastapi-transaction/requirements.txt`](15-transactions/01-fastapi-transaction/requirements.txt) | Dependencies |

### 16 — Idempotency

| Path | What it is |
|---|---|
| [`16-idempotency/README.md`](16-idempotency/README.md) | Idempotency-Key pattern |
| [`16-idempotency/01-fastapi-idempotency/README.md`](16-idempotency/01-fastapi-idempotency/README.md) | Walkthrough: same key twice |
| [`16-idempotency/01-fastapi-idempotency/main.py`](16-idempotency/01-fastapi-idempotency/main.py) | Runnable: `seen_keys` table |
| [`16-idempotency/01-fastapi-idempotency/requirements.txt`](16-idempotency/01-fastapi-idempotency/requirements.txt) | Dependencies |

### 17 — WebSockets

| Path | What it is |
|---|---|
| [`17-websockets/README.md`](17-websockets/README.md) | WebSocket vs SSE |
| [`17-websockets/01-fastapi-websocket/README.md`](17-websockets/01-fastapi-websocket/README.md) | Walkthrough |
| [`17-websockets/01-fastapi-websocket/main.py`](17-websockets/01-fastapi-websocket/main.py) | Runnable: bidirectional |
| [`17-websockets/01-fastapi-websocket/client.html`](17-websockets/01-fastapi-websocket/client.html) | Browser client |
| [`17-websockets/01-fastapi-websocket/requirements.txt`](17-websockets/01-fastapi-websocket/requirements.txt) | Dependencies |

### 18 — Webhooks

| Path | What it is |
|---|---|
| [`18-webhooks/README.md`](18-webhooks/README.md) | Why HMAC verification |
| [`18-webhooks/01-fastapi-webhook/README.md`](18-webhooks/01-fastapi-webhook/README.md) | Walkthrough: valid/wrong/duplicate |
| [`18-webhooks/01-fastapi-webhook/main.py`](18-webhooks/01-fastapi-webhook/main.py) | Runnable: HMAC + idempotency |
| [`18-webhooks/01-fastapi-webhook/requirements.txt`](18-webhooks/01-fastapi-webhook/requirements.txt) | Dependencies |

### 19 — Search

| Path | What it is |
|---|---|
| [`19-search/README.md`](19-search/README.md) | Full-text vs vector vs hybrid |
| [`19-search/01-sqlite-hybrid-search/README.md`](19-search/01-sqlite-hybrid-search/README.md) | Walkthrough |
| [`19-search/01-sqlite-hybrid-search/main.py`](19-search/01-sqlite-hybrid-search/main.py) | Runnable: FTS5 + RRF |
| [`19-search/01-sqlite-hybrid-search/requirements.txt`](19-search/01-sqlite-hybrid-search/requirements.txt) | Dependencies |

### 20 — Deploy

| Path | What it is |
|---|---|
| [`20-deploy/README.md`](20-deploy/README.md) | Seven deployment concerns |
| [`20-deploy/01-docker/Dockerfile`](20-deploy/01-docker/Dockerfile) | Multi-stage template |
| [`20-deploy/01-docker/docker-compose.yml`](20-deploy/01-docker/docker-compose.yml) | App + Postgres + Redis |
| [`20-deploy/01-docker/.dockerignore`](20-deploy/01-docker/.dockerignore) | Build context rules |

### 21 — Testing

| Path | What it is |
|---|---|
| [`21-testing/README.md`](21-testing/README.md) | Unit vs integration vs e2e |
| [`21-testing/01-pytest-example/README.md`](21-testing/01-pytest-example/README.md) | Walkthrough: 4 tests |
| [`21-testing/01-pytest-example/test_idempotency.py`](21-testing/01-pytest-example/test_idempotency.py) | The tests |
| [`21-testing/01-pytest-example/conftest.py`](21-testing/01-pytest-example/conftest.py) | Fixtures |
| [`21-testing/01-pytest-example/requirements.txt`](21-testing/01-pytest-example/requirements.txt) | Dependencies |

---

## Root files

| Path | What it is |
|---|---|
| [`SETUP.md`](SETUP.md) | How to clone, install, and run any lesson |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Recipe format for new lessons |
| [`LICENSE`](LICENSE) | MIT |
| [`.gitignore`](.gitignore) | What not to commit |
| [`assets/logo.svg`](assets/logo.svg) | Banner |
| [`.github/workflows/check-python.yml`](.github/workflows/check-python.yml) | CI: Python byte-compile |
| [`.github/workflows/check-typescript.yml`](.github/workflows/check-typescript.yml) | CI: TypeScript type-check |

---

## What this repo is and isn't

**It is:** 22 sections of small, runnable, one-concept lessons with an exercise at the bottom of each. Thirteen lessons have executed output shown in their README. The point is *understanding*, not shipping.

**It isn't:** production code, a starter template, or a full app. No authentication (only authorization), no frontend, no cloud deployment walkthroughs. See [`SETUP.md`](SETUP.md) for what each lesson needs, and [`CONTRIBUTING.md`](CONTRIBUTING.md) for what belongs here.

If you want a production template, this is the wrong repo. If you want to **understand** what a production template does, you're in the right place.

---

<div align="center">

**If this saved you time, star the repo.**

MIT License. See [`LICENSE`](LICENSE). Use it, fork it, teach with it.

</div>