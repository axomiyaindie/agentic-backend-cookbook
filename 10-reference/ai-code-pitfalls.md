# AI code pitfalls

AI assistants generate backend code fast. This file is the checklist
for reading what they generated before you ship it — the patterns that
*look* correct but are quietly broken.

Every item here has a matching lesson in this cookbook. Read the
generated code, check it against this list, and if it has one of these
problems, the linked lesson shows you what it should look like instead.

## The nine most common pitfalls

### 1. Multi-step writes without a transaction

**What the AI writes:**
```python
conn.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (amt, from_id))
conn.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (amt, to_id))
```

**Why it's wrong:** If the second statement fails (crash, network, constraint), the first one is already committed. Money vanishes.

**What it should look like:** Wrap both in `BEGIN … COMMIT … ROLLBACK`.

**Lesson:** [`15-transactions/`](../15-transactions/)

---

### 2. Reading the whole upload into memory

**What the AI writes:**
```python
content = await file.read()
dest.write_bytes(content)
```

**Why it's wrong:** A 500 MB upload uses 500 MB of RAM per request. Ten concurrent uploads crash the server. This works in tests (small files) and dies in production (real files).

**What it should look like:** Read and write in chunks — `while chunk := await file.read(1_048_576): out.write(chunk)`.

**Lesson:** [`14-file-uploads/`](../14-file-uploads/)

---

### 3. Silent exception swallowing

**What the AI writes:**
```python
try:
    do_important_thing()
except Exception:
    pass
```

**Why it's wrong:** The failure is invisible. The endpoint returns 200. The user thinks it worked. A week later you find out `do_important_thing()` has never actually run.

**What it should look like:** Either let the exception propagate (so it becomes a 500), or log it with context and return an error. Never `pass`.

**Lesson:** [`13-observability/`](../13-observability/)

---

### 4. Auth check that returns 401 when it means 403

**What the AI writes:**
```python
if user.role != "admin":
    raise HTTPException(401, "not authorized")
```

**Why it's wrong:** `401` means "you're not logged in." `403` means "you are logged in, but not allowed." The frontend treats them differently — 401 triggers a re-login loop, 403 tells the user "ask for permission." Returning 401 for a logged-in user makes the client loop forever.

**What it should look like:** `401` for missing/invalid token, `403` for valid token but insufficient role.

**Lesson:** [`03-rbac-admin/`](../03-rbac-admin/) and [`08-documentation/example-spec.md`](../08-documentation/example-spec.md)

---

### 5. SQL string concatenation

**What the AI writes:**
```python
conn.execute(f"SELECT * FROM users WHERE email = '{email}'")
```

**Why it's wrong:** SQL injection. If `email` is `' OR '1'='1`, the query returns every user. The AI often writes this when the user's prompt contains "make it simple."

**What it should look like:** Parameterised queries — `conn.execute("... WHERE email = %s", (email,))`.

**Lesson:** [`04-databases/02-postgres-crud/`](../04-databases/02-postgres-crud/)

---

### 6. No correlation ID across layers

**What the AI writes:**
```python
@app.get("/process")
def process():
    log.info("starting")                # no ID
    enqueue_job("work")                 # no ID
    return {"status": "ok"}

def worker():
    log.info("doing work")              # no ID
```

**Why it's wrong:** When something fails at 2 AM, you have three log files and no way to link them. "Which worker log line belongs to which request?" is unanswerable.

**What it should look like:** Generate a UUID at the edge, propagate it through every log line, every job payload, every tool call.

**Lesson:** [`13-observability/`](../13-observability/)

---

### 7. Blocking I/O in an async handler

**What the AI writes:**
```python
@app.get("/fetch")
async def fetch():
    response = requests.get("https://slow-api.com")   # blocking!
    return response.json()
```

**Why it's wrong:** `requests.get` is synchronous. In an `async def` handler, it blocks the entire event loop — every other request waits. Under load, the whole server freezes.

**What it should look like:** Use an async HTTP client (`httpx.AsyncClient`, `aiohttp`) inside async handlers, or run sync functions with `await asyncio.to_thread(...)`.

**Lesson:** [`12-streaming/01-fastapi-sse/main.py`](../12-streaming/01-fastapi-sse/main.py) shows the async pattern; the `async def` vs `def` distinction in [`03-rbac-admin/01-fastapi-rbac/main.py`](../03-rbac-admin/01-fastapi-rbac/main.py) is the contrast.

---

### 8. Secrets hardcoded or logged

**What the AI writes:**
```python
API_KEY = "sk-proj-abc123..."         # hardcoded
...
log.info(f"calling model with key {API_KEY}")   # logged
```

**Why it's wrong:** Hardcoded secrets end up in git history forever. Logged secrets end up in your log aggregator, visible to anyone with dashboard access.

**What it should look like:** `API_KEY = os.environ["API_KEY"]` (fail loudly if missing), and never log the value — log `"api_key set"` instead.

**Lesson:** [`13-observability/`](../13-observability/) shows structured logging; the convention is "log the ID, not the value."

---

### 9. Missing or wrong input validation

**What the AI writes:**
```python
@app.post("/user")
def create_user(data: dict):        # accepts ANY dict
    db.insert(data)
```

**Why it's wrong:** No validation. Client can send `{"role": "admin"}` and become admin. Can send 100 MB of junk. Can send fields you don't expect, which land in your database and break downstream code.

**What it should look like:** A Pydantic model with explicit fields, types, and constraints:
```python
class CreateUserRequest(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=100)]
    email: EmailStr

@app.post("/user")
def create_user(data: CreateUserRequest):
    ...
```

**Lesson:** [`10-reference/fastapi-types-example.py`](fastapi-types-example.py)

---

## How to use this file

**Before you accept an AI-generated PR:**

1. Read the diff.
2. For each function that does more than one thing (write to DB + call an API; auth + business logic; read + write), ask: **what happens if step 2 fails?**
3. For each input, ask: **what type is this, and is it validated?**
4. For each log line, ask: **can I find this log line from a request ID?**
5. For each `try/except`, ask: **what happens on the except branch?**
6. For each file read or upload, ask: **is the whole file in memory?**

If the answers are bad, the linked lesson shows the fix.

**When you're reviewing your own AI-assisted code:**

The same checklist applies. The AI is a fast typer, not a code reviewer. The reviewer is you.

---

## What's *not* on this list (and why)

Some patterns look suspicious but are usually fine:

- **`print()` instead of `log()`** — not a bug, just less useful. Not on the list because it won't cause a production incident.
- **`SELECT *` in queries** — not a bug, just less efficient. Not on the list because it rarely causes incidents at small scale.
- **Missing type hints** — not a bug in Python. Not on the list because it's a style issue.
- **`time.sleep(0.1)` between requests** — sometimes intentional (rate limiting on the client side). Not on the list because the context matters.

The list is **incidents waiting to happen**, not code style. Every item has caused real outages.

---

## The one-sentence version

**The most common AI-generated backend bug is: "it works in the test, it loses money in production"** — and almost always because the AI wrote the happy path and forgot what happens when step 2 fails.

The second most common is: **the AI reads a file into memory because `await file.read()` is the obvious thing to write**, and the server dies on the first real upload.

If you remember those two, you'll catch most of them.

---

## In another language?

Every pitfall on this list exists in every language:

| Pitfall | Go | Rust | Node | Java |
|---|---|---|---|---|
| No transaction | `db.Begin()` missing | `tx.commit()` missing | `prisma.$transaction` missing | `setAutoCommit(false)` missing |
| Buffered upload | `io.ReadAll(r.Body)` | `body.collect().await` | `await req.arrayBuffer()` | `in.readAllBytes()` |
| Silent exception | `if err != nil {}` | `let _ = result;` | `try { } catch {}` | `catch (Exception e) {}` |
| 401 vs 403 | same | same | same | same |
| SQL concatenation | `fmt.Sprintf(query, x)` | `format!("{}", x)` | `` `...${x}` `` | `"... " + x` |
| No correlation ID | missing `ctx` | missing `span` | missing `AsyncLocalStorage` | missing MDC |
| Blocking in async | `time.Sleep` in goroutine | `block_on` in async | `fs.readFileSync` in async | `Thread.sleep` in reactive |
| Hardcoded secrets | same | same | same | same |
| No validation | same | same | same | same |

The AI doesn't write bugs in only one language. The checklist is language-agnostic.