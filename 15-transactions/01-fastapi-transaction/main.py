# ─────────────────────────────────────────────────────────────
# Lesson: transactions in FastAPI (SQLite)
#
# Two endpoints that do the same transfer:
#   POST /transfer/broken  -> no transaction (the bug)
#   POST /transfer/safe    -> BEGIN ... COMMIT (the fix)
#
# The `?fail=1` query parameter forces the second write to fail,
# so you can see what happens when a multi-step write dies halfway.
#
# Without a transaction: the debit persists, the credit doesn't.
# Without a transaction: money vanishes.
#
# With a transaction: both writes are rolled back. Nothing changes.
# ─────────────────────────────────────────────────────────────

import sqlite3
from pathlib import Path

from fastapi import FastAPI, HTTPException

app = FastAPI(title="Transaction lesson")

DB_PATH = Path(__file__).parent / "transactions.db"


# ── Database setup ──────────────────────────────────────────
def _connect() -> sqlite3.Connection:
    # isolation_level=None disables Python's implicit transaction
    # handling, so we control BEGIN / COMMIT / ROLLBACK ourselves.
    # Without this, Python opens an implicit transaction and you
    # can't tell the bug from the fix.
    conn = sqlite3.connect(DB_PATH, isolation_level=None)
    conn.row_factory = sqlite3.Row
    return conn


def _init_db():
    with _connect() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS accounts (
                id      TEXT PRIMARY KEY,
                balance INTEGER NOT NULL
            );
        """)
        conn.execute("INSERT OR IGNORE INTO accounts VALUES ('alice', 100)")
        conn.execute("INSERT OR IGNORE INTO accounts VALUES ('bob',   50)")


_init_db()


def _reset_balances():
    with _connect() as conn:
        conn.execute("UPDATE accounts SET balance = 100 WHERE id = 'alice'")
        conn.execute("UPDATE accounts SET balance =  50 WHERE id = 'bob'")


def _get_balance(conn: sqlite3.Connection, account_id: str) -> int:
    row = conn.execute(
        "SELECT balance FROM accounts WHERE id = ?", (account_id,)
    ).fetchone()
    if row is None:
        raise HTTPException(404, f"no such account: {account_id}")
    return row[0]


def _simulate_failure(should_fail: bool, label: str):
    """Trigger a failure after the debit, to test the two paths."""
    if should_fail:
        raise RuntimeError(f"simulated failure after debit ({label})")


# ── The broken endpoint: no transaction ────────────────────
# If the second UPDATE fails, the first one is already committed.
# Money leaves one account and never arrives at the other.
@app.post("/transfer/broken")
def transfer_broken(from_id: str, to_id: str, amount: int, fail: bool = False):
    conn = _connect()
    try:
        # Read current balances (for the response).
        from_before = _get_balance(conn, from_id)
        to_before = _get_balance(conn, to_id)

        # Debit (UPDATE 1). Autocommits immediately.
        conn.execute(
            "UPDATE accounts SET balance = balance - ? WHERE id = ?",
            (amount, from_id),
        )

        # Failure point: if this raises, UPDATE 1 is already on disk.
        _simulate_failure(fail, "the bug")

        # Credit (UPDATE 2). Only runs if the failure didn't happen.
        conn.execute(
            "UPDATE accounts SET balance = balance + ? WHERE id = ?",
            (amount, to_id),
        )

        return {
            "status": "ok",
            "from": {"id": from_id, "before": from_before, "after": from_before - amount},
            "to":   {"id": to_id,   "before": to_before,   "after":  to_before + amount},
            "note": "no transaction — both writes happened",
        }
    finally:
        conn.close()


# ── The safe endpoint: inside a transaction ────────────────
# Both UPDATEs are inside BEGIN ... COMMIT. If either fails, the
# whole thing rolls back. No half-finished state.
@app.post("/transfer/safe")
def transfer_safe(from_id: str, to_id: str, amount: int, fail: bool = False):
    conn = _connect()
    try:
        from_before = _get_balance(conn, from_id)
        to_before = _get_balance(conn, to_id)

        conn.execute("BEGIN")
        try:
            conn.execute(
                "UPDATE accounts SET balance = balance - ? WHERE id = ?",
                (amount, from_id),
            )

            # Failure point: if this raises, the ROLLBACK below
            # undoes the debit. Nothing persists.
            _simulate_failure(fail, "safe endpoint - rolled back")

            conn.execute(
                "UPDATE accounts SET balance = balance + ? WHERE id = ?",
                (amount, to_id),
            )

            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            raise

        return {
            "status": "ok",
            "from": {"id": from_id, "before": from_before, "after": from_before - amount},
            "to":   {"id": to_id,   "before": to_before,   "after":  to_before + amount},
            "note": "transaction — both writes or neither",
        }
    finally:
        conn.close()


# ── Debug endpoints ────────────────────────────────────────
@app.get("/balances")
def balances():
    with _connect() as conn:
        rows = conn.execute("SELECT id, balance FROM accounts ORDER BY id").fetchall()
    return {r["id"]: r["balance"] for r in rows}


@app.post("/reset")
def reset():
    _reset_balances()
    return {"status": "reset"}


# ─────────────────────────────────────────────────────────────
# Exercise:
#   1. Start the server:
#        pip install -r requirements.txt
#        uvicorn main:app --reload --port 8015
#   2. Confirm the baseline:
#        curl http://127.0.0.1:8015/balances
#        -> {"alice":100, "bob":50}
#   3. The bug — no transaction, forced failure:
#        curl "http://127.0.0.1:8015/transfer/broken?from_id=alice&to_id=bob&amount=30&fail=1"
#        -> 500 error
#        curl http://127.0.0.1:8015/balances
#        -> {"alice":70, "bob":50}   (alice lost 30, bob gained 0)
#   4. Reset and try the fix:
#        curl -X POST http://127.0.0.1:8015/reset
#        curl "http://127.0.0.1:8015/transfer/safe?from_id=alice&to_id=bob&amount=30&fail=1"
#        -> 500 error
#        curl http://127.0.0.1:8015/balances
#        -> {"alice":100, "bob":50}   (nothing changed — rolled back)
#   5. Now break the fix: remove the `conn.execute("ROLLBACK")`
#      line from transfer_safe. Run step 4 again. The debit now
#      persists. That's why the ROLLBACK is not optional.
# ─────────────────────────────────────────────────────────────