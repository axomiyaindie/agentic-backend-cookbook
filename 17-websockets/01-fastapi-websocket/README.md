# FastAPI WebSocket

A single WebSocket endpoint that demonstrates **both directions**:
- The client sends a message → the server echoes it back
- The server sends a tick every second on its own

That second part is what makes this a WebSocket and not SSE.

## What you'll learn
- How a WebSocket endpoint is defined (`@app.websocket(...)`)
- How to `receive_text()` and `send_text()` on the same connection
- How to run a background sender alongside a receiver (the server-initiated messages)
- How a browser's `WebSocket` API connects and listens

## How to run
```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8017
```

Using port 8017. Then open:

```
http://127.0.0.1:8017/
```

The `client.html` is served by the same app.

## What to look at
- `main.py` — read the `ws` endpoint. Two things happen concurrently:
  1. `asyncio.create_task(tick_loop(ws))` — the server sends a tick every second
  2. The `while True` loop reads whatever the client sends
  Both run on the same connection. That's the "bidirectional" part.
- `client.html` — 30 lines. The important line is
  `const ws = new WebSocket("ws://...")`.

## Walkthrough — prove it works

**Step 1: Start the server**

```powershell
cd D:\agentic-backend-cookbook\17-websockets\01-fastapi-websocket
pip install -r requirements.txt
uvicorn main:app --reload --port 8017
```

**Step 2: Open the page**

`http://127.0.0.1:8017/` in a browser. You'll see:

- A status line: **Connected**
- A box of incoming messages
- An input field and a **Send** button

**Step 3: Watch the ticks**

Every second, a new message appears in the box:

```
[tick 1] 14:32:01
[tick 2] 14:32:02
[tick 3] 14:32:03
...
```

**Those are server-initiated messages.** The client didn't send anything.
The server pushed them. That's the difference from SSE — well, SSE also
pushes from the server. The difference is what the client can *also* do:

**Step 4: Send a message**

Type `hello` and press Send. The box shows:

```
[you] hello
[echo] hello
```

**Two things happened:**
1. The client sent `"hello"` to the server
2. The server received it and sent `"hello"` back

That's the bidirectional part. SSE could do the first half (server sends)
but not the second (client sends). WebSocket does both.

**Step 5: Prove it's a real WebSocket**

Open the browser devtools (F12) → Network tab → filter to `WS`.
You'll see one connection that stays open. Click it → Messages tab.
Every frame is visible:

```
↑ you: hello
↓ echo: hello
↓ tick: 14:32:04
↓ tick: 14:32:05
```

The `↑` and `↓` arrows tell you who sent each frame. That's the whole
protocol in one view.

## How the code does both directions

The key insight:

```python
async def ws(websocket: WebSocket):
    await websocket.accept()
    asyncio.create_task(tick_loop(websocket))    # server → client
    while True:
        msg = await websocket.receive_text()     # client → server
        await websocket.send_text(f"echo: {msg}")
```

Two concurrent activities on the same connection:
- `tick_loop` runs in the background, sending on a timer
- The `while` loop blocks on `receive_text()`, handling whatever the client sends

Both write to the same socket. FastAPI's `WebSocket` object is safe to use
from multiple tasks on the same connection (the underlying `websockets`
library handles the frame locking).

## What "the connection is open" means

A WebSocket isn't one message and done. It's a **long-lived** connection.
The server must:

- Hold the connection open as long as the client is there
- Handle disconnects cleanly (the `finally: await websocket.close()`)
- Not block on one connection — if it awaits for 10 seconds, no other
  client can be served unless the server is async

FastAPI is async, so this works. A synchronous framework would need a
thread per connection. That's why every modern framework has async
WebSocket support.

## What this example deliberately skips

- **Multiple clients.** Every client connects to the same handler, but
  they don't see each other's messages. A chat app would keep a list of
  connections and broadcast. That's the next step.
- **Authentication.** The client can pass cookies or a query token on
  connect. The lesson doesn't.
- **Reconnect logic.** If the connection drops, the client's `onclose`
  fires. Real apps reconnect with exponential backoff. `client.html` just
  shows "Disconnected".
- **Heartbeats.** Some proxies kill idle WebSocket connections after
  30–60 seconds. Production sends periodic ping frames to keep it alive.
  The server in this lesson sends ticks every second, so it stays alive
  in the demo.

Each of those is a lesson. The one here shows the mechanism.

---

## In another language?

The pattern is the same everywhere. Only the framework's API changes:

| Language | Endpoint | Send | Receive |
|---|---|---|---|
| Python (FastAPI) | `@app.websocket("/ws")` | `await ws.send_text(...)` | `await ws.receive_text()` |
| Go | `http.HandleFunc("/ws", ...)` + `gorilla/websocket` | `conn.WriteMessage(...)` | `conn.ReadMessage()` |
| Rust | axum `ws` extractor | `sender.send(Message::Text(...))` | `while let Some(msg) = receiver.next().await` |
| Node | `ws.on("connection", ...)` | `ws.send(...)` | `ws.on("message", ...)` |
| PHP | Ratchet `onMessage` | `$conn->send(...)` | `onMessage` callback |
| Ruby | ActionCable channel | `transmit(...)` | `receive(data)` method |
| Java | `@ServerEndpoint` (JSR 356) | `session.getBasicRemote().sendText(...)` | `@OnMessage` |
| C# | SignalR hub or `System.Net.WebSockets` | `SendAsync(...)` | `ReceiveAsync(...)` |

The browser-side `WebSocket` API is the same in all of them.