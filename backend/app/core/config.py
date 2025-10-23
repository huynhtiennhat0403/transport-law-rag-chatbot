"""
Configuration và settings từ environment variables
"""

from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # API key
    GROQ_API_KEY: str

    # Paths
    PROJECT_ROOT: Path = Path(__file__).parent.parent.parent
    CHROMADB_PATH: Path = PROJECT_ROOT / "data" / "law_chroma_db" 
    # ChromaDB 
    COLLECTION_NAME: str = "law_traffic_vietnam"

    # Embedding model
    EMBEDDING_MODEL_NAME: str = "BAAI/bge-m3"

    # LLM 
    DEFAULT_LLM_MODEL: str = "llama-3.3-70b-versatile"
    LLM_TEMPERATURE: float = 0.2
    LLM_MAX_TOKENS: int = 1500
    LLM_TOP_P: float = 0.9
    
    # RAG
    DEFAULT_N_RESULTS: int = 5

    class Config:
        env_file = ".env"
        case_sensitive = True

# Singleton settings 
settings = Settings()