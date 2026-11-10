# WebSockets

**WebSocket** is a bidirectional connection between the client and the
server. Once opened, both sides can send messages at any time, until
either side closes.

## The one idea to take away

SSE (`12-streaming/`) is **one-way**: server → client. That's enough for
streaming AI tokens, because the client sends one prompt and then only
receives.

WebSocket is **two-way**: server ↔ client. That's needed when the client
also sends mid-stream — chat messages, typing indicators, cursor
positions, cancel signals, multiplayer edits.

| | SSE | WebSocket |
|---|---|---|
| Direction | Server → client | Both directions |
| Protocol | Plain HTTP | HTTP upgrade to a socket |
| Reconnect | Automatic (`EventSource`) | Manual (`onclose` → reconnect) |
| Proxy-friendliness | Works everywhere | Some proxies block the upgrade |
| Best for | AI token streaming, live feeds | Chat, multiplayer, real-time collaboration |

**Rule of thumb:** if the client only receives → SSE. If the client sends
and receives → WebSocket.

## The handshake

A WebSocket starts as a normal HTTP request with two special headers:

```http
GET /ws HTTP/1.1
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: <random base64>
Sec-WebSocket-Version: 13
```

The server responds with:

```http
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: <hash of key>
```

After that 101, the HTTP request is **done** — the TCP connection stays
open, and both sides exchange framed messages instead of requests and
responses. That's the whole protocol surface you need to understand.

## The message format

WebSocket messages are frames, not lines. A frame carries:

- a small header (opcode, length, mask bit)
- the payload (bytes, usually UTF-8 text or binary)

Browsers and server libraries handle framing for you. You just call
`socket.send("hello")` and the client receives `"hello"`.

## Lesson

`01-fastapi-websocket/` — a FastAPI app with one WebSocket endpoint and a
20-line `client.html`. The server echoes messages, and a timer sends a
tick every second. You see the bidirectional part: the client types, the
server responds **and** the server also initiates messages.

## Where this fits in real code

- **Chat** — Slack, Discord, WhatsApp Web
- **Multiplayer** — Figma, Google Docs, any collaborative editor
- **Trading dashboards** — live prices, order book updates
- **AI agents** — interactive chat where the user can interrupt or steer
  mid-stream
- **Notifications** — toast popups, presence indicators

## What this lesson does not cover

- **Scaling across servers.** WebSocket connections are pinned to the
  server that accepted them. To broadcast to all clients of a user, you
  need a pub/sub system (Redis pub/sub, NATS) between servers.
- **Reconnect with state.** If the connection drops, the client reconnects
  and the server needs to know what was missed. Real apps use a message
  ID / cursor.
- **Authentication mid-connection.** The upgrade request can carry cookies
  or a token, but token refresh during an open socket is tricky.
- **Binary messages.** The lesson only sends text. Binary works the same
  way, just with `send_bytes` / `receive_bytes`.

Each is worth its own lesson. This one shows the mechanism.

---

## In another language?

The WebSocket handshake and frame format are standardized (RFC 6455).
Every language has a library:

| Language | Server | Client |
|---|---|---|
| Python | FastAPI `WebSocket`, `websockets` | `websockets`, browser `WebSocket` |
| Go | `gorilla/websocket`, `nhooyr/websocket` | browser `WebSocket` |
| Rust | `axum::extract::ws`, `tokio-tungstenite` | browser `WebSocket` |
| Node | `ws`, `socket.io` | browser `WebSocket` |
| PHP | `Ratchet` | browser `WebSocket` |
| Ruby | `faye-websocket`, ActionCable | browser `WebSocket` |
| Java | `javax.websocket`, Spring WebSocket | browser `WebSocket` |
| C# | `System.Net.WebSockets`, SignalR | browser `WebSocket` |

The browser's `WebSocket` API is the same in every language's frontend.
The server implementation is what changes.