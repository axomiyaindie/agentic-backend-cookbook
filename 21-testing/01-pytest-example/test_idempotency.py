# ─────────────────────────────────────────────────────────────
# Tests for the idempotency lesson (16-idempotency/).
#
# Four tests, one per behavior in that lesson's README:
#   1. First charge succeeds
#   2. Same key -> same charge ID, no new charge
#   3. Different key -> new charge
#   4. No key -> 400 rejected, nothing charged
#
# Run with:  pytest -v
# ─────────────────────────────────────────────────────────────

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    # Import inside the fixture so conftest.py has already patched
    # sys.path and cleared the database file by the time we import.
    import main
    return TestClient(main.app)


@pytest.fixture(autouse=True)
def reset_db():
    # Runs before every test. Clears the idempotency database so
    # tests don't leak state into each other.
    import main
    with main._connect() as conn:
        conn.execute("DELETE FROM charges")
        conn.execute("DELETE FROM seen_keys")
    yield


# ── Test 1 ──────────────────────────────────────────────────
def test_first_charge_succeeds(client):
    """A first charge with a key should succeed and return charge_id=1."""
    r = client.post(
        "/charge",
        json={"amount": 50, "user": "alice"},
        headers={"Idempotency-Key": "key-1"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["status"] == "charged"
    assert body["charge_id"] == 1
    assert body["amount"] == 50
    assert body["user"] == "alice"


# ── Test 2 (the important one) ──────────────────────────────
def test_same_key_does_not_double_charge(client):
    """
    The whole point of idempotency: sending the same request twice
    with the same key produces ONE charge, not two.
    """
    headers = {"Idempotency-Key": "key-1"}
    body = {"amount": 50, "user": "alice"}

    r1 = client.post("/charge", json=body, headers=headers)
    r2 = client.post("/charge", json=body, headers=headers)

    assert r1.status_code == 200
    assert r2.status_code == 200

    # Both responses must be the SAME charge.
    assert r1.json()["charge_id"] == r2.json()["charge_id"]

    # And the charges table must have only one row.
    charges = client.get("/charges").json()
    assert len(charges) == 1, f"expected 1 charge, got {len(charges)}: {charges}"


# ── Test 3 ──────────────────────────────────────────────────
def test_different_key_creates_new_charge(client):
    """
    Same body, different key = a new operation. Two charges.
    """
    body = {"amount": 50, "user": "alice"}

    r1 = client.post("/charge", json=body, headers={"Idempotency-Key": "key-1"})
    r2 = client.post("/charge", json=body, headers={"Idempotency-Key": "key-2"})

    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["charge_id"] != r2.json()["charge_id"]

    charges = client.get("/charges").json()
    assert len(charges) == 2


# ── Test 4 ──────────────────────────────────────────────────
def test_missing_key_is_rejected(client):
    """
    No key = 400. And critically: nothing was charged.
    The last assertion is the one that catches "validates but charges anyway".
    """
    r = client.post("/charge", json={"amount": 50, "user": "alice"})
    assert r.status_code == 400
    assert "Idempotency-Key" in r.json()["detail"]

    # The charge must NOT have happened.
    charges = client.get("/charges").json()
    assert len(charges) == 0