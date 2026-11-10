# ─────────────────────────────────────────────────────────────
# Lesson: webhook receiver with HMAC verification
#
# The whole mechanism:
#   1. Read the RAW body (before JSON parsing).
#   2. Compute HMAC-SHA256(secret, raw_body).
#   3. Compare to the X-Signature header (constant time).
#   4. Reject if missing or wrong (401).
#   5. Look up the event ID — reject as duplicate if seen.
#   6. Store the event, return 200 immediately.
#
# The signature proves the request came from a sender who knows
# the shared secret. Without it, anyone on the internet can POST
# a "charge.succeeded" event and trigger your business logic.
# ─────────────────────────────────────────────────────────────

import hashlib
import hmac
import json
import os
import sqlite3
import time
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException, Request

app = FastAPI(title="Webhook lesson")

# In production: os.environ["WEBHOOK_SECRET"]. Hardcoding here so the
# lesson runs with no setup.
SECRET = os.environ.get("WEBHOOK_SECRET", "dev-secret").encode()

DB_PATH = Path(__file__).parent / "webhooks.db"


# ── Database setup ──────────────────────────────────────────
def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, isolation_level=None)
    conn.row_factory = sqlite3.Row
    return conn


def _init_db():
    with _connect() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS seen_events (
                event_id    TEXT PRIMARY KEY,
                event_type  TEXT NOT NULL,
                payload     TEXT NOT NULL,
                received_at REAL NOT NULL
            );
        """)


_init_db()


# ── The webhook endpoint ────────────────────────────────────
@app.post("/webhook")
async def webhook(
    request: Request,
    x_signature: str | None = Header(default=None, alias="X-Signature"),
):
    # 1. Missing signature = reject immediately. No work, no lookups.
    if not x_signature:
        raise HTTPException(401, "missing signature")

    # 2. Read the RAW bytes. NOT request.json() — re-serializing
    #    changes whitespace and key order, and the HMAC would
    #    never match. This is the single most common webhook bug.
    body = await request.body()

    # 3. Compute the expected HMAC.
    expected = hmac.new(SECRET, body, hashlib.sha256).hexdigest()

    # 4. Compare in constant time. Plain `==` leaks timing info
    #    through the position of the first mismatch.
    if not hmac.compare_digest(expected, x_signature):
        raise HTTPException(401, "invalid signature")

    # 5. Parsing the JSON is safe now that we know the body is
    #    authentic. If it's malformed, that's the sender's bug —
    #    reject with 400.
    try:
        event = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(400, "invalid json")

    event_id = event.get("id")
    event_type = event.get("type")
    if not event_id or not event_type:
        raise HTTPException(400, "missing id or type")

    # 6. Idempotency: providers retry. The same event arrives more
    #    than once. If we've seen this ID, return 200 without
    #    doing the work again.
    with _connect() as conn:
        row = conn.execute(
            "SELECT event_id FROM seen_events WHERE event_id = ?",
            (event_id,),
        ).fetchone()
        if row is not None:
            return {"status": "ok", "event_id": event_id, "duplicate": True}

        # 7. Store the event. In a real receiver, this would enqueue
        #    a background job (see 11-background-jobs/) and return
        #    immediately. Slow work in the request handler causes
        #    provider timeouts and duplicate deliveries.
        conn.execute(
            "INSERT INTO seen_events (event_id, event_type, payload, received_at) "
            "VALUES (?, ?, ?, ?)",
            (event_id, event_type, json.dumps(event), time.time()),
        )

    return {"status": "ok", "event_id": event_id, "duplicate": False}


# ── Debug endpoints ────────────────────────────────────────
@app.get("/events")
def list_events():
    with _connect() as conn:
        rows = conn.execute(
            "SELECT event_id, event_type, received_at FROM seen_events "
            "ORDER BY received_at"
        ).fetchall()
    return [dict(r) for r in rows]


@app.post("/reset")
def reset():
    with _connect() as conn:
        conn.execute("DELETE FROM seen_events")
    return {"status": "reset"}


# ─────────────────────────────────────────────────────────────
# Exercise:
#   1. Start the server:
#        pip install -r requirements.txt
#        uvicorn main:app --reload --port 8018
#   2. Send a valid webhook (see the README for the sender script).
#      Expected: {"status":"ok","event_id":"evt_001","duplicate":false}
#   3. Send the SAME event again. Expected: duplicate:true, and
#      GET /events still shows one row.
#   4. Send with a wrong signature. Expected: 401 invalid signature.
#   5. Send with NO signature. Expected: 401 missing signature.
#   6. Change SECRET to "different-secret" and restart. Now send
#      the original request again. It fails with 401, because the
#      signature was computed with the old secret. That's the
#      point: the signature is only valid for one secret.
#   7. Look at the code and find the line:
#        body = await request.body()
#      Try changing it to:
#        body = json.dumps(await request.json()).encode()
#      Now every valid request fails with 401. That's the
#      "re-serialize the body" bug. Confirm it, then change it back.
# ─────────────────────────────────────────────────────────────