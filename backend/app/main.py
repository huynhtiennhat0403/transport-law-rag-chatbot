"""
FastAPI application entry point
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import chat
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager
    Code trước yield: chạy khi startup
    Code sau yield: chạy khi shutdown
    """
    # ========== STARTUP ==========
    print("\n" + "="*80)
    print("🚀 Starting Traffic Law Chatbot API")
    print("="*80)
    
    # Load models and initialize singletons
    from app.core.chromadb_client import get_collection
    from app.core.embedding_model import get_embedding_model
    from app.services.rag_service import rag_service
    
    get_collection()
    get_embedding_model()
    
    print("\n✅ API is ready!")
    print(f"📚 Collection: {settings.COLLECTION_NAME}")
    print(f"🤖 LLM Model: {settings.DEFAULT_LLM_MODEL}")
    print("="*80 + "\n")
    
    yield  # Server is running here
    
    # ========== SHUTDOWN ==========
    print("\n🛑 Shutting down API...")
    print("👋 Goodbye!\n")


# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Traffic Law Chatbot API",
    description="API cho chatbot tư vấn luật giao thông Việt Nam",
    version="1.0.0",
    lifespan=lifespan  
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api", tags=["chat"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Traffic Law Chatbot API",
        "version": "1.0.0",
        "docs": "/docs"
    }