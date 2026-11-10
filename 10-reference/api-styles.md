# API styles

Four ways to expose a backend: REST, GraphQL, gRPC, SOAP. Each exists
because it solves a problem the others don't. This file explains *what
each style is* and *why you would pick one over another*. The runnable
lessons in `01-api-design/` show how to implement the default (REST).

## The decision, in one table

| If you need... | Pick | Why |
|---|---|---|
| Simple CRUD for web/mobile, cacheable, universally understood | **REST** | Default. 92% of orgs use it. |
| Clients that need different fields, mobile + web together | **GraphQL** | One endpoint, client picks fields, no over-fetching. |
| Fast internal service-to-service, streaming, binary payloads | **gRPC** | HTTP/2 + Protobuf. 10–100× faster than JSON-RPC. |
| Enterprise integration, healthcare/finance/legacy | **SOAP** | WS-Security, XML schema, still required by many industries. |

That's the whole file in one table. The rest explains each row.

---

## 1. REST

### What REST actually is

REST stands for **Representational State Transfer**. It was defined by
Roy Fielding in his 2000 PhD dissertation, as a set of architectural
constraints for distributed systems. Most "REST APIs" implement only some
of those constraints, so "REST" in practice means **"HTTP + JSON with a
specific URL convention"**. That's what this file means by REST.

Three ideas:

**1. Everything is a resource.** A resource is any "thing" the client
might want: a user, an order, a comment, a photo. Each resource has an
identity — a URL. `GET /users/42` asks for the resource at `/users/42`,
which is user 42. `POST /users` creates a new user in the `/users`
collection. The URL names the thing; the verb names the action.

**2. Operations are HTTP verbs.** The same URL does different things
depending on the method:

| Verb | What it does | Idempotent? | Example |
|---|---|---|---|
| `GET` | Read | Yes | `GET /users/42` → return user 42 |
| `POST` | Create | **No** | `POST /users` → create a new user |
| `PUT` | Replace | Yes | `PUT /users/42` → replace user 42 with the body |
| `PATCH` | Update | Yes | `PATCH /users/42` → change only the fields in the body |
| `DELETE` | Delete | Yes | `DELETE /users/42` → remove user 42 |

"Idempotent" means: calling it twice has the same effect as calling it
once. `PUT /users/42` twice leaves user 42 in the same state as
`PUT /users/42` once. `POST /users` twice creates **two users** — that's
why POST is not idempotent, and why retrying a POST is dangerous (see
`16-idempotency/`).

**3. Responses are self-describing.** Every response carries a **status
code** that tells the client what happened, without the client needing to
parse the body:

| Code | Meaning | When |
|---|---|---|
| `200 OK` | Success | `GET`, `PATCH`, `PUT`, `DELETE` that returns a body |
| `201 Created` | A new resource was created | `POST` |
| `204 No Content` | Success, no body | `DELETE` |
| `400 Bad Request` | The client's input is invalid | Malformed JSON, missing field |
| `401 Unauthorized` | Not logged in | Missing or invalid token |
| `403 Forbidden` | Logged in, but not allowed | Valid token, wrong role |
| `404 Not Found` | The resource doesn't exist | `GET /users/9999` |
| `409 Conflict` | The request conflicts with current state | Duplicate email, idempotency key in progress |
| `422 Unprocessable Entity` | Valid JSON, but semantic errors | Field validation failed |
| `429 Too Many Requests` | Rate limited | Over the limit (see `07-rate-limiting/`) |
| `500 Internal Server Error` | The server has a bug | Unhandled exception |

This is why REST is more than "HTTP with JSON". The status code *is* the
contract. A client that sees `403` knows to show "you don't have
permission." A client that sees `401` knows to log in. They are not the
same thing, and the difference matters. The
[`03-rbac-admin/`](../03-rbac-admin/) and
[`08-documentation/example-spec.md`](../08-documentation/example-spec.md)
lessons demonstrate this.

### What a REST request actually looks like

Fetch user 42:

```http
GET /users/42 HTTP/1.1
Host: api.example.com
Authorization: Bearer token-user
```

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": 42,
  "name": "Rakibul",
  "email": "rakibul@example.com"
}
```

Create a user:

```http
POST /users HTTP/1.1
Host: api.example.com
Authorization: Bearer token-admin
Content-Type: application/json

{
  "name": "New User",
  "email": "new@example.com"
}
```

```http
HTTP/1.1 201 Created
Location: /users/43
Content-Type: application/json

{
  "id": 43,
  "name": "New User",
  "email": "new@example.com"
}
```

The `Location` header in the 201 response is part of the REST
convention — it tells the client where to find the new resource.

### The constraints that make it REST

Fielding defined six constraints. Most modern "REST APIs" implement the
first two and skip the rest. That's fine — nobody is grading you — but
it's worth knowing what "REST" actually means:

| Constraint | What it means | Do modern REST APIs follow it? |
|---|---|---|
| **Client-server** | Separate the UI from the data storage | Yes |
| **Stateless** | Every request carries everything the server needs (auth token, not a session) | Yes |
| **Cacheable** | Responses declare whether they can be cached | Sometimes |
| **Uniform interface** | Resources, verbs, self-descriptive messages | Yes |
| **Layered system** | The client doesn't know if it's talking to the origin server or a proxy | Yes |
| **Code on demand** (optional) | The server can send executable code (JavaScript) to the client | Rarely |

"Stateless" is the one that matters most in practice: **every request
must include the auth token**. There is no server-side session. This is
why REST scales — any server can handle any request.

### Strengths

- **Universal.** Every language, every tool, every proxy, every browser
  understands HTTP. There is no "REST client" to install.
- **Cacheable** via standard HTTP headers (`Cache-Control`, `ETag`).
  The browser can cache a `GET` response; nothing else needs to know.
- **Human-readable.** You can `curl` a REST endpoint and read the
  response. You can't do that with gRPC.
- **Stateless.** Any server can handle any request. Scale by adding
  servers, not by adding sessions.
- **Status codes mean something.** 200 / 401 / 403 / 404 / 429 are the
  contract between client and server.

### Trade-offs

- **Over-fetching.** The server decides what fields to return.
  `GET /users/42` might return 20 fields when the client needed 2.
- **Under-fetching.** To get user 42 and their 3 latest posts, you might
  need two requests (`GET /users/42`, then `GET /users/42/posts?limit=3`).
  GraphQL exists partly to fix this.
- **No built-in streaming.** REST returns the whole response. Streaming
  needs SSE (see `12-streaming/`) or WebSockets (`17-websockets/`).
- **Versioning is manual.** `/v1/users` vs `/v2/users` — the URL carries
  the version. Some teams prefer headers; both work.

### When to pick REST

**Almost always for the first API.** Public-facing, documented, cacheable,
universally understood. The default for a reason.

REST is wrong when:

- **Clients have very different field needs** → GraphQL
- **You're calling a service from another service** → gRPC
- **The other party requires SOAP** → SOAP

If none of those is true, REST is the answer.

### Usage

92% of organizations use REST APIs — highest of any style.

### Where this cookbook implements it

- [`01-api-design/`](../01-api-design/) — typed requests, CRUD verbs
- [`03-rbac-admin/`](../03-rbac-admin/) — REST with auth, 200/403/401
- [`15-transactions/`](../15-transactions/) — REST writes with transactions
- [`16-idempotency/`](../16-idempotency/) — REST retries, safe
- [`18-webhooks/`](../18-webhooks/) — REST receiving inbound POSTs

If you can read any of those, you can read any REST API.

---

## 2. GraphQL

**What it is:** A single endpoint (`POST /graphql`) that takes a query
describing exactly what the client wants. The server resolves the query
against multiple data sources and returns only the requested fields.

**Strengths:** No over-fetching, no under-fetching. Client specifies shape.
Strongly typed schema. One round-trip for related data. Great for mobile
(less bandwidth) and SPAs (fewer requests).

**Trade-offs:** Caching is harder (POST, custom cache keys). Complexity
moves to the server (resolvers, N+1 queries). Authorization is per-field,
not per-endpoint. Not human-readable over `curl` without a client.

**When to pick it:** When clients have different needs (mobile wants fewer
fields, web wants more), or when you'd otherwise build 5 REST endpoints
that all call the same database.

**Usage:** ~70% of developers report using GraphQL, up from ~61% in 2024.

**A real request:**

```graphql
query {
  user(id: 42) {
    name
    email
    posts(last: 3) {
      title
    }
  }
}
```

```json
{
  "data": {
    "user": {
      "name": "Rakibul",
      "email": "rakibul@example.com",
      "posts": [
        { "title": "Hello" },
        { "title": "World" },
        { "title": "Again" }
      ]
    }
  }
}
```

**One request, three resources, exactly the fields requested.** That's the
GraphQL pitch. The cost: you now need a schema, resolvers, and a client
library (Apollo, urql, Relay).

---

## 3. gRPC

**What it is:** A binary RPC protocol over HTTP/2. You define services and
messages in a `.proto` file, and `protoc` generates client and server code
in your language. The wire format is Protobuf (binary, schema-required).

**Strengths:** Very fast (binary payloads, HTTP/2 multiplexing). Strong
typing across languages (the `.proto` file is the contract). Built-in
streaming (server, client, and bidirectional). Code generation eliminates
"the client and server disagree about the shape" bugs.

**Trade-offs:** Not browser-native (needs gRPC-Web or a proxy). Binary is
opaque over `curl` (needs `grpcurl` or reflection). Schemas are a
commitment. Not human-friendly for debugging.

**When to pick it:** Internal service-to-service communication,
microservices, high-throughput low-latency, streaming data.

**Usage:** ~44% of developers use gRPC, up from ~35% in 2024. It's
growing fastest in service-to-service and AI workloads, where binary
efficiency matters.

**A real proto definition:**

```proto
syntax = "proto3";

service Users {
  rpc GetUser (GetUserRequest) returns (User);
}

message GetUserRequest {
  int64 id = 1;
}

message User {
  int64 id = 1;
  string name = 2;
  string email = 3;
}
```

Once `protoc` runs, you have a `Users` client in Go, a `Users` server in
Python, and the shapes are guaranteed to match. No hand-written JSON
marshalling, no drift.

---

## 4. SOAP

**What it is:** XML envelopes over HTTP (usually POST). Every service is
described by a WSDL (Web Services Description Language) file. Operations
are defined by name; the envelope carries the headers and body.

**Strengths:** WS-Security (enterprise-grade auth), WS-ReliableMessaging
(guaranteed delivery), WS-AtomicTransaction. Standards-based, mature.

**Trade-offs:** Verbose (every request is a full XML envelope). Slow
(parsing XML is expensive). Complex tooling. Not what anyone chooses for
a greenfield project in 2026.

**When to pick it:** You don't choose SOAP. SOAP chooses you — because
you're integrating with a bank, a hospital system, a government API, or a
legacy enterprise service that requires it.

**Usage:** ~38% of developers still use SOAP, almost entirely because of
legacy or industry requirements — healthcare (HL7), finance (SWIFT,
FIX), telecom (TM Forum), government procurement.

**A real request:**

```xml
<?xml version="1.0"?>
<soap:Envelope
    xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Header>
    <wsse:Security xmlns:wsse="...">
      <wsse:UsernameToken>
        <wsse:Username>admin</wsse:Username>
        <wsse:Password>secret</wsse:Password>
      </wsse:UsernameToken>
    </wsse:Security>
  </soap:Header>
  <soap:Body>
    <GetUser xmlns="http://example.com/users">
      <id>42</id>
    </GetUser>
  </soap:Body>
</soap:Envelope>
```

That's a lot of boilerplate to fetch one user. It exists because WS-Security
and WS-ReliableMessaging solve problems REST doesn't natively — but for
most new APIs, the cost outweighs the benefit.

---

## Side-by-side: same operation, four styles

Fetching user 42 from the API. Notice what changes and what doesn't.

| Style | Request shape | Response shape | Bytes (approx) |
|---|---|---|---|
| **REST** | `GET /users/42` | JSON | ~80 |
| **GraphQL** | `query { user(id: 42) { name } }` | JSON | ~30 (only name) |
| **gRPC** | `GetUser(42)` (binary) | Protobuf (binary) | ~15 |
| **SOAP** | XML envelope with auth header | XML | ~600 |

The pattern:

- **REST** trades byte efficiency for human readability and cacheability.
- **GraphQL** trades caching for field-level precision.
- **gRPC** trades human readability for speed and streaming.
- **SOAP** trades everything for enterprise features you may not need.

---

## What modern backends actually use

In a typical 2026 stack:

| Layer | Style | Why |
|---|---|---|
| Public API for web + mobile | **REST** | Cacheable, documented, universally supported |
| Frontend data layer (SPA) | **GraphQL** | One endpoint, no over-fetching |
| Service-to-service (internal) | **gRPC** | Fast, typed, streaming |
| Enterprise integrations | **SOAP** | Required by the other party |

It's not "pick one." It's "pick one per layer." A single backend often
exposes REST to the world, gRPC to its own microservices, and consumes
SOAP from a partner — all in the same repo.

---

## Where this cookbook fits

- `01-api-design/` teaches **REST** (typed requests, CRUD verbs, status
  codes) — the default, and the one you'll use most.
- `03-rbac-admin/` teaches **REST with auth** — how 200/403/401 work.
- `10-reference/fastapi-types-example.py` shows how the same models
  translate to real FastAPI code.

**GraphQL, gRPC, and SOAP are not taught in this cookbook as runnable
lessons** — each would need its own server, its own client, and its own
tooling (Apollo, `protoc`, WSDL parsers). That's more than 15 minutes. This
file exists so you know what they are, when to pick them, and why the
default is REST.

If you want to see them in practice, look for:

- **GraphQL:** Strawberry or Graphene (Python), Apollo Server (Node)
- **gRPC:** `grpcio` + `grpcio-tools` (Python), `@grpc/grpc-js` (Node)
- **SOAP:** `zeep` (Python), `soap` (Node)

---

## In another language?

Every API style has client and server implementations in every major
language. The concept doesn't change:

| Language | REST | GraphQL | gRPC |
|---|---|---|---|
| Python | FastAPI, Flask | Strawberry, Graphene | `grpcio` |
| Go | `net/http`, chi, echo | `gqlgen` | `google.golang.org/grpc` |
| Rust | axum, actix-web | `async-graphql` | `tonic` |
| PHP | Laravel, Slim | `webonyx/graphql-php` | `grpc/grpc` |
| Ruby | Rails, Sinatra | `graphql-ruby` | `grpc` gem |
| Java | Spring Boot | Spring GraphQL | grpc-java |
| C# | ASP.NET Core | Hot Chocolate | Grpc.AspNetCore |

The style is a design choice. The language is an implementation detail.