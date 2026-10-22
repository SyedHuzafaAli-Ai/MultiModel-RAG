# from sentence_transformers import SentenceTransformer

# model = SentenceTransformer("all-MiniLM-L6-v2")

# def get_embedding(text: str):
#     return model.encode(text).tolist()

"""
Text embedding via sentence-transformers.
Model is loaded once at import time (expensive) and reused.
"""

from sentence_transformers import SentenceTransformer
from app.config import settings
from app.logger import get_logger

logger = get_logger(__name__)

try:
    logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
    model = SentenceTransformer(settings.EMBEDDING_MODEL)
    logger.info("Embedding model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load embedding model '{settings.EMBEDDING_MODEL}': {e}")
    raise


def get_embedding(text: str) -> list[float]:
    if not text or not text.strip():
        logger.error("get_embedding called with empty text")
        raise ValueError("Cannot embed empty text")

    try:
        vector = model.encode(text).tolist()
    except Exception as e:
        logger.error(f"Embedding failed for text (len={len(text)}): {e}")
        raise

    if len(vector) != settings.EMBEDDING_DIM:
        logger.warning(
            f"Embedding dimension mismatch: got {len(vector)}, expected {settings.EMBEDDING_DIM}. "
            f"Check EMBEDDING_MODEL matches your Pinecone index dimension."
        )

    return vector