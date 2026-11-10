# Testing

Every other lesson in this cookbook ships code. This one ships the thing
that proves the code works.

## The one idea to take away

**A test is a claim that survives refactoring.**

Comments rot. Documentation goes stale. The only thing that tells you "this
code still does what it's supposed to" after six months of edits is a test
that runs on every change. That's what CI is for — and CI without tests
only checks that the code *compiles*, not that it *works*.

This cookbook's own CI (`check-python.yml`, `check-typescript.yml`) does
exactly that: it byte-compiles `.py` files and type-checks `.ts` files. It
catches syntax errors and type errors. It does **not** catch logic bugs.
That's what unit tests and integration tests are for.

## The three kinds of tests

| Kind | What it checks | Speed | Example |
|---|---|---|---|
| **Unit** | One function in isolation | Milliseconds | `assert add(2,3) == 5` |
| **Integration** | Several pieces together | 100ms–seconds | POST /login → expect token |
| **End-to-end** | The whole system, real HTTP | Seconds–minutes | Browser clicks "Pay" → DB has a charge |

**Aim for the pyramid**: many unit tests, some integration tests, few
end-to-end tests. The lower the level, the faster the feedback, and the
easier it is to find *what* broke when a test fails.

## What to test (and what not to)

**Test:**

- **Business rules** — "a user can't transfer more than their balance"
- **Boundaries** — empty input, one item, one million items
- **Error paths** — what happens when the database is down
- **Idempotency** — the same request twice produces one effect
- **Transactions** — a failed second write leaves no partial state

**Don't test:**

- **Framework behavior** — FastAPI's routing works; you don't need to test it
- **Third-party libraries** — `requests.get()` works; trust it
- **Trivial getters** — `def get_name(self): return self.name` doesn't need a test
- **Implementation details** — test *what* it does, not *how* it does it

If you refactor a function and every test still passes, the tests were
testing behavior. If half break and the behavior is unchanged, the tests
were testing implementation.

## The pytest essentials

Pytest is the standard Python test runner. Three things to know:

**1. Test files start with `test_`.** Pytest discovers them automatically.
No registration, no class inheritance. A function whose name starts with
`test_` is a test.

```python
def test_add():
    assert add(2, 3) == 5
```

**2. Fixtures share setup.** Database connections, test clients, sample
data — define them once as a fixture, inject them into tests.

```python
import pytest

@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    from main import app
    return TestClient(app)

def test_health(client):
    assert client.get("/docs").status_code == 200
```

**3. Run with `pytest`.** Not `python test_foo.py`. Pytest finds the tests,
runs them, reports pass/fail, and shows the diff on failure.

## Lesson

`01-pytest-example/` — tests for the **idempotency** lesson
(`16-idempotency/`). It's the best candidate because the "does this run
once or twice?" question is exactly what a test should answer.

The tests check:

- A first request creates a charge
- A retry with the same key creates **no** new charge
- A different key creates a **new** charge
- A request with no key is rejected

These are the four behaviors from the README. The test file is the
executable version of that README.

Run it:

```bash
cd 21-testing/01-pytest-example
pip install -r requirements.txt
pytest -v
```

You should see **4 passed**.

## Where this fits in real code

- **pytest** — the Python standard. Fast, clear output, huge plugin
  ecosystem (`pytest-cov` for coverage, `pytest-asyncio` for async).
- **FastAPI `TestClient`** — spins up the app in-process, lets you send
  real HTTP requests without a network. Fast and accurate.
- **`pytest-cov`** — shows which lines the tests actually ran. 80% is a
  good target; 100% is rarely worth chasing.
- **GitHub Actions** — runs `pytest` on every push. Extends the
  existing CI to check behavior, not just compile.
- **Coverage badge** — shows the percentage in the README. Useful signal.

## What this lesson does not cover

- **End-to-end tests** — Playwright, Selenium. Slower, but test the
  browser. This cookbook has no frontend, so no e2e.
- **Property-based testing** — Hypothesis. Generates test cases from
  property definitions. Powerful but not the first thing to learn.
- **Load testing** — k6, Locust. Simulates thousands of users. Separate
  lesson.
- **Fuzzing** — random input, checking for crashes. Separate lesson.
- **Snapshot tests** — `syrupy`, `pytest-snapshot`. Useful for serialization
  but can hide bugs if overused.

The essentials — unit tests, integration tests, fixtures, CI — are what
this lesson covers.

## The test-driven habit

You don't have to do full TDD (write the test, watch it fail, write the
code, watch it pass). But you should:

1. **Write a test for the bug you just fixed** — before you fix it, so
   you know the test catches the bug.
2. **Write a test for each business rule** — not each line of code.
3. **Run the tests before every commit** — `pytest -q` takes seconds.
4. **Add a test when you find a bug in production** — otherwise it comes back.

The rule is simple: **if a bug matters enough to fix, it matters enough
to test.** Otherwise you'll fix it again in six months.

---

## In another language?

Every language has a standard test runner. The concepts are identical:

| Language | Test runner | Fixtures | HTTP test client |
|---|---|---|---|
| Python | `pytest` | `@pytest.fixture` | `TestClient` (FastAPI), `httpx` |
| Go | built-in `testing` | `t.Cleanup()` | `httptest.NewRecorder` |
| Rust | built-in `#[test]` | `#[fixture]` (via `rstest`) | `reqwest` with a test server |
| Node | `vitest`, `jest` | `beforeEach` | `supertest` |
| PHP | PHPUnit | `setUp` | Symfony `BrowserKit` |
| Ruby | RSpec, Minitest | `before` blocks | `Rack::Test` |
| Java | JUnit 5 | `@BeforeEach` | Spring `MockMvc` |
| C# | xUnit, NUnit | `IClassFixture<T>` | `WebApplicationFactory<T>` |

The pattern is always: **arrange** (set up state), **act** (call the code),
**assert** (check the result). If you understand why the idempotency
tests check that a retry produces the *same* charge ID, you understand
testing in any language.