# Minimal queue

A hand-written job queue using SQLite and a worker loop. No Redis, no
Celery, no Docker. The whole mechanism in ~150 lines of Python.

## What you'll learn
- How a job is enqueued, picked up, executed, and acknowledged
- Why at-least-once delivery forces every job to be idempotent
- What a retry counter looks like, and what happens when it runs out
- Where the dead-letter queue fits in

## How to run
```bash
python main.py
```

That's it. No `pip install`, no `requirements.txt`. The script uses only
the Python standard library (SQLite is built in).

## What to look at
- `main.py` — read it top to bottom. The comments label each part:
  - **Database** — the `jobs` table and its columns
  - **Producer** — `enqueue()`, called from the "request" side
  - **Worker** — `run_worker()`, a loop that pulls and executes jobs
  - **Handler** — `process_job()`, the fake "do the work" function
  - **Retry + dead-letter** — what happens when `process_job` fails

## Walkthrough — what you'll see

Run `python main.py`. It:
1. Enqueues three jobs: one that succeeds, one that fails once then
   succeeds on retry, one that always fails.
2. Starts a worker that processes the queue until it's empty.
3. Prints each step: enqueued, picked up, succeeded, failed, retried,
   dead-lettered.

Expected output (roughly):

```text
[producer] enqueued job 1: succeed_after_0
[producer] enqueued job 2: succeed_after_1
[producer] enqueued job 3: always_fail

[worker] picked up job 1 (attempt 1)
[worker]   succeeded
[worker] picked up job 2 (attempt 1)
[worker]   failed: transient failure (retry scheduled)
[worker] picked up job 3 (attempt 1)
[worker]   failed: permanent failure (retry scheduled)
[worker] picked up job 2 (attempt 2)
[worker]   succeeded
[worker] picked up job 3 (attempt 2)
[worker]   failed: permanent failure (retry scheduled)
[worker] picked up job 3 (attempt 3)
[worker]   failed: permanent failure (giving up, moving to dead letter)

[summary] succeeded: 2  failed_attempts: 2  dead_letter: 1
```

The key observation: **job 2 ran twice.** The first time it failed, the
second time it succeeded. That's at-least-once delivery in action.

## The states of a job

Every job in the `jobs` table moves through these states:

| State | Meaning |
|---|---|
| `pending` | In the queue, not yet picked up |
| `running` | A worker is currently executing it |
| `succeeded` | Ran to completion, acked |
| `failed` | Ran, threw an exception, will retry |
| `dead` | Exhausted retries, moved to dead-letter |

A worker's job is to move rows from `pending` → `running` → `succeeded`
or `failed` → (retry) → `dead`. That's the whole loop.

## Why every job must be idempotent

Suppose a job is `"send welcome email to user 42"`. The worker:

1. Picks up the job
2. Sends the email
3. Crashes before marking the job as `succeeded`

On restart, the worker sees the job as still `running` (or `pending` if
your cleanup logic reset it) and runs it again. **The user gets two
emails.**

The fix is **idempotency**: make the job safe to run twice. For an email:

- Store `welcome_email_sent: true` on the user record.
- The job checks that flag first; if set, it returns immediately.

That's it. The job can run a thousand times and the user gets one email.
This is the single most important discipline of background jobs, and it's
why "just add Celery" is harder than it sounds.

## What this example deliberately skips

- **Multiple workers.** This lesson runs one worker. Production runs
  several, and the queue must handle concurrent pulls safely.
  (`SELECT ... FOR UPDATE SKIP LOCKED` in Postgres, or atomic
  `LPOP` in Redis.)
- **Worker crashes.** If the worker dies mid-job, the job stays in
  `running` forever. Production needs a "job timeout" that resets
  stuck jobs.
- **Scheduled jobs.** All jobs here run immediately. Cron jobs enqueue
  on a timer instead of on a request.
- **Priorities.** All jobs are equal. Some queues let "high priority"
  jobs jump the line.
- **Backoff.** Retries here happen immediately. Production adds
  exponential backoff so a failing downstream doesn't get hammered.

Each of those is a lesson on its own. This one shows the loop.

---

## In another language?

The states and the loop are the same everywhere:

| Language | Minimal approach |
|---|---|
| Go | `database/sql` + a goroutine loop, or `hibiken/asynq` |
| Rust | `rusqlite` + a `tokio::spawn` loop, or `apalis` |
| Node | `better-sqlite3` + a `setInterval` loop, or BullMQ |
| PHP | PDO + a CLI script, or Laravel Queues |
| Ruby | Sequel + a `Thread.new` loop, or Sidekiq |
| Java | JDBC + a `ScheduledExecutorService`, or Spring Batch |
| C# | `Microsoft.Data.Sqlite` + a `Task.Run` loop, or Hangfire |

Every production queue adds reliability features on top of this loop.
The loop itself never changes.