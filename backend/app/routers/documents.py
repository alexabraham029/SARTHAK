"""
Documents Router - Feature 5: Legal Document Explainer
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from ..models.schemas import DocumentUploadResponse, DocumentQueryRequest, DocumentQueryResponse
from ..services import session_manager, llm_service
import uuid
import os
from typing import List

router = APIRouter(prefix="/api/documents", tags=["Document Explainer"])


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Split text into overlapping chunks
    
    Args:
        text: Text to chunk
        chunk_size: Size of each chunk
        overlap: Overlap between chunks
        
    Returns:
        List of text chunks
    """
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap
    
    return chunks


def extract_text_from_file(file_content: bytes, filename: str) -> str:
    """
    Extract text from uploaded file
    
    Args:
        file_content: File bytes
        filename: Original filename
        
    Returns:
        Extracted text
    """
    file_ext = os.path.splitext(filename)[1].lower()
    
    if file_ext == '.txt':
        return file_content.decode('utf-8')
    
    elif file_ext == '.pdf':
        try:
            from pypdf import PdfReader
            from io import BytesIO
            
            pdf_file = BytesIO(file_content)
            reader = PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            raise Exception(f"Error extracting PDF: {str(e)}")
    
    elif file_ext in ['.docx', '.doc']:
        try:
            import docx2txt
            from io import BytesIO
            
            docx_file = BytesIO(file_content)
            text = docx2txt.process(docx_file)
            return text
        except Exception as e:
            raise Exception(f"Error extracting DOCX: {str(e)}")
    
    else:
        raise Exception(f"Unsupported file type: {file_ext}")


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(session_id: str, file: UploadFile = File(...)):
    """
    Feature 5: Upload and process legal document
    
    Flow:
    1. Upload document (PDF, DOCX, TXT)
    2. Extract text and chunk it
    3. Store chunks in session memory
    4. Return document ID for querying
    """
    try:
        # Validate file type
        allowed_extensions = ['.pdf', '.docx', '.doc', '.txt']
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Read file content
        file_content = await file.read()
        
        # Extract text
        text = extract_text_from_file(file_content, file.filename)
        
        if not text or len(text.strip()) < 10:
            raise HTTPException(status_code=400, detail="No text could be extracted from the document")
        
        # Chunk the text
        chunks = chunk_text(text)
        
        # Generate document ID
        document_id = str(uuid.uuid4())
        
        # Store in session
        session_manager.store_document(
            session_id=session_id,
            document_id=document_id,
            chunks=chunks,
            metadata={
                "filename": file.filename,
                "file_type": file_ext,
                "total_length": len(text),
                "num_chunks": len(chunks)
            }
        )
        
        return DocumentUploadResponse(
            session_id=session_id,
            document_id=document_id,
            filename=file.filename,
            chunks=len(chunks),
            message=f"Document processed successfully. {len(chunks)} chunks created."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")


@router.post("/query", response_model=DocumentQueryResponse)
async def query_document(request: DocumentQueryRequest):
    """
    Query uploaded document
    
    Flow:
    1. Retrieve document chunks from session
    2. Find relevant chunks (simple keyword matching or embeddings)
    3. Send relevant chunks + query + history to LLM
    4. Generate explanation
    5. Append to chat history
    """
    try:
        # Retrieve document
        document = session_manager.get_document(request.session_id, request.document_id)
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found in session")
        
        chunks = document.get('chunks', [])
        
        # Simple relevance: find chunks containing query keywords
        query_lower = request.query.lower()
        query_words = set(query_lower.split())
        
        # Score chunks by keyword overlap
        chunk_scores = []
        for idx, chunk in enumerate(chunks):
            chunk_lower = chunk.lower()
            score = sum(1 for word in query_words if word in chunk_lower)
            chunk_scores.append((idx, score, chunk))
        
        # Sort by score and take top 3 chunks
        chunk_scores.sort(key=lambda x: x[1], reverse=True)
        relevant_chunks = [chunk for _, _, chunk in chunk_scores[:3]]
        
        # Get chat history
        chat_history = session_manager.format_history_for_llm(request.session_id)
        
        # Generate explanation
        explanation = llm_service.explain_document(
            query=request.query,
            document_chunks=relevant_chunks,
            chat_history=chat_history
        )
        
        # Add to session history
        session_manager.add_message(request.session_id, "user", request.query)
        session_manager.add_message(request.session_id, "assistant", explanation)
        
        return DocumentQueryResponse(
            session_id=request.session_id,
            document_id=request.document_id,
            query=request.query,
            answer=explanation,
            relevant_chunks=[
                {"chunk_index": idx, "text": chunk[:200] + "..."}
                for idx, _, chunk in chunk_scores[:3]
            ]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying document: {str(e)}")


@router.get("/{session_id}/list")
async def list_documents(session_id: str):
    """List all uploaded documents for a session"""
    try:
        document_ids = session_manager.list_documents(session_id)
        documents = []
        
        for doc_id in document_ids:
            doc = session_manager.get_document(session_id, doc_id)
            if doc:
                documents.append({
                    "document_id": doc_id,
                    "filename": doc['metadata']['filename'],
                    "chunks": doc['metadata']['num_chunks'],
                    "uploaded_at": doc['uploaded_at'].isoformat()
                })
        
        return {"session_id": session_id, "documents": documents}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing documents: {str(e)}")
