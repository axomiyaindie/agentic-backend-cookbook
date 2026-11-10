```
# API Spec — Example: RBAC lesson

This is the API spec for the lesson in `03-rbac-admin/01-fastapi-rbac/`.
It shows what a real, complete spec looks like — every endpoint documented,
including the error cases that matter.

Base URL: `http://127.0.0.1:8000`

---

## `POST /login`

Exchange a username and password for a token. Public endpoint — no
authentication required.

**Auth:** Public

### Request

```json
{
  "username": "admin",
  "password": "admin"
}
```

### Response — 200 OK

```json
{
  "token": "token-admin",
  "role": "admin"
}
```

### Response — 401 Unauthorized

Returned when the username doesn't exist or the password is wrong.

```json
{
  "detail": "bad credentials"
}
```

### Example

```bash
curl -X POST http://127.0.0.1:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin"}'
```

### Notes

- The token is a plain string in this lesson. **Real apps use JWT.**
- This endpoint is not rate-limited in the lesson. In production it should be.

---

## `GET /me`

Return the role of the currently authenticated user. Works for any
logged-in role.

**Auth:** Logged in (any role)

### Request

Headers:
```
Authorization: Bearer <token>
```

No body, no params.

### Response — 200 OK

```json
{
  "role": "user"
}
```

### Response — 401 Unauthorized

Returned when the `Authorization` header is missing or the token is invalid.

```json
{
  "detail": "missing token"
}
```

or

```json
{
  "detail": "invalid token"
}
```

The two messages are different on purpose — "missing" tells the client
to log in, "invalid" tells them to log in again because their session
expired. See the note below on 401 vs 403.

### Example

```bash
curl http://127.0.0.1:8000/me \
  -H "Authorization: Bearer token-user"
```

---

## `GET /admin/users`

List all users and their roles. **Admin only.**

**Auth:** Admin

### Request

Headers:
```
Authorization: Bearer <token>
```

No body, no params.

### Response — 200 OK

```json
[
  {"username": "admin", "role": "admin"},
  {"username": "user",  "role": "user"}
]
```

### Response — 401 Unauthorized

Missing or invalid token.

```json
{
  "detail": "missing token"
}
```

### Response — 403 Forbidden

Valid token, but the role is not `admin`.

```json
{
  "detail": "insufficient role"
}
```

**This is the whole lesson in one status code.** The client is
authenticated (the token is real), but not authorized (the role doesn't
have permission). A client should never retry a 403 — the request will
never succeed without a role change.

### Example

```bash
# As admin — 200 OK
curl http://127.0.0.1:8000/admin/users \
  -H "Authorization: Bearer token-admin"

# As user — 403 Forbidden
curl http://127.0.0.1:8000/admin/users \
  -H "Authorization: Bearer token-user"
```

---

## `DELETE /admin/users/{username}`

Delete a user by username. **Admin only.**

**Auth:** Admin

### Request

Path parameter:

| Param | Type | Notes |
|---|---|---|
| `username` | string | The username to delete |

Headers:
```
Authorization: Bearer <token>
```

### Response — 200 OK

```json
{
  "deleted": "user"
}
```

### Response — 401 Unauthorized

```json
{
  "detail": "missing token"
}
```

### Response — 403 Forbidden

```json
{
  "detail": "insufficient role"
}
```

### Response — 404 Not Found

The authenticated user is an admin, but no user with that username exists.

```json
{
  "detail": "no such user"
}
```

**Notice the order of checks.** The server checks 401 first, then 403,
then 404. That's correct: don't reveal whether a resource exists to a
caller who isn't allowed to know.

### Example

```bash
curl -X DELETE http://127.0.0.1:8000/admin/users/user \
  -H "Authorization: Bearer token-admin"
```

---

## 401 vs 403 — the difference that trips everyone up

Both are "you can't do this", but the fix is different:

| Status | Meaning | What the client should do |
|---|---|---|
| **401 Unauthorized** | You're not logged in (or your token is invalid) | Log in, then retry |
| **403 Forbidden** | You're logged in, but your role doesn't allow this | **Don't retry.** Ask for a role change, or use a different account |

Getting this wrong is one of the most common API bugs:

- Returning **401** when the user is logged in but unauthorized →
  the client will keep re-authenticating in a loop.
- Returning **403** when the user isn't logged in → the client thinks
  logging in again won't help, and gives up.

The RBAC lesson gets this right. That's one of the things it teaches.

---

## Error response shape

All error responses use FastAPI's default shape:

```json
{
  "detail": "<human-readable message>"
}
```

If you're building a frontend or an AI client, code against this shape —
not against the specific message string. Messages can change; the shape
is a contract.

---

## Summary table

| Method | Path | Auth | Success | Errors |
|---|---|---|---|---|
| `POST` | `/login` | Public | 200 | 401 |
| `GET` | `/me` | Logged in | 200 | 401 |
| `GET` | `/admin/users` | Admin | 200 | 401, 403 |
| `DELETE` | `/admin/users/{username}` | Admin | 200 | 401, 403, 404 |

That table is the spec. Everything above it is the detail.
```