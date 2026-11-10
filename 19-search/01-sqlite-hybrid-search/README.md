# SQLite hybrid search

Three endpoints, one dataset, three ranking strategies:
- `/search/fts` — SQLite FTS5 full-text (keyword match)
- `/search/vector` — cosine similarity over fake embeddings (meaning match)
- `/search/hybrid` — reciprocal rank fusion of both

**No external services.** SQLite is built into Python. The embeddings are
a deterministic hash, so no API key is needed. The *pattern* is identical
to production (Postgres `tsvector` + `pgvector`), only the engine changes.

## What you'll learn
- How FTS5 ranks by keyword frequency (BM25)
- How cosine similarity ranks by "meaning" (even with fake embeddings)
- Why hybrid search finds documents each individual method misses
- How Reciprocal Rank Fusion (RRF) merges two ranked lists

## How to run
```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8019
```

Using port 8019. The database is created and populated on startup.

## The dataset

Seven short support documents about phone charging problems. They're
deliberately chosen so that **no single method finds all of them**:

| # | Text | Notes |
|---|---|---|
| 1 | `iPhone won't charge` | Contains "charge", "iPhone" |
| 2 | `My phone is not charging` | Contains "charging" but not "charge" (stemmed to same) |
| 3 | `Battery drains quickly` | No "charge" or "phone" — different wording, same topic |
| 4 | `Handset has power issues` | No "phone" — uses "handset"; no "charge" |
| 5 | `Device does not turn on` | Different problem entirely, but related to battery |
| 6 | `How to reset password` | Totally unrelated — control document |
| 7 | `iPhone battery replacement guide` | Contains "iPhone" and "battery" — should rank for battery queries |

## Walkthrough — prove the difference

**Step 1: Start the server**

```powershell
cd D:\agentic-backend-cookbook\19-search\01-sqlite-hybrid-search
pip install -r requirements.txt
uvicorn main:app --reload --port 8019
```

**Step 2: A keyword query where full-text wins**

Query: `iPhone charge`

```powershell
curl.exe -s "http://127.0.0.1:8019/search/fts?q=iPhone+charge"
curl.exe -s "http://127.0.0.1:8019/search/vector?q=iPhone+charge"
curl.exe -s "http://127.0.0.1:8019/search/hybrid?q=iPhone+charge"
```

Expected ranking:
- **FTS:** doc 1 (`iPhone won't charge`) first — exact word matches
- **Vector:** doc 1 and doc 7 both score high (iPhone + battery context)
- **Hybrid:** doc 1 highest — both methods agree

Full-text wins here because the query has a specific product name.
Vector search doesn't know what "iPhone" means — it's just a token in a
hash.

**Step 3: A meaning query where vector wins**

Query: `phone battery issue`

```powershell
curl.exe -s "http://127.0.0.1:8019/search/fts?q=phone+battery+issue"
curl.exe -s "http://127.0.0.1:8019/search/vector?q=phone+battery+issue"
curl.exe -s "http://127.0.0.1:8019/search/hybrid?q=phone+battery+issue"
```

Expected ranking:
- **FTS:** doc 7 (`iPhone battery replacement`) and doc 2 (`phone is not charging`) — have the words "phone" and "battery"
- **Vector:** doc 3 (`Battery drains quickly`) and doc 4 (`Handset has power issues`) also score high — related topic, different words
- **Hybrid:** all four appear — FTS contribution for doc 2 and 7, vector contribution for doc 3 and 4

Full-text misses docs 3 and 4 because they don't contain "phone" or
"battery". Vector search finds them because the hash embedding places
similar-topic words near each other.

**Step 4: A query where hybrid wins**

Query: `iPhone power problem`

```powershell
curl.exe -s "http://127.0.0.1:8019/search/fts?q=iPhone+power+problem"
curl.exe -s "http://127.0.0.1:8019/search/vector?q=iPhone+power+problem"
curl.exe -s "http://127.0.0.1:8019/search/hybrid?q=iPhone+power+problem"
```

Expected:
- **FTS:** doc 1 (`iPhone won't charge`) — has "iPhone"
- **Vector:** doc 4 (`Handset has power issues`), doc 3 (`Battery drains`) — topic similarity
- **Hybrid:** doc 1 AND doc 4 in the top results — **only hybrid finds both**

The query mixes a specific word ("iPhone") with a generic concept ("power
problem"). Full-text catches the word match; vector catches the meaning
match. Hybrid catches both.

**Step 5: A query no method finds**

Query: `password reset`

```powershell
curl.exe -s "http://127.0.0.1:8019/search/fts?q=password+reset"
curl.exe -s "http://127.0.0.1:8019/search/vector?q=password+reset"
curl.exe -s "http://127.0.0.1:8019/search/hybrid?q=password+reset"
```

Expected: all three return doc 6 (`How to reset password`) — and that's
it. **This is the control.** All methods should find the obvious match.
If they don't, something is broken.

## How Reciprocal Rank Fusion works

Given two ranked lists:

```
FTS:    [doc1, doc7, doc2]
Vector: [doc2, doc4, doc3]
```

For each document, compute:

```
score = 1 / (k + fts_rank) + 1 / (k + vector_rank)
```

with `k = 60`:

```
doc1: 1/(60+1) + 0        = 0.0164    (only FTS)
doc2: 1/(60+3) + 1/(60+1) = 0.0164    (both)
doc3: 0        + 1/(60+3) = 0.0159    (only Vector)
doc4: 0        + 1/(60+2) = 0.0161    (only Vector)
doc7: 1/(60+2) + 0        = 0.0161    (only FTS)
```

Sort by score. Documents in **both** lists win. Documents in **one**
list rank by their position in that list. Documents in **neither** list
don't appear.

That's the whole algorithm. It's 10 lines of code:

```python
def rrf(fts_results, vec_results, k=60):
    scores = {}
    for rank, doc_id in enumerate(fts_results, start=1):
        scores[doc_id] = scores.get(doc_id, 0) + 1/(k+rank)
    for rank, doc_id in enumerate(vec_results, start=1):
        scores[doc_id] = scores.get(doc_id, 0) + 1/(k+rank)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)
```

## The fake embeddings (and why they still work)

The lesson doesn't call an embedding model. It uses a deterministic hash:

```python
def fake_embed(text: str) -> list[float]:
    """Map text to a 64-dim vector deterministically."""
    h = hashlib.sha256(text.encode()).digest()
    return [b / 255.0 for b in h[:64]]
```

This produces different vectors for different texts, but it does **not**
capture meaning. So how can vector search "work" in this lesson?

It works **partially**, because:
1. Similar documents share similar words → similar hashes → similar
   cosine similarity. Not *semantic* similarity, but lexical proximity.
2. The demo dataset is small enough that even a weak signal surfaces
   the right answer.

**This is not real vector search.** It's a teaching stand-in. If you
swap in `OpenAI text-embedding-3-small`, the ranking gets dramatically
better — "Battery drains quickly" and "power issues" would genuinely
cluster together even without shared words.

The pattern — embed, cosine, rank — is identical. Only the embedding
function changes.

**To use real embeddings:** replace `fake_embed` with:

```python
from openai import OpenAI
client = OpenAI()

def real_embed(text: str) -> list[float]:
    resp = client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    return resp.data[0].embedding
```

And change `EMBEDDING_DIM` to 1536. Everything else stays the same.

## What this example deliberately skips

- **A vector index.** SQLite scans all rows for every query. Fine for
  7 docs, too slow for 1M. Postgres `pgvector` (HNSW index) or
  `sqlite-vss` handle this.
- **Real embeddings.** See above.
- **Reranking.** Production RAG adds a cross-encoder reranker on top of
  the retrieved candidates. It's slower but more accurate. Separate lesson.
- **Metadata filtering.** "Only search docs in this workspace." Needs a
  filter in the query. Postgres supports it; SQLite needs a `WHERE` clause
  around the FTS query.
- **Chunking.** Documents larger than one embedding get split. Each chunk
  is retrieved independently, then the parent document is ranked.
- **Weighting.** RRF treats both lists equally. Real systems sometimes
  weight the vector list higher for "meaning" queries and the full-text
  list higher for "exact match" queries. That's a tuning knob.

---

## In another language?

The three concepts are universal. The available tools vary:

| Language | Full-text | Vector | Hybrid |
|---|---|---|---|
| Python | SQLite FTS5 / Postgres `tsvector` | `pgvector` / `qdrant-client` | RRF in Python |
| Go | Bleve / Postgres `tsvector` | `pgvector` / Qdrant | RRF in Go |
| Rust | Tantivy / Postgres `tsvector` | `pgvector` / Qdrant | RRF in Rust |
| Node | SQLite FTS5 / `typesense` | `pgvector` / Pinecone | RRF in JS |
| PHP | Meilisearch | Qdrant / Pinecone | RRF in PHP |
| Ruby | `pg_search` | `neighbor` gem | RRF in Ruby |
| Java | Lucene / Elasticsearch | `pgvector` / Weaviate | RRF in Java |
| C# | Lucene.NET | `pgvector` / Qdrant | RRF in C# |

The algorithm — FTS5/tsvector for keyword ranking, embeddings+cosine for
meaning, RRF to merge — is the same everywhere. If you understand why
doc 4 (`Handset has power issues`) appears only in the vector result for
the "iPhone power problem" query, you understand hybrid search.