# ─────────────────────────────────────────────────────────────
# Lesson: streaming with Server-Sent Events (SSE) in FastAPI
#
# The whole mechanism:
#   1. An async generator yields one chunk at a time.
#   2. FastAPI wraps it in StreamingResponse with Content-Type
#      text/event-stream.
#   3. The browser's EventSource reads each "data:" line as it
#      arrives and fires an onmessage event.
#
# The magic is not in the protocol — SSE is just lines of text.
# The magic is in flushing: the server must push each event out
# as it's produced, not buffer them until the end. FastAPI's
# StreamingResponse flushes automatically for async generators.
# ─────────────────────────────────────────────────────────────

import asyncio
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, StreamingResponse

app = FastAPI(title="SSE lesson")

# The chunks we'll stream. One word per second.
# In a real AI app, these would be model tokens.
WORDS = ["Hello", "from", "a", "streaming", "server!"]

# How long to wait between chunks (in seconds).
# Change to 0.2 for a snappier demo, or 3 for a slower one.
DELAY = 1.0


# ── 1. The async generator ──────────────────────────────────
# This is where the streaming happens. It yields one SSE-formatted
# message at a time. Each `yield` sends a message to the client
# immediately — the client doesn't wait for the whole loop.
async def token_stream():
    for word in WORDS:
        await asyncio.sleep(DELAY)          # simulate work
        # SSE wire format: "data: <payload>\n\n". The blank line
        # separates one event from the next. Two newlines = one
        # complete message.
        yield f"data: {word}\n\n"


# ── 2. The endpoint ────────────────────────────────────────
# `StreamingResponse` handles the `Content-Type` header and the
# chunked transfer encoding. It also flushes after each yield
# for async generators, which is exactly what SSE needs.
@app.get("/stream")
async def stream(request: Request):
    # If the client disconnects, we should stop generating.
    # For a 5-second stream that's not critical, but real apps
    # check this in every loop iteration.
    async def guarded():
        async for chunk in token_stream():
            if await request.is_disconnected():
                return
            yield chunk

    return StreamingResponse(
        guarded(),
        media_type="text/event-stream",
        headers={
            # Tell any intermediate proxies not to buffer.
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# ── 3. Serve the client page ───────────────────────────────
# The HTML lives in the same folder. This endpoint just serves it
# so the user doesn't have to open a separate file.
@app.get("/")
def index():
    return FileResponse(Path(__file__).parent / "client.html")


# ─────────────────────────────────────────────────────────────
# Exercise:
#   1. Open http://127.0.0.1:8000/ in a browser. Watch the words
#      appear one at a time.
#   2. Run `curl -N http://127.0.0.1:8000/stream` in a terminal.
#      You see the raw wire format — `data:` lines and blank lines.
#   3. Change DELAY to 0.1. The whole sentence now takes half a
#      second. This is why streaming feels instant even when the
#      total work is the same.
#   4. Break streaming on purpose: replace `yield f"data: {word}\n\n"`
#      with `chunks.append(word)`, then `yield "data: " + " ".join(chunks) + "\n\n"`
#      after the loop. Now the browser shows nothing for 5 seconds,
#      then the whole sentence. That's the difference between
#      streaming and waiting.
#   5. Add an `event: done\ndata: \n\n` after the loop, and in
#      client.html add `source.addEventListener('done', ...)` to
#      close the connection. That's how real SSE clients know the
#      stream ended.
# ─────────────────────────────────────────────────────────────