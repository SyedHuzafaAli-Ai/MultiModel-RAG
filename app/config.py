"""
Centralized configuration.
Loads .env ONCE here. Every other module imports settings from
this file instead of calling os.getenv() directly.
"""

import os
from dotenv import load_dotenv
from app.logger import get_logger

logger = get_logger(__name__)

load_dotenv()


class Settings:
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "textembedding")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "data/raw")
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    EMBEDDING_DIM = 384  # must match Pinecone index dimension for all-MiniLM-L6-v2

    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 500))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 50))
    SEARCH_TOP_K = int(os.getenv("SEARCH_TOP_K", 5))

    def validate(self):
        """Call at app startup so missing keys fail immediately and clearly."""
        missing = []
        if not self.PINECONE_API_KEY:
            missing.append("PINECONE_API_KEY")
        if not self.GEMINI_API_KEY:
            missing.append("GEMINI_API_KEY")

        if missing:
            logger.error(f"Missing required environment variables: {missing}")
            raise EnvironmentError(
                f"Missing required environment variables: {missing}. Check your .env file."
            )
        logger.info("Config validated. All required environment variables present.")


settings = Settings()