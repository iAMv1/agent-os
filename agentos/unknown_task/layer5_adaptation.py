"""
Layer 5: Adaptation - Substitute failed capabilities.

When primary approaches fail, find alternative ways to achieve
the task goal using available capabilities.
"""

from typing import Dict, Any, List, Optional, Set, Callable
from dataclasses import dataclass, field
from enum import Enum


class AdaptationStrategy(Enum):
    SUBSTITUTE = "substitute"
    DECOMPOSE = "decompose"
    SIMPLIFY = "simplify"
    PARTIAL = "partial"
    WORKAROUND = "workaround"


@dataclass
class AdaptationOption:
    """An adaptation option for handling the task."""

    strategy: AdaptationStrategy
    description: str
    confidence: float
    required_capabilities: List[str] = field(default_factory=list)
    execution_steps: List[str] = field(default_factory=list)
    trade_offs: List[str] = field(default_factory=list)


@dataclass
class AdaptationLayerResult:
    """Result from adaptation layer."""

    success: bool
    selected_option: Optional[AdaptationOption] = None
    all_options: List[AdaptationOption] = field(default_factory=list)
    fallback_chain: List[str] = field(default_factory=list)
    error: Optional[str] = None


class AdaptationLayer:
    """
    Layer 5: Substitute failed capabilities with alternatives.

    Analyzes the task and finds alternative approaches when
    primary capabilities are unavailable.
    """

    def __init__(
        self,
        available_capabilities: Optional[Dict[str, Any]] = None,
    ):
        self.available_capabilities = available_capabilities or {}
        self._adaptation_history: List[Dict[str, Any]] = []
        self._strategy_templates = self._init_strategy_templates()

    def _init_strategy_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize adaptation strategy templates."""
        return {
            "file_operations": {
                "substitutes": ["read", "write", "edit", "create", "delete"],
                "workarounds": ["use shell commands", "use python scripts"],
            },
            "code_analysis": {
                "substitutes": ["grep", "regex", "ast parsing", "manual review"],
                "workarounds": ["read file contents", "search for patterns"],
            },
            "web_access": {
                "substitutes": ["webfetch", "websearch", "curl"],
                "workarounds": ["use cached data", "manual lookup"],
            },
            "data_processing": {
                "substitutes": ["python", "shell tools", "manual processing"],
                "workarounds": ["simplify format", "process in chunks"],
            },
            "system_commands": {
                "substitutes": ["bash", "powershell", "python subprocess"],
                "workarounds": ["use built-in functions", "simulate output"],
            },
        }

    def can_handle(self, task: str) -> bool:
        """Adaptation can always attempt to find alternatives."""
        return True

    def get_confidence(self, task: str) -> float:
        """Confidence based on available capabilities."""
        if not self.available_capabilities:
            return 0.3

        task_lower = task.lower()
        matched = sum(
            1 for cap in self.available_capabilities if cap.lower() in task_lower
        )

        return min(matched / max(len(task_lower.split()), 1), 1.0) * 0.7

    def handle(self, task: str) -> AdaptationLayerResult:
        """Find adaptation options for the task."""
        options = []

        for strategy in AdaptationStrategy:
            option = self._generate_option(strategy, task)
            if option:
                options.append(option)

        if not options:
            return AdaptationLayerResult(
                success=False,
                error="No adaptation options available",
            )

        options.sort(key=lambda o: o.confidence, reverse=True)
        selected = options[0]

        fallback_chain = self._build_fallback_chain(options)

        self._adaptation_history.append(
            {
                "task": task,
                "selected_strategy": selected.strategy.value,
                "confidence": selected.confidence,
                "timestamp": self._get_timestamp(),
            }
        )

        return AdaptationLayerResult(
            success=True,
            selected_option=selected,
            all_options=options,
            fallback_chain=fallback_chain,
        )

    def _generate_option(
        self, strategy: AdaptationStrategy, task: str
    ) -> Optional[AdaptationOption]:
        """Generate an adaptation option for a strategy."""
        task_lower = task.lower()
        domain = self._detect_domain(task_lower)

        if strategy == AdaptationStrategy.SUBSTITUTE:
            return self._generate_substitute(domain, task)
        elif strategy == AdaptationStrategy.DECOMPOSE:
            return self._generate_decompose(task)
        elif strategy == AdaptationStrategy.SIMPLIFY:
            return self._generate_simplify(task)
        elif strategy == AdaptationStrategy.PARTIAL:
            return self._generate_partial(task)
        elif strategy == AdaptationStrategy.WORKAROUND:
            return self._generate_workaround(domain, task)

        return None

    def _detect_domain(self, task: str) -> str:
        """Detect the task domain."""
        domain_keywords = {
            "file_operations": ["file", "read", "write", "edit", "create", "path"],
            "code_analysis": ["code", "function", "class", "import", "syntax"],
            "web_access": ["web", "url", "http", "fetch", "download"],
            "data_processing": ["data", "parse", "convert", "transform", "json"],
            "system_commands": ["run", "execute", "command", "process", "system"],
        }

        for domain, keywords in domain_keywords.items():
            if any(keyword in task for keyword in keywords):
                return domain

        return "general"

    def _generate_substitute(
        self, domain: str, task: str
    ) -> Optional[AdaptationOption]:
        """Generate substitution option."""
        template = self._strategy_templates.get(domain, {})
        substitutes = template.get("substitutes", [])

        if not substitutes:
            substitutes = ["alternative approach", "manual method"]

        return AdaptationOption(
            strategy=AdaptationStrategy.SUBSTITUTE,
            description=f"Substitute with available alternatives: {', '.join(substitutes[:3])}",
            confidence=0.6,
            required_capabilities=substitutes[:3],
            execution_steps=[
                f"Identify substitute for: {task}",
                f"Use alternative: {substitutes[0]}",
                "Execute with substitute capability",
            ],
            trade_offs=["May have reduced functionality", "Might require manual steps"],
        )

    def _generate_decompose(self, task: str) -> AdaptationOption:
        """Generate decomposition option."""
        words = task.split()
        chunks = []
        chunk_size = max(len(words) // 3, 1)

        for i in range(0, len(words), chunk_size):
            chunks.append(" ".join(words[i : i + chunk_size]))

        steps = [f"Handle subtask: {chunk}" for chunk in chunks]

        return AdaptationOption(
            strategy=AdaptationStrategy.DECOMPOSE,
            description=f"Break task into {len(chunks)} subtasks",
            confidence=0.7,
            required_capabilities=["task decomposition", "sequential execution"],
            execution_steps=steps,
            trade_offs=["Increased complexity", "Longer execution time"],
        )

    def _generate_simplify(self, task: str) -> AdaptationOption:
        """Generate simplification option."""
        return AdaptationOption(
            strategy=AdaptationStrategy.SIMPLIFY,
            description=f"Simplify task scope while preserving core goal",
            confidence=0.5,
            required_capabilities=["scope analysis"],
            execution_steps=[
                "Identify core goal",
                "Remove non-essential requirements",
                "Execute simplified version",
            ],
            trade_offs=["Reduced scope", "May not meet all requirements"],
        )

    def _generate_partial(self, task: str) -> AdaptationOption:
        """Generate partial completion option."""
        return AdaptationOption(
            strategy=AdaptationStrategy.PARTIAL,
            description=f"Complete achievable portions of the task",
            confidence=0.4,
            required_capabilities=["partial execution"],
            execution_steps=[
                "Identify achievable portions",
                "Execute what's possible",
                "Document incomplete portions",
            ],
            trade_offs=["Incomplete result", "Requires follow-up"],
        )

    def _generate_workaround(
        self, domain: str, task: str
    ) -> Optional[AdaptationOption]:
        """Generate workaround option."""
        template = self._strategy_templates.get(domain, {})
        workarounds = template.get("workarounds", [])

        if not workarounds:
            workarounds = ["manual approach"]

        return AdaptationOption(
            strategy=AdaptationStrategy.WORKAROUND,
            description=f"Use workaround: {workarounds[0]}",
            confidence=0.4,
            required_capabilities=workarounds[:2],
            execution_steps=[
                f"Apply workaround for: {task}",
                f"Method: {workarounds[0]}",
                "Verify result",
            ],
            trade_offs=["Non-standard approach", "May require verification"],
        )

    def _build_fallback_chain(self, options: List[AdaptationOption]) -> List[str]:
        """Build a fallback chain from adaptation options."""
        return [
            f"{opt.strategy.value} (confidence: {opt.confidence:.2f})"
            for opt in options
        ]

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime, timezone

        return datetime.now(timezone.utc).isoformat()

    def register_capability(self, name: str, metadata: Dict[str, Any]) -> None:
        """Register an available capability."""
        self.available_capabilities[name] = metadata

    def get_adaptation_history(self) -> List[Dict[str, Any]]:
        """Get adaptation history."""
        return list(self._adaptation_history)
