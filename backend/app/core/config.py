"""
Configuration management for Sarthak
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Sarthak"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Groq LLM (FREE)
    GROQ_API_KEY: str
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    
    # Embeddings (FREE - Local sentence-transformers)
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    
    # Pinecone (FREE TIER)
    PINECONE_API_KEY: str
    PINECONE_ENVIRONMENT: str = "us-east-1"
    PINECONE_INDEX_NAME: str = "kanoongpt-laws"

    # Web Search (Tavily)
    TAVILY_API_KEY: Optional[str] = None
    WEB_SEARCH_MAX_RESULTS: int = 5
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    # Chat History
    MAX_HISTORY_LENGTH: int = 10
    SESSION_TIMEOUT: int = 3600
    
    # Retrieval
    TOP_K_RESULTS: int = 10
    SIMILARITY_THRESHOLD: float = 0.65
    
    # Rate Limiting
    MAX_REQUESTS_PER_MINUTE: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
