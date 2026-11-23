#!/usr/bin/env python3
"""Web Interaction Tools.

Tools for web scraping, API calls, and web automation.
"""

import logging
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class WebConfig(BaseModel):
    """Configuration for web tools."""

    timeout: int = Field(default=30, gt=0, description="Request timeout in seconds")
    user_agent: str = Field(
        default="Mozilla/5.0 (compatible; CloudCurio/1.0)", description="User agent string"
    )
    max_retries: int = Field(default=3, ge=0, description="Max retry attempts")
    verify_ssl: bool = Field(default=True, description="Verify SSL certificates")


class WebScraperTool:
    """Scrape content from web pages."""

    name: str = "web_scraper"
    description: str = "Extract content and data from web pages"

    def __init__(self, config: WebConfig | None = None) -> None:
        """Initialize web scraper tool."""
        self.config = config or WebConfig()

    def execute(self, url: str, selector: str | None = None, **kwargs: Any) -> dict[str, Any]:
        """Scrape web page.

        Args:
            url: URL to scrape
            selector: CSS selector for specific elements
            **kwargs: Additional parameters

        Returns:
            Scraped content and metadata
        """
        try:
            import requests
            from bs4 import BeautifulSoup

            headers = {"User-Agent": self.config.user_agent}
            response = requests.get(
                url, headers=headers, timeout=self.config.timeout, verify=self.config.verify_ssl
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            if selector:
                elements = soup.select(selector)
                content = [el.get_text(strip=True) for el in elements]
            else:
                content = soup.get_text(strip=True)

            return {
                "status": "success",
                "url": url,
                "content": content,
                "title": soup.title.string if soup.title else "",
                "status_code": response.status_code,
            }
        except Exception as e:
            logger.error(f"Web scraping failed: {e}")
            return {"status": "error", "error": str(e), "url": url, "content": None}


class APIClientTool:
    """Make HTTP API requests."""

    name: str = "api_client"
    description: str = "Make HTTP requests to REST APIs"

    def __init__(self, config: WebConfig | None = None) -> None:
        """Initialize API client tool."""
        self.config = config or WebConfig()

    def execute(
        self,
        url: str,
        method: str = "GET",
        headers: dict[str, str] | None = None,
        data: dict[str, Any] | None = None,
        params: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Make API request.

        Args:
            url: API endpoint URL
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            headers: Request headers
            data: Request body data
            params: Query parameters
            **kwargs: Additional parameters

        Returns:
            API response data and metadata
        """
        try:
            import requests

            req_headers = {"User-Agent": self.config.user_agent}
            if headers:
                req_headers.update(headers)

            response = requests.request(
                method=method.upper(),
                url=url,
                headers=req_headers,
                json=data,
                params=params,
                timeout=self.config.timeout,
                verify=self.config.verify_ssl,
            )
            response.raise_for_status()

            try:
                response_data = response.json()
            except ValueError:
                response_data = response.text

            return {
                "status": "success",
                "status_code": response.status_code,
                "data": response_data,
                "headers": dict(response.headers),
            }
        except Exception as e:
            logger.error(f"API request failed: {e}")
            return {"status": "error", "error": str(e), "url": url, "data": None}


class SearchEngineTool:
    """Search the web using search engines."""

    name: str = "search_engine"
    description: str = "Search the web and retrieve results"

    def __init__(self, config: WebConfig | None = None) -> None:
        """Initialize search engine tool."""
        self.config = config or WebConfig()

    def execute(self, query: str, num_results: int = 10, **kwargs: Any) -> dict[str, Any]:
        """Perform web search.

        Args:
            query: Search query
            num_results: Number of results to return
            **kwargs: Additional parameters

        Returns:
            Search results with URLs and snippets
        """
        try:
            # Use DuckDuckGo as it doesn't require API keys
            import requests

            url = "https://html.duckduckgo.com/html/"
            params = {"q": query}
            headers = {"User-Agent": self.config.user_agent}

            response = requests.post(url, data=params, headers=headers, timeout=self.config.timeout)
            response.raise_for_status()

            from bs4 import BeautifulSoup

            soup = BeautifulSoup(response.text, "html.parser")

            results = []
            for result in soup.select(".result")[:num_results]:
                title_elem = result.select_one(".result__title")
                snippet_elem = result.select_one(".result__snippet")
                url_elem = result.select_one(".result__url")

                if title_elem and url_elem:
                    results.append(
                        {
                            "title": title_elem.get_text(strip=True),
                            "url": url_elem.get("href", url_elem.get_text(strip=True)),
                            "snippet": snippet_elem.get_text(strip=True) if snippet_elem else "",
                        }
                    )

            return {"status": "success", "query": query, "results": results, "count": len(results)}
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {"status": "error", "error": str(e), "query": query, "results": []}


def web_scraper_tool(config: dict[str, Any] | None = None) -> WebScraperTool:
    """Factory function for web scraper tool."""
    cfg = WebConfig(**config) if config else WebConfig()
    return WebScraperTool(cfg)


def api_client_tool(config: dict[str, Any] | None = None) -> APIClientTool:
    """Factory function for API client tool."""
    cfg = WebConfig(**config) if config else WebConfig()
    return APIClientTool(cfg)


def search_engine_tool(config: dict[str, Any] | None = None) -> SearchEngineTool:
    """Factory function for search engine tool."""
    cfg = WebConfig(**config) if config else WebConfig()
    return SearchEngineTool(cfg)


__all__ = [
    "APIClientTool",
    "SearchEngineTool",
    "WebConfig",
    "WebScraperTool",
    "api_client_tool",
    "search_engine_tool",
    "web_scraper_tool",
]
