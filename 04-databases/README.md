# Databases

Four engines, **the same CRUD**, so you can compare them side by side.

| Folder | Engine | Model |
|---|---|---|
| `02-postgres-crud/` | PostgreSQL | relational (tables, rows, SQL) |
| `03-mysql-crud/` | MySQL | relational (tables, rows, SQL) |
| `04-mongodb-crud/` | MongoDB | document (collections, JSON docs) |
| `05-dynamodb-crud/` | DynamoDB | key-value / wide-column (partition key) |

Read `01-database-comparison.md` first. Then each example.

Each example implements the same four operations:
- create a "user"
- read one by id
- update one by id
- delete one by id

## Why four engines and not one?

Because "which database?" is the question AI assistants get wrong most
often. When an AI generates your backend, it will pick a database for
you. If you can't read the code and see *why* it picked that one, you
won't notice when it's wrong.

Reading four implementations of the same CRUD gives you the vocabulary:

- **Relational** (Postgres, MySQL) — you declare the shape first, and
  the database enforces it. Relationships are cheap.
- **Document** (MongoDB) — you store JSON; relationships are your job.
- **Key-value** (DynamoDB) — you design access patterns first; anything
  you didn't plan for is a `Scan`, which is expensive.

After reading all four, "use Postgres" stops being a cargo cult and
starts being a decision you can justify.

## What this section does *not* teach

- **Scaling**: sharding, replicas, connection pooling. Out of scope.
- **Migrations**: `ALTER TABLE` strategy, zero-downtime deploys. Out of scope.
- **ORMs**: we use raw drivers so the SQL/query shape is visible.
- **Transactions**: mentioned, not implemented.

Those are all worth learning — but they're layer 2. This is layer 1.

---

## In another language?

The four engines don't care what language calls them. The drivers
change, the query language doesn't:

| Engine | Go | Rust | PHP | Ruby | Java | C# |
|---|---|---|---|---|---|---|
| Postgres | `jackc/pgx` | `sqlx` / `tokio-postgres` | `PDO` | `pg` gem | JDBC | Npgsql |
| MySQL | `go-sql-driver/mysql` | `sqlx` | `PDO` | `mysql2` gem | JDBC | MySqlConnector |
| MongoDB | `mongo-driver` | `mongodb` crate | `mongodb/mongodb` | `mongo` gem | `mongodb-driver` | MongoDB.Driver |
| DynamoDB | `aws-sdk-go-v2` | `aws-sdk-rust` | `aws/aws-sdk-php` | `aws-sdk-ruby` | AWS SDK | AWS SDK |

The lesson for all of them is identical: **parameterised queries**,
**explicit update fields**, **checked return values**. If you understand
what those three mean in one language, you'll spot when they're missing
in any other.