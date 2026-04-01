"""Workflow validation module - validates workflow structure and dependencies."""

import json
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field


@dataclass
class ValidationResult:
    """Result of workflow validation."""

    is_valid: bool
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    resource_estimate: Dict[str, float] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)


class WorkflowValidator:
    """Validates workflow structure, dependencies, and resource requirements."""

    def __init__(self, capability_registry):
        self.registry = capability_registry
        self.available_capabilities = set(c.name for c in self.registry.get_available())

    def validate(self, workflow) -> ValidationResult:
        """Validate a generated workflow with DAG."""
        result = ValidationResult(is_valid=True)

        self._validate_structure(workflow, result)
        self._validate_dag(workflow, result)
        self._validate_capabilities(workflow, result)
        self._validate_resources(workflow, result)
        self._validate_phase_integrity(workflow, result)

        result.is_valid = len(result.issues) == 0
        return result

    def validate_from_template(self, workflow) -> ValidationResult:
        """Validate a template-based workflow."""
        result = ValidationResult(is_valid=True)

        self._validate_template_structure(workflow, result)
        self._validate_template_capabilities(workflow, result)
        self._validate_template_phases(workflow, result)

        result.is_valid = len(result.issues) == 0
        return result

    def _validate_structure(self, workflow, result: ValidationResult):
        """Validate basic workflow structure."""
        if not workflow.name:
            result.issues.append("Workflow name is empty")
        if not workflow.description:
            result.warnings.append("Workflow description is empty")
        if not workflow.phases:
            result.issues.append("Workflow has no phases")
        if len(workflow.phases) == 0:
            result.issues.append("Workflow must have at least one phase")

        phase_names = [p.name for p in workflow.phases]
        if len(phase_names) != len(set(phase_names)):
            duplicates = [n for n in phase_names if phase_names.count(n) > 1]
            result.issues.append(
                "Duplicate phase names: %s" % ", ".join(set(duplicates))
            )

    def _validate_dag(self, workflow, result: ValidationResult):
        """Validate DAG structure and dependencies."""
        dag = workflow.dag
        phase_names = set(p.name for p in workflow.phases)

        for node in dag.nodes:
            if node not in phase_names:
                result.warnings.append(
                    "DAG node '%s' has no corresponding phase" % node
                )

        for edge in dag.edges:
            if edge.from_phase not in phase_names:
                result.issues.append(
                    "Dependency source '%s' not found in phases" % edge.from_phase
                )
            if edge.to_phase not in phase_names:
                result.issues.append(
                    "Dependency target '%s' not found in phases" % edge.to_phase
                )

        if dag.has_cycle():
            result.issues.append("Circular dependency detected in workflow DAG")

        try:
            order = dag.topological_sort()
            if len(order) != len(dag.nodes):
                result.warnings.append(
                    "Not all DAG nodes reachable in topological sort"
                )
        except ValueError as e:
            result.issues.append("DAG topology error: %s" % str(e))

    def _validate_capabilities(self, workflow, result: ValidationResult):
        """Validate that all required capabilities exist."""
        all_caps_used = set()
        for phase in workflow.phases:
            all_caps_used.update(phase.capabilities)

        unavailable = all_caps_used - self.available_capabilities
        if unavailable:
            result.warnings.append(
                "Unavailable capabilities: %s" % ", ".join(sorted(unavailable))
            )

        for phase in workflow.phases:
            if not phase.capabilities:
                result.warnings.append("Phase '%s' has no capabilities" % phase.name)

            for cap in phase.capabilities:
                if cap not in self.available_capabilities:
                    result.warnings.append(
                        "Phase '%s' uses unavailable capability '%s'"
                        % (phase.name, cap)
                    )

    def _validate_resources(self, workflow, result: ValidationResult):
        """Estimate and validate resource requirements."""
        total_timeout = sum(p.timeout_seconds for p in workflow.phases)
        total_retries = sum(p.retry_count for p in workflow.phases)
        parallel_phases = sum(1 for p in workflow.phases if p.parallel)

        result.resource_estimate = {
            "max_timeout_seconds": max(
                (p.timeout_seconds for p in workflow.phases), default=0
            ),
            "total_sequential_seconds": total_timeout,
            "max_concurrent_phases": parallel_phases,
            "total_retries": total_retries,
            "unique_capabilities": len(
                set(c for p in workflow.phases for c in p.capabilities)
            ),
        }

        if total_timeout > 7200:
            result.warnings.append(
                "Total sequential timeout exceeds 2 hours (%ds)" % total_timeout
            )

        if parallel_phases > 10:
            result.warnings.append(
                "High parallelism (%d phases) may strain resources" % parallel_phases
            )

        high_cost_caps = [
            "Agent",
            "general-purpose-agent",
            "TeamCreate",
            "RemoteAgentTask",
        ]
        high_cost_count = sum(
            1 for p in workflow.phases for c in p.capabilities if c in high_cost_caps
        )
        if high_cost_count > 5:
            result.warnings.append(
                "High-cost capabilities used %d times" % high_cost_count
            )

    def _validate_phase_integrity(self, workflow, result: ValidationResult):
        """Validate phase configuration integrity."""
        for phase in workflow.phases:
            if phase.timeout_seconds <= 0:
                result.issues.append(
                    "Phase '%s' has invalid timeout: %d"
                    % (phase.name, phase.timeout_seconds)
                )
            if phase.retry_count < 0:
                result.issues.append(
                    "Phase '%s' has invalid retry count: %d"
                    % (phase.name, phase.retry_count)
                )
            if phase.on_failure not in ("continue", "abort", "skip"):
                result.issues.append(
                    "Phase '%s' has invalid on_failure: %s"
                    % (phase.name, phase.on_failure)
                )

    def _validate_template_structure(self, workflow, result: ValidationResult):
        """Validate template-based workflow structure."""
        if not workflow.name:
            result.issues.append("Workflow name is empty")
        if not workflow.phases:
            result.issues.append("Workflow has no phases")

        phase_names = [p.name for p in workflow.phases]
        if len(phase_names) != len(set(phase_names)):
            duplicates = [n for n in phase_names if phase_names.count(n) > 1]
            result.issues.append(
                "Duplicate phase names: %s" % ", ".join(set(duplicates))
            )

    def _validate_template_capabilities(self, workflow, result: ValidationResult):
        """Validate capabilities in template workflow."""
        for phase in workflow.phases:
            for cap in phase.capabilities:
                if cap not in self.available_capabilities:
                    result.warnings.append(
                        "Phase '%s' uses unavailable capability '%s'"
                        % (phase.name, cap)
                    )

    def _validate_template_phases(self, workflow, result: ValidationResult):
        """Validate phase configurations in template workflow."""
        for phase in workflow.phases:
            if phase.timeout_seconds <= 0:
                result.issues.append("Phase '%s' has invalid timeout" % phase.name)
            if phase.on_failure not in ("continue", "abort", "skip"):
                result.issues.append(
                    "Phase '%s' has invalid on_failure: %s"
                    % (phase.name, phase.on_failure)
                )
