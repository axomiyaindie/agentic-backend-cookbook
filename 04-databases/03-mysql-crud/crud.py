# ─────────────────────────────────────────────────────────────
# Lesson: MySQL CRUD
# Same four operations as Postgres. Compare the code side by side.
#
# Two things to notice:
#   1. No `RETURNING` on INSERT — we read `cur.lastrowid` instead.
#   2. `_conn()` creates the table if it doesn't exist, so the example
#      runs with no separate `schema.sql` step. That's a MySQL convenience,
#      not a recommendation — real apps use migrations.
# ─────────────────────────────────────────────────────────────

import os
import mysql.connector

DB_CONFIG = {
    "host": os.environ.get("MYSQL_HOST", "localhost"),
    "user": os.environ.get("MYSQL_USER", "root"),
    "password": os.environ.get("MYSQL_PASSWORD", ""),
    "database": os.environ.get("MYSQL_DATABASE", "playbook"),
}

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id    INT AUTO_INCREMENT PRIMARY KEY,
    name  VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE
)
"""


def _conn():
    c = mysql.connector.connect(**DB_CONFIG)
    c.cursor().execute(SCHEMA)
    return c


def create_user(name: str, email: str) -> dict:
    conn = _conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO users (name, email) VALUES (%s, %s)",
                (name, email))
    conn.commit()
    user_id = cur.lastrowid
    cur.close()
    conn.close()
    return {"id": user_id, "name": name, "email": email}


def get_user(user_id: int) -> dict | None:
    conn = _conn()
    cur = conn.cursor()
    cur.execute("SELECT id, name, email FROM users WHERE id = %s", (user_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return None if row is None else {"id": row[0], "name": row[1], "email": row[2]}


def update_user(user_id: int, patch: dict) -> dict | None:
    allowed = {"name", "email"}
    fields = [k for k in patch if k in allowed]
    if not fields:
        return get_user(user_id)
    set_clause = ", ".join(f"{k} = %s" for k in fields)
    values = [patch[k] for k in fields] + [user_id]
    conn = _conn()
    cur = conn.cursor()
    cur.execute(f"UPDATE users SET {set_clause} WHERE id = %s", values)
    conn.commit()
    cur.close()
    conn.close()
    return get_user(user_id)


def delete_user(user_id: int) -> bool:
    conn = _conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
    conn.commit()
    ok = cur.rowcount > 0
    cur.close()
    conn.close()
    return ok


if __name__ == "__main__":
    u = create_user("Rakibul", "rakibul@example.com")
    print("created:", u)
    print("get:", get_user(u["id"]))
    print("update:", update_user(u["id"], {"name": "Rakibul Islam"}))
    print("delete:", delete_user(u["id"]))
    print("get after delete:", get_user(u["id"]))