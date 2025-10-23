"""
Pydantic schemas for requests/responses
"""

from pydantic import BaseModel, Field
from typing import List, Optional

class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    question: str = Field(...,min_length=1,  description="User's question")
    n_results: int = Field(5,ge=1, le=10,  description="Number of retrieved documents to use for context")
    show_sources: bool = Field(False, description="Whether to show source documents in the response")
    model: str = Field("llama-3.3-70b-versatile", description="LLM model to use")

class Source(BaseModel):
    """Source document model"""
    reference: str
    content: str
    relevent_score: float   

class ChatResponse(BaseModel):
    """Response model cho chat endpoint"""
    answer: str
    sources: Optional[List[Source]] = None
    question: str