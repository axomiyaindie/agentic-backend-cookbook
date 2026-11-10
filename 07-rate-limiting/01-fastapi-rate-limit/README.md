
```
# FastAPI rate limit

A single-file FastAPI app with a **hand-written** rate limiter. No
third-party library — so you can see the mechanism, not just a decorator.

## What you'll learn
- How a fixed-window rate limiter counts requests
- What HTTP 429 looks like and what headers it should include
- Why you key on IP for anonymous endpoints and on user for authed ones
- Why production uses Redis instead of an in-memory dict

## How to run
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Then open <http://127.0.0.1:8000/docs> and try the endpoints.

## What to look at
- `main.py` — read `_check_rate_limit` first. It's the whole algorithm:
  - key = client IP
  - look up the counter for this key
  - if the window has expired, reset the counter
  - increment
  - if the counter is over the limit, raise 429 with headers
- Then read the endpoints: `/limited` uses the limiter, `/unlimited`
  doesn't, so you can compare.

## Walkthrough — prove it works

The limit is **5 requests per 60 seconds**.

**Test 1: Stay under the limit**

In `/docs`, execute `GET /limited` five times.

Each response includes the headers:
```
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 4, 3, 2, 1, 0
```

Status is always **200 OK**.

**Test 2: Cross the limit (the important one)**

Execute `GET /limited` a **sixth** time.

Response:
- Status: **429 Too Many Requests**
- Body: `{"detail": "rate limit exceeded", "retry_after": <seconds>}`
- Headers:
  ```
  Retry-After: <seconds>
  X-RateLimit-Limit: 5
  X-RateLimit-Remaining: 0
  ```

**That 429 is the lesson.** The server saw the key (your IP), checked
the counter, and refused.

**Test 3: Wait and recover**

Wait 60 seconds, execute `GET /limited` again.

Response: **200 OK**. The window reset.

**Test 4: `/unlimited` always works**

Execute `GET /unlimited` as many times as you want. It has no limiter
attached, so it always returns 200. That's the control.

## What the response headers actually mean

| Header | Meaning | Why it matters |
|---|---|---|
| `X-RateLimit-Limit` | How many requests per window | Client knows the quota |
| `X-RateLimit-Remaining` | How many are left | Client can self-throttle before being blocked |
| `Retry-After` | Seconds until the window resets | Client knows when to retry |

Without these headers, the client is guessing. With them, it can back
off gracefully instead of hammering the endpoint.

## Why this implementation isn't production-ready

- **Single process.** The counter lives in a Python dict. Two uvicorn
  workers = two separate counters = two separate limits. Production uses
  Redis so all processes share the same counter.
- **Fixed window, not sliding.** At the boundary (t=59s to t=0s), a
  client can do 10 requests in 2 seconds and stay under the limit.
  Sliding window or token bucket fixes this.
- **No key for authenticated users.** This lesson keys on IP. If you
  have auth, you should key on user ID too — otherwise one user on a
  shared network affects everyone behind the same NAT.
- **No cleanup.** Expired entries stay in `_WINDOWS` forever. Real
  caches expire.

Every one of these limitations is what a production rate limiter (Redis
+ sliding window + cleanup job) actually solves. The mechanism in this
lesson is the seed of all of them.

---

## In another language?

The algorithm is identical. Only the storage changes:

| Language | In-process counter | Shared store |
|---|---|---|
| Go | `sync.Map` + `time.Now` | `redis/go-redis` |
| Rust | `Mutex<HashMap>` | `redis` crate |
| PHP | `apcu` | `predis/predis` |
| Ruby | `Hash` | `redis` gem |
| Java | `ConcurrentHashMap` | Jedis |
| C# | `ConcurrentDictionary` | StackExchange.Redis |

The flow is always: key → lookup counter → check window → increment
→ decide. Redis makes it shared; the algorithm doesn't change.
```