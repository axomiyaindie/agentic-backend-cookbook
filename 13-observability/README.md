# Observability

**Observability** is the ability to answer "what happened?" when something
breaks, without guessing.

## The one idea to take away

You have three tools for answering "what happened?", and they answer
different questions:

| Tool | Answers | Example |
|---|---|---|
| **Logs** | What happened at this moment? | `request_id=abc user=42 GET /users/42 -> 200` |
| **Metrics** | How many times did this happen? | `http_requests_total{status="500"} = 3` |
| **Traces** | Where did the time go? | `GET /users/42 → db.query 120ms → render 15ms` |

If you only have logs, you can't see trends. If you only have metrics,
you can't see why a specific request failed. If you only have traces,
you can't see errors that happen outside a request. **You need all three**
— but if you're starting from zero, **logs are the place to begin**, and
**correlation IDs are the thing that makes logs useful.**

## Correlation IDs — the single most useful technique

Every log line from a single user request should carry the same ID:

```
request_id=abc123 user=42 GET /users/42 -> 200
request_id=abc123 enqueued job send_email(user=42)
request_id=abc123 job send_email(user=42) -> succeeded
```

Now "what happened for user 42 at 14:32?" is one search for `abc123`,
not three log files to correlate by timestamp.

**In an AI app, this matters more than anywhere else**, because one user
request touches the most layers:

1. HTTP request → the API
2. API → the AI model (slow, remote)
3. AI model → a tool call (MCP server)
4. Tool call → a database
5. Response → a background job (for follow-up work)

Without a correlation ID, following a single user's request across those
five layers is guesswork. With one, it's a single search.

## Lesson

`01-fastapi-request-id/` — a FastAPI middleware that:
- Generates a request ID for every incoming request
- Logs it with every line
- Passes it to background jobs so the same ID appears in the job log

The lesson ties directly to `11-background-jobs`: the ID that starts in
the HTTP layer follows the job into the worker.

## Where this fits in real code

- **Logs** — structured JSON logs (one object per line). Tools: Datadog,
  Loki, CloudWatch, Better Stack.
- **Metrics** — counters and histograms. Tools: Prometheus, StatsD,
  CloudWatch, Datadog.
- **Traces** — distributed request traces. Tools: OpenTelemetry, Jaeger,
  Tempo, Datadog APM.
- **Correlation IDs** — a field in every log line and every trace span.
  Every framework has a way to do this; in FastAPI it's middleware.

## What this lesson does not cover

- **Metrics** — a real metrics lesson needs Prometheus (or a substitute)
  running. It's a 30-minute setup, which breaks the 15-minute rule.
  The README mentions Prometheus as "the next step."
- **Traces** — same problem: OpenTelemetry, a collector, and a backend
  (Jaeger or Tempo). Out of scope for a 15-minute lesson.
- **Log aggregation** — how logs get from your app to a central store.
  Depends on your infrastructure.
- **Alerting** — "wake me up when errors exceed 1%." This depends on
  your metrics backend.

Each of those is worth its own lesson eventually. The mechanism in this
lesson — one ID that follows a request — is the seed of all of them.

---

## In another language?

Correlation IDs are universal. Every language and framework has a way to
generate one, attach it to a request, and log it:

| Language | Middleware pattern |
|---|---|
| Go | `net/http` middleware that stores the ID in `context.Context` |
| Rust | axum extractor that stores the ID in request extensions |
| PHP | Laravel middleware that adds the ID to the log context |
| Ruby | Rack middleware that stores the ID in `Thread.current` |
| Java | Spring `OncePerRequestFilter` that sets MDC (Mapped Diagnostic Context) |
| C# | ASP.NET middleware that stores the ID in `HttpContext.Items` |

The mechanism is always: generate → attach → log → propagate. If you
understand this lesson, you can implement it in any of them.