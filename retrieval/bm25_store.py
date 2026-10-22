"""
Local keyword-search corpus for hybrid search.
Every chunk stored in Pinecone is mirrored here (in a SQLite file)
so we can also run BM25 keyword search and fuse it with vector search.
"""

import sqlite3
import os
from rank_bm25 import BM25Okapi
from app.logger import get_logger

logger = get_logger(__name__)

DB_PATH = "data/bm25_corpus.db"


def _get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            id TEXT PRIMARY KEY,
            text TEXT,
            source TEXT,
            page INTEGER,
            doc_id TEXT
        )
    """)
    return conn


def add_chunk(chunk_id: str, text: str, source: str, page: int, doc_id: str):
    try:
        conn = _get_conn()
        conn.execute(
            "INSERT OR REPLACE INTO chunks (id, text, source, page, doc_id) VALUES (?, ?, ?, ?, ?)",
            (chunk_id, text, source, page, doc_id)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to store chunk {chunk_id} in BM25 corpus: {e}")
        # Non-fatal: hybrid search will just have less BM25 coverage.


def bm25_search(query: str, top_k: int = 10) -> list[dict]:
    try:
        conn = _get_conn()
        rows = conn.execute("SELECT id, text, source, page FROM chunks").fetchall()
        conn.close()
    except Exception as e:
        logger.error(f"BM25 corpus read failed: {e}")
        return []

    if not rows:
        logger.warning("BM25 corpus is empty — no keyword search results possible yet")
        return []

    corpus_ids = [r[0] for r in rows]
    corpus_texts = [r[1] for r in rows]
    tokenized = [t.lower().split() for t in corpus_texts]

    bm25 = BM25Okapi(tokenized)
    scores = bm25.get_scores(query.lower().split())

    ranked = sorted(zip(corpus_ids, scores, rows), key=lambda x: x[1], reverse=True)[:top_k]

    results = []
    for chunk_id, score, row in ranked:
        if score <= 0:
            continue
        results.append({
            "id": chunk_id,
            "text": row[1],
            "source": row[2],
            "page": row[3],
            "bm25_score": float(score)
        })

    logger.info(f"BM25 search returned {len(results)} results for query '{query}'")
    return results