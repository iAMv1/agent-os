#!/usr/bin/env python3
"""
Adaptive Workflow Engine - Main Orchestrator

Analyzes any software development task and dynamically composes
the optimal workflow using all available capabilities from the
AI Coding Agent runtime system.

Usage:
    python workflow-engine.py "Build a REST API for a todo app"
    python workflow-engine.py "Fix the login bug" --mode thorough
    python workflow-engine.py "Design the architecture for a microservice" --depth deep
    python workflow-engine.py "Build a web app" --dynamic --dag
"""

import sys
import os
import json
import argparse
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from task_classifier import TaskClassifier
from capability_registry import CapabilityRegistry
from workflow_composer import WorkflowComposer
from execution_engine import ExecutionEngine
from adaptation_layer import AdaptationLayer
from workflow_validator import WorkflowValidator
from workflow_metrics import WorkflowMetricsCollector
from workflow_rollback import RollbackManager


def main():
    parser = argparse.ArgumentParser(description="Adaptive Workflow Engine")
    parser.add_argument("task", help="Task description")
    parser.add_argument(
        "--mode", choices=["fast", "balanced", "thorough"], default="balanced"
    )
    parser.add_argument(
        "--depth", choices=["shallow", "standard", "deep"], default="standard"
    )
    parser.add_argument("--output", choices=["json", "text"], default="text")
    parser.add_argument(
        "--dynamic", action="store_true", help="Use dynamic workflow generation"
    )
    parser.add_argument(
        "--dag", action="store_true", help="Use DAG-based parallel execution"
    )
    parser.add_argument(
        "--validate-only", action="store_true", help="Only validate, don't execute"
    )
    parser.add_argument(
        "--metrics", action="store_true", help="Show metrics after execution"
    )
    args = parser.parse_args()

    print("=" * 70)
    print("ADAPTIVE WORKFLOW ENGINE v2.0")
    print("=" * 70)
    print("Task: %s" % args.task)
    print("Mode: %s | Depth: %s" % (args.mode, args.depth))
    print("Dynamic: %s | DAG: %s" % (args.dynamic, args.dag))
    print("Timestamp: %s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 70)

    print("\n[1/6] Initializing components...")
    classifier = TaskClassifier()
    registry = CapabilityRegistry()
    adaptation_layer = AdaptationLayer()
    composer = WorkflowComposer(registry)
    engine = ExecutionEngine(registry, adaptation_layer)
    validator = WorkflowValidator(registry)
    metrics = WorkflowMetricsCollector()
    rollback_mgr = RollbackManager()

    print("  - Task classifier: ready")
    print(
        "  - Capability registry: %d capabilities loaded" % len(registry.capabilities)
    )
    print("  - Workflow composer: ready (templates + dynamic)")
    print("  - Execution engine: ready (parallel + DAG + checkpoints)")
    print("  - Adaptation layer: ready")
    print("  - Workflow validator: ready")
    print("  - Metrics collector: ready")
    print("  - Rollback manager: ready")

    print("\n[2/6] Classifying task...")
    classification = classifier.classify(args.task)
    classification_dict = classifier.to_dict(classification)

    print("  - Task type: %s" % classification.task_type)
    print(
        "  - SDLC stages: %s" % ", ".join([s.value for s in classification.sdlc_stages])
    )
    print("  - Complexity: %s" % classification.complexity.value)
    print("  - Domain: %s" % classification.domain.value)
    print("  - Estimated files: %d" % classification.estimated_files)
    print("  - Requires user input: %s" % classification.requires_user_input)
    print("  - Confidence: %.0f%%" % (classification.confidence * 100))

    print("\n[3/6] Composing workflow...")
    if args.dynamic:
        workflow = composer.compose_dynamic(classification, args.task)
        print("  - Workflow: %s [DYNAMIC]" % workflow.name)
        print("  - Phases: %d" % len(workflow.phases))
        print("  - DAG nodes: %d" % len(workflow.dag.nodes))
        print("  - DAG edges: %d" % len(workflow.dag.edges))
        if workflow.critical_path:
            print("  - Critical path: %s" % " -> ".join(workflow.critical_path))
        print("  - Estimated duration: %.0fs" % workflow.estimated_duration_seconds)
    else:
        workflow = composer.compose(classification)
        print("  - Workflow: %s [TEMPLATE]" % workflow.name)
        print("  - Phases: %d" % len(workflow.phases))
        print("  - Required capabilities: %d" % len(workflow.required_capabilities))
        print("  - Estimated duration: %s" % workflow.estimated_duration)

    print("\n[3.5/6] Validating workflow...")
    validation = (
        validator.validate(workflow)
        if args.dynamic
        else validator.validate_from_template(workflow)
    )
    print("  - Valid: %s" % validation.is_valid)
    if validation.issues:
        for issue in validation.issues:
            print("  - ISSUE: %s" % issue)
    if validation.warnings:
        for warning in validation.warnings[:5]:
            print("  - WARNING: %s" % warning)
    if validation.resource_estimate:
        print("  - Resource estimate:")
        for key, val in validation.resource_estimate.items():
            print("    - %s: %s" % (key, val))

    if args.validate_only:
        print("\nValidation complete. Use --execute to run the workflow.")
        return

    print("\n[4/6] Preparing rollback checkpoints...")
    context = {
        "task_description": args.task,
        "classification": classification_dict,
        "mode": args.mode,
        "depth": args.depth,
    }
    checkpoint_id = rollback_mgr.save_state(workflow, context)
    print("  - Checkpoint saved: %s" % checkpoint_id)

    print("\n[5/6] Executing workflow...")
    if args.dag and args.dynamic:
        result = engine.execute_with_dag(workflow, context)
    else:
        result = engine.execute(workflow, context)

    print("  - Status: %s" % result.status.value)
    completed = len(
        [p for p in result.phase_results if p.status.value in ["completed", "adapted"]]
    )
    print("  - Phases completed: %d/%d" % (completed, len(result.phase_results)))
    print("  - Adaptations made: %d" % len(result.adaptations_made))
    print("  - Total duration: %.2fs" % result.total_duration_seconds)
    print("  - Checkpoints: %d" % len(result.checkpoints))
    print("  - Rollback available: %s" % result.rollback_available)

    print("\n[6/6] Generating output...")

    if args.output == "json":
        output = {
            "task": args.task,
            "classification": classification_dict,
            "validation": {
                "is_valid": validation.is_valid,
                "issues": validation.issues,
                "warnings": validation.warnings,
                "resource_estimate": validation.resource_estimate,
            },
            "workflow": {
                "name": workflow.name,
                "description": workflow.description,
                "phases": [
                    {
                        "name": p.name,
                        "description": p.description,
                        "capabilities": p.capabilities,
                        "parallel": p.parallel,
                        "timeout_seconds": p.timeout_seconds,
                        "retry_count": p.retry_count,
                        "on_failure": p.on_failure,
                    }
                    for p in workflow.phases
                ],
            },
            "execution": {
                "status": result.status.value,
                "total_duration_seconds": result.total_duration_seconds,
                "adaptations_made": result.adaptations_made,
                "phase_results": [
                    {
                        "phase": pr.phase_name,
                        "status": pr.status.value,
                        "duration_seconds": pr.duration_seconds,
                        "capabilities_used": pr.capabilities_used,
                        "error": pr.error,
                    }
                    for pr in result.phase_results
                ],
            },
            "checkpoints": result.checkpoints,
            "rollback_available": result.rollback_available,
        }
        print(json.dumps(output, indent=2))
    else:
        print("\n" + "=" * 70)
        print("WORKFLOW PLAN")
        print("=" * 70)
        print(composer.get_workflow_plan(workflow))

        print("\n" + "=" * 70)
        print("EXECUTION RESULT")
        print("=" * 70)
        print(result.final_output)

    if args.metrics:
        print("\n" + "=" * 70)
        print("METRICS REPORT")
        print("=" * 70)
        print(composer.get_metrics_report())

        analytics = engine.get_analytics()
        if "execution_summary" in analytics:
            es = analytics["execution_summary"]
            print("\nExecution Analytics:")
            print("  Total executions: %d" % es["total_executions"])
            print("  Success rate: %.1f%%" % (es["success_rate"] * 100))
            print("  Avg duration: %.1fs" % es["avg_duration_seconds"])

    print("\n" + "=" * 70)
    print("CAPABILITY REGISTRY SUMMARY")
    print("=" * 70)
    print(registry.summary())

    print("\n" + "=" * 70)
    print("DONE")
    print("=" * 70)


if __name__ == "__main__":
    main()
