"""
AgentOS Unknown Task Orchestrator

Main orchestrator for the 7-layer unknown task handling system.
Coordinates all layers, tracks what works, and learns from outcomes.
"""

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import time
from datetime import datetime, timezone

from agentos.unknown_task.layer1_skills import SkillsLayer, SkillsLayerResult
from agentos.unknown_task.layer2_mcp import MCPLayer, MCPLayerResult
from agentos.unknown_task.layer3_toolsearch import ToolSearchLayer, ToolSearchResult
from agentos.unknown_task.layer4_research import ResearchLayer, ResearchLayerResult
from agentos.unknown_task.layer5_adaptation import (
    AdaptationLayer,
    AdaptationLayerResult,
)
from agentos.unknown_task.layer6_memory import MemoryLayer, MemoryLayerResult
from agentos.unknown_task.layer7_fallback import FallbackLayer, FallbackLayerResult


class LayerName(Enum):
    SKILLS = "layer1_skills"
    MCP = "layer2_mcp"
    TOOL_SEARCH = "layer3_toolsearch"
    RESEARCH = "layer4_research"
    ADAPTATION = "layer5_adaptation"
    MEMORY = "layer6_memory"
    FALLBACK = "layer7_fallback"


class TaskOutcome(Enum):
    RESOLVED = "resolved"
    PARTIAL = "partial"
    FAILED = "failed"
    DEFERRED = "deferred"


@dataclass
class LayerResult:
    """Unified result from any layer."""

    layer: LayerName
    success: bool
    confidence: float
    result_data: Any = None
    execution_time_ms: float = 0.0
    error: Optional[str] = None


@dataclass
class TaskExecutionRecord:
    """Record of a task execution for learning."""

    task: str
    outcome: TaskOutcome
    layers_attempted: List[LayerName] = field(default_factory=list)
    successful_layer: Optional[LayerName] = None
    total_time_ms: float = 0.0
    timestamp: Optional[str] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class UnknownTaskOrchestrator:
    """
    Main orchestrator for the 7-layer unknown task handling system.

    Coordinates escalation through layers, tracks outcomes,
    and builds knowledge for future task handling.
    """

    def __init__(
        self,
        skills_layer: Optional[SkillsLayer] = None,
        mcp_layer: Optional[MCPLayer] = None,
        tool_search_layer: Optional[ToolSearchLayer] = None,
        research_layer: Optional[ResearchLayer] = None,
        adaptation_layer: Optional[AdaptationLayer] = None,
        memory_layer: Optional[MemoryLayer] = None,
        fallback_layer: Optional[FallbackLayer] = None,
        confidence_threshold: float = 0.5,
    ):
        self.skills = skills_layer or SkillsLayer()
        self.mcp = mcp_layer or MCPLayer()
        self.tool_search = tool_search_layer or ToolSearchLayer()
        self.research = research_layer or ResearchLayer()
        self.adaptation = adaptation_layer or AdaptationLayer()
        self.memory = memory_layer or MemoryLayer()
        self.fallback = fallback_layer or FallbackLayer()

        self.confidence_threshold = confidence_threshold
        self._execution_history: List[TaskExecutionRecord] = []
        self._layer_order = [
            (LayerName.MEMORY, self.memory),
            (LayerName.SKILLS, self.skills),
            (LayerName.MCP, self.mcp),
            (LayerName.TOOL_SEARCH, self.tool_search),
            (LayerName.RESEARCH, self.research),
            (LayerName.ADAPTATION, self.adaptation),
            (LayerName.FALLBACK, self.fallback),
        ]

    async def handle_task(self, task: str) -> LayerResult:
        """
        Handle an unknown task through the 7-layer system.

        Escalates through layers until one can handle the task
        or falls back to graceful degradation.
        """
        start_time = time.time()
        layers_attempted = []

        for layer_name, layer in self._layer_order:
            layer_start = time.time()

            if not layer.can_handle(task):
                continue

            layers_attempted.append(layer_name)
            result = await self._execute_layer(layer_name, layer, task)

            layer_time = (time.time() - layer_start) * 1000
            result.execution_time_ms = layer_time

            if result.success:
                total_time = (time.time() - start_time) * 1000
                self._record_outcome(
                    task,
                    TaskOutcome.RESOLVED,
                    layers_attempted,
                    layer_name,
                    total_time,
                )

                if layer_name != LayerName.MEMORY:
                    self._store_learning(task, result)

                return result

        total_time = (time.time() - start_time) * 1000
        self._record_outcome(
            task,
            TaskOutcome.FAILED,
            layers_attempted,
            None,
            total_time,
        )

        return LayerResult(
            layer=LayerName.FALLBACK,
            success=False,
            confidence=0.0,
            error="All layers failed to handle task",
            execution_time_ms=total_time,
        )

    async def _execute_layer(
        self, layer_name: LayerName, layer: Any, task: str
    ) -> LayerResult:
        """Execute a single layer and wrap the result."""
        try:
            result = layer.handle(task)
            return self._wrap_result(layer_name, result)
        except Exception as e:
            return LayerResult(
                layer=layer_name,
                success=False,
                confidence=0.0,
                error=str(e),
            )

    def _wrap_result(self, layer_name: LayerName, result: Any) -> LayerResult:
        """Wrap a layer-specific result into a unified LayerResult."""
        if isinstance(result, SkillsLayerResult):
            return LayerResult(
                layer=layer_name,
                success=result.success,
                confidence=self.skills.get_confidence(
                    result.matched_skills[0].skill_name
                )
                if result.matched_skills
                else 0.0,
                result_data=result,
            )

        if isinstance(result, MCPLayerResult):
            return LayerResult(
                layer=layer_name,
                success=result.success,
                confidence=len(result.connected_servers) * 0.3,
                result_data=result,
            )

        if isinstance(result, ToolSearchResult):
            return LayerResult(
                layer=layer_name,
                success=result.success,
                confidence=max(
                    (t.confidence for t in result.discovered_tools), default=0.0
                ),
                result_data=result,
            )

        if isinstance(result, ResearchLayerResult):
            return LayerResult(
                layer=layer_name,
                success=result.success,
                confidence=len(result.consolidated_findings) * 0.2,
                result_data=result,
            )

        if isinstance(result, AdaptationLayerResult):
            return LayerResult(
                layer=layer_name,
                success=result.success,
                confidence=result.selected_option.confidence
                if result.selected_option
                else 0.0,
                result_data=result,
            )

        if isinstance(result, MemoryLayerResult):
            return LayerResult(
                layer=layer_name,
                success=result.success,
                confidence=max(
                    (m.confidence for m in result.retrieved_memories), default=0.0
                ),
                result_data=result,
            )

        if isinstance(result, FallbackLayerResult):
            return LayerResult(
                layer=layer_name,
                success=result.success,
                confidence=0.1,
                result_data=result,
            )

        return LayerResult(
            layer=layer_name,
            success=getattr(result, "success", False),
            confidence=0.0,
            result_data=result,
        )

    def _record_outcome(
        self,
        task: str,
        outcome: TaskOutcome,
        layers_attempted: List[LayerName],
        successful_layer: Optional[LayerName],
        total_time_ms: float,
    ) -> None:
        """Record task execution outcome for learning."""
        record = TaskExecutionRecord(
            task=task,
            outcome=outcome,
            layers_attempted=layers_attempted,
            successful_layer=successful_layer,
            total_time_ms=total_time_ms,
        )
        self._execution_history.append(record)

    def _store_learning(self, task: str, result: LayerResult) -> None:
        """Store learning from successful task handling."""
        try:
            self.memory.handle(
                task,
                store_result={
                    "task": task,
                    "layer": result.layer.value,
                    "confidence": result.confidence,
                    "metadata": {
                        "execution_time_ms": result.execution_time_ms,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    },
                },
            )
        except Exception:
            pass

    def get_layer_confidence(self, task: str) -> Dict[str, float]:
        """Get confidence scores for all layers."""
        confidences = {}
        for layer_name, layer in self._layer_order:
            confidences[layer_name.value] = layer.get_confidence(task)
        return confidences

    def get_recommended_layer(self, task: str) -> Optional[LayerName]:
        """Get the recommended layer for handling the task."""
        best_layer = None
        best_confidence = 0.0

        for layer_name, layer in self._layer_order:
            confidence = layer.get_confidence(task)
            if confidence > best_confidence:
                best_confidence = confidence
                best_layer = layer_name

        return best_layer if best_confidence >= self.confidence_threshold else None

    def get_execution_history(self) -> List[TaskExecutionRecord]:
        """Get task execution history."""
        return list(self._execution_history)

    def get_stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics."""
        total = len(self._execution_history)
        resolved = sum(
            1 for r in self._execution_history if r.outcome == TaskOutcome.RESOLVED
        )
        failed = sum(
            1 for r in self._execution_history if r.outcome == TaskOutcome.FAILED
        )

        layer_success_counts = {}
        for record in self._execution_history:
            if record.successful_layer:
                layer = record.successful_layer.value
                layer_success_counts[layer] = layer_success_counts.get(layer, 0) + 1

        return {
            "total_tasks": total,
            "resolved": resolved,
            "failed": failed,
            "success_rate": resolved / total if total > 0 else 0,
            "layer_success_counts": layer_success_counts,
            "avg_execution_time_ms": (
                sum(r.total_time_ms for r in self._execution_history) / total
                if total > 0
                else 0
            ),
        }

    def reset(self) -> None:
        """Reset orchestrator state."""
        self._execution_history.clear()
