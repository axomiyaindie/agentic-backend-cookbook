# Streaming

**Streaming** means sending a response in pieces as each piece is ready,
instead of building the whole thing and sending it at once.

## The one idea to take away

The AI model doesn't produce its answer all at once — it produces one
token at a time, over seconds. If you wait for the whole answer before
sending anything, the user stares at a blank screen for 10 seconds. If
you stream each token as it arrives, the user sees words appear.

**Same total work, completely different felt experience.**

This is why every AI chat interface streams. It's not about speed — it's
about *perceived* speed. The first token arrives in ~300ms; the last in
~8 seconds. Without streaming, the user waits 8 seconds for anything.
With streaming, the user starts reading at 300ms and is done by 8.

## Two transports

| | **SSE** (Server-Sent Events) | **WebSocket** |
|---|---|---|
| **Direction** | Server → client only | Bidirectional |
| **Protocol** | Plain HTTP | HTTP upgrade to a socket |
| **Browser support** | Built-in (`EventSource`) | Built-in (`WebSocket`) |
| **Reconnect** | Automatic | You have to implement it |
| **Proxy-friendliness** | Works through any HTTP proxy | Some proxies block the upgrade |
| **Best for** | Streaming AI tokens, live feeds, notifications | Chat, multiplayer, anything the client also sends mid-stream |

**Rule of thumb:** if the client only needs to *receive*, use SSE. If the
client needs to *send mid-stream* (typing indicators, cancel signals,
real-time collaboration), use WebSocket.

Most AI chat interfaces use SSE because the client only sends one thing
(the prompt) and then only receives (the tokens).

## The wire format (SSE)

SSE is a plain HTTP response with `Content-Type: text/event-stream`.
The body is a sequence of events, each formatted like this:

```
data: first chunk\n\n
data: second chunk\n\n
data: third chunk\n\n
```

Each `data:` line is one message. The blank line separates messages. The
client's `EventSource` fires an `onmessage` for each one, in order.

That's the entire protocol. No framing library, no handshake, no
serialization format. Just lines of text.

## Lesson

`01-fastapi-sse/` — a FastAPI server that streams 5 chunks with a 1-second
delay between each, plus a 30-line `client.html` that displays them live
in a browser. You can watch the words appear one at a time.

## Where this fits in real code

- **SSE** — OpenAI API (streaming completions), Anthropic API (streaming
  messages), GitHub Actions logs, Vercel AI SDK's `useChat`.
- **WebSocket** — Slack, Discord, Figma, Google Docs, any multiplayer
  editor, live trading dashboards.
- **Long-polling** — the 2010 answer to this problem. Still used when
  proxies block SSE and WebSocket. Avoid for new code.

## What this lesson does not cover

- **Streaming from a real LLM** — the server streams fake tokens. Swapping
  in a real model means replacing `fake_token_stream()` with a real
  async generator. The FastAPI plumbing doesn't change.
- **Backpressure** — what happens if the client is slow and the server is
  fast. Real systems add a buffer with a max size.
- **Cancelation** — if the user closes the tab, the stream should stop.
  FastAPI handles this with `await request.is_disconnected()`.
- **Multiplexing** — sending multiple streams over one connection. SSE
  handles this with named events; WebSocket handles it with message
  envelopes.

Each of these is worth its own lesson eventually. The mechanism in this
lesson is the seed of all of them.

---

## In another language?

The SSE wire format is universal. Any HTTP framework can produce it:

| Language | SSE server | SSE client |
|---|---|---|
| Python | FastAPI `StreamingResponse` | `httpx-sse`, `sse-starlette` |
| Go | `net/http` + `http.Flusher` | `r3labs/sse` |
| Rust | axum `Sse` | `reqwest-eventsource` |
| Node | Express `res.write` | `EventSource` (built-in in browsers) |
| Ruby | Rails `ActionController::Live` | `EventSource` (built-in in browsers) |
| Java | Spring WebFlux `Flux<String>` | `okhttp-sse` |
| C# | ASP.NET `IAsyncEnumerable` | `Microsoft.Net.Http` |

The one thing every server must do: **flush after every event**. Without
flushing, the framework buffers the response and the client receives
everything at once at the end — which defeats the entire point.