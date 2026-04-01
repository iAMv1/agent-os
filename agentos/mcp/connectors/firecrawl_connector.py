"""
Firecrawl MCP Connector

Web scraping and crawling using the Firecrawl API.
Provides tools for scraping, crawling, and mapping websites.
"""

import os
from typing import Any, Dict, List, Optional

from agentos.mcp.connectors import (
    MCPConnector,
    AuthType,
    ConnectorResult,
    ToolDefinition,
    ConnectorState,
)


class FirecrawlConnector(MCPConnector):
    """
    MCP connector for Firecrawl web scraping.

    Tools provided:
    - firecrawl_scrape: Scrape a single URL
    - firecrawl_crawl: Crawl multiple pages from a starting URL
    - firecrawl_map: Map all URLs on a website
    - firecrawl_extract: Extract structured data from pages
    - firecrawl_search: Search and scrape results

    Authentication:
    - API key via FIRECRAWL_API_KEY env var or config
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(
            name="firecrawl",
            auth_type=AuthType.API_KEY,
            config=config or {},
        )
        self._client = None

    async def connect(self) -> ConnectorResult:
        """Initialize Firecrawl client."""
        try:
            self.state = ConnectorState.CONNECTING

            api_key = self.config.get("api_key") or os.environ.get("FIRECRAWL_API_KEY")
            if not api_key:
                return ConnectorResult.fail(
                    "Firecrawl API key not found. Set FIRECRAWL_API_KEY env var or pass api_key in config."
                )

            try:
                from firecrawl import FirecrawlApp

                self._client = FirecrawlApp(api_key=api_key)
            except ImportError:
                return ConnectorResult.fail(
                    "firecrawl-py package not installed. Run: pip install firecrawl-py"
                )

            self.state = ConnectorState.CONNECTED
            return ConnectorResult.ok(
                output={"connector": "firecrawl", "status": "connected"},
                metadata={"auth_type": "api_key"},
            )

        except Exception as e:
            self.state = ConnectorState.ERROR
            return ConnectorResult.fail(f"Failed to connect to Firecrawl: {str(e)}")

    async def disconnect(self) -> ConnectorResult:
        """Disconnect Firecrawl client."""
        try:
            self._client = None
            self._tools = None
            self._tools_loaded = False
            self.state = ConnectorState.DISCONNECTED
            return ConnectorResult.ok(
                output={"connector": "firecrawl", "status": "disconnected"}
            )
        except Exception as e:
            return ConnectorResult.fail(
                f"Failed to disconnect from Firecrawl: {str(e)}"
            )

    async def get_tools(self) -> List[ToolDefinition]:
        """Return Firecrawl tools."""
        return [
            ToolDefinition(
                name="firecrawl_scrape",
                description="Scrape content from a single URL",
                parameters={
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "URL to scrape",
                        },
                        "formats": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Output formats (markdown, html, rawHtml, links, screenshot)",
                            "default": ["markdown"],
                        },
                        "only_main_content": {
                            "type": "boolean",
                            "description": "Only return main content, exclude nav/footers",
                            "default": True,
                        },
                        "include_tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "HTML tags to include",
                        },
                        "exclude_tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "HTML tags to exclude",
                        },
                        "wait_for": {
                            "type": "integer",
                            "description": "Wait time in ms for JS rendering",
                            "default": 0,
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "Request timeout in ms",
                            "default": 30000,
                        },
                    },
                    "required": ["url"],
                },
                handler=self._scrape,
            ),
            ToolDefinition(
                name="firecrawl_crawl",
                description="Crawl multiple pages starting from a URL",
                parameters={
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "Starting URL for crawl",
                        },
                        "max_depth": {
                            "type": "integer",
                            "description": "Maximum crawl depth",
                            "default": 2,
                        },
                        "max_pages": {
                            "type": "integer",
                            "description": "Maximum pages to crawl",
                            "default": 10,
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Max pages to return",
                            "default": 10,
                        },
                        "allow_external_links": {
                            "type": "boolean",
                            "description": "Allow crawling external domains",
                            "default": False,
                        },
                        "include_paths": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "URL path patterns to include",
                        },
                        "exclude_paths": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "URL path patterns to exclude",
                        },
                    },
                    "required": ["url"],
                },
                handler=self._crawl,
            ),
            ToolDefinition(
                name="firecrawl_map",
                description="Map all URLs on a website",
                parameters={
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "URL to map",
                        },
                        "search": {
                            "type": "string",
                            "description": "Filter URLs by search term",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Max URLs to return",
                            "default": 5000,
                        },
                        "ignore_sitemap": {
                            "type": "boolean",
                            "description": "Ignore sitemap.xml",
                            "default": False,
                        },
                    },
                    "required": ["url"],
                },
                handler=self._map,
            ),
            ToolDefinition(
                name="firecrawl_extract",
                description="Extract structured data from web pages",
                parameters={
                    "type": "object",
                    "properties": {
                        "urls": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "URLs to extract data from",
                        },
                        "prompt": {
                            "type": "string",
                            "description": "Natural language prompt for extraction",
                        },
                        "schema": {
                            "type": "object",
                            "description": "JSON schema for structured extraction",
                        },
                    },
                    "required": ["urls", "prompt"],
                },
                handler=self._extract,
            ),
            ToolDefinition(
                name="firecrawl_search",
                description="Search the web and scrape results",
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of results",
                            "default": 5,
                        },
                        "scrape_options": {
                            "type": "object",
                            "description": "Options for scraping search results",
                        },
                    },
                    "required": ["query"],
                },
                handler=self._search,
            ),
        ]

    async def call_tool(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> ConnectorResult:
        """Execute a Firecrawl tool."""
        check = self._ensure_connected()
        if not check.success:
            return check

        tools = await self._load_tools_if_needed()
        tool = next((t for t in tools if t.name == tool_name), None)
        if not tool:
            return ConnectorResult.fail(
                f"Unknown Firecrawl tool: {tool_name}. Available: {[t.name for t in tools]}"
            )

        try:
            result = await tool.handler(**arguments)
            return result
        except Exception as e:
            return ConnectorResult.fail(
                f"Firecrawl tool '{tool_name}' failed: {str(e)}"
            )

    async def _scrape(
        self,
        url: str,
        formats: Optional[List[str]] = None,
        only_main_content: bool = True,
        include_tags: Optional[List[str]] = None,
        exclude_tags: Optional[List[str]] = None,
        wait_for: int = 0,
        timeout: int = 30000,
    ) -> ConnectorResult:
        """Scrape content from a URL."""
        try:
            params = {
                "formats": formats or ["markdown"],
                "onlyMainContent": only_main_content,
                "waitFor": wait_for,
                "timeout": timeout,
            }
            if include_tags:
                params["includeTags"] = include_tags
            if exclude_tags:
                params["excludeTags"] = exclude_tags

            result = self._client.scrape_url(url, params)
            return ConnectorResult.ok(
                output=result,
                metadata={"url": url, "formats": formats or ["markdown"]},
            )
        except Exception as e:
            return ConnectorResult.fail(f"Firecrawl scrape failed: {str(e)}")

    async def _crawl(
        self,
        url: str,
        max_depth: int = 2,
        max_pages: int = 10,
        limit: int = 10,
        allow_external_links: bool = False,
        include_paths: Optional[List[str]] = None,
        exclude_paths: Optional[List[str]] = None,
    ) -> ConnectorResult:
        """Crawl multiple pages from a starting URL."""
        try:
            params = {
                "maxDepth": max_depth,
                "maxPages": max_pages,
                "limit": limit,
                "allowExternalLinks": allow_external_links,
                "returnOnlyUrls": False,
            }
            if include_paths:
                params["includePaths"] = include_paths
            if exclude_paths:
                params["excludePaths"] = exclude_paths

            result = self._client.crawl_url(url, params)
            return ConnectorResult.ok(
                output=result,
                metadata={"url": url, "max_pages": max_pages},
            )
        except Exception as e:
            return ConnectorResult.fail(f"Firecrawl crawl failed: {str(e)}")

    async def _map(
        self,
        url: str,
        search: Optional[str] = None,
        limit: int = 5000,
        ignore_sitemap: bool = False,
    ) -> ConnectorResult:
        """Map all URLs on a website."""
        try:
            params = {
                "limit": limit,
                "ignoreSitemap": ignore_sitemap,
            }
            if search:
                params["search"] = search

            result = self._client.map_url(url, params)
            urls = result.get("urls", []) if isinstance(result, dict) else result
            return ConnectorResult.ok(
                output={"urls": urls, "count": len(urls)},
                metadata={"url": url, "limit": limit},
            )
        except Exception as e:
            return ConnectorResult.fail(f"Firecrawl map failed: {str(e)}")

    async def _extract(
        self,
        urls: List[str],
        prompt: str,
        schema: Optional[Dict[str, Any]] = None,
    ) -> ConnectorResult:
        """Extract structured data from pages."""
        try:
            params = {
                "prompt": prompt,
            }
            if schema:
                params["schema"] = schema

            result = self._client.extract(urls, params)
            return ConnectorResult.ok(
                output=result,
                metadata={"urls": urls, "prompt": prompt},
            )
        except Exception as e:
            return ConnectorResult.fail(f"Firecrawl extract failed: {str(e)}")

    async def _search(
        self,
        query: str,
        limit: int = 5,
        scrape_options: Optional[Dict[str, Any]] = None,
    ) -> ConnectorResult:
        """Search and scrape results."""
        try:
            params = {
                "limit": limit,
            }
            if scrape_options:
                params["scrapeOptions"] = scrape_options

            result = self._client.search(query, params)
            return ConnectorResult.ok(
                output=result,
                metadata={"query": query, "limit": limit},
            )
        except Exception as e:
            return ConnectorResult.fail(f"Firecrawl search failed: {str(e)}")
