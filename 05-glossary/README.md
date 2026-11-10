# Glossary

Plain-English definitions of every term used in this repo. If a lesson
uses a word you don't know, it should be here.

## API and HTTP

**API** — a contract that says "send me this shape, I'll send you that shape".

**HTTP verb** — the *action* part of a request: `GET` (read), `POST` (create),
`PUT` (replace), `PATCH` (change), `DELETE` (remove).

**Endpoint** — a URL path + verb that does something. `GET /users/42` is
an endpoint. `POST /login` is an endpoint.

**Status code** — the number the server sends back. `200` = ok, `201` =
created, `204` = ok but no body, `400` = bad request, `401` = not logged in,
`403` = logged in but not allowed, `404` = not found, `500` = server bug.

**Header** — metadata sent alongside a request. `Authorization: Bearer ...`
is a header. `Content-Type: application/json` is a header.

**Body** — the data part of a request or response. In JSON APIs, the body
is a JSON object.

## Types and validation

**Type** (TypeScript) — a description of a value's shape, checked at compile
time. Doesn't exist at runtime. If the type says `email: string`, TypeScript
won't stop a user from typing `"not-an-email"` into that field.

**Schema** (JSON Schema / Pydantic) — a description of a value's shape,
checked at *runtime*. This is what actually rejects bad input. Types check
*your* code; schemas check *the caller's* data.

**Validation** — the act of checking that incoming data matches a schema.
Always happens on the server, regardless of what the client claims.

## Authentication and access control

**Authentication** — proving *who* you are. Usually a password, then a token.

**Authorization** — deciding *what* you're allowed to do. RBAC is one way.

**RBAC** — Role-Based Access Control. Permissions are attached to *roles*,
and users have roles. "Admins can delete, users can't."

**Token** — a string the client sends on each request to prove who it is.
Real apps use JWTs; this repo uses plain strings for teaching.

**JWT** — JSON Web Token. A signed, self-contained token that carries
claims (like the user's role) and an expiry. Signed so the server can
verify it wasn't tampered with.

**Dependency injection** — a pattern where a function declares "I need X"
instead of creating X itself. In FastAPI, `Depends(...)` does this. It's
how `require_role("admin")` gets plugged into an endpoint.

## MCP and AI tooling

**MCP** — Model Context Protocol. A standard way for AI clients to discover
and call tools. Tools have a name, description, input schema, and handler.

**Tool** (MCP) — one callable function exposed to an AI client.
`add_numbers` is a tool. `get_weather` is a tool.

**JSON-RPC** — the message format MCP uses. Every message is a JSON object
with `jsonrpc`, `method`, `params`, `id`.

## Databases

**Relational database** — stores data in tables with typed columns and
foreign-key relationships. Postgres and MySQL are relational.

**Document database** — stores JSON-like documents in collections. MongoDB
is a document database. No fixed schema.

**Key-value / wide-column database** — data is keyed by a partition key,
and access must go through it. DynamoDB is this kind.

**Schema** (database) — the structure of a table: its columns, their types,
and their constraints. `CREATE TABLE ...` defines a schema.

**Partition key** — the field DynamoDB uses to decide which physical shard
stores an item. Queries must include it to be fast.

**Index** — a data structure the database maintains to make certain lookups
fast. In DynamoDB you must design your keys up front; in Postgres you can
add indexes after the fact.

**Query** — asking the database for data. In SQL, a `SELECT`. In DynamoDB,
a `Query` operation with a key condition.

**Scan** — reading every item in a table. In DynamoDB, expensive and
discouraged. There is no cheap `Scan` at scale.

**Migration** — a versioned change to your database schema. Real apps run
migrations instead of hand-editing the database.

## Security (mentioned but not implemented here)

**SQL injection** — an attack where user input is concatenated into a SQL
string and changes what the query does. Prevented by parameterised queries.

**Parameterised query** — a SQL query where values are passed separately
from the query text (`%s`, `$1`, `?` placeholders). Prevents SQL injection.

**Hashing** (passwords) — storing a one-way transformation of a password
(bcrypt, argon2) instead of the password itself. If the database leaks,
the attacker still can't log in. This repo does **not** do this — it's a
teaching shortcut, not a real implementation.