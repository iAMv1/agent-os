"""Tests for the WorkflowComposer."""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "engines"))

from task_classifier import TaskClassifier, TaskComplexity, Domain
from capability_registry import CapabilityRegistry
from workflow_composer import WorkflowComposer


class TestWorkflowComposer:
    def setup_method(self):
        self.classifier = TaskClassifier()
        self.registry = CapabilityRegistry()
        self.composer = WorkflowComposer(self.registry)

    def test_compose_implementation_workflow(self):
        classification = self.classifier.classify("Build a REST API")
        workflow = self.composer.compose(classification)
        assert workflow is not None
        assert len(workflow.phases) > 0
        assert len(workflow.required_capabilities) > 0

    def test_compose_bug_fix_workflow(self):
        classification = self.classifier.classify("Fix the login bug")
        workflow = self.composer.compose(classification)
        assert workflow is not None
        assert len(workflow.phases) > 0

    def test_compose_deployment_workflow(self):
        classification = self.classifier.classify("Deploy to production")
        workflow = self.composer.compose(classification)
        assert workflow is not None
        assert "deployment" in [s.lower() for s in workflow.stages]

    def test_compose_testing_workflow(self):
        classification = self.classifier.classify("Write unit tests")
        workflow = self.composer.compose(classification)
        assert workflow is not None
        assert len(workflow.phases) > 0

    def test_get_workflow_plan_returns_string(self):
        classification = self.classifier.classify("Build a feature")
        workflow = self.composer.compose(classification)
        plan = self.composer.get_workflow_plan(workflow)
        assert isinstance(plan, str)
        assert len(plan) > 0

    def test_workflow_has_name_and_description(self):
        classification = self.classifier.classify("Build something")
        workflow = self.composer.compose(classification)
        assert len(workflow.name) > 0
        assert len(workflow.description) > 0

    def test_workflow_phases_have_capabilities(self):
        classification = self.classifier.classify("Build a REST API")
        workflow = self.composer.compose(classification)
        for phase in workflow.phases:
            assert len(phase.capabilities) > 0
