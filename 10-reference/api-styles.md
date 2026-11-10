# API styles

Four ways to expose a backend: REST, GraphQL, gRPC, SOAP. Each exists
because it solves a problem the others don't. Read this before
`01-api-design/` — that section shows *how* a request looks; this file
explains *why* you would pick one style over another.

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

**What it is:** Resources are URLs. Operations are HTTP verbs
(`GET`, `POST`, `PUT`, `PATCH`, `DELETE`). Responses are typically JSON.
Status codes carry meaning (`200`, `201`, `404`, `403`, `429`).

**Strengths:** Universal. Every language, every tool, every proxy
understands it. Cacheable via HTTP headers. Browser-friendly.

**Trade-offs:** Over-fetching (the server decides what you get), under-fetching
(you need multiple round-trips), versioning (the URL carries the API version),
and no built-in streaming.

**When to pick it:** Almost always for the first API. Public-facing,
documented, cacheable. It's the default for a reason.

**Usage:** 92% of organizations use REST APIs — highest of any style .

**A real request:**

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

This is exactly what the RBAC lesson (`03-rbac-admin/`) implements. If you
can read that lesson, you can read any REST API.

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

**Usage:** ~70% of developers report using GraphQL, up from ~61% in 2024 .

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

**Usage:** ~44% of developers use gRPC, up from ~35% in 2024 . It's
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
FIX), telecom (TM Forum), government procurement .

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