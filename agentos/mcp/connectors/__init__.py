"""
MCP Connector Interface

Base classes and interfaces for all MCP connectors.
Provides a standard interface for connecting to external services.
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional
from enum import Enum


class AuthType(Enum):
    """Authentication types supported by connectors."""

    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    BEARER_TOKEN = "bearer_token"
    BASIC = "basic"
    NONE = "none"


class ConnectorState(Enum):
    """Connector lifecycle states."""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    DISCONNECTING = "disconnecting"


class ToolDefinition:
    """Definition of a tool provided by a connector."""

    def __init__(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        handler: Callable[..., Any],
    ):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.handler = handler

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }


class ConnectorResult:
    """Standard result format for all connector operations."""

    def __init__(
        self,
        success: bool,
        output: Any = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.success = success
        self.output = output
        self.error = error
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "metadata": self.metadata,
        }

    @classmethod
    def ok(cls, output: Any = None, metadata: Optional[Dict[str, Any]] = None):
        return cls(success=True, output=output, metadata=metadata)

    @classmethod
    def fail(cls, error: str, metadata: Optional[Dict[str, Any]] = None):
        return cls(success=False, error=error, metadata=metadata)


class MCPConnector(ABC):
    """
    Abstract base class for all MCP connectors.

    All connectors must implement:
    - connect(): Establish connection to the service
    - disconnect(): Clean up connection resources
    - get_tools(): Return list of available tools (deferred loading)
    - call_tool(): Execute a tool by name with arguments

    Standard features:
    - Deferred tool loading (tools only loaded when needed)
    - Authentication handling (API keys, OAuth, etc.)
    - Graceful error handling
    - Standard result format {success, error, output}
    """

    def __init__(
        self,
        name: str,
        auth_type: AuthType = AuthType.NONE,
        config: Optional[Dict[str, Any]] = None,
    ):
        self.name = name
        self.auth_type = auth_type
        self.config = config or {}
        self.state = ConnectorState.DISCONNECTED
        self._tools: Optional[List[ToolDefinition]] = None
        self._tools_loaded = False
        self._connection = None

    @abstractmethod
    async def connect(self) -> ConnectorResult:
        """Establish connection to the external service."""
        pass

    @abstractmethod
    async def disconnect(self) -> ConnectorResult:
        """Disconnect and clean up resources."""
        pass

    @abstractmethod
    async def get_tools(self) -> List[ToolDefinition]:
        """Return list of available tools. Supports deferred loading."""
        pass

    @abstractmethod
    async def call_tool(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> ConnectorResult:
        """Execute a tool by name with the given arguments."""
        pass

    @property
    def is_connected(self) -> bool:
        return self.state == ConnectorState.CONNECTED

    def _set_auth(self, **kwargs) -> None:
        """Store authentication credentials in config."""
        self.config.update(kwargs)

    def _get_auth_header(self) -> Dict[str, str]:
        """Build authentication headers based on auth type."""
        if self.auth_type == AuthType.API_KEY:
            api_key = self.config.get("api_key")
            header_name = self.config.get("api_key_header", "Authorization")
            if api_key:
                return {header_name: f"Bearer {api_key}"}
        elif self.auth_type == AuthType.BEARER_TOKEN:
            token = self.config.get("token")
            if token:
                return {"Authorization": f"Bearer {token}"}
        elif self.auth_type == AuthType.BASIC:
            import base64

            username = self.config.get("username", "")
            password = self.config.get("password", "")
            credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
            return {"Authorization": f"Basic {credentials}"}
        return {}

    def _ensure_connected(self) -> ConnectorResult:
        """Check that connector is connected before operation."""
        if not self.is_connected:
            return ConnectorResult.fail(
                f"Connector '{self.name}' is not connected. Call connect() first."
            )
        return ConnectorResult.ok()

    async def _load_tools_if_needed(self) -> List[ToolDefinition]:
        """Load tools on first access (deferred loading)."""
        if not self._tools_loaded:
            self._tools = await self.get_tools()
            self._tools_loaded = True
        return self._tools or []

    def get_info(self) -> Dict[str, Any]:
        """Return connector metadata."""
        return {
            "name": self.name,
            "auth_type": self.auth_type.value,
            "state": self.state.value,
            "tools_loaded": self._tools_loaded,
            "tool_count": len(self._tools) if self._tools else 0,
        }
