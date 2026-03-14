"""
Search Router - Feature 2: Law Section Semantic Search
"""

from fastapi import APIRouter, HTTPException
from ..models.schemas import SearchRequest, SearchResponse, LawSection
from ..services import pinecone_service
from ..core.config import get_settings

router = APIRouter(prefix="/api/search", tags=["Semantic Search"])
settings = get_settings()


@router.post("/", response_model=SearchResponse)
async def semantic_search(request: SearchRequest):
    """
    Law section semantic search
    
    Flow:
    1. Embed the search query
    2. Query Pinecone for top-k similar law sections
    3. Return retrieved sections
    
    Supports:
    - Filtering by specific laws (e.g., only IPC, CrPC)
    - Adjustable top_k results
    """
    try:
        # Search Pinecone
        search_results = pinecone_service.search_laws(
            query=request.query,
            top_k=request.top_k,
            law_filter=request.law_filter
        )
        
        # Format results
        results = []
        for result in search_results:
            metadata = result.get('metadata', {})
            results.append(LawSection(
                id=metadata.get('id', ''),
                law=metadata.get('law', ''),
                law_name=metadata.get('law_name', ''),
                chapter=metadata.get('chapter'),
                chapter_title=metadata.get('chapter_title'),
                section=metadata.get('section', ''),
                title=metadata.get('title', ''),
                text=metadata.get('text', ''),
                score=result.get('score')
            ))
        
        return SearchResponse(
            query=request.query,
            results=results,
            total_results=len(results)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error performing search: {str(e)}")


@router.get("/laws")
async def get_available_laws():
    """Get list of available laws for filtering"""
    return {
        "laws": [
            {"code": "IPC", "name": "Indian Penal Code"},
            {"code": "CrPC", "name": "Code of Criminal Procedure"},
            {"code": "CPC", "name": "Code of Civil Procedure"},
            {"code": "IEA", "name": "Indian Evidence Act"},
            {"code": "MVA", "name": "Motor Vehicles Act"},
            {"code": "NIA", "name": "Negotiable Instruments Act"},
            {"code": "IDA", "name": "Indian Divorce Act"},
            {"code": "HMA", "name": "Hindu Marriage Act"}
        ]
    }
