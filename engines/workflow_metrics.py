"""Workflow metrics collection and analytics module."""

import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict
from datetime import datetime


@dataclass
class PhaseMetrics:
    """Metrics for a single phase execution."""

    phase_name: str
    execution_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    total_duration_seconds: float = 0.0
    min_duration_seconds: float = float("inf")
    max_duration_seconds: float = 0.0
    adaptation_count: int = 0
    last_execution_time: Optional[float] = None


@dataclass
class WorkflowMetrics:
    """Aggregated metrics for a workflow."""

    workflow_name: str
    execution_count: int = 0
    total_duration_seconds: float = 0.0
    success_rate: float = 0.0
    phase_metrics: Dict[str, PhaseMetrics] = field(default_factory=dict)
    adaptation_frequency: Dict[str, int] = field(default_factory=dict)
    resource_usage: Dict[str, float] = field(default_factory=dict)


class WorkflowMetricsCollector:
    """Collects and analyzes workflow execution metrics."""

    def __init__(self):
        self.phase_metrics: Dict[str, PhaseMetrics] = {}
        self.workflow_metrics: Dict[str, WorkflowMetrics] = {}
        self.execution_log: List[Dict[str, Any]] = []
        self.adaptation_log: List[Dict[str, Any]] = []
        self.start_time = time.time()

    def record_phase_start(self, workflow_name: str, phase_name: str) -> str:
        """Record the start of a phase execution."""
        execution_id = "%s_%s_%d" % (workflow_name, phase_name, int(time.time() * 1000))
        self.execution_log.append(
            {
                "execution_id": execution_id,
                "workflow_name": workflow_name,
                "phase_name": phase_name,
                "start_time": time.time(),
                "status": "running",
            }
        )
        return execution_id

    def record_phase_complete(
        self,
        execution_id: str,
        success: bool,
        duration: float,
        capabilities_used: List[str],
        adaptations: List[str] = None,
    ):
        """Record the completion of a phase execution."""
        for entry in self.execution_log:
            if entry["execution_id"] == execution_id:
                entry["end_time"] = time.time()
                entry["duration"] = duration
                entry["status"] = "success" if success else "failure"
                entry["capabilities_used"] = capabilities_used
                entry["adaptations"] = adaptations or []
                break

        phase_name = None
        workflow_name = None
        for entry in self.execution_log:
            if entry["execution_id"] == execution_id:
                phase_name = entry["phase_name"]
                workflow_name = entry["workflow_name"]
                break

        if phase_name:
            if phase_name not in self.phase_metrics:
                self.phase_metrics[phase_name] = PhaseMetrics(phase_name=phase_name)

            pm = self.phase_metrics[phase_name]
            pm.execution_count += 1
            pm.total_duration_seconds += duration
            pm.min_duration_seconds = min(pm.min_duration_seconds, duration)
            pm.max_duration_seconds = max(pm.max_duration_seconds, duration)
            pm.last_execution_time = time.time()

            if success:
                pm.success_count += 1
            else:
                pm.failure_count += 1

            if adaptations:
                pm.adaptation_count += len(adaptations)
                for adaptation in adaptations:
                    self.adaptation_log.append(
                        {
                            "type": adaptation,
                            "phase": phase_name,
                            "workflow": workflow_name,
                            "timestamp": time.time(),
                        }
                    )

    def record_workflow_created(self, workflow):
        """Record that a workflow was created."""
        name = getattr(workflow, "name", "unknown")
        if name not in self.workflow_metrics:
            self.workflow_metrics[name] = WorkflowMetrics(workflow_name=name)
        self.workflow_metrics[name].execution_count += 1

    def record_workflow_complete(
        self,
        workflow_name: str,
        success: bool,
        total_duration: float,
        phase_results: List[Any],
    ):
        """Record workflow completion."""
        if workflow_name not in self.workflow_metrics:
            self.workflow_metrics[workflow_name] = WorkflowMetrics(
                workflow_name=workflow_name
            )

        wm = self.workflow_metrics[workflow_name]
        wm.total_duration_seconds += total_duration

        for pr in phase_results:
            phase_name = getattr(pr, "phase_name", None) or getattr(pr, "phase", None)
            if phase_name:
                if phase_name not in wm.phase_metrics:
                    wm.phase_metrics[phase_name] = PhaseMetrics(phase_name=phase_name)
                pm = wm.phase_metrics[phase_name]
                pm.execution_count += 1
                duration = getattr(pr, "duration_seconds", 0)
                pm.total_duration_seconds += duration
                pm.min_duration_seconds = min(pm.min_duration_seconds, duration)
                pm.max_duration_seconds = max(pm.max_duration_seconds, duration)
                if (
                    getattr(pr, "status", None) == "completed"
                    or getattr(pr, "status", None) == "success"
                ):
                    pm.success_count += 1
                else:
                    pm.failure_count += 1

        total_executions = wm.execution_count
        success_count = sum(
            1
            for e in self.execution_log
            if e.get("workflow_name") == workflow_name and e.get("status") == "success"
        )
        wm.success_rate = (
            success_count / total_executions if total_executions > 0 else 0.0
        )

    def record_adaptation(
        self, adaptation_type: str, workflow_name: str, phase_name: str
    ):
        """Record an adaptation event."""
        self.adaptation_log.append(
            {
                "type": adaptation_type,
                "workflow": workflow_name,
                "phase": phase_name,
                "timestamp": time.time(),
            }
        )

        if workflow_name in self.workflow_metrics:
            wm = self.workflow_metrics[workflow_name]
            wm.adaptation_frequency[adaptation_type] = (
                wm.adaptation_frequency.get(adaptation_type, 0) + 1
            )

    def record_resource_usage(
        self, workflow_name: str, resource_name: str, usage: float
    ):
        """Record resource usage for a workflow."""
        if workflow_name in self.workflow_metrics:
            self.workflow_metrics[workflow_name].resource_usage[resource_name] = usage

    def generate_report(self) -> str:
        """Generate a human-readable performance report."""
        lines = [
            "Workflow Performance Report",
            "=" * 50,
            "Generated: %s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Uptime: %.0f seconds" % (time.time() - self.start_time),
            "",
            "Total executions: %d" % len(self.execution_log),
            "Total adaptations: %d" % len(self.adaptation_log),
            "",
        ]

        if self.workflow_metrics:
            lines.append("Workflow Metrics:")
            lines.append("-" * 40)
            for name, wm in self.workflow_metrics.items():
                lines.append("")
                lines.append("  Workflow: %s" % name)
                lines.append("  Executions: %d" % wm.execution_count)
                lines.append("  Success rate: %.1f%%" % (wm.success_rate * 100))
                lines.append("  Total duration: %.1fs" % wm.total_duration_seconds)

                if wm.adaptation_frequency:
                    lines.append("  Adaptations:")
                    for atype, count in sorted(
                        wm.adaptation_frequency.items(), key=lambda x: -x[1]
                    ):
                        lines.append("    - %s: %d" % (atype, count))

        if self.phase_metrics:
            lines.append("")
            lines.append("Phase Metrics:")
            lines.append("-" * 40)
            for name, pm in sorted(self.phase_metrics.items()):
                lines.append("")
                lines.append("  Phase: %s" % name)
                lines.append("  Executions: %d" % pm.execution_count)
                avg = (
                    pm.total_duration_seconds / pm.execution_count
                    if pm.execution_count > 0
                    else 0
                )
                lines.append("  Avg duration: %.2fs" % avg)
                lines.append(
                    "  Min/Max: %.2fs / %.2fs"
                    % (
                        pm.min_duration_seconds
                        if pm.min_duration_seconds != float("inf")
                        else 0,
                        pm.max_duration_seconds,
                    )
                )
                success_rate = (
                    (pm.success_count / pm.execution_count * 100)
                    if pm.execution_count > 0
                    else 0
                )
                lines.append("  Success rate: %.1f%%" % success_rate)

        optimizations = self._suggest_optimizations()
        if optimizations:
            lines.append("")
            lines.append("Optimization Suggestions:")
            lines.append("-" * 40)
            for opt in optimizations:
                lines.append("  - %s" % opt)

        return "\n".join(lines)

    def get_analytics(self) -> Dict[str, Any]:
        """Get execution analytics as a dictionary."""
        analytics = {
            "total_executions": len(self.execution_log),
            "total_adaptations": len(self.adaptation_log),
            "uptime_seconds": time.time() - self.start_time,
            "workflows": {},
            "phases": {},
            "adaptation_trends": {},
        }

        for name, wm in self.workflow_metrics.items():
            analytics["workflows"][name] = {
                "executions": wm.execution_count,
                "success_rate": wm.success_rate,
                "total_duration": wm.total_duration_seconds,
                "adaptation_frequency": wm.adaptation_frequency,
                "resource_usage": wm.resource_usage,
            }

        for name, pm in self.phase_metrics.items():
            avg = (
                pm.total_duration_seconds / pm.execution_count
                if pm.execution_count > 0
                else 0
            )
            success_rate = (
                pm.success_count / pm.execution_count if pm.execution_count > 0 else 0
            )
            analytics["phases"][name] = {
                "executions": pm.execution_count,
                "avg_duration": avg,
                "min_duration": pm.min_duration_seconds
                if pm.min_duration_seconds != float("inf")
                else 0,
                "max_duration": pm.max_duration_seconds,
                "success_rate": success_rate,
                "adaptations": pm.adaptation_count,
            }

        adaptation_counts = defaultdict(int)
        for entry in self.adaptation_log:
            adaptation_counts[entry["type"]] += 1
        analytics["adaptation_trends"] = dict(adaptation_counts)

        return analytics

    def _suggest_optimizations(self) -> List[str]:
        """Suggest optimizations based on collected metrics."""
        suggestions = []

        for name, pm in self.phase_metrics.items():
            if pm.execution_count < 2:
                continue

            avg = pm.total_duration_seconds / pm.execution_count
            if avg > 600:
                suggestions.append(
                    "Phase '%s' averages %.0fs - consider breaking into smaller phases"
                    % (name, avg)
                )

            failure_rate = (
                pm.failure_count / pm.execution_count if pm.execution_count > 0 else 0
            )
            if failure_rate > 0.3:
                suggestions.append(
                    "Phase '%s' has %.0f%% failure rate - investigate root causes"
                    % (name, failure_rate * 100)
                )

            if (
                pm.max_duration_seconds > pm.min_duration_seconds * 5
                and pm.min_duration_seconds > 0
            ):
                suggestions.append(
                    "Phase '%s' has high duration variance (%.0fs-%.0fs) - check for inconsistent inputs"
                    % (name, pm.min_duration_seconds, pm.max_duration_seconds)
                )

        for name, wm in self.workflow_metrics.items():
            if wm.adaptation_frequency:
                total_adaptations = sum(wm.adaptation_frequency.values())
                if total_adaptations > wm.execution_count * 2:
                    suggestions.append(
                        "Workflow '%s' adapts frequently (%d times) - consider redesigning phases"
                        % (name, total_adaptations)
                    )

        if not suggestions:
            suggestions.append("No optimizations suggested - metrics look healthy")

        return suggestions

    def get_phase_trend(
        self, phase_name: str, window: int = 10
    ) -> List[Dict[str, Any]]:
        """Get execution trend for a specific phase."""
        entries = [e for e in self.execution_log if e.get("phase_name") == phase_name]
        entries = entries[-window:]
        return entries

    def get_slowest_phases(self, top_n: int = 5) -> List[Dict[str, Any]]:
        """Get the slowest phases by average duration."""
        phase_avgs = []
        for name, pm in self.phase_metrics.items():
            if pm.execution_count > 0:
                avg = pm.total_duration_seconds / pm.execution_count
                phase_avgs.append(
                    {
                        "name": name,
                        "avg_duration": avg,
                        "executions": pm.execution_count,
                    }
                )
        phase_avgs.sort(key=lambda x: x["avg_duration"], reverse=True)
        return phase_avgs[:top_n]

    def get_failing_phases(self, threshold: float = 0.1) -> List[Dict[str, Any]]:
        """Get phases with failure rate above threshold."""
        failing = []
        for name, pm in self.phase_metrics.items():
            if pm.execution_count > 0:
                failure_rate = pm.failure_count / pm.execution_count
                if failure_rate > threshold:
                    failing.append(
                        {
                            "name": name,
                            "failure_rate": failure_rate,
                            "failures": pm.failure_count,
                        }
                    )
        failing.sort(key=lambda x: x["failure_rate"], reverse=True)
        return failing
