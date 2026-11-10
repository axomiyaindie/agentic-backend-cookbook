# Search

Three ways to find things in your data, each solving a different problem:

| Type | Matches | Example query | Best for |
|---|---|---|---|
| **Full-text** | Words (stemmed, ranked) | "charging problems" | Keyword search over documents |
| **Vector** | Meaning (embeddings) | "why won't my phone charge" | Semantic search, RAG |
| **Hybrid** | Both, reranked | "phone not charging" | Production AI search |

## The one idea to take away

Full-text search and vector search find **different things**.

Full-text searches for the **words you typed**, after stemming (running →
run) and ignoring stopwords (the, a, of). It ranks results by keyword
frequency and rarity.

Vector search searches for the **meaning** of what you typed, by comparing
embeddings — numerical vectors that capture semantic similarity. "Phone
won't charge" and "handset is not charging" have very different words but
nearly identical embeddings.

| Query | Full-text finds | Vector finds |
|---|---|---|
| "iPhone battery issue" | Docs containing "iPhone", "battery", "issue" | Docs about battery problems, even if they say "power" and "drain" |
| "how to reset password" | Docs with those exact words | Docs about account recovery, password reset, login help |
| SKU "AX-4402" | The exact SKU | Unreliable — SKUs don't have semantic meaning |

**Neither is strictly better.** They fail on different things. That's why
production search is usually **hybrid**: run both, merge the ranked lists,
rerank by a combined score.

## Why this matters for AI backends

Search is the **retrieval** half of RAG (retrieval-augmented generation).
When you ask an AI a question about your own documents, the pipeline is:

```
question → search docs → take top N → stuff into prompt → model answers
```

If the search returns the wrong docs, the model answers the wrong question.
Full-text alone misses paraphrases. Vector alone misses exact terms (SKUs,
error codes, product names). Hybrid gets both.

This is why every serious RAG system is hybrid. If you're building one,
the search layer is where the quality is won or lost.

## The three implementations

### 1. Full-text

SQLite has FTS5 (a built-in full-text engine with BM25 ranking).
Postgres has `tsvector` + `ts_rank`. Both implement the same idea:
tokenize the text, stem each word, index the stems, rank by term frequency.

```sql
-- SQLite FTS5
CREATE VIRTUAL TABLE docs_fts USING fts5(body);
SELECT rowid, body, bm25(docs_fts) AS rank
FROM docs_fts
WHERE docs_fts MATCH 'charging OR problem'
ORDER BY rank;
```

**Pros:** No embedding model needed. Fast. Exact matches.
**Cons:** Misses synonyms. Bad at typos. Bad at meaning.

### 2. Vector

Each document is converted to a vector (an embedding) that captures its
meaning. Queries are converted the same way, and you rank by cosine
distance. SQLite doesn't have a built-in vector index, but the math is
simple enough to compute in Python for a small dataset.

Production options:
- Postgres + `pgvector` (HNSW index)
- SQLite + `sqlite-vss`
- Qdrant, Weaviate, Pinecone (dedicated vector databases)

**Pros:** Finds semantically similar results. Works across phrasings.
**Cons:** Needs an embedding model. No exact matches — SKUs and error
codes fail. Cost: one embedding call per document, per query.

### 3. Hybrid

Run both, merge the results. The common algorithm is **Reciprocal Rank
Fusion (RRF)**:

```
score(doc) = 1 / (k + rank_fulltext(doc)) + 1 / (k + rank_vector(doc))
```

Where `k` is a constant (usually 60). Documents ranked high by either
method end up high in the merged list. Documents ranked high by **both**
end up highest.

**Pros:** Best of both. Handles queries that work in one but not the other.
**Cons:** Two indexes, more complex query, slightly slower.

## Lesson

`01-sqlite-hybrid-search/` — a FastAPI app with three endpoints:

- `GET /search/fts?q=...` — SQLite FTS5, BM25 ranking
- `GET /search/vector?q=...` — cosine similarity over fake embeddings
- `GET /search/hybrid?q=...` — reciprocal rank fusion of both

The README walks you through a query where each method wins.

**The embeddings are fake** (a deterministic hash → vector, so the lesson
runs without an API key). The README explains how to swap in a real
embedding model. The **pattern** is what matters, and it's identical with
real embeddings.

## Where this fits in real code

- **RAG** — the "retrieve" half of retrieval-augmented generation.
- **E-commerce** — product search. Typos matter (vector), SKUs matter
  (full-text), so it's always hybrid.
- **Support docs** — full-text for product names, vector for "my thing
  won't turn on."
- **Internal tools** — search across tickets, docs, messages, code.

## What this lesson does not cover

- **Real embeddings.** The lesson uses a hash-based fake. Real embeddings
  come from a model (OpenAI `text-embedding-3-small`, Cohere, or a local
  model like `sentence-transformers`). The README shows the swap.
- **Vector index.** SQLite can't index vectors efficiently. This lesson
  scans all rows and computes cosine similarity in Python — fine for
  hundreds of documents, too slow for millions. Production uses
  `pgvector`, `sqlite-vss`, or a dedicated vector DB.
- **Reranking.** Modern RAG stacks add a second stage: retrieve 50
  candidates, then rerank with a cross-encoder model. This lesson stops
  at the retrieval stage.
- **Chunking.** Documents longer than the embedding model's context get
  split into chunks, each embedded separately. That's its own lesson.
- **Metadata filtering.** "Search only documents in this workspace" needs
  a filter alongside the vector search. Postgres pgvector supports this
  natively; SQLite doesn't.

The mechanism here — text match, meaning match, fused ranking — is the
seed of all of them.

---

## In another language?

The concepts are universal. The available tools vary:

| Language | Full-text | Vector | Hybrid |
|---|---|---|---|
| Python | SQLite FTS5, Postgres `tsvector` | `pgvector`, `qdrant-client` | RRF in Python |
| Go | Bleve, Postgres `tsvector` | `pgvector`, Qdrant | RRF in Go |
| Rust | Tantivy, Postgres `tsvector` | `pgvector`, Qdrant | RRF in Rust |
| Node | SQLite FTS5, `typesense` | `pgvector`, Pinecone | RRF in JS |
| PHP | Meilisearch, `tsvector` | Qdrant, Pinecone | RRF in PHP |
| Ruby | pg_search, `tsvector` | `neighbor` gem, Qdrant | RRF in Ruby |
| Java | Lucene, Elasticsearch | pgvector, Weaviate | RRF in Java |
| C# | Lucene.NET, `tsvector` | pgvector, Qdrant | RRF in C# |

The algorithm — tokenize+rank for text, embed+cosine for vectors, RRF to
merge — is the same everywhere. If you understand why the lesson's query
returns different results from each endpoint, you understand hybrid search
in any language.