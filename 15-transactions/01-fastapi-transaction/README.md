# FastAPI transaction

Two endpoints that do the same transfer, one without a transaction (the
bug) and one with (the fix). The `?fail=1` query parameter forces the
second write to fail, so you can see the difference.

## What you'll learn
- What a transaction protects against
- Why "two writes in a row" is not the same as "two writes atomically"
- How to wrap related writes in `BEGIN … COMMIT` with SQLite
- Why the failure case is the case that matters

## How to run
```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8015
```

Using port 8015. The database is created automatically on first request.

## What to look at
- `main.py` — read `transfer_broken` first, then `transfer_safe`. The
  difference is three lines: `BEGIN`, `COMMIT`, and the `try/except`
  that calls `ROLLBACK`.
- `_simulate_failure()` — the function that makes the second write fail
  when `?fail=1` is set. This stands in for a real production failure
  (network error, constraint violation, process crash).

## The setup

Every request to `/transfer/*` starts with the same seed data:
- Alice has $100
- Bob has $50

Transfer $30 from Alice to Bob. If it succeeds:
- Alice has $70
- Bob has $80

If it half-succeeds (only the debit): Alice has $70, Bob has $50 — **$30 vanished.**

If it half-succeeds (only the credit): Alice has $100, Bob has $80 — **$30 appeared from nowhere.**

## Walkthrough — prove it works

**Step 1: Start the server**

```powershell
cd D:\agentic-backend-cookbook\15-transactions\01-fastapi-transaction
pip install -r requirements.txt
uvicorn main:app --reload --port 8015
```

**Step 2: The happy path (both endpoints)**

```powershell
# Reset balances and check
curl.exe http://127.0.0.1:8015/balances

# Transfer that succeeds (no ?fail=1)
curl.exe "http://127.0.0.1:8015/transfer/broken?from_id=alice&to_id=bob&amount=30"
curl.exe http://127.0.0.1:8015/balances
# Alice: 70, Bob: 80
```

Both endpoints succeed on the happy path. The difference only appears
when something goes wrong.

**Step 3: The bug — no transaction, forced failure**

```powershell
curl.exe "http://127.0.0.1:8015/transfer/broken?from_id=alice&to_id=bob&amount=30&fail=1"
```

Response: **500 Internal Server Error**
```json
{"detail":"simulated failure after debit (the bug)"}
```

Now check the balances:

```powershell
curl.exe http://127.0.0.1:8015/balances
```

Expected:
```json
{"alice": 70, "bob": 50}
```

**Look at that.** Alice lost $30. Bob gained nothing. **$30 has vanished
from the system.** That is what happens when a multi-step write is not
wrapped in a transaction.

**Step 4: The fix — transaction, forced failure**

First, reset:

```powershell
curl.exe -X POST http://127.0.0.1:8015/reset
curl.exe http://127.0.0.1:8015/balances
# Alice: 100, Bob: 50
```

Now trigger the same failure, but on the transactional endpoint:

```powershell
curl.exe "http://127.0.0.1:8015/transfer/safe?from_id=alice&to_id=bob&amount=30&fail=1"
```

Response: **500 Internal Server Error** (the failure still happens)
```json
{"detail":"simulated failure after debit (safe endpoint - rolled back)"}
```

But now check the balances:

```powershell
curl.exe http://127.0.0.1:8015/balances
```

Expected:
```json
{"alice": 100, "bob": 50}
```

**Nothing changed.** Alice still has $100. Bob still has $50. The
transaction was rolled back when the failure hit — the debit was undone.

**That's the entire lesson.** Same failure, different outcome, because
one endpoint wrapped the writes in a transaction and the other didn't.

## Why the failure simulation matters

Without the `?fail=1` option, both endpoints would always succeed, and
the transaction would look unnecessary. The point of the lesson is not
that transactions make good code work — it's that they make **good code
survive bad days**.

The failure you simulate here (`_simulate_failure()`) stands in for:

- **Network error** between your app and the database after the first UPDATE
- **Constraint violation** on the second UPDATE (e.g. balance would go negative)
- **Process crash** mid-request (your app dies between UPDATE 1 and UPDATE 2)
- **Timeout** — the second write is too slow and the DB drops the connection

All of those happen in production. **None of them are caught by unit tests
that always succeed.** The only defense is the transaction.

## How the transaction looks in the code

```python
conn.execute("BEGIN")
try:
    conn.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (amount, from_id))
    conn.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (amount, to_id))
    conn.execute("COMMIT")
except Exception:
    conn.execute("ROLLBACK")
    raise
```

That's it. Three lines different from the broken version. **Three lines
stand between a working system and a money-losing one.**

## What SQLite specifically does

SQLite auto-commits every statement by default. That's why the broken
endpoint's first UPDATE persists even though the request fails. To get
transactional behavior, you must explicitly `BEGIN` and `COMMIT`.

Postgres and MySQL have the same default (`autocommit = true` for most
drivers). The fix is the same: wrap the related writes.

## What this example deliberately skips

- **Isolation levels.** SQLite's `BEGIN` uses serializable isolation by
  default (the strictest). Postgres defaults to `READ COMMITTED`. Both
  prevent the bug this lesson demonstrates; they differ for more subtle
  concurrency cases.
- **Distributed transactions.** Real money movement often spans two
  services. Atomicity across services requires 2PC or sagas — out of scope.
- **Idempotency.** If the client retries a transfer that succeeded, you
  get two transfers. That needs an `Idempotency-Key` header and a
  `seen_keys` table. Out of scope; mentioned in `11-background-jobs`.
- **Connection pooling.** Each request opens a new SQLite connection.
  Production uses a pool. The transaction semantics are identical.

---

## In another language?

The transaction pattern is the same everywhere. The API is what changes:

| Language | How to run a transaction |
|---|---|
| Python (SQLite) | `conn.execute("BEGIN")` … `conn.commit()` |
| Python (psycopg3) | `with conn.transaction():` |
| Python (SQLAlchemy) | `async with session.begin():` |
| Go (database/sql) | `tx, _ := db.Begin(); ...; tx.Commit()` |
| Rust (sqlx) | `let mut tx = pool.begin().await?; tx.commit().await?` |
| Node (Prisma) | `prisma.$transaction(async (tx) => { ... })` |
| Ruby (ActiveRecord) | `ActiveRecord::Base.transaction { ... }` |
| Java (JDBC) | `conn.setAutoCommit(false); ...; conn.commit()` |
| C# (EF Core) | `using var tx = db.Database.BeginTransaction()` |

Every one of them does the same thing: group operations, commit or roll
back as a unit. If you understand why the lesson's `/transfer/broken`
loses money, you understand transactions in any language.