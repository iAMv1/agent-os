"""
Exa MCP Connector

Web search and content extraction using the Exa AI API.
Provides tools for semantic search, URL extraction, and answer generation.
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


class ExaConnector(MCPConnector):
    """
    MCP connector for Exa AI web search and content extraction.

    Tools provided:
    - exa_search: Semantic web search
    - exa_extract: Extract content from URLs
    - exa_find_similar: Find similar pages to a URL
    - exa_answer: Get AI-generated answers with citations
    - exa_research: Deep research on a topic

    Authentication:
    - API key via EXA_API_KEY env var or config
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(
            name="exa",
            auth_type=AuthType.API_KEY,
            config=config or {},
        )
        self._client = None

    async def connect(self) -> ConnectorResult:
        """Initialize Exa client with authentication."""
        try:
            self.state = ConnectorState.CONNECTING

            api_key = self.config.get("api_key") or os.environ.get("EXA_API_KEY")
            if not api_key:
                return ConnectorResult.fail(
                    "Exa API key not found. Set EXA_API_KEY env var or pass api_key in config."
                )

            try:
                from exa_py import Exa

                self._client = Exa(api_key=api_key)
            except ImportError:
                return ConnectorResult.fail(
                    "exa_py package not installed. Run: pip install exa-py"
                )

            self.state = ConnectorState.CONNECTED
            return ConnectorResult.ok(
                output={"connector": "exa", "status": "connected"},
                metadata={"auth_type": "api_key"},
            )

        except Exception as e:
            self.state = ConnectorState.ERROR
            return ConnectorResult.fail(f"Failed to connect to Exa: {str(e)}")

    async def disconnect(self) -> ConnectorResult:
        """Disconnect Exa client."""
        try:
            self._client = None
            self._tools = None
            self._tools_loaded = False
            self.state = ConnectorState.DISCONNECTED
            return ConnectorResult.ok(
                output={"connector": "exa", "status": "disconnected"}
            )
        except Exception as e:
            return ConnectorResult.fail(f"Failed to disconnect from Exa: {str(e)}")

    async def get_tools(self) -> List[ToolDefinition]:
        """Return Exa tools."""
        return [
            ToolDefinition(
                name="exa_search",
                description="Perform semantic web search with Exa AI",
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query",
                        },
                        "num_results": {
                            "type": "integer",
                            "description": "Number of results (default: 10)",
                            "default": 10,
                        },
                        "include_domains": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Domains to include in results",
                        },
                        "exclude_domains": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Domains to exclude from results",
                        },
                        "start_published_date": {
                            "type": "string",
                            "description": "Start date for results (YYYY-MM-DD)",
                        },
                        "end_published_date": {
                            "type": "string",
                            "description": "End date for results (YYYY-MM-DD)",
                        },
                        "use_autoprompt": {
                            "type": "boolean",
                            "description": "Use autoprompt for better results",
                            "default": True,
                        },
                    },
                    "required": ["query"],
                },
                handler=self._search,
            ),
            ToolDefinition(
                name="exa_extract",
                description="Extract content from specific URLs",
                parameters={
                    "type": "object",
                    "properties": {
                        "urls": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of URLs to extract content from",
                        },
                        "text": {
                            "type": "boolean",
                            "description": "Extract text content",
                            "default": True,
                        },
                        "highlights": {
                            "type": "boolean",
                            "description": "Extract highlights",
                            "default": False,
                        },
                        "summary": {
                            "type": "boolean",
                            "description": "Generate summary of content",
                            "default": False,
                        },
                    },
                    "required": ["urls"],
                },
                handler=self._extract,
            ),
            ToolDefinition(
                name="exa_find_similar",
                description="Find pages similar to a given URL",
                parameters={
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "URL to find similar pages for",
                        },
                        "num_results": {
                            "type": "integer",
                            "description": "Number of results (default: 10)",
                            "default": 10,
                        },
                    },
                    "required": ["url"],
                },
                handler=self._find_similar,
            ),
            ToolDefinition(
                name="exa_answer",
                description="Get AI-generated answer with citations from web sources",
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Question or topic to get answer for",
                        },
                        "text": {
                            "type": "boolean",
                            "description": "Include full text of sources",
                            "default": False,
                        },
                    },
                    "required": ["query"],
                },
                handler=self._answer,
            ),
            ToolDefinition(
                name="exa_research",
                description="Deep research on a topic with comprehensive results",
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Research topic or question",
                        },
                        "num_results": {
                            "type": "integer",
                            "description": "Number of sources to analyze (default: 20)",
                            "default": 20,
                        },
                    },
                    "required": ["query"],
                },
                handler=self._research,
            ),
        ]

    async def call_tool(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> ConnectorResult:
        """Execute an Exa tool."""
        check = self._ensure_connected()
        if not check.success:
            return check

        tools = await self._load_tools_if_needed()
        tool = next((t for t in tools if t.name == tool_name), None)
        if not tool:
            return ConnectorResult.fail(
                f"Unknown Exa tool: {tool_name}. Available: {[t.name for t in tools]}"
            )

        try:
            result = await tool.handler(**arguments)
            return result
        except Exception as e:
            return ConnectorResult.fail(f"Exa tool '{tool_name}' failed: {str(e)}")

    async def _search(
        self,
        query: str,
        num_results: int = 10,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        start_published_date: Optional[str] = None,
        end_published_date: Optional[str] = None,
        use_autoprompt: bool = True,
    ) -> ConnectorResult:
        """Perform semantic web search."""
        try:
            result = self._client.search_and_contents(
                query,
                num_results=num_results,
                include_domains=include_domains,
                exclude_domains=exclude_domains,
                start_published_date=start_published_date,
                end_published_date=end_published_date,
                use_autoprompt=use_autoprompt,
            )
            results = []
            for r in result.results:
                results.append(
                    {
                        "title": getattr(r, "title", ""),
                        "url": getattr(r, "url", ""),
                        "text": getattr(r, "text", ""),
                        "published_date": getattr(r, "published_date", ""),
                        "author": getattr(r, "author", ""),
                    }
                )
            return ConnectorResult.ok(
                output={"results": results, "count": len(results)},
                metadata={"query": query, "num_results": num_results},
            )
        except Exception as e:
            return ConnectorResult.fail(f"Exa search failed: {str(e)}")

    async def _extract(
        self,
        urls: List[str],
        text: bool = True,
        highlights: bool = False,
        summary: bool = False,
    ) -> ConnectorResult:
        """Extract content from URLs."""
        try:
            result = self._client.get_contents(
                urls,
                text=text,
                highlights=highlights,
                summary=summary,
            )
            extracted = []
            for r in result.results:
                item = {"url": getattr(r, "url", "")}
                if text:
                    item["text"] = getattr(r, "text", "")
                if highlights:
                    item["highlights"] = getattr(r, "highlights", [])
                if summary:
                    item["summary"] = getattr(r, "summary", "")
                extracted.append(item)
            return ConnectorResult.ok(
                output={"extracted": extracted, "count": len(extracted)},
                metadata={"urls": urls},
            )
        except Exception as e:
            return ConnectorResult.fail(f"Exa extract failed: {str(e)}")

    async def _find_similar(self, url: str, num_results: int = 10) -> ConnectorResult:
        """Find similar pages to a URL."""
        try:
            result = self._client.find_similar(
                url,
                num_results=num_results,
            )
            results = []
            for r in result.results:
                results.append(
                    {
                        "title": getattr(r, "title", ""),
                        "url": getattr(r, "url", ""),
                        "text": getattr(r, "text", ""),
                        "score": getattr(r, "score", 0),
                    }
                )
            return ConnectorResult.ok(
                output={"results": results, "count": len(results)},
                metadata={"source_url": url, "num_results": num_results},
            )
        except Exception as e:
            return ConnectorResult.fail(f"Exa find similar failed: {str(e)}")

    async def _answer(self, query: str, text: bool = False) -> ConnectorResult:
        """Get AI-generated answer with citations."""
        try:
            result = self._client.answer(
                query,
                text=text,
            )
            output = {
                "answer": getattr(result, "answer", ""),
            }
            if hasattr(result, "citations") and result.citations:
                output["citations"] = [
                    {"url": getattr(c, "url", ""), "title": getattr(c, "title", "")}
                    for c in result.citations
                ]
            return ConnectorResult.ok(
                output=output,
                metadata={"query": query},
            )
        except Exception as e:
            return ConnectorResult.fail(f"Exa answer failed: {str(e)}")

    async def _research(self, query: str, num_results: int = 20) -> ConnectorResult:
        """Deep research on a topic."""
        try:
            result = self._client.search_and_contents(
                query,
                num_results=num_results,
                text=True,
                summary=True,
            )
            sources = []
            for r in result.results:
                sources.append(
                    {
                        "title": getattr(r, "title", ""),
                        "url": getattr(r, "url", ""),
                        "text": getattr(r, "text", ""),
                        "summary": getattr(r, "summary", ""),
                    }
                )
            return ConnectorResult.ok(
                output={"sources": sources, "count": len(sources)},
                metadata={"query": query, "num_results": num_results},
            )
        except Exception as e:
            return ConnectorResult.fail(f"Exa research failed: {str(e)}")
