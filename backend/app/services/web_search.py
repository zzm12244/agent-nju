from __future__ import annotations

from app.config import get_settings
from app.models import SourceSnippet

try:
    from langchain_community.tools.tavily_search import TavilySearchResults
except ImportError:
    TavilySearchResults = None


class WebSearchService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def search(self, query: str, limit: int = 3) -> list[SourceSnippet]:
        if not self.settings.tavily_api_key or TavilySearchResults is None:
            return []

        tool = TavilySearchResults(
            max_results=limit,
            tavily_api_key=self.settings.tavily_api_key,
        )
        results = tool.invoke({'query': query})
        snippets: list[SourceSnippet] = []
        for item in results:
            snippets.append(
                SourceSnippet(
                    source_type='web',
                    title=item.get('title', item.get('url', 'web result')),
                    excerpt=item.get('content', '')[:400],
                )
            )
        return snippets
