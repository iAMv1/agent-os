"""
Layer 2: MCP - Connect MCP servers for domain capabilities.

When skills don't cover the task, check if any MCP servers
can provide the required domain capabilities.
"""

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import asyncio


class MCPServerState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    FAILED = "failed"


@dataclass
class MCPToolInfo:
    """Information about an MCP tool."""

    name: str
    description: str
    server_name: str
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MCPServerInfo:
    """Information about an MCP server."""

    name: str
    state: MCPServerState
    tools: List[MCPToolInfo] = field(default_factory=list)
    error: Optional[str] = None


@dataclass
class MCPLayerResult:
    """Result from MCP layer processing."""

    success: bool
    connected_servers: List[str] = field(default_factory=list)
    available_tools: List[MCPToolInfo] = field(default_factory=list)
    recommended_server: Optional[str] = None
    error: Optional[str] = None


class MCPLayer:
    """
    Layer 2: Connect MCP servers for domain capabilities.

    Discovers and connects to MCP servers that can provide tools
    for handling the unknown task.
    """

    def __init__(self, mcp_config: Optional[Dict[str, Any]] = None):
        self.mcp_config = mcp_config or {}
        self._servers: Dict[str, MCPServerInfo] = {}
        self._tool_index: Dict[str, List[str]] = {}
        self._initialize_servers()

    def _initialize_servers(self) -> None:
        """Initialize server info from config."""
        for server_name, server_config in self.mcp_config.items():
            self._servers[server_name] = MCPServerInfo(
                name=server_name,
                state=MCPServerState.DISCONNECTED,
            )

    def can_handle(self, task: str) -> bool:
        """Check if MCP servers can potentially handle this task."""
        return self.get_confidence(task) > 0.0

    def get_confidence(self, task: str) -> float:
        """Get confidence score for MCP-based handling."""
        task_lower = task.lower()
        task_words = set(task_lower.split())

        if not self._servers:
            return 0.0

        max_confidence = 0.0

        for server_name, server_info in self._servers.items():
            server_confidence = self._score_server_match(server_info, task_words)
            max_confidence = max(max_confidence, server_confidence)

        return max_confidence

    def _score_server_match(self, server: MCPServerInfo, task_words: set) -> float:
        """Score how well a server matches the task."""
        if not server.tools:
            return 0.1

        matched = 0
        for tool in server.tools:
            tool_text = f"{tool.name} {tool.description}".lower()
            if any(word in tool_text for word in task_words):
                matched += 1

        return min(matched / max(len(task_words), 1), 1.0) * 0.8

    async def handle(self, task: str) -> MCPLayerResult:
        """Attempt to handle task by connecting relevant MCP servers."""
        task_lower = task.lower()
        task_words = set(task_lower.split())

        server_scores = []
        for server_name, server_info in self._servers.items():
            score = self._score_server_match(server_info, task_words)
            if score > 0.0:
                server_scores.append((server_name, score))

        if not server_scores:
            return MCPLayerResult(
                success=False,
                error="No MCP servers match the task domain",
            )

        server_scores.sort(key=lambda x: x[1], reverse=True)
        recommended_server = server_scores[0][0]

        connected = []
        all_tools = []

        for server_name, score in server_scores:
            try:
                await self._connect_server(server_name)
                connected.append(server_name)
                server_info = self._servers[server_name]
                all_tools.extend(server_info.tools)
            except Exception as e:
                self._servers[server_name].state = MCPServerState.FAILED
                self._servers[server_name].error = str(e)

        if not connected:
            return MCPLayerResult(
                success=False,
                error="Failed to connect to any matching MCP servers",
            )

        return MCPLayerResult(
            success=True,
            connected_servers=connected,
            available_tools=all_tools,
            recommended_server=recommended_server,
        )

    async def _connect_server(self, server_name: str) -> None:
        """Connect to an MCP server."""
        server_info = self._servers.get(server_name)
        if not server_info:
            raise ValueError(f"Unknown server: {server_name}")

        if server_info.state == MCPServerState.CONNECTED:
            return

        server_info.state = MCPServerState.CONNECTING

        server_config = self.mcp_config.get(server_name, {})
        command = server_config.get("command", "")
        args = server_config.get("args", [])

        if not command:
            server_info.state = MCPServerState.FAILED
            server_info.error = "No command configured for server"
            return

        tools = await self._discover_tools(server_name, server_config)
        server_info.tools = tools
        server_info.state = MCPServerState.CONNECTED

    async def _discover_tools(
        self, server_name: str, config: Dict[str, Any]
    ) -> List[MCPToolInfo]:
        """Discover available tools from an MCP server."""
        tools = config.get("tools", [])
        result = []

        for tool_data in tools:
            tool = MCPToolInfo(
                name=tool_data.get("name", ""),
                description=tool_data.get("description", ""),
                server_name=server_name,
                parameters=tool_data.get("parameters", {}),
            )
            result.append(tool)

            if tool.name not in self._tool_index:
                self._tool_index[tool.name] = []
            self._tool_index[tool.name].append(server_name)

        return result

    def register_server(self, name: str, config: Dict[str, Any]) -> None:
        """Register a new MCP server."""
        self.mcp_config[name] = config
        self._servers[name] = MCPServerInfo(
            name=name,
            state=MCPServerState.DISCONNECTED,
        )

    def get_server_status(self) -> Dict[str, MCPServerState]:
        """Get status of all registered servers."""
        return {name: info.state for name, info in self._servers.items()}

    def get_available_tools(self) -> List[MCPToolInfo]:
        """Get all available tools from connected servers."""
        tools = []
        for server_info in self._servers.values():
            if server_info.state == MCPServerState.CONNECTED:
                tools.extend(server_info.tools)
        return tools
