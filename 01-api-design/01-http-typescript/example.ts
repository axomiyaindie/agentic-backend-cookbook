// ─────────────────────────────────────────────────────────────
// Lesson: HTTP + TypeScript types
//
// Goal: show that an API is just a typed function over HTTP.
// We define the shape ONCE as a TypeScript type, then use it on
// both the "client" and "server" side of a fake request.
// ─────────────────────────────────────────────────────────────

// 1. Define the shape of a "user" — the single source of truth.
type User = {
  id: number;
  name: string;
  email: string;
};

// 2. Define the shape of a request to create a user.
//    Note: no `id` — the server assigns it.
type CreateUserRequest = Omit<User, "id">;

// 3. Define the shape of every successful response.
type ApiResponse<T> = {
  ok: true;
  data: T;
} | {
  ok: false;
  error: string;
};

// 4. This is our "server". It takes a typed request and returns
//    a typed response. In a real app this would be an HTTP handler.
function createUser(req: CreateUserRequest): ApiResponse<User> {
  if (!req.email.includes("@")) {
    return { ok: false, error: "invalid email" };
  }
  return {
    ok: true,
    data: { id: 1, name: req.name, email: req.email },
  };
}

// 5. This is our "client". It calls the function as if it were
//    an HTTP request. The type of `req` and `res` comes from the
//    definitions above — no duplication.
const req: CreateUserRequest = {
  name: "Rakibul",
  email: "rakibul@example.com",
};

const res = createUser(req);

// 6. TypeScript narrows the union based on `ok`.
if (res.ok) {
  console.log("Created user:", res.data);
} else {
  console.error("Failed:", res.error);
}

// ─────────────────────────────────────────────────────────────
// Exercise: change `req.email` to "not-an-email" and re-run.
// Notice the compiler still allows it, but the server rejects it.
//
// That gap — "the type says it's valid, the server says it isn't" —
// is why real APIs validate at runtime too (e.g. Zod, Pydantic).
// We'll see that in later lessons.
// ─────────────────────────────────────────────────────────────