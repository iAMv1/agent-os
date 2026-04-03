"""Tests for the CapabilityRegistry."""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "engines"))

from capability_registry import CapabilityRegistry, CapabilityType
from task_classifier import SDLCStage


class TestCapabilityRegistry:
    def setup_method(self):
        self.registry = CapabilityRegistry()

    def test_registry_has_capabilities(self):
        assert len(self.registry.capabilities) > 0

    def test_get_by_name_returns_capability(self):
        cap = self.registry.get_by_name("Bash")
        assert cap is not None
        assert cap.name == "Bash"

    def test_get_by_name_returns_none_for_unknown(self):
        cap = self.registry.get_by_name("NonExistentCapability")
        assert cap is None

    def test_get_by_type_returns_capabilities(self):
        tools = self.registry.get_by_type(CapabilityType.TOOL)
        assert len(tools) > 0
        for cap in tools:
            assert cap.cap_type == CapabilityType.TOOL

    def test_get_parallel_safe_returns_capabilities(self):
        parallel_caps = self.registry.get_parallel_safe(SDLCStage.IMPLEMENTATION)
        assert isinstance(parallel_caps, list)

    def test_summary_returns_string(self):
        summary = self.registry.summary()
        assert isinstance(summary, str)
        assert len(summary) > 0

    def test_all_capability_types_present(self):
        types = set(cap.cap_type for cap in self.registry.capabilities.values())
        expected_types = {
            CapabilityType.TOOL,
            CapabilityType.AGENT,
            CapabilityType.SERVICE,
            CapabilityType.HOOK,
            CapabilityType.COMMAND,
        }
        assert expected_types.issubset(types)

    def test_capability_has_name_and_description(self):
        for cap in self.registry.capabilities.values():
            assert cap.name is not None
            assert len(cap.name) > 0
            assert cap.description is not None
            assert len(cap.description) > 0

    def test_get_capabilities_have_stages(self):
        caps = list(self.registry.capabilities.values())
        for cap in caps[:5]:
            assert len(cap.stages) > 0

    def test_get_available_returns_capabilities(self):
        available = self.registry.get_available()
        assert len(available) > 0

    def test_to_dict_produces_valid_output(self):
        d = self.registry.to_dict()
        assert isinstance(d, dict)
        assert len(d) > 0
        assert "Bash" in d
