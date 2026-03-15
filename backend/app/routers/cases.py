"""
Cases Router - Features 3 & 4: Case Law Summarizer & Case Similarity Search
"""

from fastapi import APIRouter, HTTPException
from ..models.schemas import (
    CaseSummaryRequest,
    CaseSummaryResponse,
    CaseSimilarityRequest,
    CaseSimilarityResponse,
    CaseLaw
)
from ..services import session_manager, pinecone_service, llm_service

router = APIRouter(prefix="/api/cases", tags=["Case Laws"])


@router.post("/summarize", response_model=CaseSummaryResponse)
async def summarize_case(request: CaseSummaryRequest):
    """
    Feature 3: Case Law Summarizer
    
    Flow:
    1. Embed case name/query
    2. Retrieve case from Pinecone
    3. Send case data + chat history to LLM
    4. Generate structured summary
    5. Append to chat history
    """
    try:
        # Search for the case
        search_results = pinecone_service.search_cases(
            query=request.case_query,
            top_k=1
        )
        
        if not search_results:
            raise HTTPException(status_code=404, detail="Case not found")
        
        # Get the top match
        case_match = search_results[0]
        metadata = case_match.get('metadata', {})
        
        # Get chat history
        chat_history = session_manager.format_history_for_llm(request.session_id)
        
        # Generate summary
        summary = llm_service.summarize_case(
            case_data=metadata,
            chat_history=chat_history
        )
        
        # Add to session history
        session_manager.add_message(request.session_id, "user", f"Summarize: {request.case_query}")
        session_manager.add_message(request.session_id, "assistant", summary)
        
        # Build case object
        case = CaseLaw(
            id=metadata.get('id', ''),
            case_name=metadata.get('case_name', ''),
            court=metadata.get('court', ''),
            year=metadata.get('year'),
            citation=metadata.get('citation'),
            facts=metadata.get('facts'),
            judgment=metadata.get('judgment', ''),
            judge=metadata.get('judge'),
            petitioner=metadata.get('petitioner'),
            respondent=metadata.get('respondent'),
            score=case_match.get('score')
        )
        
        return CaseSummaryResponse(
            session_id=request.session_id,
            case=case,
            summary=summary
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error summarizing case: {str(e)}")


@router.post("/similar", response_model=CaseSimilarityResponse)
async def find_similar_cases(request: CaseSimilarityRequest):
    """
    Feature 4: Case Similarity Search
    
    Flow:
    1. Embed user's case description
    2. Query Pinecone for top-k similar cases
    3. Retrieve case details
    4. Optionally generate comparative analysis
    """
    try:
        # Search for similar cases
        search_results = pinecone_service.search_cases(
            query=request.case_description,
            top_k=request.top_k,
            court_filter=request.court_filter
        )
        
        if not search_results:
            return CaseSimilarityResponse(
                query=request.case_description,
                similar_cases=[],
                total_results=0
            )
        
        # Format results
        similar_cases = []
        for result in search_results:
            metadata = result.get('metadata', {})
            similar_cases.append(CaseLaw(
                id=metadata.get('id', ''),
                case_name=metadata.get('case_name', ''),
                court=metadata.get('court', ''),
                year=metadata.get('year'),
                citation=metadata.get('citation'),
                facts=metadata.get('facts'),
                judgment=metadata.get('judgment', ''),
                judge=metadata.get('judge'),
                petitioner=metadata.get('petitioner'),
                respondent=metadata.get('respondent'),
                score=result.get('score')
            ))
        
        return CaseSimilarityResponse(
            query=request.case_description,
            similar_cases=similar_cases,
            total_results=len(similar_cases)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding similar cases: {str(e)}")


@router.post("/compare")
async def compare_with_cases(case_description: str, session_id: str):
    """
    Generate detailed comparison between user's case and similar cases
    """
    try:
        # Find similar cases
        search_results = pinecone_service.search_cases(
            query=case_description,
            top_k=5
        )
        
        if not search_results:
            raise HTTPException(status_code=404, detail="No similar cases found")
        
        # Extract case metadata
        cases_data = [result.get('metadata', {}) for result in search_results]
        
        # Generate comparison
        comparison = llm_service.generate_case_comparison(
            user_case=case_description,
            similar_cases=cases_data
        )
        
        # Add to session history
        session_manager.add_message(session_id, "user", f"Compare my case: {case_description}")
        session_manager.add_message(session_id, "assistant", comparison)
        
        return {
            "session_id": session_id,
            "comparison": comparison,
            "similar_cases_count": len(cases_data)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing cases: {str(e)}")


@router.get("/courts")
async def get_available_courts():
    """Get list of courts for filtering"""
    return {
        "courts": [
            "Supreme Court",
            "High Court",
            "District Court",
            "Sessions Court"
        ]
    }
