# ─────────────────────────────────────────────────────────────
# Lesson: minimal job queue with SQLite
#
# The whole mechanism:
#   1. Producer inserts a row into `jobs` with status='pending'.
#   2. Worker pulls one pending row, marks it 'running'.
#   3. Worker executes the handler.
#   4a. Success → status='succeeded'.
#   4b. Failure → increment attempts. If under MAX_ATTEMPTS,
#       status='pending' (retry). If over, status='dead'.
#
# No Redis, no Celery, no Docker. Just SQLite and a loop. The
# production versions do exactly this, faster and with more
# features.
# ─────────────────────────────────────────────────────────────

import json
import sqlite3
import time
from typing import Callable

DB_PATH = ":memory:"           # swap for "jobs.db" for persistence
MAX_ATTEMPTS = 3
POLL_INTERVAL = 0.1             # seconds between empty-queue polls


# ── 1. Database schema ──────────────────────────────────────
SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    payload     TEXT    NOT NULL,
    status      TEXT    NOT NULL DEFAULT 'pending',
    attempts    INTEGER NOT NULL DEFAULT 0,
    last_error  TEXT,
    created_at  REAL    NOT NULL,
    updated_at  REAL    NOT NULL
);
"""


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


# ── 2. Producer ─────────────────────────────────────────────
def enqueue(conn: sqlite3.Connection, name: str, payload: dict) -> int:
    now = time.time()
    cur = conn.execute(
        "INSERT INTO jobs (name, payload, status, created_at, updated_at) "
        "VALUES (?, ?, 'pending', ?, ?)",
        (name, json.dumps(payload), now, now),
    )
    conn.commit()
    return cur.lastrowid


# ── 3. Handlers ─────────────────────────────────────────────
# A handler is a function that takes a payload dict and either
# returns (success) or raises (failure). The worker decides what
# to do based on which one happened.
def succeed_after_0(payload: dict):
    print("[handler] succeed_after_0: ok")


def succeed_after_1(payload: dict):
    # Fails on the first call, succeeds on the second.
    # The counter lives in the payload, which the worker persists
    # back to the DB after every attempt — that's how the handler
    # remembers it already ran once.
    n = payload.get("_calls", 0) + 1
    payload["_calls"] = n
    if n < 2:
        raise RuntimeError("transient failure")
    print("[handler] succeed_after_1: ok on attempt 2")


def always_fail(payload: dict):
    raise RuntimeError("permanent failure")


HANDLERS: dict[str, Callable[[dict], None]] = {
    "succeed_after_0": succeed_after_0,
    "succeed_after_1": succeed_after_1,
    "always_fail": always_fail,
}


# ── 4. Worker ───────────────────────────────────────────────
def pull_one(conn: sqlite3.Connection) -> sqlite3.Row | None:
    # Atomic claim: mark one pending row as running, return it.
    # In Postgres this would use SELECT ... FOR UPDATE SKIP LOCKED.
    now = time.time()
    row = conn.execute(
        "SELECT id FROM jobs WHERE status = 'pending' "
        "ORDER BY id LIMIT 1"
    ).fetchone()
    if not row:
        return None
    conn.execute(
        "UPDATE jobs SET status = 'running', updated_at = ? WHERE id = ?",
        (now, row["id"]),
    )
    conn.commit()
    return conn.execute("SELECT * FROM jobs WHERE id = ?", (row["id"],)).fetchone()


def finish(conn: sqlite3.Connection, job_id: int, status: str,
           error: str | None = None):
    conn.execute(
        "UPDATE jobs SET status = ?, last_error = ?, updated_at = ? WHERE id = ?",
        (status, error, time.time(), job_id),
    )
    conn.commit()


def fail(conn: sqlite3.Connection, job: sqlite3.Row, error: str):
    attempts = job["attempts"] + 1
    if attempts >= MAX_ATTEMPTS:
        conn.execute(
            "UPDATE jobs SET status='dead', attempts=?, last_error=?, "
            "updated_at=? WHERE id=?",
            (attempts, error, time.time(), job["id"]),
        )
        print(f"[worker]   giving up after {attempts} attempts -> dead letter")
    else:
        conn.execute(
            "UPDATE jobs SET status='pending', attempts=?, last_error=?, "
            "updated_at=? WHERE id=?",
            (attempts, error, time.time(), job["id"]),
        )
        print(f"[worker]   failed (attempt {attempts}/{MAX_ATTEMPTS}), retrying")
    conn.commit()


def run_worker(conn: sqlite3.Connection, max_jobs: int = 100):
    processed = 0
    while processed < max_jobs:
        job = pull_one(conn)
        if job is None:
            # Empty queue: check if any job is still pending (retries).
            pending = conn.execute(
                "SELECT COUNT(*) FROM jobs WHERE status='pending'"
            ).fetchone()[0]
            if pending == 0:
                return
            time.sleep(POLL_INTERVAL)
            continue
        processed += 1
        attempt = job["attempts"] + 1
        print(f"[worker] picked up job {job['id']} (attempt {attempt})")

        # Load the payload once. The handler may mutate it
        # (e.g. increment `_calls`). We persist it back to the DB
        # after the handler runs — on both success and failure —
        # so the mutation survives a future retry. Without this,
        # `succeed_after_1` would never see its own prior attempt.
        payload = json.loads(job["payload"])
        try:
            HANDLERS[job["name"]](payload)
            conn.execute(
                "UPDATE jobs SET payload=?, updated_at=? WHERE id=?",
                (json.dumps(payload), time.time(), job["id"]),
            )
            finish(conn, job["id"], "succeeded")
            print("[worker]   succeeded")
        except Exception as e:
            conn.execute(
                "UPDATE jobs SET payload=?, updated_at=? WHERE id=?",
                (json.dumps(payload), time.time(), job["id"]),
            )
            fail(conn, job, str(e))


# ── 5. Demo ─────────────────────────────────────────────────
if __name__ == "__main__":
    conn = connect()

    print("[producer] enqueuing three jobs")
    j1 = enqueue(conn, "succeed_after_0", {})
    j2 = enqueue(conn, "succeed_after_1", {})
    j3 = enqueue(conn, "always_fail", {})
    print(f"[producer] enqueued jobs {j1}, {j2}, {j3}")
    print()

    print("[worker] starting")
    run_worker(conn)
    print()

    # Summary
    rows = conn.execute(
        "SELECT status, COUNT(*) c FROM jobs GROUP BY status"
    ).fetchall()
    summary = {r["status"]: r["c"] for r in rows}
    print("[summary] " + "  ".join(f"{k}: {v}" for k, v in sorted(summary.items())))
    print()

    # Show the final state of every job
    print("[final state]")
    for r in conn.execute("SELECT id, name, status, attempts FROM jobs ORDER BY id"):
        print(f"  job {r['id']} ({r['name']}): status={r['status']}, "
              f"attempts={r['attempts']}")


# ─────────────────────────────────────────────────────────────
# Exercise:
#   1. Run `python main.py`. Job 2 should fail once and succeed
#      on attempt 2 — that's at-least-once delivery.
#   2. Change DB_PATH to "jobs.db" and run twice. The second run
#      sees the previous run's jobs. That's why every job must be
#      idempotent: if the worker restarts, it reprocesses.
#   3. Add a handler `send_email` that raises on the first call
#      and succeeds on the second. Then add a `jobs_sent` table
#      and have send_email check it before sending. Now the job
#      is safe to run twice — that's idempotency in practice.
#   4. Change MAX_ATTEMPTS to 1. Job 2 now dead-letters on the
#      first failure — it can't retry.
#   5. Add a `priority` column and change `pull_one` to
#      `ORDER BY priority DESC, id`. High-priority jobs jump
#      the queue.
# ─────────────────────────────────────────────────────────────