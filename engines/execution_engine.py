import json
import time
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class ExecutionStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ADAPTED = "adapted"


@dataclass
class PhaseResult:
    phase_name: str
    status: ExecutionStatus
    output: str
    duration_seconds: float
    capabilities_used: List[str]
    error: Optional[str] = None
    adaptations: List[str] = None


@dataclass
class WorkflowResult:
    workflow_name: str
    status: ExecutionStatus
    phase_results: List[PhaseResult]
    total_duration_seconds: float
    adaptations_made: List[str]
    final_output: str


class ExecutionEngine:
    """Executes composed workflows with adaptation and error handling."""

    def __init__(self, capability_registry, adaptation_layer=None):
        self.registry = capability_registry
        self.adaptation_layer = adaptation_layer
        self.execution_history: List[WorkflowResult] = []

    def execute(self, workflow, context: Dict = None) -> WorkflowResult:
        """Execute a workflow and return the result."""
        if context is None:
            context = {}

        start_time = time.time()
        phase_results = []
        adaptations_made = []
        overall_status = ExecutionStatus.RUNNING

        for phase in workflow.phases:
            # Check if we should skip this phase
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

            # Execute the phase
            phase_start = time.time()
            try:
                result = self._execute_phase(phase, context)
                phase_duration = time.time() - phase_start

                phase_results.append(
                    PhaseResult(
                        phase_name=phase.name,
                        status=result.get("status", ExecutionStatus.COMPLETED),
                        output=result.get("output", ""),
                        duration_seconds=phase_duration,
                        capabilities_used=result.get("capabilities_used", []),
                        error=result.get("error"),
                        adaptations=result.get("adaptations", []),
                    )
                )

                # Track adaptations
                if result.get("adaptations"):
                    adaptations_made.extend(result["adaptations"])

                # Check if phase failed
                if result.get("status") == ExecutionStatus.FAILED:
                    if phase.on_failure == "abort":
                        overall_status = ExecutionStatus.FAILED
                    elif phase.on_failure == "skip":
                        # Continue but mark as failed
                        pass
                    elif phase.on_failure == "continue":
                        # Continue execution
                        pass

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
                    )
                )
                if phase.on_failure == "abort":
                    overall_status = ExecutionStatus.FAILED

        total_duration = time.time() - start_time

        # Determine final status
        if overall_status == ExecutionStatus.RUNNING:
            overall_status = ExecutionStatus.COMPLETED

        # Generate final output
        final_output = self._generate_final_output(phase_results, adaptations_made)

        result = WorkflowResult(
            workflow_name=workflow.name,
            status=overall_status,
            phase_results=phase_results,
            total_duration_seconds=total_duration,
            adaptations_made=adaptations_made,
            final_output=final_output,
        )

        self.execution_history.append(result)
        return result

    def _execute_phase(self, phase, context: Dict) -> Dict:
        """Execute a single workflow phase."""
        capabilities_used = []
        outputs = []
        adaptations = []

        # Get capability details
        capabilities = []
        for cap_name in phase.capabilities:
            cap = self.registry.get_by_name(cap_name)
            if cap:
                capabilities.append(cap)
                capabilities_used.append(cap_name)

        # Check parallel safety
        if phase.parallel:
            # Execute parallel-safe capabilities
            parallel_caps = [c for c in capabilities if c.parallel_safe]
            sequential_caps = [c for c in capabilities if not c.parallel_safe]

            # Execute parallel capabilities
            for cap in parallel_caps:
                try:
                    output = self._execute_capability(cap, context)
                    outputs.append(
                        {
                            "capability": cap.name,
                            "output": output,
                            "status": "success",
                        }
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

            # Execute sequential capabilities
            for cap in sequential_caps:
                try:
                    output = self._execute_capability(cap, context)
                    outputs.append(
                        {
                            "capability": cap.name,
                            "output": output,
                            "status": "success",
                        }
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
            # Execute all capabilities sequentially
            for cap in capabilities:
                try:
                    output = self._execute_capability(cap, context)
                    outputs.append(
                        {
                            "capability": cap.name,
                            "output": output,
                            "status": "success",
                        }
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

        # Check for errors
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

        # Apply adaptation layer if available
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
        """Generate instructions for executing a tool capability."""
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
        """Generate instructions for executing an agent capability."""
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
        """Generate instructions for using a service capability."""
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
        """Generate instructions for setting up a hook capability."""
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
        """Generate instructions for executing a command capability."""
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
        """Resolve input specification using context."""
        # Simple template resolution
        result = input_spec
        for key, value in context.items():
            placeholder = "${%s}" % key
            if placeholder in result:
                result = result.replace(placeholder, str(value))
        return result

    def _generate_final_output(
        self, phase_results: List[PhaseResult], adaptations: List[str]
    ) -> str:
        """Generate final workflow output."""
        lines = [
            "## Workflow Execution Complete",
            "",
            "### Phase Results:",
        ]

        for pr in phase_results:
            status_icon = {
                ExecutionStatus.COMPLETED: "[OK]",
                ExecutionStatus.FAILED: "[FAIL]",
                ExecutionStatus.SKIPPED: "[SKIP]",
                ExecutionStatus.ADAPTED: "[ADAPT]",
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
        """Generate summary of all executions."""
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
            lines.append("")

        return "\n".join(lines)
