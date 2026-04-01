"""
MCP Connector Registry

Central registry for discovering, managing, and lifecycle-controlling MCP connectors.
Supports lazy initialization, health monitoring, and tool aggregation across connectors.
"""

import os
import json
from typing import Any, Dict, List, Optional, Type

from agentos.mcp.connectors import (
    MCPConnector,
    ConnectorResult,
    ConnectorState,
    ToolDefinition,
)


class ConnectorRegistry:
    """
    Registry for MCP connectors with discovery and lifecycle management.

    Features:
    - Register/unregister connectors
    - Lazy initialization (connectors only connect when used)
    - Health monitoring
    - Tool aggregation across all connectors
    - Configuration from environment or config files
    - Bulk connect/disconnect
    """

    def __init__(self, config_path: Optional[str] = None):
        self._connectors: Dict[str, MCPConnector] = {}
        self._connector_configs: Dict[str, Dict[str, Any]] = {}
        self._config_path = config_path
        self._load_config()

    def _load_config(self) -> None:
        """Load connector configurations from file."""
        if self._config_path and os.path.exists(self._config_path):
            try:
                with open(self._config_path, "r") as f:
                    config = json.load(f)
                self._connector_configs = config.get("connectors", {})
            except (json.JSONDecodeError, IOError):
                self._connector_configs = {}

    def save_config(self) -> None:
        """Save current connector configurations to file."""
        if self._config_path:
            config = {"connectors": self._connector_configs}
            os.makedirs(os.path.dirname(self._config_path), exist_ok=True)
            with open(self._config_path, "w") as f:
                json.dump(config, f, indent=2)

    def register(
        self, connector: MCPConnector, config: Optional[Dict[str, Any]] = None
    ) -> None:
        """Register a connector instance."""
        self._connectors[connector.name] = connector
        if config:
            self._connector_configs[connector.name] = config

    def register_class(
        self,
        connector_class: Type[MCPConnector],
        name: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> MCPConnector:
        """Register a connector class (lazy instantiation)."""
        merged_config = {
            **(
                self._connector_configs.get(
                    name or connector_class.__name__.lower(), {}
                )
            ),
            **(config or {}),
        }
        connector = connector_class(config=merged_config)
        self.register(connector, merged_config)
        return connector

    def unregister(self, name: str) -> bool:
        """Unregister a connector."""
        if name in self._connectors:
            connector = self._connectors.pop(name)
            if connector.is_connected:
                import asyncio

                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        asyncio.ensure_future(connector.disconnect())
                    else:
                        loop.run_until_complete(connector.disconnect())
                except Exception:
                    pass
            self._connector_configs.pop(name, None)
            return True
        return False

    def get(self, name: str) -> Optional[MCPConnector]:
        """Get a connector by name."""
        return self._connectors.get(name)

    def list_connectors(self) -> List[str]:
        """List all registered connector names."""
        return list(self._connectors.keys())

    async def connect(self, name: str) -> ConnectorResult:
        """Connect a specific connector."""
        connector = self._connectors.get(name)
        if not connector:
            return ConnectorResult.fail(f"Connector '{name}' not found in registry.")
        return await connector.connect()

    async def disconnect(self, name: str) -> ConnectorResult:
        """Disconnect a specific connector."""
        connector = self._connectors.get(name)
        if not connector:
            return ConnectorResult.fail(f"Connector '{name}' not found in registry.")
        return await connector.disconnect()

    async def connect_all(self) -> Dict[str, ConnectorResult]:
        """Connect all registered connectors."""
        results = {}
        for name, connector in self._connectors.items():
            results[name] = await connector.connect()
        return results

    async def disconnect_all(self) -> Dict[str, ConnectorResult]:
        """Disconnect all registered connectors."""
        results = {}
        for name, connector in self._connectors.items():
            results[name] = await connector.disconnect()
        return results

    async def get_all_tools(self) -> List[Dict[str, Any]]:
        """Get all tools from all connected connectors."""
        all_tools = []
        for name, connector in self._connectors.items():
            if connector.is_connected:
                tools = await connector._load_tools_if_needed()
                for tool in tools:
                    tool_dict = tool.to_dict()
                    tool_dict["connector"] = name
                    all_tools.append(tool_dict)
        return all_tools

    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        connector_name: Optional[str] = None,
    ) -> ConnectorResult:
        """
        Call a tool by name.

        If connector_name is specified, only try that connector.
        Otherwise, search all connected connectors for the tool.
        """
        if connector_name:
            connector = self._connectors.get(connector_name)
            if not connector:
                return ConnectorResult.fail(f"Connector '{connector_name}' not found.")
            return await connector.call_tool(tool_name, arguments)

        for name, connector in self._connectors.items():
            if not connector.is_connected:
                continue
            tools = await connector._load_tools_if_needed()
            if any(t.name == tool_name for t in tools):
                return await connector.call_tool(tool_name, arguments)

        return ConnectorResult.fail(
            f"Tool '{tool_name}' not found in any connected connector."
        )

    async def health_check(self) -> Dict[str, Any]:
        """Check health of all connectors."""
        health = {}
        for name, connector in self._connectors.items():
            info = connector.get_info()
            health[name] = {
                "state": info["state"],
                "tools_loaded": info["tools_loaded"],
                "tool_count": info["tool_count"],
                "healthy": connector.is_connected,
            }
        return health

    def get_status(self) -> Dict[str, Any]:
        """Get registry status summary."""
        connected = sum(1 for c in self._connectors.values() if c.is_connected)
        total = len(self._connectors)
        return {
            "total_connectors": total,
            "connected": connected,
            "disconnected": total - connected,
            "connectors": {
                name: connector.get_info()
                for name, connector in self._connectors.items()
            },
        }

    @classmethod
    def from_env(cls, config_path: Optional[str] = None) -> "ConnectorRegistry":
        """Create registry with connectors discovered from environment variables."""
        registry = cls(config_path=config_path)

        env_connectors = {
            "exa": "EXA_API_KEY",
            "firecrawl": "FIRECRAWL_API_KEY",
            "browserbase": "BROWSERBASE_API_KEY",
            "github": "GITHUB_TOKEN",
            "database": "DATABASE_URL",
        }

        for name, env_var in env_connectors.items():
            if os.environ.get(env_var):
                connector_class = _get_connector_class(name)
                if connector_class:
                    registry.register_class(connector_class, name=name)

        return registry


def _get_connector_class(name: str) -> Optional[Type[MCPConnector]]:
    """Get connector class by name."""
    mapping = {
        "exa": "agentos.mcp.connectors.exa_connector.ExaConnector",
        "firecrawl": "agentos.mcp.connectors.firecrawl_connector.FirecrawlConnector",
        "browserbase": "agentos.mcp.connectors.browserbase_connector.BrowserbaseConnector",
        "github": "agentos.mcp.connectors.github_connector.GitHubConnector",
        "database": "agentos.mcp.connectors.database_connector.DatabaseConnector",
    }

    import importlib

    path = mapping.get(name)
    if not path:
        return None

    module_path, class_name = path.rsplit(".", 1)
    try:
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    except (ImportError, AttributeError):
        return None


def create_default_registry(config_path: Optional[str] = None) -> ConnectorRegistry:
    """Create a registry with all available connectors."""
    registry = ConnectorRegistry(config_path=config_path)

    connector_classes = [
        ("exa", "agentos.mcp.connectors.exa_connector.ExaConnector"),
        ("firecrawl", "agentos.mcp.connectors.firecrawl_connector.FirecrawlConnector"),
        (
            "browserbase",
            "agentos.mcp.connectors.browserbase_connector.BrowserbaseConnector",
        ),
        ("github", "agentos.mcp.connectors.github_connector.GitHubConnector"),
        ("database", "agentos.mcp.connectors.database_connector.DatabaseConnector"),
    ]

    for name, path in connector_classes:
        connector_class = _get_connector_class(name)
        if connector_class:
            registry.register_class(connector_class, name=name)

    return registry
