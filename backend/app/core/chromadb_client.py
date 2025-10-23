"""
ChromaDB client singleton
"""

import chromadb
from functools import lru_cache
from app.core.config import settings

@lru_cache()
def get_chromadb_client() -> chromadb.Client:
    """Create and return a ChromaDB client singleton."""
    client = chromadb.PersistentClient(path=str(settings.CHROMADB_PATH))
    print(f"ChromaDB client initialized at {settings.CHROMADB_PATH}")
    return client

@lru_cache()
def get_chromadb_collection() -> chromadb.Collection:
    """Get or create the ChromaDB collection."""
    client = get_chromadb_client()
    collection = client.get_collection(name=settings.COLLECTION_NAME)
    print(f"ChromaDB collection '{settings.COLLECTION_NAME}' is ready.")
    return collection