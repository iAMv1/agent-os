import json
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class AdaptationType(Enum):
    CAPABILITY_SUBSTITUTION = "capability_substitution"
    PHASE_MERGE = "phase_merge"
    PHASE_SPLIT = "phase_split"
    TIMEOUT_ADJUSTMENT = "timeout_adjustment"
    RETRY_ADJUSTMENT = "retry_adjustment"
    PARALLELISM_CHANGE = "parallelism_change"
    WORKFLOW_SWITCH = "workflow_switch"
    CONTEXT_ENRICHMENT = "context_enrichment"


@dataclass
class Adaptation:
    adaptation_type: AdaptationType
    description: str
    before: str
    after: str
    reason: str
    timestamp: float


class AdaptationLayer:
    """Monitors workflow execution and adapts dynamically based on feedback."""

    def __init__(self):
        self.adaptations: List[Adaptation] = []
        self.execution_metrics: Dict[str, List[float]] = {}
        self.failure_counts: Dict[str, int] = {}
        self.success_counts: Dict[str, int] = {}

    def adapt_phase(self, phase, outputs: List[Dict], context: Dict) -> Optional[Dict]:
        """Adapt a phase based on execution outputs."""
        adaptations = []
        context_updates = {}

        # Analyze outputs for failures
        errors = [o for o in outputs if o.get("status") == "error"]
        successes = [o for o in outputs if o.get("status") == "success"]

        # Adaptation 1: Capability substitution on failure
        if errors:
            for error_output in errors:
                cap_name = error_output.get("capability", "unknown")
                self.failure_counts[cap_name] = self.failure_counts.get(cap_name, 0) + 1

                # Try to find a substitute capability
                substitute = self._find_substitute(cap_name, context)
                if substitute:
                    adaptations.append(
                        Adaptation(
                            adaptation_type=AdaptationType.CAPABILITY_SUBSTITUTION,
                            description="Substituted %s with %s"
                            % (cap_name, substitute),
                            before=cap_name,
                            after=substitute,
                            reason="Capability %s failed: %s"
                            % (cap_name, error_output.get("error", "unknown")),
                            timestamp=time.time(),
                        )
                    )

        # Adaptation 2: Timeout adjustment based on execution time
        for output in outputs:
            cap_name = output.get("capability", "unknown")
            if cap_name not in self.execution_metrics:
                self.execution_metrics[cap_name] = []
            # Track execution times for future adjustments

        # Adaptation 3: Context enrichment based on outputs
        for output in successes:
            cap_name = output.get("capability", "unknown")
            self.success_counts[cap_name] = self.success_counts.get(cap_name, 0) + 1

            # Enrich context with successful outputs
            if output.get("output"):
                context_key = "%s_output" % cap_name.lower().replace("-", "_")
                context_updates[context_key] = output["output"]

        # Adaptation 4: Parallelism change based on error rate
        total = len(outputs)
        error_rate = len(errors) / total if total > 0 else 0

        if error_rate > 0.5:
            adaptations.append(
                Adaptation(
                    adaptation_type=AdaptationType.PARALLELISM_CHANGE,
                    description="Reduced parallelism due to high error rate (%.0f%%)"
                    % (error_rate * 100),
                    before="parallel",
                    after="sequential",
                    reason="More than 50%% of capabilities failed",
                    timestamp=time.time(),
                )
            )
            context_updates["reduce_parallelism"] = True

        # Adaptation 5: Workflow switch if too many failures
        total_failures = sum(self.failure_counts.values())
        total_successes = sum(self.success_counts.values())
        total_attempts = total_failures + total_successes

        if total_attempts > 10 and total_failures / total_attempts > 0.6:
            adaptations.append(
                Adaptation(
                    adaptation_type=AdaptationType.WORKFLOW_SWITCH,
                    description="Switching to simpler workflow due to persistent failures",
                    before="complex",
                    after="simple",
                    reason="More than 60%% of all capability attempts failed",
                    timestamp=time.time(),
                )
            )
            context_updates["switch_to_simple_workflow"] = True

        if not adaptations and not context_updates:
            return None

        return {
            "outputs": outputs,
            "adaptations": [a.description for a in adaptations],
            "context_updates": context_updates,
        }

    def _find_substitute(self, failed_cap: str, context: Dict) -> Optional[str]:
        """Find a substitute capability for a failed one."""
        # Capability substitution map
        substitutes = {
            "LSP": ["Grep", "FileRead"],
            "NotebookEdit": ["FileWrite", "FileEdit"],
            "PowerShell": ["Bash"],
            "RemoteTrigger": ["ScheduleCron"],
            "TeamCreate": ["Agent"],
            "SendMessage": ["Agent"],
            "verification-agent": ["general-purpose-agent"],
            "fork-agent": ["general-purpose-agent"],
            "Explore-agent": ["Grep", "Glob", "FileRead"],
            "Plan-agent": ["general-purpose-agent"],
            "agent-code-guide-agent": ["WebSearch", "WebFetch"],
            "WebSearch": ["WebFetch"],
            "WebFetch": ["WebSearch"],
        }

        return substitutes.get(failed_cap)

    def get_adaptation_report(self) -> str:
        """Generate a report of all adaptations made."""
        if not self.adaptations:
            return "No adaptations made."

        lines = [
            "Adaptation Report",
            "=" * 40,
            "Total adaptations: %d" % len(self.adaptations),
            "",
            "By type:",
        ]

        type_counts = {}
        for adaptation in self.adaptations:
            type_name = adaptation.adaptation_type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1

        for type_name, count in sorted(type_counts.items(), key=lambda x: -x[1]):
            lines.append("  %s: %d" % (type_name, count))

        lines.append("")
        lines.append("Recent adaptations:")
        for adaptation in self.adaptations[-10:]:
            lines.append(
                "- %s: %s" % (adaptation.adaptation_type.value, adaptation.description)
            )

        return "\n".join(lines)

    def record_adaptation(self, adaptation: Adaptation):
        """Record an adaptation."""
        self.adaptations.append(adaptation)
