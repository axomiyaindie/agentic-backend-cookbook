# Roadmap

Read in this order. Each step assumes you finished the previous one.

## 1. API design (`01-api-design/`)
Start here. Everything else is an API.
- Read `01-http-typescript/` → how a request becomes a typed function call
- Read `02-crud-model/` → how Create/Read/Update/Delete map to HTTP verbs

## 2. MCP connectors (`02-mcp-connectors/`)
Once you understand HTTP, learn how an AI client calls *tools* over a
standard protocol instead of bespoke endpoints.

## 3. RBAC admin (`03-rbac-admin/`)
Now that you can build APIs, learn how to protect them — who is admin,
who is user, and how the server checks.

## 4. Databases (`04-databases/`)
Same CRUD, four different engines. Read the comparison first, then each
example in order.

## 5. Glossary (`05-glossary/`)
If a term in any lesson is unfamiliar, look it up here.

---

## "Vibe coding" safety net

If you're building with an AI assistant and it produces backend code you
don't understand, check it against this repo:

- Does it define types for its request/response? → `01-api-design/01-http-typescript/`
- Does it expose tools to an AI? → `02-mcp-connectors/`
- Does it check *who* is allowed to do *what*? → `03-rbac-admin/`
- Does it use the right database for the job? → `04-databases/01-database-comparison.md`

If the answer to any of those is "no", that's what to fix first.