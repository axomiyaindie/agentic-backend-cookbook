# ─────────────────────────────────────────────────────────────
# Lesson: correlation IDs in FastAPI
#
# The pattern:
#   1. Middleware reads X-Request-ID from the incoming request,
#      or generates a UUID if the client didn't send one.
#   2. It stores the ID in a ContextVar, so any function called
#      during the request can log with it — no need to pass it
#      through every function signature.
#   3. It logs request_start and request_end with the ID.
#   4. The response echoes the ID back, so the client can grep
#      its own logs for the same ID.
#   5. For background work, the ID is passed inside the job
#      payload — so the worker logs the same ID even though it
#      runs after the HTTP request has ended.
# ─────────────────────────────────────────────────────────────

import asyncio
import json
import sys
import time
import uuid
from contextvars import ContextVar
from threading import Thread

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI(title="Request ID lesson")

# ── 1. The context variable ─────────────────────────────────
# Every log line reads from here. The middleware sets it at
# the start of each request. `default=None` means: outside a
# request, log lines have request_id=null.
_request_id: ContextVar[str | None] = ContextVar("request_id", default=None)


def log(event: str, **fields):
    """Structured log: one JSON object per line, always with request_id."""
    record = {
        "ts": round(time.time(), 3),
        "event": event,
        "request_id": _request_id.get(),
        **fields,
    }
    print(json.dumps(record), file=sys.stdout, flush=True)


# ── 2. Middleware ───────────────────────────────────────────
@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    # Reuse the client's ID if it sent one. Otherwise generate.
    rid = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    token = _request_id.set(rid)
    start = time.perf_counter()

    log("request_start", method=request.method, path=request.url.path)
    try:
        response = await call_next(request)
    except Exception as e:
        log("request_error", error=str(e))
        _request_id.reset(token)
        raise
    duration_ms = round((time.perf_counter() - start) * 1000, 1)
    log("request_end", method=request.method, path=request.url.path,
        status=response.status_code, duration_ms=duration_ms)

    # Echo the ID back so the client can correlate its own logs.
    response.headers["X-Request-ID"] = rid
    _request_id.reset(token)
    return response


# ── 3. Simple endpoint ──────────────────────────────────────
@app.get("/hello")
def hello():
    log("hello_called")
    return {"message": "hello", "request_id": _request_id.get()}


# ── 4. Background job ───────────────────────────────────────
# This "job" runs in a thread AFTER the HTTP request ends.
# The ContextVar is empty at that point — so we pass the ID
# explicitly through the job payload.
def run_job_in_thread(payload: dict):
    rid = payload["request_id"]
    token = _request_id.set(rid)
    try:
        log("job_running", job=payload["job"], user=payload["user"])
        time.sleep(0.3)  # pretend to do work
        log("job_succeeded", job=payload["job"], user=payload["user"])
    finally:
        _request_id.reset(token)


@app.post("/enqueue")
def enqueue(user: int = 42):
    rid = _request_id.get()
    log("job_enqueued", job="send_email", user=user)

    Thread(
        target=run_job_in_thread,
        args=({"request_id": rid, "job": "send_email", "user": user},),
    ).start()

    return JSONResponse(
        {"status": "enqueued", "request_id": rid},
        status_code=202,
    )


# ─────────────────────────────────────────────────────────────
# Exercise:
#   1. Run the server (uvicorn main:app --reload --port 8013).
#   2. curl -H "X-Request-ID: my-trace-123" http://127.0.0.1:8013/hello
#      Watch the server log: every line has request_id=my-trace-123.
#   3. curl http://127.0.0.1:8013/hello  (no header)
#      The server generates a UUID. The response header echoes it.
#   4. curl -H "X-Request-ID: job-trace-456" http://127.0.0.1:8013/enqueue
#      The job log lines also carry request_id=job-trace-456, even
#      though they run in a separate thread after the request ended.
#   5. Add a /slow endpoint that does `await asyncio.sleep(2)`.
#      The request_end log will show duration_ms ~2000. That's how
#      you find slow endpoints in production without guessing.
# ─────────────────────────────────────────────────────────────