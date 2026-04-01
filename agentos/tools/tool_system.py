"""
AgentOS Tool System

Concurrent vs serial tool execution:
- Concurrent: Read-only operations (FileRead, Grep, Glob, WebFetch, WebSearch) run in parallel
- Serial: Mutating operations (FileEdit, FileWrite, Bash) run one at a time

Tool assembly from built-in + MCP with deduplication (built-in wins).
"""

from typing import Dict, List, Any, Optional, Set
from enum import Enum
from dataclasses import dataclass


class ToolSafety(Enum):
    CONCURRENT_SAFE = "concurrent_safe"
    SERIAL_ONLY = "serial_only"


@dataclass
class ToolDefinition:
    """Definition of a tool."""

    name: str
    description: str
    safety: ToolSafety
    source: str  # "built-in" or MCP server name
    parameters: Dict[str, Any]


class ToolRegistry:
    """Registry of all available tools."""

    def __init__(self):
        self.tools: Dict[str, ToolDefinition] = {}
        self.concurrent_tools: List[str] = []
        self.serial_tools: List[str] = []

    def register_tool(self, tool: ToolDefinition) -> None:
        """Register a tool. Built-in tools take precedence over MCP tools."""
        if tool.name in self.tools:
            existing = self.tools[tool.name]
            if existing.source == "built-in":
                return  # Built-in wins over MCP
            # Replace MCP tool with new definition
        self.tools[tool.name] = tool
        if tool.safety == ToolSafety.CONCURRENT_SAFE:
            if tool.name not in self.concurrent_tools:
                self.concurrent_tools.append(tool.name)
        else:
            if tool.name not in self.serial_tools:
                self.serial_tools.append(tool.name)

    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        """Get a tool by name."""
        return self.tools.get(name)

    def get_concurrent_tools(self) -> List[ToolDefinition]:
        """Get all concurrent-safe tools."""
        return [
            self.tools[name] for name in self.concurrent_tools if name in self.tools
        ]

    def get_serial_tools(self) -> List[ToolDefinition]:
        """Get all serial-only tools."""
        return [self.tools[name] for name in self.serial_tools if name in self.tools]

    def list_tools(self) -> List[str]:
        """List all tool names."""
        return list(self.tools.keys())

    def remove_tool(self, name: str) -> None:
        """Remove a tool."""
        if name in self.tools:
            tool = self.tools.pop(name)
            if tool.safety == ToolSafety.CONCURRENT_SAFE:
                self.concurrent_tools.remove(name)
            else:
                self.serial_tools.remove(name)

    def merge_mcp_tools(
        self, server_name: str, mcp_tools: List[Dict[str, Any]]
    ) -> None:
        """Merge tools from an MCP server."""
        for tool_data in mcp_tools:
            tool = ToolDefinition(
                name=tool_data.get("name", ""),
                description=tool_data.get("description", ""),
                safety=ToolSafety.SERIAL_ONLY,  # MCP tools default to serial
                source=server_name,
                parameters=tool_data.get("parameters", {}),
            )
            self.register_tool(tool)

    def get_tool_stats(self) -> Dict[str, Any]:
        """Get tool registry statistics."""
        return {
            "total_tools": len(self.tools),
            "concurrent_tools": len(self.concurrent_tools),
            "serial_tools": len(self.serial_tools),
            "sources": list(set(t.source for t in self.tools.values())),
        }


class ToolExecutor:
    """Executes tools with concurrent/serial batching."""

    def __init__(self, registry: ToolRegistry):
        self.registry = registry
        self.execution_log: List[Dict[str, Any]] = []

    def execute_concurrent_tools(
        self, tool_calls: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Execute concurrent-safe tools in parallel."""
        results = []
        for call in tool_calls:
            tool_name = call.get("tool", "")
            tool = self.registry.get_tool(tool_name)
            if tool and tool.safety == ToolSafety.CONCURRENT_SAFE:
                result = self._execute_tool(call)
                results.append(result)
        return results

    def execute_serial_tools(
        self, tool_calls: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Execute serial-only tools one at a time."""
        results = []
        for call in tool_calls:
            tool_name = call.get("tool", "")
            tool = self.registry.get_tool(tool_name)
            if tool and tool.safety == ToolSafety.SERIAL_ONLY:
                result = self._execute_tool(call)
                results.append(result)
        return results

    def _execute_tool(self, call: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single tool call."""
        tool_name = call.get("tool", "")
        arguments = call.get("arguments", {})
        tool = self.registry.get_tool(tool_name)

        if not tool:
            return {
                "tool": tool_name,
                "status": "error",
                "error": f"Tool '{tool_name}' not found",
            }

        # Tool execution would happen here
        # For now, return a placeholder
        return {
            "tool": tool_name,
            "status": "success",
            "output": f"Executed {tool_name} with {arguments}",
        }

    def partition_tool_calls(
        self, tool_calls: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Partition tool calls into concurrent and serial batches."""
        concurrent = []
        serial = []

        for call in tool_calls:
            tool_name = call.get("tool", "")
            tool = self.registry.get_tool(tool_name)
            if tool and tool.safety == ToolSafety.CONCURRENT_SAFE:
                concurrent.append(call)
            else:
                serial.append(call)

        return {
            "concurrent": concurrent,
            "serial": serial,
        }
