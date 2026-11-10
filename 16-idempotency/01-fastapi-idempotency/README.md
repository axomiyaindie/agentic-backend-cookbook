# FastAPI idempotency

A `/charge` endpoint protected by the `Idempotency-Key` header pattern.
Send the same key three times, and the user is charged exactly once.

## What you'll learn
- How the `Idempotency-Key` header short-circuits a retried request
- What the `seen_keys` table stores (and why the response body is in it)
- Why `in_progress` is a state (and why it returns 409)
- Why this is the other half of the transaction story

## How to run
```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8016
```

Using port 8016. The database is created on first request.

## What to look at
- `main.py` — read `charge()` first. It's the whole lesson in ~30 lines:
  1. Read `Idempotency-Key` header (reject if missing)
  2. Look up the key in `seen_keys`
  3. If `completed` → return the stored response **verbatim**
  4. If `in_progress` → return 409 Conflict
  5. Otherwise → run the charge, store the response, return it
- `_do_charge()` — the actual (fake) charge logic. Kept separate so the
  idempotency layer is visible.

## Walkthrough — prove it works

> **Windows note:** `curl.exe` with a JSON body fails in PowerShell,
> because PowerShell strips the quotes before curl sees them. The result
> is a `JSON decode error` from FastAPI, not a problem with the server.
> Use `Invoke-RestMethod` for requests with JSON bodies. It's a native
> PowerShell cmdlet and handles JSON correctly.
>
> Simple GETs still work fine with `curl.exe`.

**Step 1: Start the server**

```powershell
cd D:\agentic-backend-cookbook\16-idempotency\01-fastapi-idempotency
pip install -r requirements.txt
uvicorn main:app --reload --port 8016
```

**Step 2: Baseline**

```powershell
curl.exe -s http://127.0.0.1:8016/charges
```

Expected: `[]` — no charges yet.

**Step 3: Charge once with a key**

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8016/charge `
  -ContentType "application/json" `
  -Headers @{"Idempotency-Key"="demo-key-1"} `
  -Body '{"amount": 50, "user": "alice"}'
```

Expected:
```json
{"status":"charged","charge_id":1,"amount":50,"user":"alice"}
```

Check the charges table:

```powershell
curl.exe -s http://127.0.0.1:8016/charges
```

Expected: **one** charge.

**Step 4: Retry with the SAME key (the whole point)**

Send **exactly the same request** again:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8016/charge `
  -ContentType "application/json" `
  -Headers @{"Idempotency-Key"="demo-key-1"} `
  -Body '{"amount": 50, "user": "alice"}'
```

Expected: **the exact same response** — same `charge_id` as Step 3:
```json
{"status":"charged","charge_id":1,"amount":50,"user":"alice"}
```

But now check the charges table:

```powershell
curl.exe -s http://127.0.0.1:8016/charges
```

Expected: **still one charge.** The server did **not** run the handler
again — it returned the stored response. Without idempotency, this step
would have created a second charge and the user would be billed twice.

**Step 5: Send again with a NEW key**

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8016/charge `
  -ContentType "application/json" `
  -Headers @{"Idempotency-Key"="demo-key-2"} `
  -Body '{"amount": 50, "user": "alice"}'
```

Expected:
```json
{"status":"charged","charge_id":2,"amount":50,"user":"alice"}
```

Now the charges table has **two** charges. Same body, different key. The
server treated it as a new operation.

**Step 6: Send without any key**

```powershell
try {
  Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8016/charge `
    -ContentType "application/json" `
    -Body '{"amount": 50, "user": "alice"}'
} catch {
  $_.Exception.Response.StatusCode.value__
  $_.ErrorDetails.Message
}
```

Expected:
```text
400
{"detail":"missing Idempotency-Key header"}
```

**That's the difference between "safe by default" and "safe if the client
remembers".** Requiring the header turns a client bug into a clear error
message, not a silent double-charge.

**Step 7: Inspect the key table**

```powershell
curl.exe -s http://127.0.0.1:8016/keys
```

Expected: two keys, both `completed`:
```json
[{"key":"demo-key-1","status":"completed"},{"key":"demo-key-2","status":"completed"}]
```

## The three lines that matter

```python
existing = get_key(idempotency_key)
if existing and existing["status"] == "completed":
    return existing["response"]                    # ← the fix
```

Three lines. Delete them and Step 4 charges the user twice. Keep them and
the retry is harmless.

## Why store the response body, not just the key

If a client retries, it expects the **same response**. Not a different
response. If a request with key `demo-key-1` originally returned:

```json
{"status":"charged","charge_id":1,"amount":50,"user":"alice"}
```

…then a retry must return that same `charge_id: 1`. If instead you only
stored the key and returned an error like `"already processed"`, the
client doesn't know what actually happened — it has to do a separate GET
to check.

Storing the **full response** means the retry is transparent. The client
can't tell whether its first attempt succeeded or its retry did. That's
the goal: **retries become invisible.**

## The four states of a key

| State | Meaning | What a retry sees |
|---|---|---|
| *(absent)* | First time for this key | Handler runs, response stored, returned |
| `in_progress` | A request with this key is currently running | 409 Conflict |
| `completed` | A prior request succeeded | Stored response returned verbatim |
| `failed` | A prior request errored | Key is cleared, request runs again |

`in_progress` handles **concurrent** retries — the client (or a retry
library) fires two requests within milliseconds. Only one can win.

`failed` handles **recoverable** errors — if the first attempt hit a
transient DB error, the retry should try again. This lesson doesn't
demonstrate failure-recovery (it would need a second failure flag), but
the code path exists and is one line.

## What this example deliberately skips

- **Concurrent requests with the same key.** This lesson returns 409 for
  `in_progress` but does not hold a lock. A second request with the same
  key while the first is still running gets a 409 immediately — it doesn't
  wait. Stripe's implementation actually waits up to 24 hours. Both are
  valid; waiting is more complex.
- **Key expiry.** `seen_keys` grows forever. Production deletes rows
  after 24 hours.
- **Body hashing.** If the client reuses a key with a different body, this
  lesson still returns the stored response. Stripe checks the body hash
  and returns 422 if it differs. This prevents a client bug from silently
  charging the wrong amount.
- **Response truncation.** If the stored response is large, the `response`
  column grows. Stripe truncates to a fixed size. This lesson stores the
  full body.
- **Cross-process locking.** SQLite's row lock is enough for this lesson.
  Postgres would use a unique constraint + `SELECT ... FOR UPDATE`;
  Redis would use `SET key NX EX 86400`.

Each of those is a lesson of its own. The mechanism in this lesson — key,
lookup, store, return — is the seed of all of them.

## Testing note: why not `curl.exe`?

On Windows PowerShell, this:

```powershell
curl.exe -X POST ... -d '{\"amount\":50}'
```

does **not** send the JSON you expect. PowerShell strips the inner quotes
before passing the string to `curl.exe`, so FastAPI sees `{amount:50}`
and returns `{"type":"json_invalid","msg":"JSON decode error"}`.

Three things that **do** work:

1. `Invoke-RestMethod` (used above) — the idiomatic PowerShell client.
2. `curl.exe --data-raw "{\`"amount\`":50}"` — escaping **with backticks**,
   not backslashes. Ugly but works.
3. Running from `cmd.exe` or Git Bash instead of PowerShell.

This lesson uses `Invoke-RestMethod` because it's the clearest, and it
works on every Windows PowerShell version.

---

## In another language?

The pattern is identical. The storage backend changes, and the framework
hook changes, but the four steps are the same:

| Language | Storage backend | Hook |
|---|---|---|
| Python (FastAPI) | SQLite in this lesson | A `Depends` or a plain function |
| Go | `database/sql` | A middleware that wraps `http.Handler` |
| Rust | `sqlx` | An extractor that runs before the handler |
| Node (Express) | Prisma / Knex | `app.use()` middleware |
| Node (Fastify) | Prisma | `preHandler` hook |
| Ruby (Rails) | ActiveRecord | `before_action` in a controller |
| Java (Spring) | JDBC | A `HandlerInterceptor` |
| C# (ASP.NET) | EF Core | An `IAsyncActionFilter` |

Every one of them does the same four steps. If you understand why the
lesson's step 4 charges the user once, you understand idempotency in any
language.