"""Routers module initialization"""
from .chat import router as chat_router
from .search import router as search_router
from .cases import router as cases_router
from .documents import router as documents_router

__all__ = ["chat_router", "search_router", "cases_router", "documents_router"]
