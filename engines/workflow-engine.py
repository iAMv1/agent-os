#!/usr/bin/env python3
"""
Adaptive Workflow Engine - Main Orchestrator

Analyzes any software development task and dynamically composes
the optimal workflow using all available capabilities from the
AI Coding Agent runtime system.

Usage:
    python main.py "Build a REST API for a todo app"
    python main.py "Fix the login bug" --mode thorough
    python main.py "Design the architecture for a microservice" --depth deep
"""

import sys
import os
import json
import argparse
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from classifier.task_classifier import TaskClassifier
from registry.capability_registry import CapabilityRegistry
from engine.workflow_composer import WorkflowComposer
from engine.execution_engine import ExecutionEngine
from engine.adaptation_layer import AdaptationLayer


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
    args = parser.parse_args()

    print("=" * 70)
    print("ADAPTIVE WORKFLOW ENGINE")
    print("=" * 70)
    print("Task: %s" % args.task)
    print("Mode: %s | Depth: %s" % (args.mode, args.depth))
    print("Timestamp: %s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 70)

    # Step 1: Initialize components
    print("\n[1/5] Initializing components...")
    classifier = TaskClassifier()
    registry = CapabilityRegistry()
    adaptation_layer = AdaptationLayer()
    composer = WorkflowComposer(registry)
    engine = ExecutionEngine(registry, adaptation_layer)

    print("  - Task classifier: ready")
    print(
        "  - Capability registry: %d capabilities loaded" % len(registry.capabilities)
    )
    print("  - Workflow composer: ready")
    print("  - Execution engine: ready")
    print("  - Adaptation layer: ready")

    # Step 2: Classify task
    print("\n[2/5] Classifying task...")
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
    print("  - Keywords: %s" % ", ".join(classification.keywords))
    print("  - Confidence: %.0f%%" % (classification.confidence * 100))

    # Step 3: Compose workflow
    print("\n[3/5] Composing workflow...")
    workflow = composer.compose(classification)
    workflow_plan = composer.get_workflow_plan(workflow)

    print("  - Workflow: %s" % workflow.name)
    print("  - Phases: %d" % len(workflow.phases))
    print("  - Required capabilities: %d" % len(workflow.required_capabilities))
    print("  - Optional capabilities: %d" % len(workflow.optional_capabilities))
    print("  - Estimated duration: %s" % workflow.estimated_duration)
    print("  - Estimated cost: %s" % workflow.estimated_cost)

    # Step 4: Execute workflow
    print("\n[4/5] Executing workflow...")
    context = {
        "task_description": args.task,
        "classification": classification_dict,
        "mode": args.mode,
        "depth": args.depth,
    }

    result = engine.execute(workflow, context)

    print("  - Status: %s" % result.status.value)
    print(
        "  - Phases completed: %d/%d"
        % (
            len(
                [
                    p
                    for p in result.phase_results
                    if p.status.value in ["completed", "adapted"]
                ]
            ),
            len(result.phase_results),
        )
    )
    print("  - Adaptations made: %d" % len(result.adaptations_made))
    print("  - Total duration: %.2fs" % result.total_duration_seconds)

    # Step 5: Generate output
    print("\n[5/5] Generating output...")

    if args.output == "json":
        output = {
            "task": args.task,
            "classification": classification_dict,
            "workflow": {
                "name": workflow.name,
                "description": workflow.description,
                "stages": workflow.stages,
                "estimated_duration": workflow.estimated_duration,
                "estimated_cost": workflow.estimated_cost,
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
                "required_capabilities": workflow.required_capabilities,
                "optional_capabilities": workflow.optional_capabilities,
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
        }
        print(json.dumps(output, indent=2))
    else:
        print("\n" + "=" * 70)
        print("WORKFLOW PLAN")
        print("=" * 70)
        print(workflow_plan)

        print("\n" + "=" * 70)
        print("EXECUTION INSTRUCTIONS")
        print("=" * 70)

        for i, phase in enumerate(workflow.phases, 1):
            print("\n--- Phase %d: %s ---" % (i, phase.name))
            print("Description: %s" % phase.description)
            print(
                "Parallel: %s | Timeout: %ds | Retries: %d"
                % (phase.parallel, phase.timeout_seconds, phase.retry_count)
            )
            print("\nCapabilities to use:")
            for cap_name in phase.capabilities:
                cap = registry.get_by_name(cap_name)
                if cap:
                    print(
                        "  - %s (%s): %s"
                        % (cap.name, cap.cap_type.value, cap.description)
                    )

        print("\n" + "=" * 70)
        print("EXECUTION RESULT")
        print("=" * 70)
        print(result.final_output)

        print("\n" + "=" * 70)
        print("CAPABILITY REGISTRY SUMMARY")
        print("=" * 70)
        print(registry.summary())

    print("\n" + "=" * 70)
    print("DONE")
    print("=" * 70)


if __name__ == "__main__":
    main()
