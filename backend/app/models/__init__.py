"""Models module initialization"""
from .schemas import (
    LawSection,
    CaseLaw,
    ChatMessage,
    ChatRequest,
    ChatResponse,
    SearchRequest,
    SearchResponse,
    CaseSummaryRequest,
    CaseSummaryResponse,
    CaseSimilarityRequest,
    CaseSimilarityResponse,
    DocumentUploadResponse,
    DocumentQueryRequest,
    DocumentQueryResponse,
    HealthResponse
)

__all__ = [
    "LawSection",
    "CaseLaw",
    "ChatMessage",
    "ChatRequest",
    "ChatResponse",
    "SearchRequest",
    "SearchResponse",
    "CaseSummaryRequest",
    "CaseSummaryResponse",
    "CaseSimilarityRequest",
    "CaseSimilarityResponse",
    "DocumentUploadResponse",
    "DocumentQueryRequest",
    "DocumentQueryResponse",
    "HealthResponse"
]
