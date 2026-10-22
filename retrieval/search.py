"""
Hybrid search: dense (Pinecone) + sparse (BM25), fused with
Reciprocal Rank Fusion (RRF).
"""

from embeddings.embedder import get_embedding
from retrieval.pinecone_client import index
from retrieval.bm25_store import bm25_search
from app.config import settings
from app.logger import get_logger

logger = get_logger(__name__)

RRF_K = 60  # standard RRF constant


def _dense_search(query: str, top_k: int) -> list[dict]:
    try:
        query_vector = get_embedding(query)
        results = index.query(vector=query_vector, top_k=top_k, include_metadata=True)
    except Exception as e:
        logger.error(f"Dense search failed: {e}")
        return []

    matches = []
    for match in results.get("matches", []):
        metadata = match.get("metadata", {})
        matches.append({
            "text": metadata.get("text", ""),
            "page": metadata.get("page"),
            "source": metadata.get("source", "unknown"),
            "dense_score": match.get("score")
        })
    return matches


def search_chunks(query: str, top_k: int = None) -> list[dict]:
    if not query or not query.strip():
        logger.warning("search_chunks called with empty query")
        return []

    top_k = top_k or settings.SEARCH_TOP_K
    candidate_k = max(top_k * 4, 20)  # pull a wider pool before fusing/reranking

    dense_results = _dense_search(query, candidate_k)
    sparse_results = bm25_search(query, candidate_k)

    # Reciprocal Rank Fusion — combine two ranked lists by rank, not raw score,
    # since dense cosine scores and BM25 scores aren't on the same scale.
    fused_scores: dict[str, float] = {}
    text_lookup: dict[str, dict] = {}

    for rank, item in enumerate(dense_results):
        key = item["text"]
        fused_scores[key] = fused_scores.get(key, 0) + 1 / (RRF_K + rank + 1)
        text_lookup[key] = item

    for rank, item in enumerate(sparse_results):
        key = item["text"]
        fused_scores[key] = fused_scores.get(key, 0) + 1 / (RRF_K + rank + 1)
        text_lookup.setdefault(key, item)

    ranked_keys = sorted(fused_scores, key=fused_scores.get, reverse=True)[:candidate_k]
    fused = [{**text_lookup[k], "fused_score": fused_scores[k]} for k in ranked_keys]

    logger.info(
        f"Hybrid search '{query}': {len(dense_results)} dense + {len(sparse_results)} sparse -> "
        f"{len(fused)} fused candidates"
    )
    return fused[:top_k]  # reranker (next step) will refine this further