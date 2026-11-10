# ─────────────────────────────────────────────────────────────
# Reference: Pydantic request/response models in FastAPI
#
# This file shows how the API concepts from `api-styles.md` become
# real Python code. It doesn't cover FastAPI routing or auth —
# those are in `01-api-design/` and `03-rbac-admin/`.
#
# The point: typed request/response models are how FastAPI turns
# a REST endpoint into a contract that a client (human or AI) can
# read.
#
# Run with:
#   pip install fastapi uvicorn pydantic
#   uvicorn fastapi-types-example:app --reload
# Then open http://127.0.0.1:8000/docs
# ─────────────────────────────────────────────────────────────

from typing import Annotated
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr, Field


# ─────────────────────────────────────────────────────────────
# 1. The core idea: one model for input, one for output.
#
# The REQUEST model is what the client sends.
# The RESPONSE model is what the server sends back.
#
# They are different on purpose. The request never contains an
# `id` — the server assigns it. The response always contains `id`.
# ─────────────────────────────────────────────────────────────

# Request: what the client sends to create a user.
class CreateUserRequest(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=100)]
    email: EmailStr


# Response: what the server sends back.
# `response_model=` on an endpoint tells FastAPI to filter the
# output through this model, so extra fields don't leak.
class UserResponse(BaseModel):
    id: int
    name: str
    email: str


# ─────────────────────────────────────────────────────────────
# 2. Nested models: when a response contains another object.
# ─────────────────────────────────────────────────────────────

class PostSummary(BaseModel):
    id: int
    title: str


class UserWithPosts(BaseModel):
    id: int
    name: str
    email: str
    posts: list[PostSummary] = []


# ─────────────────────────────────────────────────────────────
# 3. Pagination: the shape most list endpoints actually use.
#
# Real APIs need pagination. The shape is always the same:
# items + total count + cursor or page info.
# ─────────────────────────────────────────────────────────────

class Page[T](BaseModel):
    items: list[T]
    total: int
    page: int
    page_size: int


# ─────────────────────────────────────────────────────────────
# 4. Update models: partial updates via PATCH.
#
# Every field is Optional. The client sends only what changed.
# This is why the `PUT` vs `PATCH` distinction matters — PUT
# requires all fields; PATCH allows subsets.
# ─────────────────────────────────────────────────────────────

class UpdateUserRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None


# ─────────────────────────────────────────────────────────────
# 5. Error models: the shape of every 4xx/5xx response.
#
# FastAPI's default error shape is `{"detail": "..."}`. If you
# return a custom error model, use the same top-level key so
# clients can code against one shape.
# ─────────────────────────────────────────────────────────────

class ErrorResponse(BaseModel):
    detail: str


# ─────────────────────────────────────────────────────────────
# 6. The app: endpoints that use these models.
#
# Notice how `response_model=` makes the contract explicit at
# the endpoint level. A client reading `/docs` sees exactly what
# shape each endpoint returns — because FastAPI uses the type
# annotations to generate the OpenAPI schema.
# ─────────────────────────────────────────────────────────────

app = FastAPI(
    title="Pydantic types reference",
    description="Typed request/response models for REST APIs",
)

# A fake database. Replace with a real one in production.
_USERS: dict[int, dict] = {
    1: {"id": 1, "name": "Rakibul", "email": "rakibul@example.com"},
}
_next_id = {"n": 2}


@app.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input"},
    },
)
def create_user(body: CreateUserRequest):
    # FastAPI already validated `body` against `CreateUserRequest`
    # before this function runs. If we got here, name and email
    # passed their Field constraints.
    user = {
        "id": _next_id["n"],
        "name": body.name,
        "email": body.email,
    }
    _USERS[user["id"]] = user
    _next_id["n"] += 1
    return user


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    user = _USERS.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user not found",
        )
    return user


@app.get("/users", response_model=Page[UserResponse])
def list_users(page: int = 1, page_size: int = 20):
    all_users = list(_USERS.values())
    start = (page - 1) * page_size
    end = start + page_size
    return {
        "items": all_users[start:end],
        "total": len(all_users),
        "page": page,
        "page_size": page_size,
    }


@app.patch("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, body: UpdateUserRequest):
    user = _USERS.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user not found",
        )
    # PATCH semantics: only change fields the client sent.
    if body.name is not None:
        user["name"] = body.name
    if body.email is not None:
        user["email"] = body.email
    return user


# ─────────────────────────────────────────────────────────────
# Exercise:
#   1. Run the server. Open /docs.
#   2. Look at the schema under "Schemas" at the bottom of the
#      page. That is generated entirely from the Pydantic models
#      above. No manual schema writing.
#   3. POST to /users with an invalid email. The server returns
#      422 with the exact field that failed — because EmailStr
#      did its job at the request boundary.
#   4. Add a `posts: list[PostSummary] = []` field to UserResponse,
#      then return a user with posts. The response model validates
#      the nested shape too.
#   5. Change `page_size: int = 20` to
#      `page_size: Annotated[int, Field(ge=1, le=100)] = 20`.
#      Now FastAPI rejects page_size=1000 with a 422.
# ─────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────
# Why this matters for AI-generated code
#
# When an AI assistant generates a FastAPI endpoint, it almost
# always produces a Pydantic model for the request and one for
# the response. The patterns above are the ones it uses. If you
# can read these five model types (create, response, nested,
# pagination, patch), you can read any FastAPI code an assistant
# produces — and tell whether it's typing its inputs properly.
#
# What to look for:
#   ✅ `response_model=` on every endpoint
#   ✅ Separate Create/Response models (not one model for both)
#   ✅ `EmailStr` or `Field(min_length=...)` for validation
#   ✅ Optional fields in update models
#   ❌ A raw `dict` accepted as input
#   ❌ No `response_model=` (leaks internal fields)
#   ❌ `BaseModel` used without any field constraints
#
# If an AI-generated endpoint has ❌ items, that's where to ask
# questions before shipping.
# ─────────────────────────────────────────────────────────────