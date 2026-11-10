✅ FILE 4 pushed: `0b7aa9d..78dbf3c`, 65 insertions, and the line count confirms **57 lines** — real content, not empty. That lesson is now complete and runnable.

---

## FILE 5 of 27

**Path:**
```
D:\agentic-backend-cookbook\01-api-design\02-crud-model\README.md
```

**Open it:**
```powershell
code D:\agentic-backend-cookbook\01-api-design\02-crud-model\README.md
```

**Paste this:**
```
# CRUD models

## What you'll learn
- How Create/Read/Update/Delete map to HTTP verbs
- Why `PUT` and `PATCH` are different
- What status codes to return for each

## How to run
```bash
npx tsx example.ts
```

## What to look at
- `example.ts` — a tiny in-memory "resource" implemented four ways.

---

## In another language?

CRUD is the same four operations in every language. What changes is
the HTTP framework and the data structure underneath:

| Language | HTTP framework | In-memory store |
|---|---|---|
| Go | `net/http` + chi | `map[int]User` + `sync.RWMutex` |
| Rust | axum or actix-web | `HashMap<i64, User>` + `Mutex` |
| PHP | Laravel or Slim | array + session |
| Ruby | Sinatra or Rails | Hash |
| Java | Spring Boot | `ConcurrentHashMap<Long, User>` |
| C# | ASP.NET Core minimal APIs | `ConcurrentDictionary<long, User>` |

The mapping is universal:

| Operation | HTTP verb | Status code |
|---|---|---|
| Create | `POST` | 201 Created |
| Read one | `GET` | 200 OK / 404 Not Found |
| Read all | `GET` | 200 OK |
| Update (partial) | `PATCH` | 200 OK / 404 Not Found |
| Replace | `PUT` | 200 OK / 404 Not Found |
| Delete | `DELETE` | 204 No Content / 404 Not Found |
```