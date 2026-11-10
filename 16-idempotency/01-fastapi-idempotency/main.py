# ─────────────────────────────────────────────────────────────
# Lesson: idempotency in FastAPI (SQLite)
#
# The problem: a client sends "charge $50", the server charges the
# card, and the response is lost. The client retries. Without
# idempotency, the user is charged $100.
#
# The fix: the client sends an Idempotency-Key header. The server
# looks it up in `seen_keys`:
#   - completed  -> return the STORED response, do NOT run again
#   - in_progress -> return 409 (a concurrent duplicate is running)
#   - failed     -> clear the key and run the handler again
#   - absent     -> run the handler, store the response
#
# Every retry with the same key returns the same response, and the
# handler only runs once.
# ─────────────────────────────────────────────────────────────

import json
import sqlite3
import time
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Response
from pydantic import BaseModel

app = FastAPI(title="Idempotency lesson")

DB_PATH = Path(__file__).parent / "idempotency.db"


# ── Database setup ──────────────────────────────────────────
def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, isolation_level=None)
    conn.row_factory = sqlite3.Row
    return conn


def _init_db():
    with _connect() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS seen_keys (
                key         TEXT PRIMARY KEY,
                status      TEXT NOT NULL,
                response    TEXT,
                created_at  REAL NOT NULL
            );
            CREATE TABLE IF NOT EXISTS charges (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user       TEXT NOT NULL,
                amount     INTEGER NOT NULL,
                created_at REAL NOT NULL
            );
        """)


_init_db()


# ── Request / response models ───────────────────────────────
class ChargeRequest(BaseModel):
    amount: int
    user: str


# ── The actual charge logic (the thing we want to run once) ─
def _do_charge(req: ChargeRequest) -> dict[str, Any]:
    with _connect() as conn:
        cur = conn.execute(
            "INSERT INTO charges (user, amount, created_at) VALUES (?, ?, ?)",
            (req.user, req.amount, time.time()),
        )
        charge_id = cur.lastrowid
    return {
        "status": "charged",
        "charge_id": charge_id,
        "amount": req.amount,
        "user": req.user,
    }


# ── Idempotent endpoint ─────────────────────────────────────
@app.post("/charge")
def charge(
    body: ChargeRequest,
    response: Response,
    idempotency_key: str | None = Header(default=None),
):
    # 1. Require the key. Missing key = clear client error.
    if not idempotency_key:
        raise HTTPException(400, "missing Idempotency-Key header")

    with _connect() as conn:
        # 2. Look up the key.
        row = conn.execute(
            "SELECT status, response FROM seen_keys WHERE key = ?",
            (idempotency_key,),
        ).fetchone()

        if row is not None:
            if row["status"] == "completed":
                # 3a. Already done. Return the stored response verbatim.
                response.headers["Idempotent-Replayed"] = "true"
                return json.loads(row["response"])

            if row["status"] == "in_progress":
                # 3b. A concurrent duplicate is running. Reject.
                raise HTTPException(
                    409,
                    "a request with this Idempotency-Key is already in progress",
                )

            # 3c. Previous attempt failed. Delete and retry.
            conn.execute(
                "DELETE FROM seen_keys WHERE key = ?",
                (idempotency_key,),
            )

        # 4. Claim the key as in_progress.
        try:
            conn.execute(
                "INSERT INTO seen_keys (key, status, created_at) VALUES (?, ?, ?)",
                (idempotency_key, "in_progress", time.time()),
            )
        except sqlite3.IntegrityError:
            # Someone else claimed it between our read and our write.
            raise HTTPException(409, "a request with this Idempotency-Key is already in progress")

    # 5. Run the real work.
    try:
        result = _do_charge(body)
    except Exception as e:
        # 6a. Handler failed. Mark the key failed so a retry can proceed.
        with _connect() as conn:
            conn.execute(
                "UPDATE seen_keys SET status = 'failed' WHERE key = ?",
                (idempotency_key,),
            )
        raise HTTPException(500, f"charge failed: {e}")

    # 6b. Handler succeeded. Store the response and mark completed.
    with _connect() as conn:
        conn.execute(
            "UPDATE seen_keys SET status = 'completed', response = ? WHERE key = ?",
            (json.dumps(result), idempotency_key),
        )

    return result


# ── Debug endpoints ────────────────────────────────────────
@app.get("/charges")
def list_charges():
    with _connect() as conn:
        rows = conn.execute(
            "SELECT id, user, amount FROM charges ORDER BY id"
        ).fetchall()
    return [{"id": r["id"], "user": r["user"], "amount": r["amount"]} for r in rows]


@app.get("/keys")
def list_keys():
    with _connect() as conn:
        rows = conn.execute(
            "SELECT key, status, created_at FROM seen_keys ORDER BY created_at"
        ).fetchall()
    return [{"key": r["key"], "status": r["status"]} for r in rows]


@app.post("/reset")
def reset():
    with _connect() as conn:
        conn.execute("DELETE FROM charges")
        conn.execute("DELETE FROM seen_keys")
    return {"status": "reset"}


# ─────────────────────────────────────────────────────────────
# Exercise:
#   1. Start the server:
#        pip install -r requirements.txt
#        uvicorn main:app --reload --port 8016
#   2. Send a charge:
#        curl -X POST http://127.0.0.1:8016/charge \
#          -H "Content-Type: application/json" \
#          -H "Idempotency-Key: demo-key-1" \
#          -d '{"amount":50,"user":"alice"}'
#      Response: {"status":"charged","charge_id":1,...}
#   3. Send the SAME request again (same key, same body):
#      Same response, but check /charges:
#        curl http://127.0.0.1:8016/charges
#      Only ONE charge exists. The handler did not run again.
#   4. Send the same body with a NEW key ("demo-key-2"):
#      A SECOND charge now exists. Different key = new operation.
#   5. Send without any key:
#      HTTP 400 "missing Idempotency-Key header". Safe by default.
#   6. Look at /keys: you'll see the two keys and their states.
#      Both are "completed".
#   7. Delete the idempotency.db file and restart the server.
#      Now send the same key as before. Because the DB is gone,
#      the key is treated as new — the user is charged again.
#      That's why "the server must persist seen_keys somewhere
#      that survives restarts" (Redis, Postgres). SQLite on disk
#      is fine for a single server; production uses a shared store.
# ─────────────────────────────────────────────────────────────