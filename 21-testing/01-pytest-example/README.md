# Pytest example

Tests for the **idempotency** lesson (`16-idempotency/`). It's the best
candidate because the "does this run once or twice?" question is exactly
what a test should answer.

## What you'll learn
- How `pytest` discovers and runs tests
- How to use `TestClient` to send HTTP requests without a real server
- How to use a fixture to reset state between tests
- What "arrange / act / assert" looks like in real code
- Why the four tests here are the four behaviors from the idempotency README

## How to run
```bash
pip install -r requirements.txt
pytest -v
```

Expected:
```
test_idempotency.py::test_first_charge_succeeds PASSED
test_idempotency.py::test_same_key_does_not_double_charge PASSED
test_idempotency.py::test_different_key_creates_new_charge PASSED
test_idempotency.py::test_missing_key_is_rejected PASSED

============================== 4 passed in 0.5s ==============================
```

No server needs to be running — `TestClient` starts the app in-process.

## What to look at
- `test_idempotency.py` — four tests, each corresponding to one behavior
  from the idempotency README:
  1. First charge succeeds
  2. Same key → same charge ID, no new charge
  3. Different key → new charge
  4. No key → 400 rejected

## The four tests, explained

**Test 1: First charge succeeds**

```python
def test_first_charge_succeeds(client):
    r = client.post("/charge", json={"amount": 50, "user": "alice"},
                    headers={"Idempotency-Key": "key-1"})
    assert r.status_code == 200
    assert r.json()["status"] == "charged"
    assert r.json()["charge_id"] == 1
```

**Arrange:** `client` fixture (a fresh TestClient with a reset DB).
**Act:** POST a charge.
**Assert:** 200, status is "charged", and it got charge ID 1.

This is the happy path. If it fails, the endpoint is broken.

---

**Test 2: Same key → same charge ID, no new charge**

```python
def test_same_key_does_not_double_charge(client):
    headers = {"Idempotency-Key": "key-1"}
    body = {"amount": 50, "user": "alice"}
    r1 = client.post("/charge", json=body, headers=headers)
    r2 = client.post("/charge", json=body, headers=headers)

    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["charge_id"] == r2.json()["charge_id"]

    charges = client.get("/charges").json()
    assert len(charges) == 1     # only one charge, not two
```

**Act:** Send the same request twice.
**Assert:** Both return 200, both return the **same charge ID**, and the
`/charges` list has **one** entry, not two.

**This is the test that catches the bug idempotency prevents.** Delete the
`seen_keys` lookup from `main.py` and this test fails: `len(charges)`
becomes 2.

---

**Test 3: Different key → new charge**

```python
def test_different_key_creates_new_charge(client):
    body = {"amount": 50, "user": "alice"}
    r1 = client.post("/charge", json=body, headers={"Idempotency-Key": "key-1"})
    r2 = client.post("/charge", json=body, headers={"Idempotency-Key": "key-2"})

    assert r1.json()["charge_id"] != r2.json()["charge_id"]

    charges = client.get("/charges").json()
    assert len(charges) == 2
```

**Act:** Two requests, same body, **different** keys.
**Assert:** Two charges. That's the whole point — the key distinguishes
operations, not the body.

---

**Test 4: No key → 400 rejected**

```python
def test_missing_key_is_rejected(client):
    r = client.post("/charge", json={"amount": 50, "user": "alice"})
    assert r.status_code == 400
    assert "Idempotency-Key" in r.json()["detail"]

    charges = client.get("/charges").json()
    assert len(charges) == 0     # nothing was charged
```

**Act:** POST without a key.
**Assert:** 400, error mentions the header, and **no charge was created**.

That last assertion is the important one. If the endpoint validates the
header but charges first, the test catches it.

## The fixture that makes it work

```python
@pytest.fixture
def client():
    # ... reset the DB, return a TestClient
```

The fixture has two jobs:
1. **Reset the database** before each test, so tests don't affect each other
2. **Return a `TestClient`** wired to the app

Without the reset, Test 2 would see Test 1's charge and fail. Test isolation
is what makes tests trustworthy.

```python
@pytest.fixture
def client():
    from main import app, _reset_for_tests
    _reset_for_tests()                # clear the DB
    from fastapi.testclient import TestClient
    return TestClient(app)
```

The lesson imports `main.py` from the idempotency folder. There's a small
adapter file in this folder that makes that import work. See
`test_idempotency.py`.

## Why `TestClient` and not `requests`

`requests` would need a running server on a real port. That's slower,
flakier (port conflicts), and harder to reset between tests.

`TestClient` from FastAPI:
- **Starts the app in-process** — no real network
- **Runs the full middleware stack** — auth, CORS, validation, everything
- **Returns real `Response` objects** — `.status_code`, `.json()`, `.headers`
- **Takes ~10ms per request** — fast enough for hundreds of tests

It's the difference between "unit test that mocks everything" and "real
HTTP request with no network." Best of both.

## What CI adds

The cookbook's existing CI (`.github/workflows/check-python.yml`) runs
`python -m py_compile` on every `.py` file. That catches syntax errors.

If you add this lesson to CI, it would also run `pytest` and catch
behavioral regressions. That's the difference:

| Check | Catches |
|---|---|
| `py_compile` | `def f(:` (syntax) |
| `pytest` | `assert len(charges) == 1` fails because idempotency broke |

The first is necessary. The second is what actually tells you the code
works.

## What this example deliberately skips

- **Coverage measurement.** `pytest-cov` shows which lines ran. Useful,
  but not the lesson.
- **Test database fixtures.** Real apps use a separate test database or
  transaction rollback. This lesson clears a shared SQLite DB.
- **Mocking.** No external services are mocked here — every test hits
  the real endpoint. Mocking is a tool for when external services are
  slow or unreliable; not the default.
- **Property-based tests.** `hypothesis` generates test cases. Useful
  for parsers and encoders. Not the first thing to learn.

## Where this fits in real code

- **`pytest`** — standard Python test runner
- **`fastapi.testclient.TestClient`** — in-process HTTP testing
- **`pytest-asyncio`** — for `async def` tests
- **`pytest-cov`** — coverage measurement
- **GitHub Actions** — run `pytest` on every push

---

## In another language?

Every language has an equivalent:

| Language | Test runner | HTTP test client |
|---|---|---|
| Python | `pytest` | FastAPI `TestClient` |
| Go | `testing` (built-in) | `httptest` |
| Rust | `#[test]` (built-in) | `axum::test` |
| Node | `vitest`, `jest` | `supertest` |
| PHP | PHPUnit | Symfony `BrowserKit` |
| Ruby | RSpec, Minitest | `Rack::Test` |
| Java | JUnit 5 | `MockMvc` |
| C# | xUnit, NUnit | `WebApplicationFactory<T>` |

The four tests translate directly. If you understand why Test 2 checks
`len(charges) == 1`, you understand what to test in any language.