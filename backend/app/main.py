"""
Sarthak - FastAPI Main Application
Indian Legal AI Assistant with RAG
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .core.config import get_settings
from .routers import chat_router, search_router, cases_router, documents_router
from .services import pinecone_service
from .models.schemas import HealthResponse
from datetime import datetime

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("[*] Starting Sarthak...")
    print(f"[*] Initializing Pinecone index: {settings.PINECONE_INDEX_NAME}")
    
    try:
        pinecone_service.initialize_index()
        print("[OK] Pinecone initialized successfully")
    except Exception as e:
        print(f"[WARNING] Could not initialize Pinecone: {str(e)}")
        print("   The service will start, but vector search features may not work.")
    
    yield
    
    # Shutdown
    print("[*] Shutting down Sarthak...")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    Sarthak - AI-Powered Indian Legal Assistant
    
    Features:
    - 🗨️ **Legal Chat**: Multi-turn conversational Q&A about Indian laws
    - 🔍 **Semantic Search**: Find relevant law sections using natural language
    - 📚 **Case Summarizer**: Get structured summaries of landmark cases
    - ⚖️ **Case Similarity**: Find similar cases based on your situation
    - 📄 **Document Explainer**: Upload and analyze legal documents
    
    Powered by:
    - OpenAI GPT-4 for natural language understanding
    - Pinecone for semantic vector search
    - FastAPI for high-performance API
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router)
app.include_router(search_router)
app.include_router(cases_router)
app.include_router(documents_router)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Sarthak API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "features": [
            "Legal Chat",
            "Semantic Search",
            "Case Summarizer",
            "Case Similarity Search",
            "Document Explainer"
        ]
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        timestamp=datetime.now()
    )


@app.get("/stats", tags=["Stats"])
async def get_stats():
    """Get system statistics"""
    try:
        from .services import session_manager
        
        index_stats = {}
        try:
            index_stats = pinecone_service.get_index_stats()
        except:
            index_stats = {"error": "Could not retrieve index stats"}
        
        return {
            "active_sessions": session_manager.get_session_count(),
            "pinecone_stats": index_stats,
            "version": settings.APP_VERSION
        }
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
