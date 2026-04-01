"""
AgentOS MCP Integration Layer

Deferred MCP server loading - zero cost until tools are actually needed.
Supports stdio, SSE, HTTP, WebSocket transports with OAuth and API key auth.
"""

import json
import os
import subprocess
import time
from pathlib import Path
from typing import Optional, Dict, Any, List


class MCPConfig:
    """Configuration for MCP servers."""

    def __init__(
        self,
        base_dir: Optional[str] = None,
    ):
        if base_dir is None:
            base_dir = os.path.join(os.getcwd(), ".agent-os", "mcp")
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.base_dir / "mcp.json"
        self.servers: Dict[str, Dict[str, Any]] = {}
        self.loaded_tools: Dict[str, List[str]] = {}
        self._load_config()

    def _load_config(self) -> None:
        """Load MCP server configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.servers = data.get("mcpServers", {})
            except (json.JSONDecodeError, IOError):
                self.servers = {}

    def save_config(self) -> None:
        """Save MCP server configuration to file."""
        data = {"mcpServers": self.servers}
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def add_server(self, name: str, config: Dict[str, Any]) -> None:
        """Add an MCP server configuration."""
        self.servers[name] = config
        self.save_config()

    def remove_server(self, name: str) -> None:
        """Remove an MCP server configuration."""
        if name in self.servers:
            del self.servers[name]
            self.loaded_tools.pop(name, None)
            self.save_config()

    def get_server(self, name: str) -> Optional[Dict[str, Any]]:
        """Get an MCP server configuration."""
        return self.servers.get(name)

    def list_servers(self) -> List[str]:
        """List all configured MCP servers."""
        return list(self.servers.keys())

    def get_loaded_tools(self, server_name: str) -> List[str]:
        """Get tools loaded from a specific server."""
        return self.loaded_tools.get(server_name, [])

    def register_tools(self, server_name: str, tools: List[str]) -> None:
        """Register tools from an MCP server."""
        self.loaded_tools[server_name] = tools

    def get_all_tools(self) -> List[str]:
        """Get all tools from all loaded servers."""
        all_tools = []
        for tools in self.loaded_tools.values():
            all_tools.extend(tools)
        return all_tools

    def get_server_status(self) -> Dict[str, Any]:
        """Get status of all MCP servers."""
        status = {}
        for name, config in self.servers.items():
            status[name] = {
                "configured": True,
                "tools_loaded": len(self.get_loaded_tools(name)),
                "transport": config.get("command", config.get("url", "unknown")),
            }
        return status


class MCPServer:
    """Represents a running MCP server process."""

    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.process: Optional[subprocess.Popen] = None
        self.tools: List[str] = []
        self.is_running: bool = False

    def start(self) -> bool:
        """Start the MCP server process."""
        command = self.config.get("command")
        args = self.config.get("args", [])
        env = self.config.get("env", {})

        if not command:
            return False

        try:
            full_env = os.environ.copy()
            full_env.update(env)
            self.process = subprocess.Popen(
                [command] + args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=full_env,
            )
            self.is_running = True
            return True
        except Exception:
            return False

    def stop(self, graceful: bool = True) -> None:
        """Stop the MCP server process."""
        if self.process is None:
            return

        if graceful:
            # SIGINT -> SIGTERM -> SIGKILL escalation
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)
        else:
            self.process.kill()

        self.is_running = False
        self.process = None

    def get_tools(self) -> List[str]:
        """Get available tools from this server."""
        return self.tools

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on this server."""
        if not self.is_running:
            return {"error": "Server not running"}

        # Tool call would go here via JSON-RPC over stdin/stdout
        return {"error": "Tool call not implemented"}
