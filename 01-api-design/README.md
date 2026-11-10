# API Design

Two lessons:
1. **HTTP + TypeScript types** — how a request becomes a typed function
2. **CRUD models** — how Create/Read/Update/Delete map to HTTP

Both examples are single files. Read top to bottom.

---

## Language policy

The **concepts** here are language-agnostic. HTTP is HTTP. A request
shape is a request shape. None of that changes if you write Go, Rust,
PHP, Ruby, Java, C#, or Elixir.

The examples are in **TypeScript** only because it's the most skimmable
language for a reader who already knows JavaScript, and because the types
show the concept directly. They are **reference implementations**, not a
recommendation.

Each lesson README ends with a **"In another language?"** table mapping
the concept to Go, Rust, PHP, Ruby, Java, and C#. If your language isn't
listed, the shape is the same — find your HTTP framework and your
validation library, and the rest follows.