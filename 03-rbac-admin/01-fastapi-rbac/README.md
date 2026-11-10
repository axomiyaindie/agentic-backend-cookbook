✅ FILE 11 pushed: `cd6abc0..084d59d`, 51 insertions.

---

## FILE 12 of 27

**Path:**
```
D:\agentic-backend-cookbook\03-rbac-admin\01-fastapi-rbac\README.md
```

**Open it:**
```powershell
code D:\agentic-backend-cookbook\03-rbac-admin\01-fastapi-rbac\README.md
```

**Paste this:**
```
# FastAPI RBAC

## What you'll learn
- How a request carries identity (a token in `Authorization`)
- How the server resolves a token → role
- How a dependency checks the role and rejects with 403

## How to run
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Then open <http://127.0.0.1:8000/docs> and try the endpoints.

## Demo users
| Username | Password | Role |
|---|---|---|
| admin | admin | admin |
| user  | user  | user |

## What to look at
- `main.py` — read `get_current_role` first, then the endpoints.

## Walkthrough — prove it works

1. `POST /login` with `{"username": "admin", "password": "admin"}`
   → copy the returned `token`.
2. Click **Authorize** (top right of `/docs`), paste `Bearer <token>`.
3. `GET /admin/users` → **200 OK** with the user list.
4. Log out, log in as `user`/`user`, repeat step 2.
5. `GET /admin/users` → **403 Forbidden** with
   `{"detail": "insufficient role"}`.

That 403 is RBAC working. The endpoint didn't disappear — the server
still knows it exists. It just refused to run it for this role.

---

## In another language?

| Language | Equivalent middleware/guard |
|---|---|
| Go | `func requireRole(r *http.Request, roles ...string) error` |
| Rust | axum extractor that returns `Result<Claims, StatusCode>` |
| PHP | `Route::middleware('can:admin')` (Laravel) |
| Ruby | `before_action :require_admin` |
| Java | `@PreAuthorize("hasRole('ADMIN')")` (Spring Security) |
| C# | `[Authorize(Roles = "Admin")]` on the controller/action |

Two ideas are portable no matter what:
1. **Identity extraction** — pull the token out of the request header.
2. **Role check** — compare the role against what the endpoint allows.

FastAPI's `Depends(...)` is just a clean way to compose those two steps.
In Go, you'd write them as a middleware function. In Java, as an
annotation. Same logic, different ergonomics.

## Important note

The tokens in this lesson are fake (`"token-admin"`, `"token-user"`).
Real apps should:
- Use **JWT** (signed, with expiry) or opaque tokens in a DB.
- Store passwords **hashed** (bcrypt/argon2), never plain.
- Rotate tokens, enforce HTTPS, set short expiries.

This lesson teaches the **access control pattern** — not auth itself.
```