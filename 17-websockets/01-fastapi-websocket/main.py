# ─────────────────────────────────────────────────────────────
# Lesson: WebSocket in FastAPI
#
# The endpoint does TWO things at once on the same connection:
#   1. A background task sends a "tick" every second (server → client)
#   2. The main loop reads whatever the client sends and echoes it
#      back (client → server → client)
#
# That bidirectional flow is what distinguishes WebSocket from SSE.
# SSE can only do the server-to-client half.
# ─────────────────────────────────────────────────────────────

import asyncio
import time
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse

app = FastAPI(title="WebSocket lesson")

TICK_INTERVAL = 1.0   # seconds between server-initiated ticks


# ── The background tick loop ────────────────────────────────
# Runs as a task alongside the main receive loop. Wraps every
# send in a try so a disconnect during the tick doesn't crash
# the task silently.
async def tick_loop(ws: WebSocket):
    n = 0
    try:
        while True:
            await asyncio.sleep(TICK_INTERVAL)
            n += 1
            await ws.send_text(f"[tick {n}] {time.strftime('%H:%M:%S')}")
    except Exception:
        # Client disconnected. Nothing to do — the main handler
        # will also see the disconnect and clean up.
        return


# ── The WebSocket endpoint ─────────────────────────────────
@app.websocket("/ws")
async def ws(websocket: WebSocket):
    # 1. Accept the upgrade. From this line onward, the connection
    #    is a WebSocket, not an HTTP request.
    await websocket.accept()

    # 2. Start the background tick task. It runs concurrently with
    #    the receive loop below. Both write to the same socket.
    tick_task = asyncio.create_task(tick_loop(websocket))

    # 3. The receive loop. Blocks on receive_text() until the
    #    client sends something or the connection closes.
    try:
        while True:
            msg = await websocket.receive_text()
            await websocket.send_text(f"[echo] {msg}")
    except WebSocketDisconnect:
        # The client closed the connection (tab closed, network
        # dropped, explicit ws.close()). Clean up the tick task.
        pass
    finally:
        tick_task.cancel()
        try:
            await tick_task
        except asyncio.CancelledError:
            pass


# ── Serve the client page ─────────────────────────────────
@app.get("/")
def index():
    return FileResponse(Path(__file__).parent / "client.html")


# ─────────────────────────────────────────────────────────────
# Exercise:
#   1. Start the server:
#        pip install -r requirements.txt
#        uvicorn main:app --reload --port 8017
#   2. Open http://127.0.0.1:8017/ in two browser tabs.
#      Both tabs get ticks — the server sends to each connection
#      independently. But a message sent from one tab does NOT
#      reach the other. WebSocket is per-connection, not broadcast.
#   3. To make it a chat, add a global `set[WebSocket]` of
#      connections. On every message, loop over the set and
#      `send_text` to each. That's how a real chat works.
#   4. Close the browser tab. The server's tick loop gets an
#      exception on the next send, the task exits, the receive
#      loop sees WebSocketDisconnect. Both clean up. No leak.
#   5. Change TICK_INTERVAL to 0.1. You get 10 ticks per second.
#      The browser can handle it. This is why WebSocket is used
#      for live dashboards — it scales to high message rates that
#      HTTP polling can't match.
# ─────────────────────────────────────────────────────────────