# Agentic Backend Cookbook

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Check Python](https://github.com/axomiyaindie/agentic-backend-cookbook/actions/workflows/check-python.yml/badge.svg)](https://github.com/axomiyaindie/agentic-backend-cookbook/actions/workflows/check-python.yml)
[![Check TypeScript](https://github.com/axomiyaindie/agentic-backend-cookbook/actions/workflows/check-typescript.yml/badge.svg)](https://github.com/axomiyaindie/agentic-backend-cookbook/actions/workflows/check-typescript.yml)

# Agentic Backend Cookbook

An **open-source teaching cookbook** for developers who want to understand
the backend behind AI applications — not just the frontend.

Every folder is a **self-contained recipe** you can read, run, and modify.
Nothing here is a finished product. Everything here is a **runnable example**
of one concept, with a README that tells you exactly which files to look at.

## Who this is for

- Frontend devs who want to understand what happens "behind the API call"
- Self-taught devs who can build a UI but freeze when asked "how does auth work"
- Anyone learning by **reading real code**, not tutorials

## What you'll learn (by folder)

| Folder | Concept |
|---|---|
| `00-roadmap/` | Suggested reading order |
| `01-api-design/` | HTTP + TypeScript types + CRUD models |
| `02-mcp-connectors/` | How MCP (Model Context Protocol) servers work |
| `03-rbac-admin/` | Role-based access control with admin + user panels |
| `04-databases/` | Postgres, MySQL, MongoDB, DynamoDB — same CRUD, different engines |
| `05-glossary/` | Plain-English definitions of every term used in this repo |

## How to use this repo

1. Pick a folder from the table above.
2. Read its `README.md` first — it explains **what** the lesson is and **why** it matters.
3. Open the example file(s) and read the comments.
4. Run it (each folder has its own run instructions).
5. Break it. Change one line. See what happens.

> ⚠️ **Do not copy this into production.** These are teaching examples.
> They are intentionally simplified, have no tests, and skip hardening.

## Stack used in examples

- **TypeScript / Node** for API + MCP lessons
- **Python / FastAPI** for the RBAC lesson
- **Postgres, MySQL, MongoDB, DynamoDB** for the database lesson
- No frontend framework is required to follow any lesson

## License

MIT — see `LICENSE`.
