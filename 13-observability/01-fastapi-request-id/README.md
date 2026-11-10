# FastAPI request ID

A middleware that generates a correlation ID for every incoming request,
logs it on every line, and passes it to a background job so the same ID
appears in the job log.

## What you'll learn
- How a middleware generates and attaches a request ID
- How to log structured lines with a stable `request_id` field
- How to pass the ID from an HTTP handler to a background job
- Why this is the single most useful debugging technique for AI backends

## How to run
```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8013
```

Using port 8013 to avoid collisions with earlier lessons. Then:

```bash
curl -s -H "X-Request-ID: my-trace-123" http://127.0.0.1:8013/hello
```

Open the terminal where uvicorn is running. You'll see three log lines,
all carrying `request_id=my-trace-123`.

## What to look at
- `main.py` — read the middleware first (`@app.middleware("http")`). It:
  1. Reads `X-Request-ID` from the incoming headers, or generates one
  2. Stores it in a `ContextVar` so every log line can find it
  3. Logs the request start and end with the ID
  4. Echoes the ID back in the response header
- Then read `log()` — the one function that always includes the ID.
- Then read the `/enqueue` endpoint — it passes the ID into a fake
  background job so the same ID appears in the job log.

## Walkthrough — prove it works

**Test 1: Client-supplied ID is used**

```bash
curl -s -H "X-Request-ID: my-trace-123" http://127.0.0.1:8013/hello
```

Server log:
```
{"ts": "...", "level": "info", "event": "request_start", "request_id": "my-trace-123", "method": "GET", "path": "/hello"}
{"ts": "...", "level": "info", "event": "request_end",   "request_id": "my-trace-123", "status": 200, "duration_ms": 1}
```

The ID you sent is the ID in the logs. Response header also echoes it:
```
X-Request-ID: my-trace-123
```

**Test 2: No ID → server generates one**

```bash
curl -s http://127.0.0.1:8013/hello
```

Server log:
```
{"request_id": "a1b2c3d4-...", ...}
```

A random UUID. The response header echoes it too, so a client can grep its
own logs for the same ID.

**Test 3: The ID follows into a background job**

```bash
curl -s -H "X-Request-ID: job-trace-456" http://127.0.0.1:8013/enqueue
```

Server log:
```
{"request_id": "job-trace-456", "event": "request_start", "path": "/enqueue"}
{"request_id": "job-trace-456", "event": "job_enqueued", "job": "send_email", "user": 42}
{"request_id": "job-trace-456", "event": "request_end", "status": 202}
{"request_id": "job-trace-456", "event": "job_running",  "job": "send_email", "user": 42}
{"request_id": "job-trace-456", "event": "job_succeeded", "job": "send_email", "user": 42}
```

**Same ID on every line.** The HTTP request enqueued the job, and the
worker (running in a background thread) still logs the same `request_id`
— because the ID was passed as part of the job payload, not just
inherited from the HTTP context. That's the key pattern.

**Test 4: Search by ID**

```bash
curl -s http://127.0.0.1:8013/hello  # copy the request_id from the response header
```

Then in the server terminal, search for the ID. Every line from that
request appears together. This is how you debug "why did user 42's
request fail at 14:32" in production.

## Why structured logs (JSON) instead of plain text

A plain log line like:

```
INFO: 127.0.0.1:5678 - "GET /hello HTTP/1.1" 200 OK
```

is readable but not **searchable**. You can't query "show me all requests
with duration_ms > 500" without a regex.

A structured log line like:

```json
{"ts": "...", "event": "request_end", "request_id": "abc", "status": 200, "duration_ms": 1}
```

is a JSON object. Your log aggregator (Loki, Datadog, CloudWatch) can
filter on fields: `duration_ms > 500 AND status = 500`. That's how
production debugging actually works.

This lesson uses JSON because the format demonstrates the point. In a real
app you'd use `structlog` or `python-json-logger`.

## The `ContextVar` trick

Why store the ID in a `ContextVar` instead of passing it as an argument
to every function?

Because middleware runs outside the request handler, but its logs need
the same `request_id`. A `ContextVar` is Python's way to make "ambient"
context available to any function called during that request, without
threading it through every call signature.

This is the same mechanism as Go's `context.Context`, Node's
`AsyncLocalStorage`, Ruby's `Thread.current`, and Java's MDC. Every
language has one. FastAPI uses `contextvars.ContextVar`.

## What this example deliberately skips

- **Real background queue.** The "job" runs in a `threading.Thread` —
  same process, same memory. Production uses Celery, BullMQ, etc. The
  correlation ID pattern is the same; only the transport changes.
- **Real log aggregation.** Logs go to stdout. Production ships them to
  a store (Loki, Datadog, CloudWatch). The format is what matters here.
- **Metrics and traces.** This lesson is only about logs + correlation.
  Metrics and traces build on the same IDs but need their own infrastructure.
- **Sampling.** In production, you don't log every request (too much
  data). You sample. The pattern is the same; the volume management is
  separate.

---

## In another language?

The pattern is identical. Every framework has a "request context" and
every language has a way to attach data to it:

| Language | How the ID propagates |
|---|---|
| Python | `contextvars.ContextVar` + FastAPI middleware |
| Go | `context.Context` + `net/http` middleware |
| Rust | axum request extensions + a `tracing` span |
| PHP | Laravel's log context (`Log::withContext`) |
| Ruby | `Thread.current[:request_id]` + Rack middleware |
| Java | SLF4J MDC + a `OncePerRequestFilter` |
| C# | `HttpContext.Items` + `ILogger` scope |

The mechanism is always: **generate at the edge, attach to context, log
everywhere, propagate to async work.** If you understand this lesson, you
can implement it in any of them.