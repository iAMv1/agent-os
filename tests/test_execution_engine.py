"""Tests for the ExecutionEngine."""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "engines"))

from task_classifier import TaskClassifier
from capability_registry import CapabilityRegistry
from workflow_composer import WorkflowComposer
from execution_engine import ExecutionEngine, ExecutionStatus
from adaptation_layer import AdaptationLayer


class TestExecutionEngine:
    def setup_method(self):
        self.classifier = TaskClassifier()
        self.registry = CapabilityRegistry()
        self.adaptation = AdaptationLayer()
        self.composer = WorkflowComposer(self.registry)
        self.engine = ExecutionEngine(self.registry, self.adaptation)

    def test_execute_simple_workflow(self):
        classification = self.classifier.classify("Build a REST API")
        workflow = self.composer.compose(classification)
        context = {
            "task_description": "Build a REST API",
            "classification": self.classifier.to_dict(classification),
            "mode": "balanced",
            "depth": "standard",
        }
        result = self.engine.execute(workflow, context)
        assert result is not None
        assert result.status == ExecutionStatus.COMPLETED
        assert len(result.phase_results) > 0

    def test_execute_produces_phase_results(self):
        classification = self.classifier.classify("Fix a bug")
        workflow = self.composer.compose(classification)
        context = {
            "task_description": "Fix a bug",
            "classification": self.classifier.to_dict(classification),
            "mode": "fast",
            "depth": "shallow",
        }
        result = self.engine.execute(workflow, context)
        for phase_result in result.phase_results:
            assert phase_result.phase_name is not None
            assert phase_result.status is not None
            assert phase_result.output is not None

    def test_execute_with_empty_context(self):
        classification = self.classifier.classify("Do something")
        workflow = self.composer.compose(classification)
        result = self.engine.execute(workflow, {})
        assert result is not None
        assert result.status == ExecutionStatus.COMPLETED

    def test_final_output_is_non_empty_string(self):
        classification = self.classifier.classify("Build a feature")
        workflow = self.composer.compose(classification)
        context = {
            "task_description": "Build a feature",
            "classification": self.classifier.to_dict(classification),
        }
        result = self.engine.execute(workflow, context)
        assert isinstance(result.final_output, str)
        assert len(result.final_output) > 0
