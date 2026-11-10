# ─────────────────────────────────────────────────────────────
# Lesson: hybrid search with SQLite (FTS5 + fake vectors)
#
# Three endpoints, one dataset, three ranking strategies:
#   GET /search/fts     -> SQLite FTS5, BM25 rank
#   GET /search/vector  -> cosine similarity over fake embeddings
#   GET /search/hybrid  -> Reciprocal Rank Fusion of both
#
# The embeddings are a deterministic hash, not a real model — so
# this lesson runs with no API key. The PATTERN is identical to
# production (Postgres tsvector + pgvector); only the engine and
# the embedding function change.
# ─────────────────────────────────────────────────────────────

import hashlib
import math
import sqlite3
from pathlib import Path

from fastapi import FastAPI, Query

app = FastAPI(title="Hybrid search lesson")

DB_PATH = Path(__file__).parent / "search.db"
EMBEDDING_DIM = 64


# ── The dataset ─────────────────────────────────────────────
# Deliberately chosen so that no single method finds all of
# them. The README walks through the specific queries.
DOCS = [
    (1, "iPhone won't charge"),
    (2, "My phone is not charging"),
    (3, "Battery drains quickly"),
    (4, "Handset has power issues"),
    (5, "Device does not turn on"),
    (6, "How to reset password"),
    (7, "iPhone battery replacement guide"),
]


# ── Fake embeddings ────────────────────────────────────────
# A deterministic hash mapped to a unit-ish vector. NOT
# semantic — two texts get similar vectors only if they share
# tokens. But it's enough to demonstrate the mechanism, and it
# runs with no model.
#
# To swap in real embeddings:
#   from openai import OpenAI
#   client = OpenAI()
#   def fake_embed(text):
#       resp = client.embeddings.create(
#           model="text-embedding-3-small", input=text)
#       return resp.data[0].embedding
# And set EMBEDDING_DIM = 1536.
def fake_embed(text: str) -> list[float]:
    # Use each token's hash so similar token sets → similar vectors.
    vec = [0.0] * EMBEDDING_DIM
    tokens = text.lower().replace("'", "").replace(".", "").split()
    for tok in tokens:
        h = hashlib.sha256(tok.encode()).digest()
        for i in range(EMBEDDING_DIM):
            # -1.0 .. 1.0 from each byte
            vec[i] += (h[i % len(h)] / 255.0) * 2 - 1
    # Normalize
    norm = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [x / norm for x in vec]


def cosine(a: list[float], b: list[float]) -> float:
    # Both vectors are already normalized, so cosine = dot product.
    return sum(x * y for x, y in zip(a, b))


# ── Database setup ─────────────────────────────────────────
def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, isolation_level=None)
    conn.row_factory = sqlite3.Row
    return conn


def _init_db():
    conn = _connect()
    try:
        conn.executescript("""
            DROP TABLE IF EXISTS docs;
            DROP TABLE IF EXISTS docs_fts;

            CREATE TABLE docs (
                id         INTEGER PRIMARY KEY,
                body       TEXT NOT NULL,
                embedding  BLOB NOT NULL
            );

            CREATE VIRTUAL TABLE docs_fts USING fts5(
                body,
                content='docs',
                content_rowid='id'
            );
        """)

        # Insert docs and embeddings
        for doc_id, body in DOCS:
            emb = fake_embed(body)
            # Store as bytes — 8 bytes per float
            blob = b"".join(x.to_bytes(8, "little", signed=True) for x in emb)
            conn.execute(
                "INSERT INTO docs (id, body, embedding) VALUES (?, ?, ?)",
                (doc_id, body, blob),
            )
            conn.execute(
                "INSERT INTO docs_fts (rowid, body) VALUES (?, ?)",
                (doc_id, body),
            )
    finally:
        conn.close()


def _load_embedding(blob: bytes) -> list[float]:
    return [
        int.from_bytes(blob[i : i + 8], "little", signed=True) / 10**15
        for i in range(0, len(blob), 8)
    ]


_init_db()


# ── Full-text search (FTS5 + BM25) ─────────────────────────
def search_fts(query: str, limit: int = 10) -> list[dict]:
    with _connect() as conn:
        # FTS5 MATCH syntax: quote each token to avoid operators
        tokens = [t for t in query.lower().split() if t]
        if not tokens:
            return []
        match = " OR ".join(f'"{t}"' for t in tokens)
        rows = conn.execute(
            """
            SELECT d.id, d.body, bm25(docs_fts) AS rank
            FROM docs_fts
            JOIN docs d ON d.id = docs_fts.rowid
            WHERE docs_fts MATCH ?
            ORDER BY rank
            LIMIT ?
            """,
            (match, limit),
        ).fetchall()
        # bm25 returns lower-is-better; negate so higher-is-better
        return [{"id": r["id"], "body": r["body"], "score": -r["rank"]} for r in rows]


# ── Vector search (cosine over fake embeddings) ───────────
def search_vector(query: str, limit: int = 10) -> list[dict]:
    q_emb = fake_embed(query)
    with _connect() as conn:
        rows = conn.execute("SELECT id, body, embedding FROM docs").fetchall()
    scored = []
    for r in rows:
        doc_emb = _load_embedding(r["embedding"])
        scored.append({
            "id": r["id"],
            "body": r["body"],
            "score": cosine(q_emb, doc_emb),
        })
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:limit]


# ── Hybrid search (Reciprocal Rank Fusion) ────────────────
def search_hybrid(query: str, limit: int = 10, k: int = 60) -> list[dict]:
    fts = search_fts(query, limit=50)
    vec = search_vector(query, limit=50)
    # Build id -> metadata (body)
    meta = {r["id"]: r["body"] for r in fts + vec}
    # Accumulate RRF scores
    scores: dict[int, float] = {}
    for rank, r in enumerate(fts, start=1):
        scores[r["id"]] = scores.get(r["id"], 0) + 1 / (k + rank)
    for rank, r in enumerate(vec, start=1):
        scores[r["id"]] = scores.get(r["id"], 0) + 1 / (k + rank)
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:limit]
    return [
        {"id": doc_id, "body": meta.get(doc_id, ""), "score": score}
        for doc_id, score in ranked
    ]


# ── Endpoints ─────────────────────────────────────────────
@app.get("/search/fts")
def fts_endpoint(q: str = Query(..., min_length=1)):
    return {"method": "fts", "query": q, "results": search_fts(q)}


@app.get("/search/vector")
def vector_endpoint(q: str = Query(..., min_length=1)):
    return {"method": "vector", "query": q, "results": search_vector(q)}


@app.get("/search/hybrid")
def hybrid_endpoint(q: str = Query(..., min_length=1)):
    return {"method": "hybrid", "query": q, "results": search_hybrid(q)}


@app.get("/docs")
def list_docs():
    with _connect() as conn:
        rows = conn.execute("SELECT id, body FROM docs ORDER BY id").fetchall()
    return [dict(r) for r in rows]


# ─────────────────────────────────────────────────────────────
# Exercise:
#   1. Start the server:
#        pip install -r requirements.txt
#        uvicorn main:app --reload --port 8019
#   2. Query "iPhone charge" on all three endpoints.
#      Full-text wins — the word "iPhone" is an exact match.
#   3. Query "phone battery issue".
#      Vector finds docs that don't contain "phone" or "battery"
#      but are topically similar. Full-text misses those.
#   4. Query "iPhone power problem".
#      Only hybrid finds BOTH the exact-match doc and the
#      meaning-match doc. That's the lesson.
#   5. Look at the `search_hybrid` function. It calls both
#      searches, then merges by RRF. The constant `k=60` controls
#      how much a single #1 rank can dominate. Try k=1 and k=200.
#      Notice the top result changes.
#   6. Swap `fake_embed` for a real embedding function (OpenAI,
#      Cohere, or sentence-transformers). Change EMBEDDING_DIM to
#      match (1536 for OpenAI, 384 for MiniLM). The pattern
#      doesn't change; only the ranking quality improves.
# ─────────────────────────────────────────────────────────────