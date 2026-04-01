import json
import time
import copy
import threading
from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from collections import defaultdict

from workflow_metrics import WorkflowMetricsCollector


class ExecutionStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ADAPTED = "adapted"
    CHECKPOINTED = "checkpointed"
    ROLLED_BACK = "rolled_back"


@dataclass
class PhaseResult:
    phase_name: str
    status: ExecutionStatus
    output: str
    duration_seconds: float
    capabilities_used: List[str]
    error: Optional[str] = None
    adaptations: List[str] = field(default_factory=list)
    checkpoint_id: Optional[str] = None
    resource_usage: Dict[str, float] = field(default_factory=dict)


@dataclass
class WorkflowResult:
    workflow_name: str
    status: ExecutionStatus
    phase_results: List[PhaseResult]
    total_duration_seconds: float
    adaptations_made: List[str]
    final_output: str
    checkpoints: List[str] = field(default_factory=list)
    rollback_available: bool = False


@dataclass
class ExecutionCheckpoint:
    """Checkpoint for execution state."""

    checkpoint_id: str
    phase_index: int
    phase_name: str
    context_snapshot: Dict
    completed_phases: List[PhaseResult]
    timestamp: float
    resource_state: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProgressUpdate:
    """Real-time progress update."""

    workflow_name: str
    current_phase: str
    phase_index: int
    total_phases: int
    phase_progress: float
    status: str
    elapsed_seconds: float
    estimated_remaining_seconds: float
    message: str


class ExecutionEngine:
    """Executes composed workflows with adaptation and error handling."""

    MIN_SUBAGENTS = 5
    MAX_SUBAGENTS = 25

    def __init__(self, capability_registry, adaptation_layer=None):
        self.registry = capability_registry
        self.adaptation_layer = adaptation_layer
        self.execution_history: List[WorkflowResult] = []
        self.metrics = WorkflowMetricsCollector()
        self.checkpoints: Dict[str, ExecutionCheckpoint] = {}
        self.active_resources: Dict[str, List[str]] = defaultdict(list)
        self.resource_usage: Dict[str, Dict[str, float]] = defaultdict(
            lambda: defaultdict(float)
        )
        self.progress_callbacks: List[Callable[[ProgressUpdate], None]] = []
        self._execution_lock = threading.Lock()
        self._current_execution_id: Optional[str] = None

    def add_progress_callback(self, callback: Callable[[ProgressUpdate], None]):
        """Add a callback for real-time progress updates."""
        self.progress_callbacks.append(callback)

    def _notify_progress(self, update: ProgressUpdate):
        """Notify all progress callbacks."""
        for callback in self.progress_callbacks:
            try:
                callback(update)
            except Exception:
                pass

    def execute(self, workflow, context: Optional[Dict] = None) -> WorkflowResult:
        """Execute a workflow and return the result."""
        if context is None:
            context = {}

        execution_id = "%s_%d" % (workflow.name, int(time.time() * 1000))
        self._current_execution_id = execution_id

        start_time = time.time()
        phase_results = []
        adaptations_made = []
        overall_status = ExecutionStatus.RUNNING
        checkpoints = []

        dag = getattr(workflow, "dag", None)
        if dag:
            try:
                execution_order = self._resolve_execution_order(workflow)
            except ValueError:
                execution_order = list(range(len(workflow.phases)))
        else:
            execution_order = list(range(len(workflow.phases)))

        for idx in execution_order:
            phase = workflow.phases[idx]

            if overall_status == ExecutionStatus.FAILED:
                phase_results.append(
                    PhaseResult(
                        phase_name=phase.name,
                        status=ExecutionStatus.SKIPPED,
                        output="Skipped due to previous failure",
                        duration_seconds=0,
                        capabilities_used=[],
                    )
                )
                continue

            checkpoint_id = self._create_checkpoint(
                execution_id, idx, phase.name, context, phase_results
            )
            checkpoints.append(checkpoint_id)

            self.metrics.record_phase_start(workflow.name, phase.name)

            self._notify_progress(
                ProgressUpdate(
                    workflow_name=workflow.name,
                    current_phase=phase.name,
                    phase_index=idx,
                    total_phases=len(workflow.phases),
                    phase_progress=0.0,
                    status="starting",
                    elapsed_seconds=time.time() - start_time,
                    estimated_remaining_seconds=self._estimate_remaining(
                        workflow, idx, phase_results
                    ),
                    message="Starting phase: %s" % phase.name,
                )
            )

            phase_start = time.time()
            try:
                result = self._execute_phase(phase, context)
                phase_duration = time.time() - phase_start

                status = result.get("status", ExecutionStatus.COMPLETED)
                phase_result = PhaseResult(
                    phase_name=phase.name,
                    status=status,
                    output=result.get("output", ""),
                    duration_seconds=phase_duration,
                    capabilities_used=result.get("capabilities_used", []),
                    error=result.get("error"),
                    adaptations=result.get("adaptations", []),
                    checkpoint_id=checkpoint_id,
                    resource_usage=dict(self.resource_usage[phase.name]),
                )
                phase_results.append(phase_result)

                self.metrics.record_phase_complete(
                    execution_id,
                    success=(
                        status in (ExecutionStatus.COMPLETED, ExecutionStatus.ADAPTED)
                    ),
                    duration=phase_duration,
                    capabilities_used=phase_result.capabilities_used,
                    adaptations=phase_result.adaptations,
                )

                if result.get("adaptations"):
                    adaptations_made.extend(result["adaptations"])

                if status == ExecutionStatus.FAILED:
                    if phase.on_failure == "abort":
                        overall_status = ExecutionStatus.FAILED
                    elif phase.on_failure == "skip":
                        pass
                    elif phase.on_failure == "continue":
                        pass

                self._notify_progress(
                    ProgressUpdate(
                        workflow_name=workflow.name,
                        current_phase=phase.name,
                        phase_index=idx,
                        total_phases=len(workflow.phases),
                        phase_progress=1.0,
                        status=status.value,
                        elapsed_seconds=time.time() - start_time,
                        estimated_remaining_seconds=self._estimate_remaining(
                            workflow, idx, phase_results
                        ),
                        message="Phase %s %s (%.1fs)"
                        % (phase.name, status.value, phase_duration),
                    )
                )

            except Exception as e:
                phase_duration = time.time() - phase_start
                phase_results.append(
                    PhaseResult(
                        phase_name=phase.name,
                        status=ExecutionStatus.FAILED,
                        output="",
                        duration_seconds=phase_duration,
                        capabilities_used=[],
                        error=str(e),
                        checkpoint_id=checkpoint_id,
                    )
                )
                self.metrics.record_phase_complete(
                    execution_id,
                    success=False,
                    duration=phase_duration,
                    capabilities_used=[],
                    adaptations=[],
                )
                if phase.on_failure == "abort":
                    overall_status = ExecutionStatus.FAILED

        total_duration = time.time() - start_time

        if overall_status == ExecutionStatus.RUNNING:
            overall_status = ExecutionStatus.COMPLETED

        final_output = self._generate_final_output(phase_results, adaptations_made)

        result = WorkflowResult(
            workflow_name=workflow.name,
            status=overall_status,
            phase_results=phase_results,
            total_duration_seconds=total_duration,
            adaptations_made=adaptations_made,
            final_output=final_output,
            checkpoints=checkpoints,
            rollback_available=len(checkpoints) > 0,
        )

        self.metrics.record_workflow_complete(
            workflow.name,
            success=(overall_status == ExecutionStatus.COMPLETED),
            total_duration=total_duration,
            phase_results=phase_results,
        )

        with self._execution_lock:
            self.execution_history.append(result)

        self._current_execution_id = None
        return result

    def execute_with_dag(
        self, workflow, context: Optional[Dict] = None
    ) -> WorkflowResult:
        """Execute a workflow using DAG-based parallel execution."""
        if context is None:
            context = {}

        dag = getattr(workflow, "dag", None)
        if not dag:
            return self.execute(workflow, context)

        start_time = time.time()
        phase_results = []
        adaptations_made = []
        overall_status = ExecutionStatus.RUNNING
        checkpoints = []
        completed_phases = set()
        phase_map = {p.name: p for p in workflow.phases}

        try:
            groups = dag.get_parallel_groups()
        except ValueError:
            return self.execute(workflow, context)

        for group_idx, group in enumerate(groups):
            if overall_status == ExecutionStatus.FAILED:
                for phase_name in group:
                    if phase_name in phase_map:
                        phase_results.append(
                            PhaseResult(
                                phase_name=phase_name,
                                status=ExecutionStatus.SKIPPED,
                                output="Skipped due to previous failure",
                                duration_seconds=0,
                                capabilities_used=[],
                            )
                        )
                continue

            group_results = []
            for phase_name in group:
                if phase_name not in phase_map:
                    continue

                phase = phase_map[phase_name]
                deps = dag.get_dependencies(phase_name)
                if deps and not all(d in completed_phases for d in deps):
                    group_results.append(
                        PhaseResult(
                            phase_name=phase_name,
                            status=ExecutionStatus.SKIPPED,
                            output="Dependencies not met",
                            duration_seconds=0,
                            capabilities_used=[],
                        )
                    )
                    continue

                checkpoint_id = self._create_checkpoint(
                    workflow.name, group_idx, phase_name, context, phase_results
                )
                checkpoints.append(checkpoint_id)

                self.metrics.record_phase_start(workflow.name, phase_name)

                phase_start = time.time()
                try:
                    result = self._execute_phase(phase, context)
                    phase_duration = time.time() - phase_start

                    status = result.get("status", ExecutionStatus.COMPLETED)
                    phase_result = PhaseResult(
                        phase_name=phase_name,
                        status=status,
                        output=result.get("output", ""),
                        duration_seconds=phase_duration,
                        capabilities_used=result.get("capabilities_used", []),
                        error=result.get("error"),
                        adaptations=result.get("adaptations", []),
                        checkpoint_id=checkpoint_id,
                    )
                    group_results.append(phase_result)

                    self.metrics.record_phase_complete(
                        "%s_dag" % workflow.name,
                        success=(
                            status
                            in (ExecutionStatus.COMPLETED, ExecutionStatus.ADAPTED)
                        ),
                        duration=phase_duration,
                        capabilities_used=phase_result.capabilities_used,
                        adaptations=phase_result.adaptations,
                    )

                    if status == ExecutionStatus.COMPLETED:
                        completed_phases.add(phase_name)

                    if result.get("adaptations"):
                        adaptations_made.extend(result["adaptations"])

                    if status == ExecutionStatus.FAILED and phase.on_failure == "abort":
                        overall_status = ExecutionStatus.FAILED

                except Exception as e:
                    phase_duration = time.time() - phase_start
                    group_results.append(
                        PhaseResult(
                            phase_name=phase_name,
                            status=ExecutionStatus.FAILED,
                            output="",
                            duration_seconds=phase_duration,
                            capabilities_used=[],
                            error=str(e),
                            checkpoint_id=checkpoint_id,
                        )
                    )
                    self.metrics.record_phase_complete(
                        "%s_dag" % workflow.name,
                        success=False,
                        duration=phase_duration,
                        capabilities_used=[],
                        adaptations=[],
                    )

            phase_results.extend(group_results)

        total_duration = time.time() - start_time
        if overall_status == ExecutionStatus.RUNNING:
            overall_status = ExecutionStatus.COMPLETED

        final_output = self._generate_final_output(phase_results, adaptations_made)

        result = WorkflowResult(
            workflow_name=workflow.name,
            status=overall_status,
            phase_results=phase_results,
            total_duration_seconds=total_duration,
            adaptations_made=adaptations_made,
            final_output=final_output,
            checkpoints=checkpoints,
            rollback_available=len(checkpoints) > 0,
        )

        self.metrics.record_workflow_complete(
            workflow.name,
            success=(overall_status == ExecutionStatus.COMPLETED),
            total_duration=total_duration,
            phase_results=phase_results,
        )

        with self._execution_lock:
            self.execution_history.append(result)

        return result

    def _resolve_execution_order(self, workflow) -> List[int]:
        """Resolve execution order from DAG."""
        dag = getattr(workflow, "dag", None)
        if not dag:
            return list(range(len(workflow.phases)))

        try:
            order = dag.topological_sort()
        except ValueError:
            return list(range(len(workflow.phases)))

        phase_map = {p.name: i for i, p in enumerate(workflow.phases)}
        return [phase_map[name] for name in order if name in phase_map]

    def _create_checkpoint(
        self,
        execution_id: str,
        phase_index: int,
        phase_name: str,
        context: Dict,
        completed: List[PhaseResult],
    ) -> str:
        """Create an execution checkpoint."""
        import hashlib

        timestamp = time.time()
        checkpoint_id = hashlib.md5(
            (
                "%s_%s_%d_%s" % (execution_id, phase_name, phase_index, timestamp)
            ).encode()
        ).hexdigest()[:12]

        self.checkpoints[checkpoint_id] = ExecutionCheckpoint(
            checkpoint_id=checkpoint_id,
            phase_index=phase_index,
            phase_name=phase_name,
            context_snapshot=copy.deepcopy(context),
            completed_phases=list(completed),
            timestamp=timestamp,
            resource_state={
                "resources": list(self.active_resources.get(phase_name, []))
            },
        )

        return checkpoint_id

    def restore_checkpoint(self, checkpoint_id: str) -> Optional[Dict]:
        """Restore execution state from a checkpoint."""
        if checkpoint_id not in self.checkpoints:
            return None

        cp = self.checkpoints[checkpoint_id]
        return {
            "context": copy.deepcopy(cp.context_snapshot),
            "completed_phases": list(cp.completed_phases),
            "phase_index": cp.phase_index,
            "phase_name": cp.phase_name,
        }

    def get_checkpoints(self, workflow_name: Optional[str] = None) -> List[Dict]:
        """Get all checkpoints, optionally filtered by workflow."""
        result = []
        for cp in self.checkpoints.values():
            if workflow_name and not cp.checkpoint_id.startswith(workflow_name):
                continue
            result.append(
                {
                    "checkpoint_id": cp.checkpoint_id,
                    "phase_name": cp.phase_name,
                    "phase_index": cp.phase_index,
                    "timestamp": datetime.fromtimestamp(cp.timestamp).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                }
            )
        return result

    def _estimate_remaining(
        self, workflow, current_idx: int, completed: List[PhaseResult]
    ) -> float:
        """Estimate remaining execution time."""
        completed_durations = {pr.phase_name: pr.duration_seconds for pr in completed}
        remaining = 0.0
        for i in range(current_idx + 1, len(workflow.phases)):
            phase = workflow.phases[i]
            if phase.name in completed_durations:
                remaining += completed_durations[phase.name]
            else:
                remaining += phase.timeout_seconds * 0.5
        return remaining

    def _execute_phase(self, phase, context: Dict) -> Dict:
        """Execute a single workflow phase."""
        capabilities_used = []
        outputs = []
        adaptations = []

        capabilities = []
        for cap_name in phase.capabilities:
            cap = self.registry.get_by_name(cap_name)
            if cap:
                capabilities.append(cap)
                capabilities_used.append(cap_name)

        self.resource_usage[phase.name]["cpu_percent"] = 0.0
        self.resource_usage[phase.name]["memory_mb"] = 0.0
        self.resource_usage[phase.name]["capabilities_count"] = len(capabilities)

        if phase.parallel:
            parallel_caps = [c for c in capabilities if c.parallel_safe]
            sequential_caps = [c for c in capabilities if not c.parallel_safe]

            num_parallel = min(len(parallel_caps), self.MAX_SUBAGENTS)
            for cap in parallel_caps[: self.MAX_SUBAGENTS]:
                try:
                    output = self._execute_capability(cap, context)
                    outputs.append(
                        {"capability": cap.name, "output": output, "status": "success"}
                    )
                except Exception as e:
                    outputs.append(
                        {
                            "capability": cap.name,
                            "output": "",
                            "status": "error",
                            "error": str(e),
                        }
                    )

            for cap in sequential_caps:
                try:
                    output = self._execute_capability(cap, context)
                    outputs.append(
                        {"capability": cap.name, "output": output, "status": "success"}
                    )
                except Exception as e:
                    outputs.append(
                        {
                            "capability": cap.name,
                            "output": "",
                            "status": "error",
                            "error": str(e),
                        }
                    )
        else:
            for cap in capabilities:
                try:
                    output = self._execute_capability(cap, context)
                    outputs.append(
                        {"capability": cap.name, "output": output, "status": "success"}
                    )
                except Exception as e:
                    outputs.append(
                        {
                            "capability": cap.name,
                            "output": "",
                            "status": "error",
                            "error": str(e),
                        }
                    )

        errors = [o for o in outputs if o["status"] == "error"]
        if errors and len(errors) > len(outputs) / 2:
            return {
                "status": ExecutionStatus.FAILED,
                "output": "\n".join(
                    [o["output"] for o in outputs if o["status"] == "success"]
                ),
                "capabilities_used": capabilities_used,
                "error": "Too many capability failures: %s"
                % ", ".join([e["error"] for e in errors[:3]]),
                "adaptations": adaptations,
            }

        if self.adaptation_layer:
            adaptation_result = self.adaptation_layer.adapt_phase(
                phase, outputs, context
            )
            if adaptation_result:
                outputs = adaptation_result.get("outputs", outputs)
                adaptations.extend(adaptation_result.get("adaptations", []))
                context.update(adaptation_result.get("context_updates", {}))

        return {
            "status": ExecutionStatus.COMPLETED,
            "output": "\n".join([o["output"] for o in outputs if o["output"]]),
            "capabilities_used": capabilities_used,
            "adaptations": adaptations,
        }

    def _execute_capability(self, capability, context: Dict) -> str:
        """Execute a single capability."""
        cap_type = capability.cap_type.value

        if cap_type == "tool":
            return self._execute_tool(capability, context)
        elif cap_type == "agent":
            return self._execute_agent(capability, context)
        elif cap_type == "service":
            return self._execute_service(capability, context)
        elif cap_type == "hook":
            return self._execute_hook(capability, context)
        elif cap_type == "command":
            return self._execute_command(capability, context)
        else:
            return "Capability type '%s' not directly executable" % cap_type

    def _execute_tool(self, capability, context: Dict) -> str:
        return """## Execute: %s

**Description:** %s
**Inputs:** %s
**Expected Output:** %s

**Instructions:**
1. Use the %s tool with the following parameters:
   - Input: %s
   - Context: Current workflow phase is '%s'

2. Process the output and store results for next phase.

**Dependencies:** %s
""" % (
            capability.name,
            capability.description,
            capability.inputs,
            capability.outputs,
            capability.name,
            self._resolve_input(capability.inputs, context),
            context.get("current_phase", "unknown"),
            ", ".join(capability.dependencies) if capability.dependencies else "None",
        )

    def _execute_agent(self, capability, context: Dict) -> str:
        return """## Execute: %s (Agent)

**Description:** %s
**Inputs:** %s
**Expected Output:** %s

**Instructions:**
1. Spawn an agent using the Agent tool with:
   - subagent_type: %s
   - prompt: %s
   - run_in_background: %s

2. Monitor agent progress and collect results.

**Dependencies:** %s
""" % (
            capability.name,
            capability.description,
            capability.inputs,
            capability.outputs,
            capability.name.replace("-agent", "")
            if "-agent" in capability.name
            else "general-purpose",
            context.get("agent_prompt", capability.description),
            context.get("parallel", "true"),
            ", ".join(capability.dependencies) if capability.dependencies else "None",
        )

    def _execute_service(self, capability, context: Dict) -> str:
        return """## Use: %s (Service)

**Description:** %s
**Inputs:** %s
**Expected Output:** %s

**Instructions:**
1. Configure the %s service with:
   - Input: %s

2. Process the service output.

**Dependencies:** %s
""" % (
            capability.name,
            capability.description,
            capability.inputs,
            capability.outputs,
            capability.name,
            self._resolve_input(capability.inputs, context),
            ", ".join(capability.dependencies) if capability.dependencies else "None",
        )

    def _execute_hook(self, capability, context: Dict) -> str:
        return """## Setup: %s (Hook)

**Description:** %s
**Inputs:** %s
**Expected Output:** %s

**Instructions:**
1. Register the %s hook with:
   - Event: %s
   - Handler: Based on workflow context

2. Monitor hook executions during workflow.

**Dependencies:** %s
""" % (
            capability.name,
            capability.description,
            capability.inputs,
            capability.outputs,
            capability.name,
            capability.name.split("-")[0],
            ", ".join(capability.dependencies) if capability.dependencies else "None",
        )

    def _execute_command(self, capability, context: Dict) -> str:
        return """## Execute: %s (Command)

**Description:** %s
**Inputs:** %s
**Expected Output:** %s

**Instructions:**
1. Run the /%s command with:
   - Arguments: %s

2. Process command output.

**Dependencies:** %s
""" % (
            capability.name,
            capability.description,
            capability.inputs,
            capability.outputs,
            capability.name.replace("-command", ""),
            self._resolve_input(capability.inputs, context),
            ", ".join(capability.dependencies) if capability.dependencies else "None",
        )

    def _resolve_input(self, input_spec: str, context: Dict) -> str:
        result = input_spec
        for key, value in context.items():
            placeholder = "${%s}" % key
            if placeholder in result:
                result = result.replace(placeholder, str(value))
        return result

    def _generate_final_output(
        self, phase_results: List[PhaseResult], adaptations: List[str]
    ) -> str:
        lines = ["## Workflow Execution Complete", "", "### Phase Results:"]

        for pr in phase_results:
            status_icon = {
                ExecutionStatus.COMPLETED: "[OK]",
                ExecutionStatus.FAILED: "[FAIL]",
                ExecutionStatus.SKIPPED: "[SKIP]",
                ExecutionStatus.ADAPTED: "[ADAPT]",
                ExecutionStatus.CHECKPOINTED: "[CHECKPOINT]",
                ExecutionStatus.ROLLED_BACK: "[ROLLBACK]",
            }.get(pr.status, "[??]")

            lines.append(
                "- %s %s (%.1fs)" % (status_icon, pr.phase_name, pr.duration_seconds)
            )
            if pr.error:
                lines.append("  Error: %s" % pr.error)
            if pr.adaptations:
                lines.append("  Adaptations: %s" % ", ".join(pr.adaptations))

        if adaptations:
            lines.append("")
            lines.append("### Adaptations Made:")
            for adaptation in adaptations:
                lines.append("- %s" % adaptation)

        return "\n".join(lines)

    def get_execution_summary(self) -> str:
        if not self.execution_history:
            return "No executions recorded."

        lines = [
            "Execution History Summary",
            "=" * 40,
            "Total executions: %d" % len(self.execution_history),
            "",
        ]

        for i, result in enumerate(self.execution_history, 1):
            lines.append("Execution %d: %s" % (i, result.workflow_name))
            lines.append("  Status: %s" % result.status.value)
            lines.append("  Duration: %.1fs" % result.total_duration_seconds)
            lines.append("  Phases: %d" % len(result.phase_results))
            lines.append("  Adaptations: %d" % len(result.adaptations_made))
            lines.append("  Checkpoints: %d" % len(result.checkpoints))
            lines.append("")

        return "\n".join(lines)

    def get_analytics(self) -> Dict[str, Any]:
        """Get comprehensive execution analytics."""
        analytics = self.metrics.get_analytics()

        if self.execution_history:
            total = len(self.execution_history)
            success = sum(
                1
                for e in self.execution_history
                if e.status == ExecutionStatus.COMPLETED
            )
            failed = sum(
                1 for e in self.execution_history if e.status == ExecutionStatus.FAILED
            )
            avg_duration = (
                sum(e.total_duration_seconds for e in self.execution_history) / total
            )

            analytics["execution_summary"] = {
                "total_executions": total,
                "success_count": success,
                "failure_count": failed,
                "success_rate": success / total if total > 0 else 0,
                "avg_duration_seconds": avg_duration,
            }

        analytics["checkpoint_count"] = len(self.checkpoints)
        analytics["resource_usage"] = dict(self.resource_usage)

        return analytics
