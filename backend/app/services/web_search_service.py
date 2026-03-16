"""
Web search service used to augment legal chat responses when enabled.
Uses Tavily Search API for robust web retrieval.
"""

from typing import List, Dict, Any
import httpx
from ..core.config import get_settings

settings = get_settings()


class WebSearchService:
    """Robust web search provider for chat augmentation."""

    def __init__(self):
        self.base_url = "https://api.tavily.com/search"

    def search(self, query: str, max_results: int = 3) -> List[Dict[str, Any]]:
        if not query.strip() or not settings.TAVILY_API_KEY:
            return []

        try:
            response = httpx.post(
                self.base_url,
                json={
                    "api_key": settings.TAVILY_API_KEY,
                    "query": f"Indian law {query}",
                    "search_depth": "advanced",
                    "include_answer": True,
                    "include_raw_content": False,
                    "topic": "general",
                    "max_results": max_results,
                },
                timeout=12.0,
            )
            response.raise_for_status()
            payload = response.json()
        except Exception:
            return []

        results: List[Dict[str, Any]] = []

        answer = payload.get("answer")
        if answer:
            results.append(
                {
                    "title": "Tavily summary",
                    "text": answer,
                    "url": None,
                    "source": "Tavily",
                }
            )

        for item in payload.get("results", []):
            content = item.get("content") or ""
            title = item.get("title") or "Web result"
            url = item.get("url")

            if not content.strip():
                continue

            results.append(
                {
                    "title": title,
                    "text": content,
                    "url": url,
                    "source": "Tavily",
                }
            )

        deduped: List[Dict[str, Any]] = []
        seen = set()
        for item in results:
            key = (item.get("url"), item.get("text"))
            if key in seen:
                continue
            seen.add(key)
            deduped.append(item)
            if len(deduped) >= max_results:
                break

        return deduped


web_search_service = WebSearchService()
