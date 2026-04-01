"""
Layer 7: Fallback - Graceful degradation chains.

Final layer: when all else fails, provide graceful degradation
with clear communication about limitations and alternatives.
"""

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone


class FallbackLevel(Enum):
    PARTIAL_EXECUTION = "partial_execution"
    GUIDED_MANUAL = "guided_manual"
    BEST_EFFORT = "best_effort"
    EXPLAIN_LIMITATIONS = "explain_limitations"
    DEFER_TO_HUMAN = "defer_to_human"


@dataclass
class FallbackStep:
    """A single step in the fallback chain."""

    level: FallbackLevel
    description: str
    instructions: List[str] = field(default_factory=list)
    expected_outcome: str = ""
    limitations: List[str] = field(default_factory=list)


@dataclass
class FallbackLayerResult:
    """Result from fallback layer."""

    success: bool
    fallback_level: FallbackLevel
    steps: List[FallbackStep] = field(default_factory=list)
    message: str = ""
    alternatives: List[str] = field(default_factory=list)
    error: Optional[str] = None


class FallbackLayer:
    """
    Layer 7: Graceful degradation when all other layers fail.

    Provides the best possible response given the limitations,
    with clear guidance on what can and cannot be done.
    """

    def __init__(self, max_fallback_depth: int = 5):
        self.max_fallback_depth = max_fallback_depth
        self._fallback_history: List[Dict[str, Any]] = []

    def can_handle(self, task: str) -> bool:
        """Fallback can always provide some response."""
        return True

    def get_confidence(self, task: str) -> float:
        """Fallback confidence is always low."""
        return 0.1

    def handle(self, task: str) -> FallbackLayerResult:
        """Execute fallback chain for the task."""
        fallback_chain = self._build_fallback_chain(task)

        for step in fallback_chain:
            result = self._attempt_fallback(step, task)
            if result.success:
                self._record_fallback(task, step.level, True)
                return result

        final_result = self._create_final_fallback(task)
        self._record_fallback(task, FallbackLevel.DEFER_TO_HUMAN, False)
        return final_result

    def _build_fallback_chain(self, task: str) -> List[FallbackStep]:
        """Build a chain of fallback steps."""
        chain = []

        chain.append(
            FallbackStep(
                level=FallbackLevel.PARTIAL_EXECUTION,
                description="Attempt partial execution of achievable portions",
                instructions=self._generate_partial_instructions(task),
                expected_outcome="Partial task completion",
                limitations=["Not all requirements will be met"],
            )
        )

        chain.append(
            FallbackStep(
                level=FallbackLevel.GUIDED_MANUAL,
                description="Provide step-by-step guidance for manual execution",
                instructions=self._generate_manual_instructions(task),
                expected_outcome="User can complete task manually with guidance",
                limitations=["Requires user intervention", "Slower than automated"],
            )
        )

        chain.append(
            FallbackStep(
                level=FallbackLevel.BEST_EFFORT,
                description="Provide best-effort response with available knowledge",
                instructions=self._generate_best_effort_instructions(task),
                expected_outcome="Best possible response given limitations",
                limitations=[
                    "May not fully address the task",
                    "Quality not guaranteed",
                ],
            )
        )

        chain.append(
            FallbackStep(
                level=FallbackLevel.EXPLAIN_LIMITATIONS,
                description="Clearly explain what cannot be done and why",
                instructions=self._generate_limitation_explanation(task),
                expected_outcome="User understands limitations",
                limitations=["No task completion"],
            )
        )

        chain.append(
            FallbackStep(
                level=FallbackLevel.DEFER_TO_HUMAN,
                description="Defer to human judgment and intervention",
                instructions=self._generate_defer_instructions(task),
                expected_outcome="Human takes over task handling",
                limitations=["Complete handoff required"],
            )
        )

        return chain[: self.max_fallback_depth]

    def _attempt_fallback(self, step: FallbackStep, task: str) -> FallbackLayerResult:
        """Attempt a fallback step."""
        if step.level == FallbackLevel.PARTIAL_EXECUTION:
            return FallbackLayerResult(
                success=False,
                fallback_level=step.level,
                steps=[step],
                message="Partial execution not available for this task",
                alternatives=step.instructions,
            )

        if step.level == FallbackLevel.GUIDED_MANUAL:
            return FallbackLayerResult(
                success=True,
                fallback_level=step.level,
                steps=[step],
                message="Manual guidance provided for task",
                alternatives=step.instructions,
            )

        if step.level == FallbackLevel.BEST_EFFORT:
            return FallbackLayerResult(
                success=True,
                fallback_level=step.level,
                steps=[step],
                message="Best-effort response provided",
                alternatives=step.instructions,
            )

        return FallbackLayerResult(
            success=False,
            fallback_level=step.level,
            steps=[step],
            message="Fallback step not applicable",
        )

    def _create_final_fallback(self, task: str) -> FallbackLayerResult:
        """Create the final fallback response."""
        return FallbackLayerResult(
            success=False,
            fallback_level=FallbackLevel.DEFER_TO_HUMAN,
            steps=[
                FallbackStep(
                    level=FallbackLevel.DEFER_TO_HUMAN,
                    description="All automated approaches exhausted",
                    instructions=[
                        f"Task: {task}",
                        "All 7 layers of the unknown task handling system have been attempted.",
                        "Recommend human review and intervention.",
                    ],
                    limitations=["No automated solution available"],
                )
            ],
            message="Task requires human intervention - all automated approaches exhausted",
            alternatives=[
                "Break task into smaller, more specific subtasks",
                "Provide additional context or domain information",
                "Install required tools or capabilities",
                "Consult domain-specific documentation",
            ],
        )

    def _generate_partial_instructions(self, task: str) -> List[str]:
        """Generate partial execution instructions."""
        return [
            f"Analyzing task: {task}",
            "Identifying achievable portions...",
            "Executing what's possible with available capabilities",
            "Documenting incomplete portions for follow-up",
        ]

    def _generate_manual_instructions(self, task: str) -> List[str]:
        """Generate manual execution instructions."""
        return [
            f"Task: {task}",
            "Step 1: Understand the task requirements",
            "Step 2: Identify required tools/capabilities",
            "Step 3: Install or access required resources",
            "Step 4: Execute the task manually",
            "Step 5: Verify the results",
        ]

    def _generate_best_effort_instructions(self, task: str) -> List[str]:
        """Generate best-effort instructions."""
        return [
            f"Best-effort response for: {task}",
            "Providing general guidance based on available knowledge",
            "Recommend verifying with domain-specific resources",
        ]

    def _generate_limitation_explanation(self, task: str) -> List[str]:
        """Generate limitation explanation."""
        return [
            f"Unable to fully handle task: {task}",
            "Reason: No matching capabilities found in any layer",
            "Layers attempted: Skills, MCP, Tool Search, Research, Adaptation, Memory",
            "Recommendation: Provide more context or install required capabilities",
        ]

    def _generate_defer_instructions(self, task: str) -> List[str]:
        """Generate defer-to-human instructions."""
        return [
            f"Task deferred: {task}",
            "All automated approaches have been exhausted",
            "Human intervention recommended",
            "Consider breaking task into smaller subtasks",
        ]

    def _record_fallback(self, task: str, level: FallbackLevel, success: bool) -> None:
        """Record fallback attempt."""
        self._fallback_history.append(
            {
                "task": task,
                "level": level.value,
                "success": success,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    def get_fallback_history(self) -> List[Dict[str, Any]]:
        """Get fallback history."""
        return list(self._fallback_history)

    def get_fallback_stats(self) -> Dict[str, Any]:
        """Get fallback statistics."""
        total = len(self._fallback_history)
        success = sum(1 for h in self._fallback_history if h["success"])

        level_counts = {}
        for h in self._fallback_history:
            level = h["level"]
            level_counts[level] = level_counts.get(level, 0) + 1

        return {
            "total_attempts": total,
            "successful": success,
            "failed": total - success,
            "success_rate": success / total if total > 0 else 0,
            "level_distribution": level_counts,
        }
