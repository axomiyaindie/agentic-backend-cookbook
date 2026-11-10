# Caching

**Caching** = storing the result of an expensive operation so the next
request can skip the work.

## The one idea to take away

A cache is a **trade**: you accept *possibly stale data* in exchange for
*speed*. That trade is worth it when:

- The computation is expensive (database query, external API call, AI model call)
- The result doesn't change often
- A small delay in freshness is acceptable

It's the wrong trade when the data must always be current (bank balances,
stock levels, anything with "real-time" in the requirement).

## The core flow (cache-aside)

```
1. Request comes in
2. Look in cache
3. Cache HIT  → return cached value  (fast)
4. Cache MISS → compute value
              → store in cache with TTL
              → return fresh value     (slow, but only once)
```

That's it. Every caching system — Redis, Memcached, CDN, browser cache —
follows this shape.

## The three hard problems

1. **Invalidation** — when does the cached value become wrong?
   - Time-based (TTL): stale after N seconds. Simple, always slightly wrong.
   - Event-based: delete the key when the data changes. Correct, but you
     must remember to do it everywhere.
2. **Stampede** — when a popular cache key expires, 1,000 requests all
   miss at once and hammer the database. Solutions: locks, jitter,
   serving stale while refreshing.
3. **Size** — caches live in memory, and memory is finite. You need an
   eviction policy (LRU, LFU, TTL).

## Lesson

`01-fastapi-cache/` — a single-file FastAPI app with one endpoint that
simulates a slow operation (2 seconds), then caches the result. First call
is slow, second call is instant. You can watch the timer in the response.

## Where this fits in real code

- **Redis** — the default production cache. Supports TTL, eviction, pub/sub.
- **Memcached** — older, simpler, still used for pure key-value caching.
- **CDN** (Cloudflare, Fastly) — HTTP-level caching for static and semi-static responses.
- **In-process** (Python `functools.lru_cache`, Node `node-cache`) — for single-server apps.

---

## In another language?

Caching is universal. The pattern is the same, only the client changes:

| Language | In-memory cache | Redis client |
|---|---|---|
| Go | `sync.Map` + TTL | `redis/go-redis` |
| Rust | `moka` crate | `redis` crate |
| PHP | `apcu` | `predis/predis` |
| Ruby | `ActiveSupport::Cache::MemoryStore` | `redis` gem |
| Java | Caffeine | Jedis / Lettuce |
| C# | `IMemoryCache` | StackExchange.Redis |

The `cache-aside` flow above maps 1:1 to every one of them. If you
understand *why* cache-aside works, you can implement it in any language
in under an hour.
```