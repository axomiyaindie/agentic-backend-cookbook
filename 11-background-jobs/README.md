# Background jobs

**Background jobs** move work out of the request cycle. The client asks
for something, the server acknowledges it immediately, and a separate
process does the actual work later.

## The one idea to take away

The **request** and the **work** are separate. When a user uploads a PDF
and asks for a summary, you don't want the HTTP request to block for 30
seconds while the AI model runs. You want:

```
client → POST /summarize  → 202 Accepted (job id)  → client polls or gets notified
                           ↳ enqueued
                             worker picks up job → runs model → stores result
```

The request returns in milliseconds. The work takes as long as it takes.

## When to use a job queue

| Situation | Job queue? |
|---|---|
| Sending an email | Yes — SMTP is slow and can fail |
| Resizing an uploaded image | Yes — CPU-bound |
| Calling a slow AI model | Yes — seconds to minutes |
| A fast database write | No — do it inline |
| A `< 100ms` operation | No — the queue overhead is worse |
| A `> 1s` operation | Yes — always |

The rule of thumb: **if the operation takes more than a second, or can
fail and be retried, it belongs in a queue.**

## The three parts of every queue

1. **Producer** — the code that enqueues a job. Runs in the HTTP handler.
2. **Queue** — persistent storage of pending jobs. Can be a database
   table, Redis list, or a dedicated broker.
3. **Worker** — a separate process that pulls jobs and executes them.
   Can be one worker or a hundred.

That's the whole architecture. Everything else is scale and reliability.

## The reliability contract

A queue makes one guarantee: **at-least-once delivery**. A job will be
executed at least once, possibly more if a worker crashes mid-job and the
job is retried.

This means:

- **Jobs must be idempotent.** Running the same job twice must produce
  the same result. "Send an email" is not idempotent (the user gets two
  emails). "Mark user 42 as verified" is idempotent.
- **Failures need a retry limit.** Otherwise a bad job retries forever.
- **Failed-after-retries jobs need a dead-letter queue.** A separate queue
  that humans can inspect.

These three rules are why "just add Celery" is harder than it looks.

## Lesson

`01-minimal-queue/` — a hand-written queue using SQLite (stdlib) and a
worker loop. No Redis, no Celery, no Docker. You see the enqueue, the
worker pull, the retry, and the dead-letter path in one file.

## Where this fits in real code

- **Celery** (Python) — the most common Python job queue. Redis or
  RabbitMQ as the broker. Battle-tested, complex.
- **BullMQ** (Node) — Redis-backed. Clean API, good for TypeScript apps.
- **Sidekiq** (Ruby) — Redis-backed, the Rails default.
- **Dramatiq** (Python) — lighter than Celery, good docs.
- **Postgres-based queues** — `SKIP LOCKED` + a `jobs` table. What
  this lesson implements, scaled up. Works surprisingly well up to
  thousands of jobs/sec.
- **Managed** — AWS SQS, Google Cloud Tasks, Cloudflare Queues.

## What this lesson does not cover

- **Distributed workers** — this lesson runs workers in the same process.
  Production runs them as separate services.
- **Scheduled jobs (cron)** — enqueue on a timer, not on a request.
  Same queue, different producer.
- **Priorities** — some jobs jump the line. Adds complexity to the
  queue schema.
- **Rate limiting** — if you have 10,000 jobs, you may not want to run
  them all at once. Workers pull at a controlled rate.

Each of those is worth its own lesson eventually. The mechanism in this
lesson is the seed of all of them.

---

## In another language?

The producer / queue / worker triangle is universal:

| Language | Common library | Queue backend |
|---|---|---|
| Python | Celery, RQ, Dramatiq | Redis, RabbitMQ, Postgres |
| Go | `hibiken/asynq`, `riverqueue/river` | Redis, Postgres |
| Node | BullMQ, Bull | Redis |
| Rust | `apalis`, `sidekiq-rs` | Redis, Postgres |
| Ruby | Sidekiq, Resque | Redis |
| Java | Spring Batch, Quartz | Any |
| C# | Hangfire, MassTransit | SQL Server, RabbitMQ, Redis |

Every one of them implements the same contract: enqueue → store → pull →
execute → ack (or retry). If you understand this lesson, you can read
any of them in an afternoon.