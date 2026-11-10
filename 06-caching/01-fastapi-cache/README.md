✅ FILE 1 pushed: `1de41e6..c4ebe98`, 95 insertions.

---

## FILE 2 — `06-caching/01-fastapi-cache/README.md`

**Path:**
```
D:\agentic-backend-cookbook\06-caching\01-fastapi-cache\README.md
```

**Create folder and file:**
```powershell
cd D:\agentic-backend-cookbook
New-Item -ItemType Directory -Force -Path 06-caching\01-fastapi-cache | Out-Null
code 06-caching\01-fastapi-cache\README.md
```

**Paste this:**
```
# FastAPI cache

A single-file FastAPI app that demonstrates cache-aside with TTL.

## What you'll learn
- How a cache turns a slow operation into an instant one
- What a TTL is and why cached data must expire
- Why invalidation is the hard part of caching
- How to see a cache miss and a cache hit side by side

## How to run
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Then open <http://127.0.0.1:8000/docs> and try the endpoints.

## What to look at
- `main.py` — read `slow_operation` first. It sleeps for 2 seconds
  on purpose. Then read `get_cached` — it stores the result with a
  timestamp, checks TTL on each request, and returns "fresh" or "cached".

## Walkthrough — prove it works

**Test 1: Cache miss (slow)**

Open `/docs`, execute `GET /data` once.

Response:
```json
{
  "value": "expensive result #1",
  "source": "computed",
  "elapsed_ms": 2003
}
```

Notice `source: "computed"` and `elapsed_ms` around 2000. That's the
slow operation running for real.

**Test 2: Cache hit (fast)**

Execute `GET /data` again immediately.

Response:
```json
{
  "value": "expensive result #1",
  "source": "cache",
  "elapsed_ms": 1
}
```

Same value, `source: "cache"`, `elapsed_ms` near 0. The operation didn't
run — the cached result was returned.

**Test 3: TTL expiry (slow again)**

Wait 10 seconds (the TTL is 5), then execute `GET /data` again.

Response:
```json
{
  "value": "expensive result #2",
  "source": "computed",
  "elapsed_ms": 2001
}
```

Back to slow, and the value incremented. The cache expired and recomputed.

**Test 4: Manual invalidation**

Execute `POST /cache/clear`, then `GET /data` again. Same result as
Test 3 — immediate recompute.

## The three cache properties you can see here

| Property | Where to see it |
|---|---|
| **Cache hit** | Test 2 — `elapsed_ms` near 0 |
| **TTL expiration** | Test 3 — wait 10s, cache recomputes |
| **Invalidation** | Test 4 — `POST /cache/clear` forces recompute |

## What this example doesn't do

- **No Redis.** The cache is a Python dict in memory. It dies when the
  server restarts. Redis makes it persistent and shared across processes.
- **No eviction policy.** A real cache needs a max size and an eviction
  rule (LRU, LFU). This example grows forever — fine for a demo, wrong
  for production.
- **No stampede protection.** If 1,000 clients hit `/data` right after
  the TTL expires, all 1,000 will run `slow_operation`. Production caches
  add a lock so only one computes.
- **No `Cache-Control` headers.** HTTP caching is a separate layer; this
  lesson is application-level.

## Why not just use `@lru_cache`?

Python's `functools.lru_cache` is excellent for pure functions. It's the
wrong tool here because:
- It has no TTL (values live until evicted or the process restarts)
- It can't be invalidated on demand
- It doesn't tell you whether the call was a hit or a miss

Building the cache by hand — even 15 lines — teaches the mechanism.
Then you can use `lru_cache` or Redis with understanding, not cargo cult.

---

## In another language?

The four operations — get, set, TTL check, invalidate — are the same
everywhere:

| Language | Minimal cache |
|---|---|
| Go | `map[string]entry` + `sync.RWMutex` + `time.Now()` check |
| Rust | `HashMap` + `Mutex` + `Instant` for TTL |
| PHP | `apcu_fetch` / `apcu_store` with TTL arg |
| Ruby | `Hash` + `Time.now` or `ActiveSupport::Cache` |
| Java | `ConcurrentHashMap` + `System.currentTimeMillis()` |
| C# | `ConcurrentDictionary` + `DateTime.UtcNow` |

For production, use Redis and the language's Redis client. The flow is
identical — only the storage backend changes.
```