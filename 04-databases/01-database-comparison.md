# Database comparison — pick the right one

The point of this file is **not** to say one is best. It's to give you
the mental model to choose, and to understand what an AI assistant is
doing when it picks one for you.

## The four you'll see in this repo

### PostgreSQL (relational, SQL)
- **Data shape:** tables with typed columns, foreign keys
- **Great at:** anything with relationships, transactions, correctness
- **Also does:** JSON, vectors (pgvector), full-text search
- **Default choice** for most backends unless you have a reason
- **When to reach for it:** you don't know yet → start here

### MySQL (relational, SQL)
- **Data shape:** tables, like Postgres
- **Great at:** the same things, with a different ecosystem and history
- **Differences from Postgres:** historically weaker JSON, different
  extension story; performance is comparable for typical CRUD
- **When to reach for it:** your host provides it and you don't need
  Postgres-specific features

### MongoDB (document)
- **Data shape:** collections of JSON-like documents
- **Great at:** nested data that changes shape, rapid iteration
- **Trade-off:** relationships are your job (no foreign keys)
- **When to reach for it:** the data is naturally a document
  (e.g. a CMS page with arbitrary blocks)

### DynamoDB (key-value / wide-column)
- **Data shape:** items keyed by a partition key (+ optional sort key)
- **Great at:** very high scale, predictable latency, AWS-native
- **Trade-off:** you must design access patterns up front —
  you can't just "query anything" like with SQL
- **When to reach for it:** AWS-only stack, high scale, known access
  patterns, and you're willing to design for them

## How to decide (short version)

| Question | If yes → |
|---|---|
| Do I need relationships / joins / transactions? | **Postgres** or **MySQL** |
| Is my data naturally a document that changes shape? | **MongoDB** |
| Do I need AWS-native, very high scale, fixed access patterns? | **DynamoDB** |
| I don't know / it's a learning project | **Postgres** |

## What's the same across all four

Every example in `02-` through `05-` implements:
- `create_user(name, email)`
- `get_user(id)`
- `update_user(id, patch)`
- `delete_user(id)`

Read them side by side. The **shape** of the CRUD is the same. The
**code** is different because each engine has its own client and
query language.

## What an AI assistant is likely to pick (and why)

When you ask an AI to "add a database", here's the pattern:

| Assistant says | Real reason | When it's wrong |
|---|---|---|
| "Let's use Postgres" | Default safe choice | Rarely — it's a good default |
| "Let's use MongoDB" | Trained on MERN-stack tutorials | When you actually need joins/transactions |
| "Let's use DynamoDB" | AWS-flavored training data | When you don't know your access patterns yet |
| "Let's use SQLite" | Simplest possible code | When multiple users/processes need to write |

The takeaway: **if the AI picks a database, ask why.** If the reason is
"it's popular" or "it's what the tutorial used", that's not a reason.
The four folders here exist so you can read the actual trade-offs.

## Bonus: which one would I use for *this repo*?

Postgres. Every folder in `04-databases/` could be rewritten as a
Postgres table without losing anything, and I could add pgvector later
if a lesson needed embeddings. That's the point: **one boring choice
that covers everything** beats four clever choices stitched together.