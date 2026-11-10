// ─────────────────────────────────────────────────────────────
// Lesson: CRUD models
//
// CRUD = Create, Read, Update, Delete.
// Each maps to an HTTP verb:
//
//   Create  → POST    /users        → 201 Created
//   Read    → GET     /users/:id    → 200 OK, or 404 Not Found
//   Read all→ GET     /users        → 200 OK
//   Update  → PATCH   /users/:id    → 200 OK, or 404 Not Found
//   Delete  → DELETE  /users/:id    → 204 No Content, or 404 Not Found
//
// PUT vs PATCH:
//   PUT   replaces the whole object (missing fields are erased)
//   PATCH changes only the fields you send
//   In teaching code we use PATCH because it's less destructive.
// ─────────────────────────────────────────────────────────────

type User = { id: number; name: string; email: string };

// The "database" — just a map for teaching purposes.
const db = new Map<number, User>();
let nextId = 1;

// ── Create ──────────────────────────────────────────────────
function createUser(input: Omit<User, "id">): User {
  const user = { id: nextId++, ...input };
  db.set(user.id, user);
  return user;
}

// ── Read one ────────────────────────────────────────────────
function getUser(id: number): User | undefined {
  return db.get(id);
}

// ── Read all ────────────────────────────────────────────────
function listUsers(): User[] {
  return [...db.values()];
}

// ── Update (PATCH semantics) ────────────────────────────────
function updateUser(id: number, patch: Partial<Omit<User, "id">>): User | undefined {
  const existing = db.get(id);
  if (!existing) return undefined;
  const updated = { ...existing, ...patch };
  db.set(id, updated);
  return updated;
}

// ── Delete ──────────────────────────────────────────────────
function deleteUser(id: number): boolean {
  return db.delete(id);
}

// ── Demo ────────────────────────────────────────────────────
const a = createUser({ name: "A", email: "a@example.com" });
const b = createUser({ name: "B", email: "b@example.com" });

console.log("list:", listUsers());
console.log("get a:", getUser(a.id));
console.log("patch a:", updateUser(a.id, { name: "A!" }));
console.log("delete a:", deleteUser(a.id));
console.log("list after delete:", listUsers());

// ─────────────────────────────────────────────────────────────
// Exercise: add a `findByEmail(email)` function.
// Then think: should it return one user, or an array? What would
// the HTTP endpoint look like? What status code for "no match"?
// ─────────────────────────────────────────────────────────────