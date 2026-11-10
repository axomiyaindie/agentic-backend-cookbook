# ─────────────────────────────────────────────────────────────
# Lesson: cache-aside with TTL in FastAPI
#
# The flow:
#   1. Request comes in.
#   2. Look in cache.
#   3. HIT  → return cached value (fast).
#   4. MISS → run slow_operation(), store with timestamp, return.
#
# We use a Python dict as the cache. In production, replace `_CACHE`
# with Redis — the logic above stays the same.
# ─────────────────────────────────────────────────────────────

import time
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Cache lesson")

TTL_SECONDS = 5

# The "cache" — one entry, keyed by a fixed string.
# Real caches are keyed by (endpoint, user_id, params...) so different
# callers don't share entries.
_CACHE: dict[str, dict] = {}


class DataResponse(BaseModel):
    value: str
    source: str          # "computed" or "cache"
    elapsed_ms: int


def slow_operation() -> str:
    """Pretend this is an expensive query or AI model call."""
    time.sleep(2)
    return f"expensive result #{_COUNTER['n']}"


_COUNTER = {"n": 0}


@app.get("/data", response_model=DataResponse)
def get_data():
    now = time.time()
    start = time.perf_counter()

    # 1. Look in cache.
    entry = _CACHE.get("data")
    if entry and (now - entry["timestamp"]) < TTL_SECONDS:
        # 2a. HIT — return cached value.
        return DataResponse(
            value=entry["value"],
            source="cache",
            elapsed_ms=int((time.perf_counter() - start) * 1000),
        )

    # 2b. MISS — compute, store, return.
    _COUNTER["n"] += 1
    value = slow_operation()
    _CACHE["data"] = {"value": value, "timestamp": now}
    return DataResponse(
        value=value,
        source="computed",
        elapsed_ms=int((time.perf_counter() - start) * 1000),
    )


@app.post("/cache/clear")
def clear_cache():
    _CACHE.clear()
    return {"cleared": True}


@app.get("/cache/status")
def cache_status():
    entry = _CACHE.get("data")
    if not entry:
        return {"cached": False}
    age = time.time() - entry["timestamp"]
    return {
        "cached": True,
        "value": entry["value"],
        "age_seconds": round(age, 1),
        "expires_in": round(max(0, TTL_SECONDS - age), 1),
    }


# ─────────────────────────────────────────────────────────────
# Exercise:
#   1. Call GET /data twice in a row. Compare elapsed_ms.
#      The first is ~2000, the second ~0. That's the cache working.
#   2. Wait 10 seconds, call GET /data again. It's slow again, and
#      the value incremented — the TTL expired.
#   3. Change TTL_SECONDS to 60 and restart. Now the cache stays
#      warm for a minute. Try to prove the value doesn't change.
#   4. Add a POST /data endpoint that writes new data and clears the
#      cache. This is what "invalidation" looks like in real code.
# ─────────────────────────────────────────────────────────────