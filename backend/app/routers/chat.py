"""
Chat Router - Feature 1: Legal Chat (Core Q&A)
"""

from fastapi import APIRouter, HTTPException
from ..models.schemas import ChatRequest, ChatResponse
from ..services import session_manager, pinecone_service, llm_service
from ..core.config import get_settings

router = APIRouter(prefix="/api/chat", tags=["Legal Chat"])
settings = get_settings()


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Legal Chat endpoint with multi-turn conversation support
    
    Flow:
    1. Append user query to chat history
    2. Embed the query
    3. Query Pinecone for relevant law sections
    4. Send chat history + retrieved sections + query to LLM
    5. Generate answer and append to history
    6. Return response
    """
    try:
        # Add user message to history
        session_manager.add_message(request.session_id, "user", request.message)
        
        # Search for relevant law sections
        search_results = pinecone_service.search_laws(
            query=request.message,
            top_k=settings.TOP_K_RESULTS
        )
        
        # Get chat history for context
        chat_history = []
        if request.include_history:
            chat_history = session_manager.format_history_for_llm(request.session_id)
        
        # Generate response using LLM
        response_text = llm_service.generate_chat_response(
            query=request.message,
            context=search_results,
            chat_history=chat_history[:-1] if chat_history else None  # Exclude current query
        )
        
        # Add assistant response to history
        session_manager.add_message(request.session_id, "assistant", response_text)
        
        # Format sources
        from ..models.schemas import LawSection
        sources = []
        for result in search_results:
            metadata = result.get('metadata', {})
            sources.append(LawSection(
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
        
        return ChatResponse(
            session_id=request.session_id,
            message=response_text,
            sources=sources
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")


@router.delete("/{session_id}")
async def clear_chat_history(session_id: str):
    """Clear chat history for a session"""
    try:
        session_manager.clear_session(session_id)
        return {"message": f"Chat history cleared for session {session_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing history: {str(e)}")


@router.get("/{session_id}/history")
async def get_chat_history(session_id: str):
    """Get chat history for a session"""
    try:
        history = session_manager.get_history(session_id)
        return {"session_id": session_id, "history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving history: {str(e)}")
