"""Workflow rollback module - saves state and enables rollback on failure."""

import json
import time
import copy
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Checkpoint:
    """A saved state checkpoint for rollback."""

    checkpoint_id: str
    workflow_name: str
    phase_name: str
    timestamp: float
    context_snapshot: Dict[str, Any]
    phase_outputs: Dict[str, Any]
    resource_state: Dict[str, Any]
    rollback_actions: List[str] = field(default_factory=list)


@dataclass
class RollbackResult:
    """Result of a rollback operation."""

    success: bool
    checkpoint_id: str
    rolled_back_phases: List[str]
    cleaned_resources: List[str]
    actions_taken: List[str]
    error: Optional[str] = None


class RollbackManager:
    """Manages workflow state checkpoints and rollback operations."""

    def __init__(self):
        self.checkpoints: Dict[str, Checkpoint] = {}
        self.rollback_log: List[Dict[str, Any]] = []
        self.active_resources: Dict[str, List[str]] = {}

    def save_state(self, workflow, context: Dict, phase_name: str = "") -> str:
        """Save state before executing a phase."""
        import hashlib

        timestamp = time.time()
        checkpoint_id = hashlib.md5(
            ("%s_%s_%s" % (workflow.name, phase_name, timestamp)).encode()
        ).hexdigest()[:12]

        context_snapshot = copy.deepcopy(context)
        phase_outputs = {}

        if hasattr(context, "get"):
            for key in ["task_description", "classification", "mode", "depth"]:
                if key in context:
                    phase_outputs[key] = context[key]

        resource_state = {}
        if workflow.name in self.active_resources:
            resource_state["active_resources"] = list(
                self.active_resources[workflow.name]
            )

        checkpoint = Checkpoint(
            checkpoint_id=checkpoint_id,
            workflow_name=workflow.name,
            phase_name=phase_name or "pre-execution",
            timestamp=timestamp,
            context_snapshot=context_snapshot,
            phase_outputs=phase_outputs,
            resource_state=resource_state,
        )

        self.checkpoints[checkpoint_id] = checkpoint
        return checkpoint_id

    def save_phase_checkpoint(
        self,
        workflow_name: str,
        phase_name: str,
        context: Dict,
        outputs: Dict,
        resources: List[str],
    ) -> str:
        """Save a checkpoint after phase execution."""
        import hashlib

        timestamp = time.time()
        checkpoint_id = hashlib.md5(
            ("%s_%s_%s" % (workflow_name, phase_name, timestamp)).encode()
        ).hexdigest()[:12]

        checkpoint = Checkpoint(
            checkpoint_id=checkpoint_id,
            workflow_name=workflow_name,
            phase_name=phase_name,
            timestamp=timestamp,
            context_snapshot=copy.deepcopy(context),
            phase_outputs=outputs,
            resource_state={"active_resources": list(resources)},
        )

        self.checkpoints[checkpoint_id] = checkpoint

        if workflow_name not in self.active_resources:
            self.active_resources[workflow_name] = []
        self.active_resources[workflow_name].extend(resources)

        return checkpoint_id

    def rollback(self, checkpoint_id: str) -> RollbackResult:
        """Rollback to a specific checkpoint."""
        if checkpoint_id not in self.checkpoints:
            return RollbackResult(
                success=False,
                checkpoint_id=checkpoint_id,
                rolled_back_phases=[],
                cleaned_resources=[],
                actions_taken=[],
                error="Checkpoint not found: %s" % checkpoint_id,
            )

        checkpoint = self.checkpoints[checkpoint_id]
        actions_taken = []
        cleaned_resources = []

        phases_to_rollback = []
        for cid, cp in self.checkpoints.items():
            if (
                cp.timestamp > checkpoint.timestamp
                and cp.workflow_name == checkpoint.workflow_name
            ):
                phases_to_rollback.append(cp.phase_name)

        phases_to_rollback.sort()

        resources_to_clean = []
        if checkpoint.workflow_name in self.active_resources:
            resources_to_clean = list(self.active_resources[checkpoint.workflow_name])
            cleaned_resources = resources_to_clean
            self.active_resources[checkpoint.workflow_name] = []

        actions_taken.append("Restored context to checkpoint state")
        actions_taken.append("Cleared %d resources" % len(cleaned_resources))
        actions_taken.append(
            "Marked %d phases for re-execution" % len(phases_to_rollback)
        )

        for phase in phases_to_rollback:
            actions_taken.append("Phase '%s' marked for re-execution" % phase)

        self.rollback_log.append(
            {
                "checkpoint_id": checkpoint_id,
                "workflow_name": checkpoint.workflow_name,
                "timestamp": time.time(),
                "phases_rolled_back": phases_to_rollback,
                "resources_cleaned": cleaned_resources,
                "actions": actions_taken,
            }
        )

        return RollbackResult(
            success=True,
            checkpoint_id=checkpoint_id,
            rolled_back_phases=phases_to_rollback,
            cleaned_resources=cleaned_resources,
            actions_taken=actions_taken,
        )

    def get_restored_context(self, checkpoint_id: str) -> Optional[Dict]:
        """Get the context snapshot from a checkpoint."""
        if checkpoint_id in self.checkpoints:
            return copy.deepcopy(self.checkpoints[checkpoint_id].context_snapshot)
        return None

    def cleanup_resources(self, workflow_name: str) -> List[str]:
        """Clean up all resources for a workflow."""
        cleaned = []
        if workflow_name in self.active_resources:
            cleaned = list(self.active_resources[workflow_name])
            self.active_resources[workflow_name] = []

        self.rollback_log.append(
            {
                "type": "cleanup",
                "workflow_name": workflow_name,
                "resources_cleaned": cleaned,
                "timestamp": time.time(),
            }
        )

        return cleaned

    def get_checkpoint_history(self, workflow_name: str = None) -> List[Dict[str, Any]]:
        """Get checkpoint history, optionally filtered by workflow."""
        history = []
        for cp in sorted(self.checkpoints.values(), key=lambda x: x.timestamp):
            if workflow_name and cp.workflow_name != workflow_name:
                continue
            history.append(
                {
                    "checkpoint_id": cp.checkpoint_id,
                    "workflow_name": cp.workflow_name,
                    "phase_name": cp.phase_name,
                    "timestamp": datetime.fromtimestamp(cp.timestamp).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    "has_context": bool(cp.context_snapshot),
                    "resource_count": len(
                        cp.resource_state.get("active_resources", [])
                    ),
                }
            )
        return history

    def get_rollback_log(self) -> List[Dict[str, Any]]:
        """Get the rollback action log."""
        return list(self.rollback_log)

    def prune_old_checkpoints(
        self, max_age_seconds: float = 3600, max_count: int = 100
    ):
        """Prune old checkpoints to manage memory."""
        current_time = time.time()
        to_remove = []

        for cid, cp in self.checkpoints.items():
            if current_time - cp.timestamp > max_age_seconds:
                to_remove.append(cid)

        if len(self.checkpoints) - len(to_remove) > max_count:
            sorted_checkpoints = sorted(
                self.checkpoints.items(), key=lambda x: x[1].timestamp
            )
            excess = len(self.checkpoints) - len(to_remove) - max_count
            for cid, cp in sorted_checkpoints[:excess]:
                if cid not in to_remove:
                    to_remove.append(cid)

        for cid in to_remove:
            del self.checkpoints[cid]

        return len(to_remove)
