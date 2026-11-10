# FastAPI webhook receiver

A receiver that verifies an HMAC-SHA256 signature over the **raw body**,
deduplicates on the event ID, and returns 200 without doing slow work in
the request.

## What you'll learn
- Why the **raw body** is the only correct input to the HMAC
- How to compute and compare the signature in constant time
- How to deduplicate retried deliveries with the event ID
- Why the receiver should return 200 immediately, not after doing the work

## How to run
```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8018
```

Using port 8018. The shared secret is `dev-secret` (in `main.py`). Real
deployments load it from an environment variable.

## What to look at
- `main.py` — the whole lesson is in `/webhook`:
  1. `body = await request.body()` — **raw bytes**, before JSON parsing
  2. `expected = hmac.new(SECRET, body, sha256).hexdigest()`
  3. `hmac.compare_digest(expected, received)` — constant-time compare
  4. Look up the event ID in `seen_events` — reject duplicates
  5. Store the event, return 200

## Walkthrough — prove it works

**Step 1: Start the server**

```powershell
cd D:\agentic-backend-cookbook\18-webhooks\01-fastapi-webhook
pip install -r requirements.txt
uvicorn main:app --reload --port 8018
```

**Step 2: Send a valid webhook**

Save this small sender script as `send.py` in the same folder, or run it
inline. It computes the correct HMAC and POSTs it:

```powershell
python -c @"
import hashlib, hmac, json, urllib.request
body = json.dumps({'id': 'evt_001', 'type': 'charge.succeeded', 'amount': 500}).encode()
sig = hmac.new(b'dev-secret', body, hashlib.sha256).hexdigest()
req = urllib.request.Request(
    'http://127.0.0.1:8018/webhook', data=body,
    headers={'Content-Type': 'application/json', 'X-Signature': sig},
    method='POST')
print(urllib.request.urlopen(req).read().decode())
"@
```

Expected:
```json
{"status":"ok","event_id":"evt_001","duplicate":false}
```

**Step 3: Send the same event again (retry)**

Run the same command again. Expected:
```json
{"status":"ok","event_id":"evt_001","duplicate":true}
```

The receiver returned 200 both times — because providers expect 200 on
retries — but it only did the work once. That's idempotency at the webhook
layer.

**Step 4: Send with a wrong signature**

```powershell
python -c @"
import json, urllib.request
body = json.dumps({'id': 'evt_002', 'type': 'charge.succeeded', 'amount': 500}).encode()
req = urllib.request.Request(
    'http://127.0.0.1:8018/webhook', data=body,
    headers={'Content-Type': 'application/json', 'X-Signature': 'wrong-signature'},
    method='POST')
try:
    urllib.request.urlopen(req)
except urllib.error.HTTPError as e:
    print(e.code, e.read().decode())
"@
```

Expected:
```text
401 {"detail":"invalid signature"}
```

**The receiver rejected the request before doing anything.** No event was
stored. That's the whole point of verification: it happens *first*.

**Step 5: Send without a signature**

```powershell
python -c @"
import json, urllib.request
body = json.dumps({'id': 'evt_003', 'type': 'charge.succeeded', 'amount': 500}).encode()
req = urllib.request.Request(
    'http://127.0.0.1:8018/webhook', data=body,
    headers={'Content-Type': 'application/json'},
    method='POST')
try:
    urllib.request.urlopen(req)
except urllib.error.HTTPError as e:
    print(e.code, e.read().decode())
"@
```

Expected:
```text
401 {"detail":"missing signature"}
```

## Why the raw body matters (the gotcha that bites everyone)

This is wrong:

```python
data = await request.json()                     # parsed dict
body = json.dumps(data).encode()                # re-serialized
sig = hmac.new(SECRET, body, sha256).hexdigest()
```

The re-serialized `body` will not equal the original bytes. JSON is not
canonical: key order, whitespace, and number formatting can change. The
signature computed on the original bytes will not match a signature
computed on re-serialized bytes.

The fix:

```python
body = await request.body()                     # raw bytes
sig = hmac.new(SECRET, body, sha256).hexdigest()
data = json.loads(body)                         # parse AFTER verifying
```

**Compute the HMAC first, parse second.** That's the rule. It applies to
every provider — Stripe, GitHub, Slack, Square — because they all sign the
exact bytes they send.

## Why constant-time comparison matters

```python
if expected == received:      # WRONG
    ...
```

A plain `==` compares byte by byte and returns at the first difference.
That timing difference leaks information: an attacker can measure how many
bytes of their forged signature matched the expected one, and guess the
signature one byte at a time.

```python
if hmac.compare_digest(expected, received):   # RIGHT
    ...
```

`compare_digest` always takes the same time regardless of where the
mismatch is. For HMAC comparison specifically, that closes the timing
side-channel.

In practice, both are fine in a fast network and an HMAC with a strong
secret. But `compare_digest` is one character longer to type and
categorically correct. Use it.

## Why the receiver returns 200 immediately

If the webhook does slow work (call an API, write to a database) before
returning, the provider may time out. Then it retries. Then you do the work
twice.

The correct shape:

```python
# 1. Verify (fast)
# 2. Enqueue a background job with the event ID
# 3. Return 200
# (worker picks up the job and does the actual work)
```

That's why this lesson pairs with [`11-background-jobs/`](../../11-background-jobs/)
and [`16-idempotency/`](../../16-idempotency/). The three together are the
production webhook receiver:

- **`18-webhooks/`** — verify the signature
- **`16-idempotency/`** — don't process the same event twice
- **`11-background-jobs/`** — do the work outside the request

## What this example deliberately skips

- **Timestamp verification.** Stripe's signature covers a timestamp, and
  the receiver rejects signatures older than 5 minutes. This prevents
  replay of captured requests. This lesson doesn't implement it.
- **Multiple secrets for rotation.** Real receivers accept two secrets
  during a rollover.
- **Provider-specific header names and formats.** Stripe's header is
  `t=<timestamp>,v1=<sig>` — it has two parts. GitHub's is
  `sha256=<hex>`. This lesson uses the simplest possible format
  (`X-Signature: <hex>`) so the HMAC mechanism is visible without
  provider-specific parsing.
- **Retries on 5xx.** If the receiver returns 500, the provider retries.
  The lesson only returns 200 or 4xx.

Each is worth its own lesson eventually. The mechanism here — HMAC over
raw body + idempotency key + return 200 fast — is the seed of all of them.

---

## In another language?

The HMAC step is identical everywhere. What changes is how you read the
raw body:

| Language | Raw body access |
|---|---|
| Python (FastAPI) | `await request.body()` |
| Go | `io.ReadAll(r.Body)` **before** `json.NewDecoder` |
| Rust | `body.collect().await` in axum |
| Node (Express) | `express.raw({ type: 'application/json' })` middleware |
| Node (Fastify) | `addContentTypeParser` that keeps the raw buffer |
| Ruby (Rails) | `request.raw_post` |
| Java (Spring) | `@RequestBody byte[] body` |
| C# (ASP.NET) | Enable buffering, then `ReadToEndAsync()` |

Every framework has a way to get the raw bytes. The pitfall is the same
everywhere: if you parse first, you've lost the exact bytes the signature
was computed over.