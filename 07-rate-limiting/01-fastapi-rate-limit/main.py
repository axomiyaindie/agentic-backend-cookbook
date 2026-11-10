# ─────────────────────────────────────────────────────────────
# Lesson: fixed-window rate limiting in FastAPI
#
# The algorithm in 10 lines:
#   1. key = client IP (or user id, or API key)
#   2. look up the counter + window start for that key
#   3. if the window has expired, reset the counter and window
#   4. increment the counter
#   5. if counter > limit, raise 429 with Retry-After
#
# We use a dict as the store. In production, replace `_WINDOWS`
# with Redis so all processes share the same counters.
# ─────────────────────────────────────────────────────────────

import time
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse

app = FastAPI(title="Rate limit lesson")

LIMIT = 5
WINDOW_SECONDS = 60

# key -> {"count": int, "window_start": float}
_WINDOWS: dict[str, dict] = {}


def _check_rate_limit(request: Request) -> dict:
    """Return rate-limit info, or raise 429 if the caller is over."""
    key = request.client.host if request.client else "unknown"
    now = time.time()

    entry = _WINDOWS.get(key)
    if entry is None or (now - entry["window_start"]) >= WINDOW_SECONDS:
        # New window for this key.
        entry = {"count": 0, "window_start": now}
        _WINDOWS[key] = entry

    entry["count"] += 1
    remaining = max(0, LIMIT - entry["count"])
    reset_in = int(WINDOW_SECONDS - (now - entry["window_start"]))

    if entry["count"] > LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="rate limit exceeded",
            headers={
                "Retry-After": str(reset_in),
                "X-RateLimit-Limit": str(LIMIT),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(now + reset_in)),
            },
        )

    return {
        "limit": LIMIT,
        "remaining": remaining,
        "reset_in": reset_in,
    }


@app.get("/limited")
def limited(request: Request):
    """This endpoint is protected by the limiter."""
    info = _check_rate_limit(request)
    return {
        "message": "you got through",
        "limit": info["limit"],
        "remaining": info["remaining"],
        "reset_in": info["reset_in"],
    }


@app.get("/unlimited")
def unlimited():
    """Control endpoint — no limiter, always returns 200."""
    return {"message": "no limiter here"}


@app.get("/status")
def status_view():
    """Debug: show every tracked window."""
    return {
        "limit": LIMIT,
        "window_seconds": WINDOW_SECONDS,
        "tracked_keys": len(_WINDOWS),
        "windows": _WINDOWS,
    }


@app.post("/reset")
def reset():
    """Clear all counters — handy when testing."""
    _WINDOWS.clear()
    return {"cleared": True}


# ─────────────────────────────────────────────────────────────
# Exercise:
#   1. In /docs, call GET /limited five times. Watch the
#      X-RateLimit-Remaining header count down 4, 3, 2, 1, 0.
#   2. Call it a sixth time. You get 429 Too Many Requests with
#      a Retry-After header. That's the limiter working.
#   3. Call GET /unlimited ten times. Always 200 — no limiter.
#   4. Change LIMIT to 2 and WINDOW_SECONDS to 10. Restart.
#      The limit applies much faster now.
#   5. Try GET /status while blocked. You'll see your IP with a
#      count over the limit.
# ─────────────────────────────────────────────────────────────