"""
Pydantic models for request/response validation
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class LawSection(BaseModel):
    """Law section model"""
    id: str
    law: str
    law_name: str
    chapter: Optional[str] = None
    chapter_title: Optional[str] = None
    section: str
    title: str
    text: str
    type: str = "law_section"
    score: Optional[float] = None


class CaseLaw(BaseModel):
    """Case law model"""
    id: str
    case_name: str
    court: str
    year: Optional[int] = None
    citation: Optional[str] = None
    facts: Optional[str] = None
    judgment: str
    legal_issues: Optional[List[str]] = None
    score: Optional[float] = None


class ChatMessage(BaseModel):
    """Chat message model"""
    role: str = Field(..., description="Role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: Optional[datetime] = None


class ChatRequest(BaseModel):
    """Chat request model"""
    session_id: str = Field(..., description="Unique session identifier")
    message: str = Field(..., description="User query")
    include_history: bool = Field(default=True, description="Include chat history")


class ChatResponse(BaseModel):
    """Chat response model"""
    session_id: str
    message: str
    sources: List[LawSection] = []
    timestamp: datetime = Field(default_factory=datetime.now)


class SearchRequest(BaseModel):
    """Semantic search request"""
    query: str = Field(..., description="Search query")
    law_filter: Optional[List[str]] = Field(None, description="Filter by specific laws")
    top_k: int = Field(default=5, description="Number of results to return")


class SearchResponse(BaseModel):
    """Semantic search response"""
    query: str
    results: List[LawSection]
    total_results: int


class CaseSummaryRequest(BaseModel):
    """Case summary request"""
    session_id: str
    case_query: str = Field(..., description="Case name or description")


class CaseSummaryResponse(BaseModel):
    """Case summary response"""
    session_id: str
    case: Optional[CaseLaw]
    summary: str
    timestamp: datetime = Field(default_factory=datetime.now)


class CaseSimilarityRequest(BaseModel):
    """Case similarity request"""
    case_description: str = Field(..., description="User's case description")
    court_filter: Optional[List[str]] = Field(None, description="Filter by court")
    top_k: int = Field(default=5, description="Number of similar cases")


class CaseSimilarityResponse(BaseModel):
    """Case similarity response"""
    query: str
    similar_cases: List[CaseLaw]
    total_results: int


class DocumentUploadResponse(BaseModel):
    """Document upload response"""
    session_id: str
    document_id: str
    filename: str
    chunks: int
    message: str


class DocumentQueryRequest(BaseModel):
    """Document query request"""
    session_id: str
    document_id: str
    query: str


class DocumentQueryResponse(BaseModel):
    """Document query response"""
    session_id: str
    document_id: str
    query: str
    answer: str
    relevant_chunks: List[Dict[str, Any]]
    timestamp: datetime = Field(default_factory=datetime.now)


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.now)
