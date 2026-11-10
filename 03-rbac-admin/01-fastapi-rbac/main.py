# ─────────────────────────────────────────────────────────────
# Lesson: RBAC in FastAPI
#
# The pattern in ~90 lines:
#   1. Login returns a "token" that encodes the user's role.
#   2. A dependency (`require_role`) reads the token and checks the role.
#   3. Endpoints declare which roles they accept.
#
# We use plain strings as tokens for teaching. Real apps use JWT.
# ─────────────────────────────────────────────────────────────

from fastapi import Depends, FastAPI, Header, HTTPException, status
from pydantic import BaseModel

app = FastAPI(title="RBAC lesson")

# In a real app this would be a DB table with hashed passwords.
USERS = {
    "admin": {"password": "admin", "role": "admin"},
    "user":  {"password": "user",  "role": "user"},
}

# Token → username. Fake session store for teaching.
SESSIONS: dict[str, str] = {}


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    role: str


# ── Login ────────────────────────────────────────────────────
@app.post("/login", response_model=LoginResponse)
def login(body: LoginRequest):
    user = USERS.get(body.username)
    if not user or user["password"] != body.password:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "bad credentials")
    token = f"token-{body.username}"  # NOT a real token
    SESSIONS[token] = body.username
    return {"token": token, "role": user["role"]}


# ── Dependency: resolve token → role ─────────────────────────
def get_current_role(authorization: str = Header(default="")) -> str:
    # Expect header: "Authorization: Bearer <token>"
    if not authorization.startswith("Bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "missing token")
    token = authorization.removeprefix("Bearer ").strip()
    username = SESSIONS.get(token)
    if not username:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid token")
    return USERS[username]["role"]


# ── Dependency factory: require one of these roles ───────────
def require_role(*allowed: str):
    def _checker(role: str = Depends(get_current_role)) -> str:
        if role not in allowed:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "insufficient role")
        return role
    return _checker


# ── Endpoints ────────────────────────────────────────────────
@app.get("/me")
def me(role: str = Depends(get_current_role)):
    """Any logged-in user."""
    return {"role": role}


@app.get("/admin/users")
def list_users(_role: str = Depends(require_role("admin"))):
    """Admin only."""
    return [{"username": u, "role": v["role"]} for u, v in USERS.items()]


@app.delete("/admin/users/{username}")
def delete_user(username: str, _role: str = Depends(require_role("admin"))):
    """Admin only."""
    if username not in USERS:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "no such user")
    del USERS[username]
    return {"deleted": username}


# ─────────────────────────────────────────────────────────────
# Exercise:
#   1. Log in as `user`, copy the token.
#   2. Call GET /admin/users with "Authorization: Bearer token-user".
#      → 403 Forbidden. That's RBAC working.
#   3. Add a "moderator" role allowed to read /admin/users but not delete.
#      Hint: change the two `require_role(...)` calls.
# ─────────────────────────────────────────────────────────────