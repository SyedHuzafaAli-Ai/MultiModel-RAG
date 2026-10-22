# from pinecone import Pinecone
# from dotenv import load_dotenv
# import os
# # Load .env file
# load_dotenv()

# # Get API key from .env
# api_key = os.getenv("PINECONE_API_KEY")

# # Initialize Pinecone
# pc = Pinecone(api_key=api_key)
# from pinecone import Pinecone
# from dotenv import load_dotenv
# import os

# # Load environment variables
# load_dotenv()

# # Get API key
# api_key = os.getenv("PINECONE_API_KEY")

# try:
#     # Initialize Pinecone
#     pc = Pinecone(api_key=api_key)

#     # Connect Index
#     index_name = "textembedding"
#     index = pc.Index(index_name)

#     # Test connection
#     stats = index.describe_index_stats()

#     print("✅ Pinecone connected successfully")
#     print(stats)

# except Exception as e:
#     print("❌ Pinecone connection failed")
#     print("Error:", e)
# index_name = "textembedding"
# index = pc.Index(index_name)
"""
Pinecone connection. Single, clean initialization.
"""

from pinecone import Pinecone
from app.config import settings
from app.logger import get_logger

logger = get_logger(__name__)

try:
    pc = Pinecone(api_key=settings.PINECONE_API_KEY)
    index = pc.Index(settings.PINECONE_INDEX_NAME)

    stats = index.describe_index_stats()
    logger.info(f"Connected to Pinecone index '{settings.PINECONE_INDEX_NAME}' | stats: {stats}")

    existing_dim = stats.get("dimension")
    if existing_dim and existing_dim != settings.EMBEDDING_DIM:
        logger.error(
            f"Pinecone index dimension ({existing_dim}) does not match "
            f"embedding model dimension ({settings.EMBEDDING_DIM}). Upserts will fail until these match."
        )

except Exception as e:
    logger.error(f"Failed to connect to Pinecone index '{settings.PINECONE_INDEX_NAME}': {e}")
    raise