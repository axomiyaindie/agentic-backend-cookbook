✅ FILE 19 pushed: `95db3d1..43c94c5`, 67 insertions, 55 lines verified. **Postgres lesson complete.**

---

## FILE 20 of 27

**Path:**
```
D:\agentic-backend-cookbook\04-databases\03-mysql-crud\README.md
```

**Open it:**
```powershell
code D:\agentic-backend-cookbook\04-databases\03-mysql-crud\README.md
```

**Paste this:**
```
# MySQL CRUD

Same CRUD as Postgres, different client and slightly different
placeholder syntax.

## What you'll learn
- How the same CRUD looks with a different SQL driver
- Why `AUTO_INCREMENT` and `SERIAL` are the same idea with different names
- Where MySQL's `RETURNING` support differs (it doesn't — you read `lastrowid`)

## Setup
```bash
pip install mysql-connector-python
# create a DB called `playbook` on your MySQL instance
# then run the schema below
python crud.py
```

Set `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE` if they
differ from the defaults.

## Schema

```sql
CREATE TABLE IF NOT EXISTS users (
    id    INT AUTO_INCREMENT PRIMARY KEY,
    name  VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE
);
```

`AUTO_INCREMENT` is MySQL's version of Postgres's `SERIAL`. Same concept,
different keyword.

## What to look at
- `crud.py` — compare with `../02-postgres-crud/crud.py`. Same four
  functions, same parameterised queries, different driver.

## The key difference from Postgres

Postgres supports `RETURNING id, name, email` on `INSERT`, which gives
you the whole row back in one round-trip. MySQL does **not** support
`RETURNING` on `INSERT` (it does on `DELETE` only). So `create_user` here:

1. Inserts the row
2. Reads `cur.lastrowid`
3. Constructs the response dict from the known inputs + the new id

That's a real, practical difference between the two databases — and the
kind of thing worth knowing before an AI assistant picks one for you.

---

## In another language?

| Language | MySQL driver | Notes |
|---|---|---|
| Go | `go-sql-driver/mysql` | `LastInsertId()` on `sql.Result` |
| Rust | `sqlx` with `mysql` feature | `last_insert_id()` on result |
| PHP | `PDO` with MySQL DSN | `$pdo->lastInsertId()` |
| Ruby | `mysql2` gem | `client.last_id` |
| Java | JDBC (`mysql-connector-j`) | `Statement.RETURN_GENERATED_KEYS` |
| C# | `MySqlConnector` | `cmd.LastInsertedId` |

Every driver has the same workaround because every MySQL driver hits the
same limitation. Once you've seen it once, you'll recognise it everywhere.
```