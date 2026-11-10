Perfect. **B it is.** Starting fresh from FILE 3, with the language-neutral footer baked into every lesson README.

---

## FILE 3 of 26

**Path:**
```
D:\agentic-backend-cookbook\01-api-design\01-http-typescript\README.md
```

**Open it:**
```powershell
code D:\agentic-backend-cookbook\01-api-design\01-http-typescript\README.md
```

**Paste this:**
```
# HTTP + TypeScript types

## What you'll learn
- How to describe a request and response as TypeScript types
- Why the server should validate the same shape the client declared
- How HTTP verbs map to function calls

## How to run
```bash
npx tsx example.ts
```

## What to look at
- `example.ts` — every section is commented. Read the comments in order.

---

## In another language?

This example is in TypeScript for readability, not endorsement. The
concept — "define the shape once, use it on both sides" — maps to every
typed language:

| Language | Equivalent |
|---|---|
| Go | `type User struct { ... }` + `encoding/json` |
| Rust | `struct User` + `serde` |
| PHP | typed DTO class or array shape + `symfony/serializer` |
| Ruby | `Dry::Struct` or Sorbet `T::Struct` |
| Java | `record User(...)` + Jackson |
| C# | `record User(...)` + `System.Text.Json` |
| Kotlin | `data class User(...)` + kotlinx.serialization |

The shape is always: define the fields once → derive the request type
→ derive the response type → let the compiler (or validator) check it.
```