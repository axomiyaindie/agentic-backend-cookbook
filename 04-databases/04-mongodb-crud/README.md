✅ FILE 21 pushed: `608361e..c77b863`, 92 insertions, 77 lines verified. **MySQL lesson complete.**

---

## FILE 22 of 27

**Path:**
```
D:\agentic-backend-cookbook\04-databases\04-mongodb-crud\README.md
```

**Open it:**
```powershell
code D:\agentic-backend-cookbook\04-databases\04-mongodb-crud\README.md
```

**Paste this:**
```
# MongoDB CRUD

Same four operations — but now the "row" is a **document** and the
"table" is a **collection**. No schema, no `ALTER TABLE`.

## What you'll learn
- How the same CRUD looks when there's no schema
- How MongoDB's `_id` (ObjectId) is different from a Postgres integer id
- How partial update works without an `UPDATE ... SET` clause

## Setup
```bash
pip install pymongo
# make sure mongod is running locally, or set MONGODB_URL
python crud.py
```

`MONGODB_URL` defaults to `mongodb://localhost:27017`, DB name `playbook`.

## What to look at
- `crud.py` — read `create_user` first. Notice there's no `INSERT INTO`,
  no column list, no schema. You hand MongoDB a dict; it stores the dict.

## The three differences from SQL

**1. No schema.** The first `insert_one` defines the shape. A later
document could have extra fields, missing fields, or a different type
for the same field. MongoDB won't stop you.

**2. `_id` is auto-generated** — an `ObjectId`, not an integer. It's
serialised to a string for JSON. That's why every function takes `user_id: str`,
not `int`.

**3. Partial update is the default.** You send `{"$set": {...}}`, and
MongoDB applies only those fields. There's no equivalent of
`UPDATE users SET name = ..., email = ... WHERE ...` — you send exactly
the fields you want to change.

## What MongoDB doesn't enforce

- No foreign keys. If you store `owner_id`, nothing stops it pointing at
  a user that doesn't exist. Referential integrity is your job.
- No `NOT NULL`. A document can simply omit a field.
- No transactions across collections by default (replica sets can, but
  it's not automatic like in Postgres).

These aren't bugs — they're the trade-off that makes MongoDB flexible.
Knowing when that trade-off is worth it is the whole point of this section.

---

## In another language?

| Language | Driver | Getting the inserted `_id` |
|---|---|---|
| Go | `mongo-driver` | `result.InsertedID` |
| Rust | `mongodb` crate | `result.inserted_id` |
| PHP | `mongodb/mongodb` | `$result->getInsertedId()` |
| Ruby | `mongo` gem | `result.inserted_id` |
| Java | `mongodb-driver-sync` | `result.getInsertedId()` |
| C# | `MongoDB.Driver` | `result.InsertedId` |

The pattern is identical everywhere: `insert_one` returns a result
object; you read its `_id` to return the created document.
```