"""
Chat API endpoints
"""
from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatRequest, ChatResponse
from app.services.rag_service import rag_service

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Chat endpoint 
    
    Args:
        request: ChatRequest with question, n_results, show_sources, model
        
    Returns:
        ChatResponse with answer and sources
    """
    try:
        # Call RAG service
        answer, sources = rag_service.query(
            question=request.question, 
            n_results=request.n_results,
            show_sources=request.show_sources,
            model=request.model
        )
        
        return ChatResponse(
            answer=answer,
            sources=sources if request.show_sources else None,
            question=request.question
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi xử lý câu hỏi: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Traffic Law Chatbot API"
    }