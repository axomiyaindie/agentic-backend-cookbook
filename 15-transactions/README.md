# Transactions

A **transaction** groups several database operations so that **all of them
succeed, or none of them do**. There is no half-finished state.

## The one idea to take away

The canonical example is a money transfer. To move $100 from Alice to Bob:

```
1. UPDATE accounts SET balance = balance - 100 WHERE id = 'alice'
2. UPDATE accounts SET balance = balance + 100 WHERE id = 'bob'
```

If step 1 succeeds and step 2 fails (database crash, network error, power
loss, bug), Alice lost $100 and Bob got nothing. **Money vanished.**

A transaction wraps both statements so this can't happen:

```
BEGIN
  UPDATE accounts SET balance = balance - 100 WHERE id = 'alice'
  UPDATE accounts SET balance = balance + 100 WHERE id = 'bob'
COMMIT
```

If either UPDATE fails, the whole thing rolls back. Alice's $100 is
restored. Bob is untouched. The database returns to its prior state.

**This is the single most common thing AI-generated backend code forgets.**
An AI will happily write the two UPDATEs, one after the other, with no
transaction. It looks correct. It passes a quick test. It loses money the
first time the second UPDATE fails in production.

## Why this matters more for AI apps

AI backends do multi-step writes constantly:

| Operation | Steps that must all succeed |
|---|---|
| Charge a user | Reserve credit → record charge → update balance |
| Process a document | Mark as processing → store chunks → mark as done |
| Onboard a user | Create user → create their workspace → create their first project |
| Run an agent tool | Execute the tool → record the result → update the agent's memory |

If any of those fails halfway, the system ends up in an inconsistent state:
a user with no workspace, a document stuck at "processing" forever, an
agent that can't remember the tool it just ran.

The fix is always the same: **wrap the related writes in one transaction.**

## The two ways this lesson shows the bug

`01-fastapi-transaction/` has two endpoints:

- `POST /transfer/broken` — runs the two UPDATEs with no transaction.
  If you trigger the failure, Alice's money disappears.
- `POST /transfer/safe` — runs the two UPDATEs inside `BEGIN … COMMIT`.
  If you trigger the failure, nothing changes.

Both endpoints take `(from_id, to_id, amount)`. Both return 200 or 500.
The only difference is whether the second write is inside the transaction.

The exercise is designed to **trigger the failure on purpose** so you can
see the two behaviors side by side.

## What "ACID" actually means

You'll see the acronym everywhere. It's simpler than it sounds:

| Letter | Meaning | What it protects against |
|---|---|---|
| **A**tomicity | All or nothing | Half-finished transfers |
| **C**onsistency | Valid state → valid state | Breaking a constraint (e.g. balance going negative) |
| **I**solation | Concurrent transactions don't see each other's partial work | Two transfers interfering |
| **D**urability | Once committed, it survives a crash | Committed data disappearing |

The lesson focuses on **atomicity**, because that's the one an AI assistant
forgets most often. The other three are properties of the database, not
something you write.

## Lesson

`01-fastapi-transaction/` — a SQLite-backed FastAPI app with two endpoints:
- `POST /transfer/broken` — no transaction (the bug)
- `POST /transfer/safe` — transaction (the fix)

Plus a trigger mechanism so you can force the second write to fail
without actually breaking SQLite.

## Where this fits in real code

- **Postgres / MySQL** — `BEGIN`, `COMMIT`, `ROLLBACK`. In Python,
  `with conn.transaction():` in psycopg3, or `async with session.begin():`
  in SQLAlchemy.
- **MongoDB** — multi-document transactions (requires a replica set).
  `session.with_transaction(...)`.
- **DynamoDB** — `TransactWriteItems` for up to 25 items. Different
  API, same guarantee.
- **ORMs** — SQLAlchemy, Django's `transaction.atomic`, Prisma's
  `$transaction`, ActiveRecord's `transaction`.

Every one of them is the same concept: group the operations, commit or
roll back as a unit.

## What this lesson does not cover

- **Isolation levels.** The default (`READ COMMITTED` in Postgres) is
  usually fine. `SERIALIZABLE` prevents anomalies but costs performance.
  This is its own lesson.
- **Distributed transactions.** Two databases, one business operation.
  Much harder (2PC, sagas). Out of scope.
- **Idempotency keys.** If the client retries a transfer because the
  response was lost, the transfer should happen once. That's a different
  mechanism (`Idempotency-Key` header + a table of seen keys). Mentioned
  in `11-background-jobs`.
- **Deadlocks.** Two transactions waiting on each other's locks. The
  database detects and resolves them; your code should retry. Worth its
  own lesson.

The mechanism in this lesson — atomicity for related writes — is the
foundation all of them build on.

---

## In another language?

Every language that talks to a relational database has transactions. The
API is slightly different, but the concept is identical:

| Language | The transaction |
|---|---|
| Python (psycopg3) | `with conn.transaction():` |
| Python (SQLAlchemy) | `async with session.begin():` |
| Python (Django) | `with transaction.atomic():` |
| Go (database/sql) | `tx, _ := db.Begin(); ... tx.Commit()` |
| Rust (sqlx) | `let mut tx = pool.begin().await?; tx.commit().await?` |
| Node (Prisma) | `prisma.$transaction([...])` |
| Node (Knex) | `knex.transaction(async trx => { ... })` |
| PHP (PDO) | `$db->beginTransaction(); $db->commit()` |
| Ruby (ActiveRecord) | `ActiveRecord::Base.transaction { ... }` |
| Java (JDBC) | `conn.setAutoCommit(false); ... conn.commit()` |
| C# (EF Core) | `using var tx = db.Database.BeginTransaction()` |

If your language is missing from this list, it's because there's no popular
library — the raw database driver always supports `BEGIN`, `COMMIT`,
`ROLLBACK`. The concept is universal.