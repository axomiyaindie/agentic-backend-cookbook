✅ FILE 23 pushed: `0d37131..00151e5`, 51 insertions. **MongoDB lesson complete.**

---

## FILE 24 of 27

**Path:**
```
D:\agentic-backend-cookbook\04-databases\05-dynamodb-crud\README.md
```

**Open it:**
```powershell
code D:\agentic-backend-cookbook\04-databases\05-dynamodb-crud\README.md
```

**Paste this:**
```
# DynamoDB CRUD

Same four operations, but the mental model is fundamentally different.
This is the last database lesson because it's the most restrictive —
and understanding the restrictions is the point.

## What you'll learn
- How the partition key shapes every query you can write
- Why `Scan` is discouraged (and what `Query` requires)
- How the AWS SDK expresses partial updates

## Setup
```bash
pip install boto3
# AWS credentials via env: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
# and AWS_REGION, or run against DynamoDB Local:
#   docker run -p 8000:8000 amazon/dynamodb-local
# then set DYNAMODB_ENDPOINT=http://localhost:8000
python crud.py
```

Set `DYNAMODB_TABLE` (default `playbook-users`).

## What to look at
- `crud.py` — read `_table()` first. It defines the table with an explicit
  key schema. That key is the *only* thing you can efficiently read by.

## The three things that make DynamoDB different

**1. You design access patterns up front.** In SQL you can add an index
later and suddenly query by `email`. In DynamoDB you must define the
partition key and any secondary indexes at table creation. If you forgot
an index, you either rewrite the table or accept slow `Scan`s.

**2. `get_item` only takes the key.** There's no `WHERE` clause. You ask
for one item by its partition key, and you get it (or you don't).
Anything else is a `Query` (needs a key condition) or a `Scan` (reads
the whole table — expensive).

**3. Updates are expressions, not SQL.** `UpdateExpression: "SET #f0 = :v0"`
plus `ExpressionAttributeNames` and `ExpressionAttributeValues`. Why?
Because DynamoDB needs to know which parts of the string are identifiers
and which are values — the same reason SQL uses parameters, solved a
different way.

## When DynamoDB is the right answer

- You're already on AWS and want zero-ops database.
- You have very high, predictable scale (millions of requests/sec).
- You **know** your access patterns in advance.
- You're comfortable designing keys carefully.

## When it's the wrong answer

- You're still figuring out what queries you need.
- You need joins or multi-table transactions.
- You need ad-hoc querying (`SELECT * WHERE x LIKE ...`).
- You're not on AWS (the value proposition drops fast off-AWS).

## This is the "don't cargo-cult this" lesson

AI assistants trained on AWS tutorials will often suggest DynamoDB for
a new project. That's usually wrong for a learning project or an early-stage
app, because you don't yet know your access patterns. The code here is
correct — but the **choice** of DynamoDB is the lesson, not just the code.

---

## In another language?

| Language | SDK |
|---|---|
| Go | `aws-sdk-go-v2/service/dynamodb` |
| Rust | `aws-sdk-dynamodb` |
| PHP | `aws/aws-sdk-php` |
| Ruby | `aws-sdk-dynamodb` |
| Java | `software.amazon.awssdk:dynamodb` |
| C# | `AWSSDK.DynamoDBv2` |

Every SDK exposes the same concepts: `PutItem`, `GetItem`,
`UpdateItem`, `DeleteItem`. The expression syntax for updates is
identical because it's the wire format, not the language.
```