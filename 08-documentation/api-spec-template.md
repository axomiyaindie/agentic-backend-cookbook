# API Spec — Template

Copy this file for each endpoint you document. Fill in every section.
If a section doesn't apply, write "N/A — <reason>" instead of deleting
it, so the reader knows you considered it.

---

## Endpoint name

One sentence describing what this endpoint is for.

**Method:** `POST`

**Path:** `/users`

**Auth:** Public | Logged in | Admin only | API key

---

## Request

### Headers

| Header | Required | Value |
|---|---|---|
| `Content-Type` | yes | `application/json` |
| `Authorization` | no (but required for logged-in) | `Bearer <token>` |

### Path parameters

_None._

### Query parameters

_None._

### Body

```json
{
  "name": "string",
  "email": "string (must contain @)"
}
```

**Field notes:**

- `name` — 1–100 characters, required
- `email` — must be a valid email, must be unique, required

---

## Response

### 201 Created

```json
{
  "id": 1,
  "name": "Rakibul",
  "email": "rakibul@example.com"
}
```

### 400 Bad Request

```json
{
  "detail": "invalid email"
}
```

### 409 Conflict

```json
{
  "detail": "email already in use"
}
```

### 401 Unauthorized

```json
{
  "detail": "missing token"
}
```

### 429 Too Many Requests

Headers:
```
Retry-After: 30
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 0
```

Body:
```json
{
  "detail": "rate limit exceeded"
}
```

---

## Example

```bash
curl -X POST http://127.0.0.1:8000/users \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer token-admin" \
  -d '{"name":"Rakibul","email":"rakibul@example.com"}'
```

---

## Notes

- Free-form: anything the caller needs to know that doesn't fit above.
  For example: "This endpoint is cached for 5 seconds. Responses may be
  slightly stale."
```