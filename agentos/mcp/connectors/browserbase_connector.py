"""
Browserbase MCP Connector

Browser automation using Browserbase.
Provides tools for page navigation, screenshots, JavaScript execution, and form interaction.
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


class BrowserbaseConnector(MCPConnector):
    """
    MCP connector for Browserbase browser automation.

    Tools provided:
    - browser_navigate: Navigate to a URL
    - browser_screenshot: Take a screenshot of the current page
    - browser_click: Click an element on the page
    - browser_fill: Fill a form field
    - browser_evaluate: Execute JavaScript on the page
    - browser_get_content: Get the page content
    - browser_select: Select an option from a dropdown
    - browser_hover: Hover over an element

    Authentication:
    - API key via BROWSERBASE_API_KEY env var or config
    - Project ID via BROWSERBASE_PROJECT_ID env var or config
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(
            name="browserbase",
            auth_type=AuthType.API_KEY,
            config=config or {},
        )
        self._client = None
        self._session_id: Optional[str] = None
        self._ws_url: Optional[str] = None

    async def connect(self) -> ConnectorResult:
        """Initialize Browserbase client and create a session."""
        try:
            self.state = ConnectorState.CONNECTING

            api_key = self.config.get("api_key") or os.environ.get(
                "BROWSERBASE_API_KEY"
            )
            project_id = self.config.get("project_id") or os.environ.get(
                "BROWSERBASE_PROJECT_ID"
            )

            if not api_key:
                return ConnectorResult.fail(
                    "Browserbase API key not found. Set BROWSERBASE_API_KEY env var or pass api_key in config."
                )
            if not project_id:
                return ConnectorResult.fail(
                    "Browserbase project ID not found. Set BROWSERBASE_PROJECT_ID env var or pass project_id in config."
                )

            try:
                from browserbase import Browserbase

                self._client = Browserbase(api_key=api_key, project_id=project_id)
            except ImportError:
                return ConnectorResult.fail(
                    "browserbase package not installed. Run: pip install browserbase"
                )

            self.state = ConnectorState.CONNECTED
            return ConnectorResult.ok(
                output={"connector": "browserbase", "status": "connected"},
                metadata={"auth_type": "api_key", "project_id": project_id},
            )

        except Exception as e:
            self.state = ConnectorState.ERROR
            return ConnectorResult.fail(f"Failed to connect to Browserbase: {str(e)}")

    async def disconnect(self) -> ConnectorResult:
        """Disconnect and clean up browser session."""
        try:
            if self._session_id and self._client:
                try:
                    self._client.sessions.release(self._session_id)
                except Exception:
                    pass

            self._client = None
            self._session_id = None
            self._ws_url = None
            self._tools = None
            self._tools_loaded = False
            self.state = ConnectorState.DISCONNECTED
            return ConnectorResult.ok(
                output={"connector": "browserbase", "status": "disconnected"}
            )
        except Exception as e:
            return ConnectorResult.fail(
                f"Failed to disconnect from Browserbase: {str(e)}"
            )

    async def _get_session(self) -> ConnectorResult:
        """Get or create a browser session."""
        if not self._session_id:
            try:
                session = self._client.sessions.create()
                self._session_id = session.id
                self._ws_url = session.connect_url
            except Exception as e:
                return ConnectorResult.fail(
                    f"Failed to create browser session: {str(e)}"
                )
        return ConnectorResult.ok()

    async def get_tools(self) -> List[ToolDefinition]:
        """Return Browserbase tools."""
        return [
            ToolDefinition(
                name="browser_navigate",
                description="Navigate to a URL in the browser",
                parameters={
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "URL to navigate to",
                        },
                        "wait_until": {
                            "type": "string",
                            "description": "When to consider navigation complete (load, domcontentloaded, networkidle)",
                            "default": "networkidle",
                            "enum": ["load", "domcontentloaded", "networkidle"],
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "Navigation timeout in ms",
                            "default": 30000,
                        },
                    },
                    "required": ["url"],
                },
                handler=self._navigate,
            ),
            ToolDefinition(
                name="browser_screenshot",
                description="Take a screenshot of the current page",
                parameters={
                    "type": "object",
                    "properties": {
                        "full_page": {
                            "type": "boolean",
                            "description": "Capture full page scroll height",
                            "default": False,
                        },
                        "format": {
                            "type": "string",
                            "description": "Image format",
                            "default": "png",
                            "enum": ["png", "jpeg"],
                        },
                        "quality": {
                            "type": "integer",
                            "description": "Image quality (jpeg only, 0-100)",
                            "default": 80,
                        },
                    },
                    "required": [],
                },
                handler=self._screenshot,
            ),
            ToolDefinition(
                name="browser_click",
                description="Click an element on the page",
                parameters={
                    "type": "object",
                    "properties": {
                        "selector": {
                            "type": "string",
                            "description": "CSS selector for the element to click",
                        },
                        "button": {
                            "type": "string",
                            "description": "Mouse button (left, right, middle)",
                            "default": "left",
                        },
                        "click_count": {
                            "type": "integer",
                            "description": "Number of clicks",
                            "default": 1,
                        },
                    },
                    "required": ["selector"],
                },
                handler=self._click,
            ),
            ToolDefinition(
                name="browser_fill",
                description="Fill a form field",
                parameters={
                    "type": "object",
                    "properties": {
                        "selector": {
                            "type": "string",
                            "description": "CSS selector for the input field",
                        },
                        "value": {
                            "type": "string",
                            "description": "Value to fill",
                        },
                    },
                    "required": ["selector", "value"],
                },
                handler=self._fill,
            ),
            ToolDefinition(
                name="browser_evaluate",
                description="Execute JavaScript on the page",
                parameters={
                    "type": "object",
                    "properties": {
                        "script": {
                            "type": "string",
                            "description": "JavaScript code to execute",
                        },
                    },
                    "required": ["script"],
                },
                handler=self._evaluate,
            ),
            ToolDefinition(
                name="browser_get_content",
                description="Get the current page content",
                parameters={
                    "type": "object",
                    "properties": {
                        "format": {
                            "type": "string",
                            "description": "Content format (text, html, markdown)",
                            "default": "text",
                            "enum": ["text", "html", "markdown"],
                        },
                    },
                    "required": [],
                },
                handler=self._get_content,
            ),
            ToolDefinition(
                name="browser_select",
                description="Select an option from a dropdown",
                parameters={
                    "type": "object",
                    "properties": {
                        "selector": {
                            "type": "string",
                            "description": "CSS selector for the select element",
                        },
                        "value": {
                            "type": "string",
                            "description": "Value to select",
                        },
                    },
                    "required": ["selector", "value"],
                },
                handler=self._select,
            ),
            ToolDefinition(
                name="browser_hover",
                description="Hover over an element",
                parameters={
                    "type": "object",
                    "properties": {
                        "selector": {
                            "type": "string",
                            "description": "CSS selector for the element to hover over",
                        },
                    },
                    "required": ["selector"],
                },
                handler=self._hover,
            ),
        ]

    async def call_tool(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> ConnectorResult:
        """Execute a Browserbase tool."""
        check = self._ensure_connected()
        if not check.success:
            return check

        session_check = await self._get_session()
        if not session_check.success:
            return session_check

        tools = await self._load_tools_if_needed()
        tool = next((t for t in tools if t.name == tool_name), None)
        if not tool:
            return ConnectorResult.fail(
                f"Unknown Browserbase tool: {tool_name}. Available: {[t.name for t in tools]}"
            )

        try:
            result = await tool.handler(**arguments)
            return result
        except Exception as e:
            return ConnectorResult.fail(
                f"Browserbase tool '{tool_name}' failed: {str(e)}"
            )

    async def _navigate(
        self,
        url: str,
        wait_until: str = "networkidle",
        timeout: int = 30000,
    ) -> ConnectorResult:
        """Navigate to a URL."""
        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.connect_over_cdp(self._ws_url)
                context = (
                    browser.contexts[0]
                    if browser.contexts
                    else await browser.new_context()
                )
                page = context.pages[0] if context.pages else await context.new_page()
                response = await page.goto(url, wait_until=wait_until, timeout=timeout)
                title = await page.title()
                await browser.close()
            return ConnectorResult.ok(
                output={
                    "url": url,
                    "title": title,
                    "status": response.status if response else None,
                },
                metadata={"wait_until": wait_until},
            )
        except Exception as e:
            return ConnectorResult.fail(f"Browser navigation failed: {str(e)}")

    async def _screenshot(
        self,
        full_page: bool = False,
        format: str = "png",
        quality: int = 80,
    ) -> ConnectorResult:
        """Take a screenshot."""
        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.connect_over_cdp(self._ws_url)
                context = (
                    browser.contexts[0]
                    if browser.contexts
                    else await browser.new_context()
                )
                page = context.pages[0] if context.pages else await context.new_page()
                screenshot = await page.screenshot(
                    full_page=full_page,
                    type=format,
                    quality=quality if format == "jpeg" else None,
                )
                await browser.close()
            return ConnectorResult.ok(
                output={"screenshot_base64": screenshot.hex()},
                metadata={"format": format, "full_page": full_page},
            )
        except Exception as e:
            return ConnectorResult.fail(f"Browser screenshot failed: {str(e)}")

    async def _click(
        self,
        selector: str,
        button: str = "left",
        click_count: int = 1,
    ) -> ConnectorResult:
        """Click an element."""
        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.connect_over_cdp(self._ws_url)
                context = (
                    browser.contexts[0]
                    if browser.contexts
                    else await browser.new_context()
                )
                page = context.pages[0] if context.pages else await context.new_page()
                await page.click(selector, button=button, click_count=click_count)
                await browser.close()
            return ConnectorResult.ok(
                output={"clicked": selector},
                metadata={"selector": selector, "button": button},
            )
        except Exception as e:
            return ConnectorResult.fail(f"Browser click failed: {str(e)}")

    async def _fill(self, selector: str, value: str) -> ConnectorResult:
        """Fill a form field."""
        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.connect_over_cdp(self._ws_url)
                context = (
                    browser.contexts[0]
                    if browser.contexts
                    else await browser.new_context()
                )
                page = context.pages[0] if context.pages else await context.new_page()
                await page.fill(selector, value)
                await browser.close()
            return ConnectorResult.ok(
                output={"filled": selector, "value": value},
                metadata={"selector": selector},
            )
        except Exception as e:
            return ConnectorResult.fail(f"Browser fill failed: {str(e)}")

    async def _evaluate(self, script: str) -> ConnectorResult:
        """Execute JavaScript."""
        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.connect_over_cdp(self._ws_url)
                context = (
                    browser.contexts[0]
                    if browser.contexts
                    else await browser.new_context()
                )
                page = context.pages[0] if context.pages else await context.new_page()
                result = await page.evaluate(script)
                await browser.close()
            return ConnectorResult.ok(
                output={"result": result},
                metadata={"script_length": len(script)},
            )
        except Exception as e:
            return ConnectorResult.fail(f"Browser evaluate failed: {str(e)}")

    async def _get_content(self, format: str = "text") -> ConnectorResult:
        """Get page content."""
        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.connect_over_cdp(self._ws_url)
                context = (
                    browser.contexts[0]
                    if browser.contexts
                    else await browser.new_context()
                )
                page = context.pages[0] if context.pages else await context.new_page()
                if format == "html":
                    content = await page.content()
                elif format == "markdown":
                    content = await page.evaluate("() => document.body.innerText")
                else:
                    content = await page.inner_text("body")
                await browser.close()
            return ConnectorResult.ok(
                output={"content": content},
                metadata={"format": format, "length": len(content)},
            )
        except Exception as e:
            return ConnectorResult.fail(f"Browser get content failed: {str(e)}")

    async def _select(self, selector: str, value: str) -> ConnectorResult:
        """Select dropdown option."""
        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.connect_over_cdp(self._ws_url)
                context = (
                    browser.contexts[0]
                    if browser.contexts
                    else await browser.new_context()
                )
                page = context.pages[0] if context.pages else await context.new_page()
                await page.select_option(selector, value=value)
                await browser.close()
            return ConnectorResult.ok(
                output={"selected": selector, "value": value},
                metadata={"selector": selector},
            )
        except Exception as e:
            return ConnectorResult.fail(f"Browser select failed: {str(e)}")

    async def _hover(self, selector: str) -> ConnectorResult:
        """Hover over element."""
        try:
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.connect_over_cdp(self._ws_url)
                context = (
                    browser.contexts[0]
                    if browser.contexts
                    else await browser.new_context()
                )
                page = context.pages[0] if context.pages else await context.new_page()
                await page.hover(selector)
                await browser.close()
            return ConnectorResult.ok(
                output={"hovered": selector},
                metadata={"selector": selector},
            )
        except Exception as e:
            return ConnectorResult.fail(f"Browser hover failed: {str(e)}")
