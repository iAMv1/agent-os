"""
Layer 3: Tool Search - Discover unknown tools on demand.

When existing skills and MCP servers don't cover the task,
search for and discover new tools that could help.
"""

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import json
import os


class ToolSource(Enum):
    REGISTRY = "registry"
    MARKETPLACE = "marketplace"
    DISCOVERED = "discovered"
    GENERATED = "generated"


@dataclass
class DiscoveredTool:
    """A tool discovered through search."""

    name: str
    description: str
    source: ToolSource
    confidence: float
    installation_command: Optional[str] = None
    usage_example: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolSearchResult:
    """Result from tool search layer."""

    success: bool
    discovered_tools: List[DiscoveredTool] = field(default_factory=list)
    search_queries: List[str] = field(default_factory=list)
    installation_plan: Optional[str] = None
    error: Optional[str] = None


class ToolSearchLayer:
    """
    Layer 3: Discover unknown tools on demand.

    Searches tool registries, marketplaces, and generates tool
    definitions for handling the unknown task.
    """

    def __init__(
        self,
        tool_registry_path: Optional[str] = None,
        search_enabled: bool = True,
    ):
        self.tool_registry_path = tool_registry_path
        self.search_enabled = search_enabled
        self._local_registry: Dict[str, Dict[str, Any]] = {}
        self._search_history: List[Dict[str, Any]] = []
        self._load_local_registry()

    def _load_local_registry(self) -> None:
        """Load tool registry from local file if available."""
        if self.tool_registry_path and os.path.exists(self.tool_registry_path):
            try:
                with open(self.tool_registry_path, "r") as f:
                    data = json.load(f)
                    self._local_registry = data.get("tools", {})
            except (json.JSONDecodeError, IOError):
                self._local_registry = {}

    def can_handle(self, task: str) -> bool:
        """Check if tool discovery can help with this task."""
        return self.get_confidence(task) > 0.0

    def get_confidence(self, task: str) -> float:
        """Get confidence score for tool search."""
        task_lower = task.lower()
        task_words = set(task_lower.split())

        confidence = 0.0

        for tool_name, tool_data in self._local_registry.items():
            tool_text = f"{tool_name} {tool_data.get('description', '')}".lower()
            matches = sum(1 for word in task_words if word in tool_text)
            if matches > 0:
                confidence = max(confidence, matches / len(task_words) * 0.9)

        if self.search_enabled:
            confidence = max(confidence, 0.3)

        return confidence

    def handle(self, task: str) -> ToolSearchResult:
        """Attempt to discover tools for the task."""
        discovered = []
        search_queries = self._generate_search_queries(task)

        for query in search_queries:
            local_results = self._search_local_registry(query, task)
            discovered.extend(local_results)

            if self.search_enabled:
                external_results = self._search_external(query, task)
                discovered.extend(external_results)

        discovered.sort(key=lambda t: t.confidence, reverse=True)

        if not discovered:
            generated = self._generate_tool_definition(task)
            if generated:
                discovered.append(generated)

        if not discovered:
            return ToolSearchResult(
                success=False,
                search_queries=search_queries,
                error="No tools discovered for task",
            )

        installation_plan = self._generate_installation_plan(discovered)

        return ToolSearchResult(
            success=True,
            discovered_tools=discovered,
            search_queries=search_queries,
            installation_plan=installation_plan,
        )

    def _generate_search_queries(self, task: str) -> List[str]:
        """Generate search queries from the task."""
        task_lower = task.lower()
        words = task_lower.split()

        queries = [task_lower]

        if len(words) > 1:
            queries.append(" ".join(words[:2]))

        action_words = [
            "create",
            "build",
            "generate",
            "convert",
            "analyze",
            "process",
            "validate",
            "transform",
            "extract",
            "parse",
        ]
        for action in action_words:
            if action in task_lower:
                queries.append(f"{action} tool")
                break

        return list(set(queries))

    def _search_local_registry(self, query: str, task: str) -> List[DiscoveredTool]:
        """Search local tool registry."""
        results = []
        task_words = set(task.lower().split())

        for tool_name, tool_data in self._local_registry.items():
            tool_text = f"{tool_name} {tool_data.get('description', '')}".lower()
            matches = sum(1 for word in task_words if word in tool_text)

            if matches > 0:
                confidence = min(matches / len(task_words), 1.0)
                results.append(
                    DiscoveredTool(
                        name=tool_name,
                        description=tool_data.get("description", ""),
                        source=ToolSource.REGISTRY,
                        confidence=confidence,
                        installation_command=tool_data.get("install_command"),
                        usage_example=tool_data.get("usage_example"),
                        parameters=tool_data.get("parameters", {}),
                    )
                )

        return results

    def _search_external(self, query: str, task: str) -> List[DiscoveredTool]:
        """Search external tool sources (placeholder for web search)."""
        results = []

        common_tools = self._get_common_tool_patterns(query)
        for tool_info in common_tools:
            results.append(
                DiscoveredTool(
                    name=tool_info["name"],
                    description=tool_info["description"],
                    source=ToolSource.MARKETPLACE,
                    confidence=tool_info["confidence"],
                    installation_command=tool_info.get("install_command"),
                    usage_example=tool_info.get("usage_example"),
                )
            )

        return results

    def _get_common_tool_patterns(self, query: str) -> List[Dict[str, Any]]:
        """Match query against common tool patterns."""
        patterns = {
            "json": {
                "name": "jq",
                "description": "Command-line JSON processor",
                "confidence": 0.6,
                "install_command": "apt-get install jq",
                "usage_example": "jq '.key' file.json",
            },
            "yaml": {
                "name": "yq",
                "description": "YAML processor",
                "confidence": 0.6,
                "install_command": "pip install yq",
                "usage_example": "yq '.key' file.yaml",
            },
            "csv": {
                "name": "csvkit",
                "description": "Command-line tools for CSV",
                "confidence": 0.6,
                "install_command": "pip install csvkit",
                "usage_example": "csvstat file.csv",
            },
            "git": {
                "name": "git",
                "description": "Distributed version control",
                "confidence": 0.7,
                "install_command": "apt-get install git",
                "usage_example": "git status",
            },
            "docker": {
                "name": "docker",
                "description": "Container platform",
                "confidence": 0.6,
                "install_command": "apt-get install docker.io",
                "usage_example": "docker ps",
            },
        }

        results = []
        query_lower = query.lower()
        for keyword, tool_info in patterns.items():
            if keyword in query_lower:
                results.append(tool_info)

        return results

    def _generate_tool_definition(self, task: str) -> Optional[DiscoveredTool]:
        """Generate a tool definition for the task."""
        task_lower = task.lower()

        if "convert" in task_lower or "transform" in task_lower:
            return DiscoveredTool(
                name="custom_converter",
                description=f"Custom converter for: {task}",
                source=ToolSource.GENERATED,
                confidence=0.3,
                usage_example=f"# Implement converter for: {task}",
            )

        if "analyze" in task_lower or "process" in task_lower:
            return DiscoveredTool(
                name="custom_analyzer",
                description=f"Custom analyzer for: {task}",
                source=ToolSource.GENERATED,
                confidence=0.3,
                usage_example=f"# Implement analyzer for: {task}",
            )

        return None

    def _generate_installation_plan(self, tools: List[DiscoveredTool]) -> str:
        """Generate an installation plan for discovered tools."""
        lines = ["Tool Installation Plan", "=" * 30, ""]

        for i, tool in enumerate(tools, 1):
            lines.append(f"{i}. {tool.name} (confidence: {tool.confidence:.2f})")
            lines.append(f"   Source: {tool.source.value}")
            if tool.installation_command:
                lines.append(f"   Install: {tool.installation_command}")
            if tool.usage_example:
                lines.append(f"   Example: {tool.usage_example}")
            lines.append("")

        return "\n".join(lines)

    def register_tool(self, name: str, metadata: Dict[str, Any]) -> None:
        """Register a tool in the local registry."""
        self._local_registry[name] = metadata

    def get_registered_tools(self) -> Dict[str, Dict[str, Any]]:
        """Get all registered tools."""
        return dict(self._local_registry)
