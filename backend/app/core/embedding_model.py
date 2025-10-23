"""
Embedding model singleton
"""

from sentence_transformers import SentenceTransformer
from functools import lru_cache
from app.core.config import settings

@lru_cache()
def get_embedding_model() -> SentenceTransformer:
    """
    Load embedding model (singleton pattern)
    Only load once and reuse
    """

    model = SentenceTransformer(settings.EMBEDDING_MODEL)
    print(f"Embedding model '{settings.EMBEDDING_MODEL}' loaded.")
    return model