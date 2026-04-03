"""Tests for the TaskClassifier."""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "engines"))

from task_classifier import TaskClassifier, TaskComplexity, Domain


class TestTaskClassifier:
    def setup_method(self):
        self.classifier = TaskClassifier()

    def test_classify_implementation_task(self):
        result = self.classifier.classify("Build a REST API for a todo app")
        assert result.task_type == "implementation"
        assert result.complexity == TaskComplexity.MEDIUM
        assert result.domain == Domain.API

    def test_classify_deployment_task(self):
        result = self.classifier.classify("Deploy the app to production with CI/CD pipeline")
        assert "deployment" in result.task_type

    def test_classify_maintenance_task(self):
        result = self.classifier.classify("Update dependencies and monitor performance")
        assert "maintenance" in result.task_type

    def test_classify_frontend_domain(self):
        result = self.classifier.classify("Build a React component for the dashboard")
        assert result.domain == Domain.FRONTEND

    def test_classify_devops_domain(self):
        result = self.classifier.classify("Set up Docker containers and Kubernetes deployment")
        assert result.domain == Domain.DEVOPS

    def test_classify_security_domain(self):
        result = self.classifier.classify("Fix authentication vulnerability in the API")
        assert result.domain == Domain.SECURITY

    def test_classify_mobile_domain(self):
        result = self.classifier.classify("Build an iOS app with Swift")
        assert result.domain == Domain.MOBILE

    def test_classify_data_ml_domain(self):
        result = self.classifier.classify("Train a machine learning model for predictions")
        assert result.domain == Domain.DATA_ML

    def test_to_dict_produces_valid_output(self):
        result = self.classifier.classify("Build a feature")
        d = self.classifier.to_dict(result)
        assert isinstance(d, dict)
        assert "task_type" in d
        assert "complexity" in d
        assert "domain" in d
        assert "confidence" in d

    def test_empty_task_description(self):
        result = self.classifier.classify("")
        assert result is not None
        assert result.task_type == "implementation"

    def test_confidence_is_between_0_and_1(self):
        tasks = [
            "Build a REST API",
            "Fix a bug",
            "Write tests",
            "Deploy to production",
            "Refactor the codebase",
        ]
        for task in tasks:
            result = self.classifier.classify(task)
            assert 0.0 <= result.confidence <= 1.0
