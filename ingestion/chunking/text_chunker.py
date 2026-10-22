"""
Text chunking.
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config import settings
from app.logger import get_logger

logger = get_logger(__name__)


def chunk_text(text: str, chunk_size: int = None, chunk_overlap: int = None) -> list[str]:
    if not text or not text.strip():
        logger.warning("chunk_text called with empty/whitespace-only text. Returning no chunks.")
        return []

    chunk_size = chunk_size or settings.CHUNK_SIZE
    chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP

    if chunk_overlap >= chunk_size:
        logger.error(f"chunk_overlap ({chunk_overlap}) must be smaller than chunk_size ({chunk_size})")
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    try:
        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        chunks = splitter.split_text(text)
    except Exception as e:
        logger.error(f"Text splitting failed: {e}")
        raise

    logger.info(f"Split text into {len(chunks)} chunks (size={chunk_size}, overlap={chunk_overlap})")
    return chunks