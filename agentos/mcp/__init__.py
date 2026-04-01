"""
MCP (Model Context Protocol) Integration

Provides connector interfaces and management for external services.
"""

from agentos.mcp.connectors import (
    MCPConnector,
    AuthType,
    ConnectorState,
    ConnectorResult,
    ToolDefinition,
)
from agentos.mcp.connectors.registry import (
    ConnectorRegistry,
    create_default_registry,
)

__all__ = [
    "MCPConnector",
    "AuthType",
    "ConnectorState",
    "ConnectorResult",
    "ToolDefinition",
    "ConnectorRegistry",
    "create_default_registry",
]
