# Database types

Six families of databases, what each is actually for, and real companies
using them. Read this before `04-databases/` — that section shows *how*
the code looks; this file explains *why* you would pick one engine over
another.

## The decision, in one table

| If your data is... | Pick | Why |
|---|---|---|
| Tabular, with relationships and transactions | **Relational** (Postgres, MySQL) | Joins, ACID, constraints are built in |
| Nested JSON that changes shape | **Document** (MongoDB) | One read returns the whole document, no joins |
| Simple lookups by a single key | **Key-value** (Redis, DynamoDB) | Fastest read path; scales by adding nodes |
| Defined by relationships (who-knows-who) | **Graph** (Neo4j) | Traverses connections without joins |
| Timestamped metrics at high volume | **Time-series** (InfluxDB, TimescaleDB) | Compresses and queries time windows efficiently |
| Embeddings for AI retrieval | **Vector** (pgvector, Pinecone) | Finds semantically similar items, not exact matches |

That's the whole file in one table. The rest explains each row.

---

## 1. Relational (SQL)

**What it is:** Data lives in tables with typed columns. Relationships are
expressed as shared keys (foreign keys), and the database enforces them.
You declare the shape upfront in SQL, and every application gets the same
answer [citation:9].

**Strengths:** Joins, transactions (ACID), constraints, correctness for
free. If money moves between two rows, either both change or neither does.

**Trade-offs:** The fixed schema resists change — adding a column to a
large table can lock it. Write throughput hits a ceiling on one machine;
lifting it means sharding by hand [citation:9].

**When to pick it:** Orders, payments, inventory, users, anything with
real relationships. **If you don't know, start here.**

**Free and paid:**

| Engine | Free | Paid |
|---|---|---|
| **PostgreSQL** | Self-host, or free tiers on Supabase, Neon, Azure (B1ms ~$12/mo) [citation:2] | RDS, Aurora, Crunchy Bridge, Aiven |
| **MySQL** | Self-host, free tiers on PlanetScale, Google Cloud SQL | RDS (~$30–100/mo for small instances) [citation:2] |
| **SQLite / Turso** | SQLite is free; Turso has a free tier | Turso paid tiers for distributed reads [citation:6] |

**Real companies:** PostgreSQL is used by Uber, Spotify, and Netflix
[citation:8]. Supabase (Postgres platform) has 114k GitHub stars and 55M
npm downloads/week [citation:6].

---

## 2. Document

**What it is:** Each record is a self-contained JSON document. Two
documents in the same collection can have different fields. A single
read returns the entire document with everything nested inside it — no
join needed [citation:9].

**Strengths:** Schema flexibility, fast reads of whole records, natural
fit for content that changes shape.

**Trade-offs:** Relationships are your job (no foreign keys). The same
fact can drift across documents. Malformed records reach production
quietly because nothing enforces the shape [citation:9].

**When to pick it:** Catalogs, user profiles, content management, event
payloads where records vary and you read them whole.

**Free and paid:**

| Engine | Free | Paid |
|---|---|---|
| **MongoDB** | Community Edition (SSPL license) [citation:3] | MongoDB Atlas (free tier, usage-based paid) [citation:6] |
| **Couchbase** | Community Edition | Couchbase Capella |

**Real companies:** MongoDB Atlas has 28.7k GitHub stars and 21M npm
downloads/week [citation:6]. It's the default document store in most
MERN-stack tutorials, which is why AI assistants pick it often — not
always correctly.

---

## 3. Key-value

**What it is:** A value stored under a unique key. The key is the only
way in. One lookup returns one value, with no query planner in the way.
The store hashes each key onto a node, so adding nodes splits the key
space and lifts capacity linearly [citation:9].

**Strengths:** Fastest read path, linear scale by adding nodes, TTL for
automatic expiry.

**Trade-offs:** No queries by anything other than the key. A "hot" key
sends all traffic to one node while the rest idle. Design the key naming
scheme before you write code, because changing it later means rewriting
every caller [citation:9].

**When to pick it:** Sessions, shopping carts, feature flags, rate limit
counters, caching — anywhere you know the identifier at read time.

**Free and paid:**

| Engine | Free | Paid |
|---|---|---|
| **Redis** | Self-host; Redis Cloud free tier | Redis Cloud paid, Upstash pay-per-request [citation:6] |
| **DynamoDB** | 25 GB + 25 WCU/25 RCU always-free tier [citation:2] | $1.25/M writes, $0.25/M reads [citation:2] |

**Real companies:** Redis has 77.1k GitHub stars and 21M npm downloads/week
[citation:6]. DynamoDB is AWS-native and scales to millions of requests/sec
for workloads with known access patterns.

---

## 4. Graph

**What it is:** Data stored as nodes and edges. Edges define relationships,
and both nodes and edges can have properties. You query by traversing
connections, not by joining tables [citation:1].

**Strengths:** Relationship-first queries, efficient variable-depth
traversals. Finding "friends of friends of friends" is one traversal, not
three joins.

**Trade-offs:** Overhead if relationships are shallow. Requires careful
modeling for performance. Not ideal for bulk analytical scans [citation:1].

**When to pick it:** Social networks, fraud rings, knowledge graphs,
supply chain dependencies, recommendation engines.

**Free and paid:**

| Engine | Free | Paid |
|---|---|---|
| **Neo4j** | Community Edition (GPL) [citation:3] | Neo4j Aura (free tier, paid clusters) |
| **Amazon Neptune** | — | Neptune Serverless (pay-per-use) [citation:5] |

**Real companies:** Neo4j is the reference open-source graph database,
excelling where relationships matter as much as the data itself — fraud
detection, recommendation engines [citation:3].

---

## 5. Time-series

**What it is:** Values organized by time. Optimized for high-volume
ingestion and time-window queries. Typically append-only [citation:1].

**Strengths:** Compression, high-volume ingestion, time-window
aggregations, out-of-order ingestion handling.

**Trade-offs:** Tag cardinality management, retention cost, downsampling
strategy, specialized query languages [citation:1].

**When to pick it:** IoT sensor metrics, application telemetry, monitoring,
financial market data.

**Free and paid:**

| Engine | Free | Paid |
|---|---|---|
| **InfluxDB** | Open source (Flux language) [citation:3] | InfluxDB Cloud (usage-based) |
| **TimescaleDB** | Postgres extension, self-host | Timescale Cloud, or RDS/Azure Postgres with extension [citation:1] |

**Real companies:** InfluxDB is the open-source reference for high-frequency
metrics [citation:3]. TimescaleDB is often chosen when a team already runs
Postgres and wants time-series alongside transactional data in one database
[citation:1].

---

## 6. Vector

**What it is:** High-dimensional vector representations of data, often
generated by ML models. Retrieval is by semantic similarity, not exact match
[citation:1].

**Strengths:** Semantic search, approximate nearest-neighbor (ANN) algorithms.

**Trade-offs:** Indexing complexity, storage overhead, latency vs accuracy
trade-off, integration challenges [citation:1].

**When to pick it:** Semantic document search, recommendation engines,
image/video retrieval, RAG (retrieval-augmented generation) for AI apps.

**Free and paid:**

| Engine | Free | Paid |
|---|---|---|
| **pgvector** (Postgres extension) | Free, self-host; handled up to ~50M vectors [citation:3] | Runs on any managed Postgres (RDS, Aurora, Supabase) [citation:5] |
| **Pinecone** | Free tier | Usage-based paid |
| **Qdrant / Weaviate** | Open source, self-host | Cloud offerings |

**Real companies:** pgvector is the "just use Postgres" answer to vector
search — keeping embeddings next to business data in one database kills
the sync job between two systems [citation:7]. AWS recommends starting
with pgvector on existing Aurora/RDS Postgres before adding a dedicated
vector service [citation:5].

**Why this matters for this cookbook:** if you're building AI apps, you'll
need vector search. You almost certainly don't need a dedicated vector
database until you have millions of vectors and specific latency needs.
Start with pgvector.

---

## What "Just use Postgres" actually means

Postgres can replace a surprising number of specialized databases through
extensions [citation:7][citation:11]:

| What you might add | Postgres alternative | How good is the swap? |
|---|---|---|
| Redis (cache) | UNLOGGED tables | Workable — loses TTL, sub-ms reads |
| Redis (queue) | `SKIP LOCKED`, pgmq | Near-painless for simple jobs |
| MongoDB (documents) | JSONB | Often an upgrade — keeps transactions and joins |
| Pinecone (vectors) | pgvector | Near-painless for most RAG |
| InfluxDB (time-series) | TimescaleDB | Workable — extension to maintain |
| Neo4j (graph) | Apache AGE, recursive CTEs | Forced — degrades beyond 5–6 hops |
| Elasticsearch (search) | tsvector, pg_trgm | Workable for small scale; not for logs at petabyte scale |

The argument isn't "Postgres beats every specialized tool." It's that the
hidden cost of running *another* system — backups, monitoring, upgrades,
on-call — is severely underestimated. For a learning project or an early
startup, one database beats four [citation:11].

**When to stop using Postgres:** when the ops cost of the extension or the
performance ceiling actually bites. That's later than most people think,
and earlier than "just use Postgres" advocates admit.

---

## In another language?

None of this is language-specific. The database types are the same
whether you connect from Python, Go, TypeScript, or Java. Your language
changes the *driver* you use, not the *model* the database implements.

The practical lesson from `04-databases/` applies to all six types:
parameterised queries, explicit update fields, checked return values.
If you understand those three in one engine, you can pick up any other.