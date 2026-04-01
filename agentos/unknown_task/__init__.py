"""
AgentOS Unknown Task Handling Framework

7-layer system for handling tasks with zero prior context:
- Layer 1: Skills - Check existing skills for matching capabilities
- Layer 2: MCP - Connect MCP servers for domain capabilities
- Layer 3: Tool Search - Discover unknown tools on demand
- Layer 4: Research - Fork agents for deep research
- Layer 5: Adaptation - Substitute failed capabilities
- Layer 6: Memory - Store learned knowledge
- Layer 7: Fallback - Graceful degradation chains

Each layer implements a standard interface:
- can_handle(task) -> bool
- handle(task) -> LayerResult
- get_confidence(task) -> float
"""

from agentos.unknown_task.layer1_skills import SkillsLayer
from agentos.unknown_task.layer2_mcp import MCPLayer
from agentos.unknown_task.layer3_toolsearch import ToolSearchLayer
from agentos.unknown_task.layer4_research import ResearchLayer
from agentos.unknown_task.layer5_adaptation import AdaptationLayer
from agentos.unknown_task.layer6_memory import MemoryLayer
from agentos.unknown_task.layer7_fallback import FallbackLayer
from agentos.unknown_task.orchestrator import UnknownTaskOrchestrator, LayerResult

__all__ = [
    "SkillsLayer",
    "MCPLayer",
    "ToolSearchLayer",
    "ResearchLayer",
    "AdaptationLayer",
    "MemoryLayer",
    "FallbackLayer",
    "UnknownTaskOrchestrator",
    "LayerResult",
]
