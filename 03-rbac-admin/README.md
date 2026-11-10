# RBAC admin panel

**RBAC** = Role-Based Access Control.

The core question this lesson answers:
> "How does the server know that *this* user is allowed to do *that*?"

The pattern:
1. User logs in → server issues a token (or session).
2. Token carries the user's **role** (e.g. `admin`, `user`).
3. Every protected endpoint checks: *does this role have this permission?*

## Lesson
`01-fastapi-rbac/` — a single-file FastAPI app with:
- `POST /login` → returns a fake token containing the role
- `GET /me` → any logged-in user
- `GET /admin/users` → admin only
- `DELETE /admin/users/{id}` → admin only

This is the smallest possible demo of the pattern. Real apps use
JWT + a DB for users/roles, but the **shape** is the same.

## What "admin panel" means here

Not a UI. The "admin panel" is the set of endpoints an admin client
would call. The lesson proves the **access control**, not the interface.
A real admin panel is a frontend that hits these endpoints with an
admin token — that part is out of scope.

---

## In another language?

RBAC is universal. Every language has a way to (a) resolve identity
from a request, (b) attach a role, (c) reject when the role is wrong.

| Language | Identity | Role check |
|---|---|---|
| Go | middleware reads `Authorization` header | `if role != "admin" { 403 }` |
| Rust | extractor reads header, returns `Claims` | `guard` fn in axum/tower |
| PHP | Laravel `Gate::allows('admin')` | policy classes |
| Ruby | `before_action :require_admin` | Pundit policies |
| Java | Spring Security `@PreAuthorize("hasRole('ADMIN')")` | method security |
| C# | `[Authorize(Roles = "Admin")]` | ASP.NET Core policies |
| Python | FastAPI `Depends(require_role("admin"))` | ← this lesson |

The shape is always the same three steps. Only the syntax changes.

If you're not using a framework: any request has headers, any header
can carry a token, any token can map to a role in your database. That
mapping *is* RBAC. The framework just saves you writing it by hand.