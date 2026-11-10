✅ FILE 16 pushed: `59548a1..58e83b1`, 80 insertions. The second `git add`/`commit` pair just confirmed it — `nothing to commit` is the correct response since the first push already covered it. All good.

---

## FILE 17 of 27

**Path:**
```
D:\agentic-backend-cookbook\04-databases\02-postgres-crud\README.md
```

**Open it:**
```powershell
code D:\agentic-backend-cookbook\04-databases\02-postgres-crud\README.md
```

**Paste this:**
```
# Postgres CRUD

## What you'll learn
- The shape of a relational schema
- Parameterised queries (never string-concatenate SQL!)
- How `RETURNING` gives you the created row back

## Setup
```bash
pip install psycopg[binary]
# create a DB called `playbook` on your Postgres instance
psql -d playbook -f schema.sql
python crud.py
```

Set `DATABASE_URL` if it's not `postgresql://localhost/playbook`.

## What to look at
- `schema.sql` — the whole schema. One table.
- `crud.py` — read `create_user` first. Notice the `%s` placeholders.
  Then read the rest; every function follows the same shape.

## Walkthrough

1. Create the database and run the schema:
   ```bash
   createdb playbook
   psql -d playbook -f schema.sql
   ```
2. Run the demo:
   ```bash
   python crud.py
   ```
3. You should see four lines: created, get, update, delete, and finally
   `None` for the get-after-delete — proving the delete worked.

## The one mistake to never make

```python
# WRONG — SQL injection
conn.execute(f"SELECT * FROM users WHERE email = '{email}'")

# RIGHT — parameterised
conn.execute("SELECT * FROM users WHERE email = %s", (email,))
```

The `%s` isn't string formatting. It's a **placeholder** that psycopg
replaces with the value *after* the query is parsed. That's why it's
safe: user input can never become SQL syntax.

---

## In another language?

The three ideas — schema, parameterised query, `RETURNING` — translate
directly:

| Language | Driver | Parameters | Returning row |
|---|---|---|---|
| Go | `jackc/pgx` | `$1, $2` | `QueryRow(...).Scan(...)` |
| Rust | `sqlx` | `$1, $2` | `query_as(...).fetch_one(...)` |
| PHP | `PDO` | `:name` or `?` | `fetch(PDO::FETCH_ASSOC)` |
| Ruby | `pg` gem | `$1, $2` | `exec_params(...).first` |
| Java | JDBC | `?` | `RETURN_GENERATED_KEYS` |
| C# | Npgsql | `@p0, @p1` | `ExecuteScalar` or `RETURNING` |

Every Postgres driver supports parameterised queries. If one doesn't,
don't use it.
```