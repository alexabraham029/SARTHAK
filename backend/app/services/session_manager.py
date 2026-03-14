"""
Session Manager for multi-turn conversations
Maintains chat history for each session
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from cachetools import TTLCache
from ..models.schemas import ChatMessage


class SessionManager:
    """Manages user sessions and chat history"""
    
    def __init__(self, max_history: int = 10, session_timeout: int = 3600):
        """
        Initialize session manager
        
        Args:
            max_history: Maximum number of messages to keep per session
            session_timeout: Session timeout in seconds
        """
        self.max_history = max_history
        self.session_timeout = session_timeout
        # Use TTLCache for automatic session expiry
        self.sessions: TTLCache = TTLCache(maxsize=1000, ttl=session_timeout)
        self.document_sessions: TTLCache = TTLCache(maxsize=1000, ttl=session_timeout)
    
    def get_history(self, session_id: str) -> List[ChatMessage]:
        """Get chat history for a session"""
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        return self.sessions[session_id]
    
    def add_message(self, session_id: str, role: str, content: str):
        """Add a message to session history"""
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        
        message = ChatMessage(
            role=role,
            content=content,
            timestamp=datetime.now()
        )
        
        self.sessions[session_id].append(message)
        
        # Maintain max history length
        if len(self.sessions[session_id]) > self.max_history * 2:  # *2 for user+assistant pairs
            self.sessions[session_id] = self.sessions[session_id][-self.max_history * 2:]
    
    def clear_session(self, session_id: str):
        """Clear a specific session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def get_session_count(self) -> int:
        """Get number of active sessions"""
        return len(self.sessions)
    
    def format_history_for_llm(self, session_id: str) -> List[Dict[str, str]]:
        """Format chat history for LLM consumption"""
        history = self.get_history(session_id)
        return [{"role": msg.role, "content": msg.content} for msg in history]
    
    # Document session management
    def store_document(self, session_id: str, document_id: str, chunks: List[str], metadata: dict):
        """Store document chunks for a session"""
        if session_id not in self.document_sessions:
            self.document_sessions[session_id] = {}
        
        self.document_sessions[session_id][document_id] = {
            "chunks": chunks,
            "metadata": metadata,
            "uploaded_at": datetime.now()
        }
    
    def get_document(self, session_id: str, document_id: str) -> Optional[dict]:
        """Retrieve document data for a session"""
        if session_id in self.document_sessions:
            return self.document_sessions[session_id].get(document_id)
        return None
    
    def list_documents(self, session_id: str) -> List[str]:
        """List all document IDs for a session"""
        if session_id in self.document_sessions:
            return list(self.document_sessions[session_id].keys())
        return []


# Global session manager instance
session_manager = SessionManager()
