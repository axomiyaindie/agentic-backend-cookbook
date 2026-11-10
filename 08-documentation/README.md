# Documentation

**API documentation** = the contract between your backend and everyone
who calls it — frontend, mobile, AI agents, other services, and future you.

## The one idea to take away

An API spec is **the source of truth**, not the code.

Code changes. Comments rot. The only thing a frontend developer can
trust is a document that says: "this endpoint exists, it takes this
shape, it returns this shape, and this is who's allowed to call it."

If the doc and the code disagree, **fix the code or fix the doc** —
never leave them out of sync, because the next developer (or AI) will
believe whichever one they read first.

## Why this matters more than ever

When you're building with AI assistants, the doc is no longer just for
humans — it's the **input** to the AI. A well-documented API means the
AI can generate correct client code. A poorly-documented API means the
AI invents endpoints that don't exist.

This is also why OpenAPI/Swagger exists: an API spec that a machine can
read is an API spec an AI can use.

## What a good API doc contains

For every endpoint:

1. **Method and path** — `GET /users/{id}`
2. **Purpose** — one sentence. What is this for?
3. **Auth** — who can call it? (public, logged in, admin only)
4. **Request** — path params, query params, body (with types)
5. **Response** — status codes and shapes (success and error)
6. **Example** — a copy-pasteable `curl` or JSON snippet

What most docs **miss** and shouldn't:

- **403 vs 401** — "not logged in" vs "logged in but not allowed".
  These are different and deserve separate examples.
- **Rate limit headers** — clients need to know they exist.
- **Error shape** — is it `{"error": "..."}` or `{"detail": "..."}`?
  Pick one and document it.

## The doc template

`api-spec-template.md` — a fill-in-the-blanks template for documenting
one endpoint. Copy it, fill it in, commit it next to the code.

## The worked example

`example-spec.md` — the RBAC lesson from `03-rbac-admin/`, fully
documented as a real API spec. This shows what "done" looks like for
the entire lesson.

## Where this fits in real code

- **OpenAPI / Swagger** — machine-readable spec; generates docs and clients.
  FastAPI generates it automatically at `/openapi.json`.
- **Redoc / Swagger UI** — render an OpenAPI spec as a browsable page.
  FastAPI serves one at `/docs` by default.
- **Stoplight / Postman** — design-first tools; write the spec, generate
  the server stub.
- **Plain Markdown** — what this lesson uses. Portable, diff-friendly,
  readable on GitHub. Works for small APIs.

For teaching, Markdown is the right choice: no tooling, no vendor, and
the structure is visible. Once you understand the structure, moving to
OpenAPI is a mechanical translation.

---

## In another language?

The format is universal. Every language and framework can consume or
produce an API spec:

| Language | OpenAPI tooling |
|---|---|
| Go | `swaggo/swag`, `oapi-codegen` |
| Rust | `utoipa`, `paperclip` |
| PHP | `nelmio/api-doc-bundle`, `zircote/swagger-php` |
| Ruby | `rswag`, `grape-swagger` |
| Java | `springdoc-openapi` |
| C# | `Swashbuckle`, `NSwag` |

The language changes; the spec doesn't. That's the point of a spec.