# ─────────────────────────────────────────────────────────────
# Lesson: Postgres CRUD
#
# The important thing to notice: every query uses %s placeholders.
# NEVER format values into SQL strings — that's how SQL injection
# happens. psycopg handles escaping for you.
# ─────────────────────────────────────────────────────────────

import os
import psycopg

DSN = os.environ.get("DATABASE_URL", "postgresql://localhost/playbook")


def create_user(name: str, email: str) -> dict:
    with psycopg.connect(DSN) as conn:
        row = conn.execute(
            "INSERT INTO users (name, email) VALUES (%s, %s) "
            "RETURNING id, name, email",
            (name, email),
        ).fetchone()
        conn.commit()
        return {"id": row[0], "name": row[1], "email": row[2]}


def get_user(user_id: int) -> dict | None:
    with psycopg.connect(DSN) as conn:
        row = conn.execute(
            "SELECT id, name, email FROM users WHERE id = %s",
            (user_id,),
        ).fetchone()
        return None if row is None else {"id": row[0], "name": row[1], "email": row[2]}


def update_user(user_id: int, patch: dict) -> dict | None:
    # Build the SET clause dynamically but SAFELY — column names are
    # allow-listed, values are parameterised.
    allowed = {"name", "email"}
    fields = [k for k in patch if k in allowed]
    if not fields:
        return get_user(user_id)
    set_clause = ", ".join(f"{k} = %s" for k in fields)
    values = [patch[k] for k in fields] + [user_id]
    with psycopg.connect(DSN) as conn:
        row = conn.execute(
            f"UPDATE users SET {set_clause} WHERE id = %s "
            "RETURNING id, name, email",
            values,
        ).fetchone()
        conn.commit()
        return None if row is None else {"id": row[0], "name": row[1], "email": row[2]}


def delete_user(user_id: int) -> bool:
    with psycopg.connect(DSN) as conn:
        cur = conn.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        return cur.rowcount > 0


if __name__ == "__main__":
    u = create_user("Rakibul", "rakibul@example.com")
    print("created:", u)
    print("get:", get_user(u["id"]))
    print("update:", update_user(u["id"], {"name": "Rakibul Islam"}))
    print("delete:", delete_user(u["id"]))
    print("get after delete:", get_user(u["id"]))