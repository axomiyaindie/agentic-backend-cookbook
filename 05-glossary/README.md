# Glossary

Plain-English definitions of every term used in this repo. Grouped by
section so you can read the ones relevant to the lesson you're on.

If a lesson uses a word you don't know, it should be here. If it's
missing, open an issue or a PR.

---

## API and HTTP (`01-api-design`)

**API** — a contract that says "send me this shape, I'll send you that shape".

**HTTP verb** — the *action* part of a request: `GET` (read), `POST` (create),
`PUT` (replace), `PATCH` (change), `DELETE` (remove).

**Endpoint** — a URL path + verb that does something. `GET /users/42` is
an endpoint. `POST /login` is an endpoint.

**Status code** — the number the server sends back. `200` = ok, `201` =
created, `204` = ok but no body, `400` = bad request, `401` = not logged in,
`403` = logged in but not allowed, `404` = not found, `409` = conflict,
`422` = unprocessable, `429` = too many requests, `500` = server bug.

**Header** — metadata sent alongside a request. `Authorization: Bearer ...`
is a header. `Content-Type: application/json` is a header.

**Body** — the data part of a request or response. In JSON APIs, the body
is a JSON object.

**Idempotent** (HTTP) — a method is idempotent if calling it twice has the
same effect as calling it once. `GET`, `PUT`, `DELETE` are idempotent by
convention; `POST` is not. See `16-idempotency/` for the application-level
version.

## Types and validation (`01-api-design`, `10-reference`)

**Type** (TypeScript) — a description of a value's shape, checked at compile
time. Doesn't exist at runtime. If the type says `email: string`, TypeScript
won't stop a user from typing `"not-an-email"` into that field.

**Schema** (JSON Schema / Pydantic) — a description of a value's shape,
checked at *runtime*. This is what actually rejects bad input. Types check
*your* code; schemas check *the caller's* data.

**Validation** — the act of checking that incoming data matches a schema.
Always happens on the server, regardless of what the client claims.

**Pydantic** — Python's runtime validation library. FastAPI uses it to
validate request bodies and serialize responses. `BaseModel` is the base
class you subclass.

**Field** (Pydantic) — a single attribute on a `BaseModel`, optionally
constrained (`min_length`, `max_length`, `pattern`, `ge`, `le`).

## Authentication and access control (`03-rbac-admin`)

**Authentication** — proving *who* you are. Usually a password, then a token.

**Authorization** — deciding *what* you're allowed to do. RBAC is one way.

**RBAC** — Role-Based Access Control. Permissions are attached to *roles*,
and users have roles. "Admins can delete, users can't."

**Token** — a string the client sends on each request to prove who it is.
Real apps use JWTs; this repo uses plain strings for teaching.

**JWT** — JSON Web Token. A signed, self-contained token that carries
claims (like the user's role) and an expiry. Signed so the server can
verify it wasn't tampered with.

**Dependency injection** — a pattern where a function declares "I need X"
instead of creating X itself. In FastAPI, `Depends(...)` does this. It's
how `require_role("admin")` gets plugged into an endpoint.

**401 vs 403** — `401 Unauthorized` means "you're not logged in". `403
Forbidden` means "you're logged in, but not allowed." The client handles
them differently — 401 triggers a re-login, 403 does not. Returning 401
for a logged-in user causes a re-login loop.

## MCP and AI tooling (`02-mcp-connectors`, `09-agent-harness`)

**MCP** — Model Context Protocol. A standard way for AI clients to discover
and call tools. Tools have a name, description, input schema, and handler.

**Tool** (MCP) — one callable function exposed to an AI client.
`add_numbers` is a tool. `get_weather` is a tool.

**JSON-RPC** — the message format MCP uses. Every message is a JSON object
with `jsonrpc`, `method`, `params`, `id`.

**Agent** — a loop that asks a model what to do, executes the tool the model
asks for, feeds the result back, and repeats until the model says "done".
The model decides; the harness executes.

**Harness** — the code that runs the agent loop. Reads the model's decision,
runs the tool, appends the result to the message history, and decides when
to stop. See `09-agent-harness/`.

**Tool call** — a model's decision to invoke a named tool with specific
arguments. The model never executes code — it only emits the request.

**Agent loop** — one iteration of "decide → execute → feed back". A harness
runs this in a loop until termination.

## Databases (`04-databases`, `10-reference`)

**Relational database** — stores data in tables with typed columns and
foreign-key relationships. Postgres and MySQL are relational.

**Document database** — stores JSON-like documents in collections. MongoDB
is a document database. No fixed schema.

**Key-value / wide-column database** — data is keyed by a partition key,
and access must go through it. DynamoDB is this kind.

**Time-series database** — optimized for timestamped data (metrics, IoT).
InfluxDB, TimescaleDB.

**Vector database** — stores embeddings for semantic search. pgvector,
Pinecone, Qdrant.

**Graph database** — stores nodes and edges; queries traverse relationships.
Neo4j.

**Schema** (database) — the structure of a table: its columns, their types,
and their constraints. `CREATE TABLE ...` defines a schema.

**Partition key** — the field DynamoDB uses to decide which physical shard
stores an item. Queries must include it to be fast.

**Index** — a data structure the database maintains to make certain lookups
fast. In DynamoDB you must design your keys up front; in Postgres you can
add indexes after the fact.

**Query** — asking the database for data. In SQL, a `SELECT`. In DynamoDB,
a `Query` operation with a key condition.

**Scan** — reading every item in a table. In DynamoDB, expensive and
discouraged. There is no cheap `Scan` at scale.

**Migration** — a versioned change to your database schema. Real apps run
migrations instead of hand-editing the database.

**ACID** — Atomicity, Consistency, Isolation, Durability. The four
guarantees a relational database makes about a transaction.

**Transaction** — a group of operations that succeed or fail together.
`BEGIN ... COMMIT` or `ROLLBACK`. See `15-transactions/`.

**Rollback** — undoing the changes made since `BEGIN`. Used when a step
inside a transaction fails.

**Isolation level** — how much one transaction can see another's
in-progress work. Postgres defaults to `READ COMMITTED`; SQLite defaults
to `SERIALIZABLE`.

## Caching (`06-caching`)

**Cache** — a fast store that holds the result of an expensive operation,
so the next request can skip the work.

**Cache hit** — the requested value was in the cache. Fast.

**Cache miss** — the value wasn't in the cache. The slow path runs.

**TTL** (Time To Live) — how long a cached value stays valid. After TTL,
the next request is a cache miss.

**Cache-aside** — the pattern where the app checks the cache first, and on
a miss computes, stores, and returns. What `06-caching/` implements.

**Invalidation** — removing a cached value before its TTL expires, because
the underlying data changed.

**Eviction** — removing a cached value because the cache is full. LRU
(least recently used) and LFU (least frequently used) are common policies.

**Cache stampede** — many requests miss the same key at the same instant,
all running the expensive operation. Real systems add a lock.

## Rate limiting (`07-rate-limiting`)

**Rate limit** — a cap on how many requests a client can make in a time
window. Defensive, not optimization.

**Fixed window** — a rate limit algorithm that counts requests per calendar
minute/hour. Simple, but allows a burst at the boundary.

**Sliding window** — a rate limit algorithm that counts requests in a rolling
window. Smoother, slightly more state.

**Token bucket** — a rate limit algorithm where a bucket refills at a steady
rate, and each request takes a token. Allows controlled bursts.

**429 Too Many Requests** — the status code a rate limiter returns when the
client is over the limit.

**Retry-After** — the header that tells a client when it can try again.

**X-RateLimit-* headers** — `Limit`, `Remaining`, `Reset`. Tell a client
its quota and how much is left.

## Documentation (`08-documentation`)

**API spec** — a document describing every endpoint's method, path, request
shape, response shape, status codes, and auth requirements.

**OpenAPI** — a machine-readable API spec format. FastAPI generates one
automatically at `/openapi.json`.

**Swagger UI** — a browser view of an OpenAPI spec. FastAPI serves one at
`/docs`.

## Background jobs (`11-background-jobs`)

**Background job** — work moved out of the request cycle. The client
receives a fast acknowledgment; the actual work runs later.

**Queue** — the store of pending jobs, waiting to be picked up by a worker.

**Worker** — the process that pulls jobs from the queue and executes them.

**Producer** — the code that enqueues a job. Runs inside the HTTP request.

**At-least-once delivery** — the guarantee a queue makes: every job runs at
least once, possibly more if a worker crashes mid-job. Forces every job to
be idempotent.

**Idempotent job** — a job that produces the same result when run twice.
Required because of at-least-once delivery.

**Dead-letter queue** — the place failed jobs go after exhausting their
retries. Inspectable by humans.

**Retry** — re-running a failed job. Usually with exponential backoff
(1s, 2s, 4s, ...).

**Backoff** — the strategy of waiting longer between retries, so a failing
downstream isn't hammered.

**Celery, BullMQ, Sidekiq** — the most common Python, Node, and Ruby job
queues respectively. Not used in this repo (which uses SQLite) but named in
the README as production choices.

## Streaming (`12-streaming`)

**SSE** (Server-Sent Events) — a one-way stream from server to client over
plain HTTP. Format is `data: ...\n\n` lines. What `12-streaming/` uses.

**EventSource** — the browser API for consuming SSE. Automatically
reconnects.

**StreamingResponse** — FastAPI's wrapper for sending a response in chunks.
Used with an async generator for SSE.

**Flush** — pushing buffered output to the client immediately. Without it,
streaming doesn't stream.

**WebSocket** — a two-way connection between client and server. See
`17-websockets/`. Not the same as SSE.

## Observability (`13-observability`)

**Observability** — the ability to answer "what happened?" when something
breaks, using logs, metrics, and traces.

**Log** — a record of one event at one moment. "This request happened,"
"this error occurred."

**Metric** — a numeric measurement aggregated over time. "Requests per
second," "p99 latency."

**Trace** — the full path of one request through multiple services, with
timing at each step.

**Correlation ID** (request ID) — a unique ID generated at the edge of a
request, attached to every log line and passed through every layer. Makes
"what happened to this request?" answerable.

**Structured log** — a log line in a machine-readable format (usually JSON)
so it can be filtered by field. `{"event": "request_end", "status": 200}`
is structured. `200 OK` is not.

**ContextVar** — Python's way to make "ambient" context available to any
function called during a request, without threading it through every call
signature. Used in `13-observability/`.

**Prometheus** — a metrics backend. FastAPI has `prometheus-fastapi-instrumentator`
to expose metrics in the format Prometheus scrapes.

**MDC** (Mapped Diagnostic Context) — Java's equivalent of `ContextVar`,
used to attach the correlation ID to every log line from one request.

## File uploads (`14-file-uploads`)

**Buffering** — reading the entire file into memory before doing anything.
Simple, and catastrophic for large files.

**Chunked read** — reading the file in fixed-size pieces and processing each
one before reading the next. Constant memory regardless of file size.

**UploadFile** — FastAPI's class for an uploaded file. Wraps a
`SpooledTemporaryFile`, exposes `read(size)`.

**Multipart form** — the HTTP encoding for file uploads. Each field has a
`Content-Disposition` header and its own body.

**Presigned URL** — a URL that grants temporary permission to upload to (or
download from) object storage. Lets the client upload directly to S3
without the server seeing the file.

**Object storage** — S3, GCS, R2. The production destination for uploaded
files, not the local disk.

## Transactions (`15-transactions`)

**Atomicity** — "all or nothing". If any step in a transaction fails, none
of the steps persist.

**BEGIN / COMMIT / ROLLBACK** — the three statements that bracket a
transaction. `BEGIN` starts it, `COMMIT` saves, `ROLLBACK` discards.

**Autocommit** — the database default where every statement is committed
immediately. What makes the "broken" endpoint in `15-transactions/` lose
money.

**Deadlock** — two transactions each waiting for a lock the other holds.
The database detects and resolves it; the app should retry.

**2PC** (two-phase commit) — a protocol for atomicity across multiple
databases. Slow and fragile; sagas are usually better.

**Saga** — a pattern for atomicity across services using compensating
transactions. Out of scope for this repo.

## Idempotency (`16-idempotency`)

**Idempotency** — running an operation twice has the same effect as running
it once.

**Idempotency key** — a client-generated string (`Idempotency-Key` header)
that identifies an operation. The server uses it to dedupe retries.

**seen_keys table** — the store of keys the server has already processed.
The idempotency lesson implements this in SQLite.

**Replay** — sending the same request twice. Common in retries, page
refreshes, and webhook deliveries.

**In progress** — the state of a key while its operation is running. A
second request with the same key returns 409 in this lesson's
implementation.

**Body hash** — a hash of the request body, checked alongside the key to
ensure the client didn't reuse a key with different content. Stripe
returns 422 if they differ; this lesson doesn't implement it.

## WebSockets (`17-websockets`)

**WebSocket** — a bidirectional connection over HTTP after an upgrade
handshake.

**Upgrade handshake** — the initial HTTP request that turns into a
WebSocket. Uses `Upgrade: websocket` and `Connection: Upgrade`.

**101 Switching Protocols** — the status code the server returns to accept
the upgrade.

**Frame** — the unit of a WebSocket message. Browsers and servers handle
framing; you just call `send`.

**Ping / Pong** — control frames used to keep idle connections alive
through proxies.

## Webhooks (`18-webhooks`)

**Webhook** — an HTTP request a third party sends to you when an event
happens. The inverse of polling.

**HMAC** — Hash-based Message Authentication Code. Used to sign webhook
payloads so the receiver can verify the sender.

**Raw body** — the exact bytes of an incoming request, before any parsing.
Required for HMAC verification; re-serializing after JSON parsing changes
the bytes.

**Signature header** — the header carrying the HMAC (e.g. `X-Signature`,
`Stripe-Signature`). The receiver computes the same HMAC and compares.

**Constant-time compare** — comparing two values in time independent of
where they differ, to prevent timing attacks. `hmac.compare_digest` in
Python.

**Replay attack** — capturing a valid signed request and resending it.
Prevented by including a timestamp in the signature and rejecting old
ones.

## Search (`19-search`)

**Full-text search** — finding documents by the words they contain, after
stemming and ignoring stopwords. SQLite FTS5, Postgres `tsvector`.

**BM25** — the ranking algorithm most full-text engines use. Scores by term
frequency, rarity, and document length.

**Embedding** — a vector (usually 384–1536 numbers) that represents the
meaning of a piece of text. Generated by a model.

**Vector search** — finding documents whose embeddings are closest to the
query embedding, by cosine distance. Finds meaning, not exact words.

**Cosine similarity** — the cosine of the angle between two vectors. 1.0
means identical direction; 0 means orthogonal.

**Hybrid search** — running full-text and vector search, then merging the
results.

**RRF** (Reciprocal Rank Fusion) — the merge algorithm hybrid search uses.
`1/(k + rank)` for each list, summed per document.

**RAG** (Retrieval-Augmented Generation) — retrieve documents, then feed
them to an LLM as context. Search is the "retrieve" half.

**Chunking** — splitting long documents into pieces small enough to embed
and retrieve independently.

## Deploy (`20-deploy`)

**Dockerfile** — a recipe for building a container image. Runs top to
bottom; each `RUN` is a layer.

**Multi-stage build** — using two `FROM` lines to separate build-time and
runtime dependencies. The build stage installs compilers; the runtime
stage gets only the installed packages.

**Non-root user** — running the container as a user other than `root`. If
the app is compromised, the attacker can't escalate to the host.

**Healthcheck** — a command the orchestrator runs to know the app is ready.
Used by Docker, Kubernetes, Cloud Run.

**Compose** — a YAML file defining a multi-container local stack. One
`docker compose up` brings up the app, database, and cache together.

**Environment variable** — a setting passed to the process at runtime.
Where secrets go, instead of the code.

**`.env` file** — a local file with environment variables, not committed.
Used in development; the platform sets real env vars in production.

## Testing (`21-testing`)

**Unit test** — tests one function in isolation. Milliseconds.

**Integration test** — tests several pieces together. 100ms–seconds.

**End-to-end test** — tests the whole system through real HTTP. Seconds–
minutes.

**Fixture** — reusable setup for tests. `@pytest.fixture` in pytest.

**TestClient** — FastAPI's in-process HTTP client. Lets tests send real
requests without a running server.

**pytest** — Python's standard test runner. Files start with `test_`,
functions start with `test_`.

**Test pyramid** — many unit tests, some integration tests, few e2e tests.
Lower levels are faster and find bugs more precisely.

**Coverage** — the percentage of lines the tests execute. 80% is a good
target; 100% is rarely worth chasing.

**Mocking** — replacing a real dependency (network, database, clock) with
a fake in tests. A tool for when the real thing is slow or unreliable;
not the default.

## Security (mentioned but not implemented here)

**SQL injection** — an attack where user input is concatenated into a SQL
string and changes what the query does. Prevented by parameterised queries.

**Parameterised query** — a SQL query where values are passed separately
from the query text (`%s`, `$1`, `?` placeholders). Prevents SQL injection.

**Hashing** (passwords) — storing a one-way transformation of a password
(bcrypt, argon2) instead of the password itself. If the database leaks,
the attacker still can't log in. This repo does **not** do this — it's a
teaching shortcut, not a real implementation.

**Secrets** — API keys, passwords, signing keys. Load from environment
variables. Never commit. Never log the value.

**Path traversal** — an attack where the filename `../../etc/passwd`
escapes the intended upload directory. Prevented by stripping path
components from client-supplied filenames.