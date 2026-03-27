from __future__ import annotations

from firecrawl import FirecrawlApp

from app.config import get_settings
from app.models import SourceSnippet


class WebCrawlerService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = FirecrawlApp(api_key=self.settings.firecrawl_api_key) if self.settings.firecrawl_api_key else None

    def scrape(self, url: str) -> SourceSnippet | None:
        if not self.client:
            return None

        result = self.client.scrape_url(
            url,
            formats=['markdown'],
            timeout=self.settings.firecrawl_timeout_seconds * 1000,
        )
        markdown = self._extract_markdown(result)
        if not markdown:
            return None

        title = self._extract_title(result) or url
        return SourceSnippet(
            source_type='web',
            title=title,
            excerpt=markdown[:1200],
        )

    def _extract_markdown(self, result: object) -> str:
        if isinstance(result, dict):
            if isinstance(result.get('markdown'), str):
                return result['markdown']
            data = result.get('data')
            if isinstance(data, dict) and isinstance(data.get('markdown'), str):
                return data['markdown']
        markdown = getattr(result, 'markdown', None)
        return markdown if isinstance(markdown, str) else ''

    def _extract_title(self, result: object) -> str | None:
        if isinstance(result, dict):
            if isinstance(result.get('title'), str):
                return result['title']
            metadata = result.get('metadata')
            if isinstance(metadata, dict) and isinstance(metadata.get('title'), str):
                return metadata['title']
            data = result.get('data')
            if isinstance(data, dict):
                if isinstance(data.get('title'), str):
                    return data['title']
                metadata = data.get('metadata')
                if isinstance(metadata, dict) and isinstance(metadata.get('title'), str):
                    return metadata['title']
        title = getattr(result, 'title', None)
        return title if isinstance(title, str) else None
