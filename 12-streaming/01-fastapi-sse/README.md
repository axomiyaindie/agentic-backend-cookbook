# FastAPI SSE

A server that streams five chunks with a 1-second delay between each, plus
a 30-line HTML page that displays them as they arrive. You can watch the
words appear one at a time.

## What you'll learn
- How the `text/event-stream` wire format looks
- Why the server must **flush** after each event (or nothing streams)
- How a browser's `EventSource` consumes it without any client library
- Where this fits in a real AI chat UI

## How to run
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Then open <http://127.0.0.1:8000/> in a browser. The `client.html` is
served by the same FastAPI app, so there's nothing else to install.

## What to look at
- `main.py` — read `token_stream()` first. It's an async generator that
  yields one chunk at a time with `await asyncio.sleep(1)` between yields.
  Then read the `/stream` endpoint that wraps it in `StreamingResponse`.
- `client.html` — 30 lines. The important line is `new EventSource('/stream')`.
  Everything else is display.

## Walkthrough — prove it works

**Test 1: The live page**

Open `http://127.0.0.1:8000/`. You should see:

- A blank page with a heading
- After 1 second: "Hello"
- After 2 seconds: "Hello from"
- After 3 seconds: "Hello from a"
- After 4 seconds: "Hello from a streaming"
- After 5 seconds: "Hello from a streaming server!"

The words appear one at a time. That's SSE.

**Test 2: The raw wire format**

In a second terminal, use `curl` to see what's actually being sent:

```bash
curl -N http://127.0.0.1:8000/stream
```

(`-N` disables buffering, which is exactly what you need to see SSE.)

Expected output:

```
data: Hello

data: from

data: a

data: streaming

data: server!

```

The blank lines between events are required by the SSE spec. Each `data:`
line is one message. The client's `EventSource` fires an event for each
one, in order.

**Test 3: Without flushing, nothing streams**

The lesson is subtle: if you remove `flush` from your framework, the
client sees nothing until the whole response is done. FastAPI's
`StreamingResponse` flushes automatically for async generators — but if
you ever build this by hand (Go's `http.Flusher`, Node's `res.flush()`),
forgetting to flush is the #1 bug.

To see it, change `token_stream` to build a list and `yield` it all at
once at the end:

```python
async def token_stream():
    chunks = []
    for word in WORDS:
        await asyncio.sleep(1)
        chunks.append(word)
    yield " ".join(chunks)
```

Run again. The page is blank for 5 seconds, then shows the whole sentence.
That's the difference streaming makes — and why the flush matters.

## The two things that make SSE work

**1. The `Content-Type` header.** Must be `text/event-stream`. Without
it, the browser's `EventSource` refuses to connect.

**2. The flush after each event.** The whole point of streaming is that
the client sees each event *as it happens*, not after the response ends.
If the server buffers, the client sees one big response at the end.

FastAPI's `StreamingResponse` handles both for you. If you ever write this
in a lower-level framework, you have to do both by hand.

## What this example deliberately skips

- **Real LLM tokens.** The server streams fake words. To swap in a real
  model, replace `token_stream` with a generator that yields tokens from
  the model. The FastAPI plumbing is the same.
- **Disconnect handling.** If the user closes the tab, this server keeps
  generating for 5 seconds. Real servers check `await request.is_disconnected()`
  in the loop and `return` when the client is gone.
- **Error events.** SSE has an `event: error` message type for sending
  errors mid-stream. This example uses only the default `message` type.
- **Reconnect / last-event-id.** `EventSource` automatically reconnects
  if the connection drops, and can send `Last-Event-ID` to resume. This
  example doesn't use IDs, so it restarts from the beginning on reconnect.

Each of these is worth its own lesson eventually. The mechanism in this
lesson is the seed of all of them.

---

## In another language?

The FastAPI version uses `StreamingResponse` for flushing, but the SSE
wire format is universal:

| Language | The equivalent |
|---|---|
| Go | `http.Flusher.Flush()` after each `fmt.Fprintf(w, "data: %s\n\n", chunk)` |
| Rust | `axum::response::sse::Sse` + an `impl Stream<Item = Result<Event, _>>` |
| Node | `res.write(...)` after each chunk; call `res.flush()` if using compression |
| Ruby | `ActionController::Live` + `response.stream.write` |
| Java | Spring WebFlux `Flux<ServerSentEvent<String>>` |
| C# | `IAsyncEnumerable<string>` returned from a controller action |

Every one of them does the same thing: write the `data:` line, write the
blank line, and flush. If you can read this lesson, you can build SSE in
any of them.