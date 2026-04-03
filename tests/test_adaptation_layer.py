"""Tests for the AdaptationLayer."""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "engines"))

from adaptation_layer import AdaptationLayer, AdaptationType, Adaptation


class TestAdaptationLayer:
    def setup_method(self):
        self.adaptation = AdaptationLayer()

    def test_find_substitute_returns_list(self):
        result = self.adaptation._find_substitute("LSP", {})
        assert result is not None
        assert isinstance(result, list)
        assert "Grep" in result

    def test_find_substitute_returns_none_for_unknown(self):
        result = self.adaptation._find_substitute("NonExistentTool", {})
        assert result is None

    def test_adaptation_types_exist(self):
        assert hasattr(AdaptationType, "CAPABILITY_SUBSTITUTION")
        assert hasattr(AdaptationType, "PHASE_MERGE")
        assert hasattr(AdaptationType, "PHASE_SPLIT")
        assert hasattr(AdaptationType, "TIMEOUT_ADJUSTMENT")
        assert hasattr(AdaptationType, "WORKFLOW_SWITCH")
        assert hasattr(AdaptationType, "CONTEXT_ENRICHMENT")

    def test_adapt_phase_with_errors_triggers_substitution(self):
        outputs = [
            {"capability": "LSP", "status": "error", "error": "failed"},
            {"capability": "Bash", "status": "success", "output": "done"},
        ]
        result = self.adaptation.adapt_phase(None, outputs, {})
        assert result is not None
        assert len(result["adaptations"]) > 0

    def test_adapt_phase_with_all_success_returns_none(self):
        outputs = [
            {"capability": "Bash", "status": "success", "output": "done"},
        ]
        result = self.adaptation.adapt_phase(None, outputs, {})
        assert result is not None
        assert len(result["adaptations"]) == 0

    def test_adapt_phase_with_high_error_rate_triggers_parallelism_change(self):
        outputs = [
            {"capability": "Cap1", "status": "error", "error": "failed"},
            {"capability": "Cap2", "status": "error", "error": "failed"},
            {"capability": "Cap3", "status": "success", "output": "ok"},
        ]
        result = self.adaptation.adapt_phase(None, outputs, {})
        assert result is not None
        assert "reduce_parallelism" in result["context_updates"]

    def test_adapt_phase_enriches_context_with_successes(self):
        outputs = [
            {"capability": "Bash", "status": "success", "output": "command output"},
        ]
        result = self.adaptation.adapt_phase(None, outputs, {})
        assert result is not None
        assert "bash_output" in result["context_updates"]

    def test_failure_counts_are_tracked(self):
        outputs = [{"capability": "LSP", "status": "error", "error": "failed"}]
        self.adaptation.adapt_phase(None, outputs, {})
        assert self.adaptation.failure_counts.get("LSP", 0) > 0

    def test_success_counts_are_tracked(self):
        outputs = [{"capability": "Bash", "status": "success", "output": "ok"}]
        self.adaptation.adapt_phase(None, outputs, {})
        assert self.adaptation.success_counts.get("Bash", 0) > 0

    def test_get_adaptation_report_returns_string(self):
        report = self.adaptation.get_adaptation_report()
        assert isinstance(report, str)

    def test_record_adaptation(self):
        adaptation = Adaptation(
            adaptation_type=AdaptationType.CAPABILITY_SUBSTITUTION,
            description="Test adaptation",
            before="LSP",
            after="Grep",
            reason="Test",
            timestamp=0.0,
        )
        self.adaptation.record_adaptation(adaptation)
        assert len(self.adaptation.adaptations) == 1
