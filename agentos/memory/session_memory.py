"""
AgentOS Memory System

Threshold-based memory extraction (NOT interval-based).
Memory is only updated when ALL conditions are met:
- Token count >= 10,000 (minimum to start tracking)
- Context growth >= 5,000 tokens since last update
- Tool calls >= 3 since last update OR no tool calls in last turn

Memory preserves key context across compactions:
- Task specifications
- File lists being worked on
- Workflow state
- Errors and corrections
- Learnings and insights
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List


class MemoryConfig:
    """Configuration for memory extraction thresholds."""

    def __init__(
        self,
        minimum_message_tokens_to_init: int = 10000,
        minimum_tokens_between_update: int = 5000,
        tool_calls_between_updates: int = 3,
        extraction_stale_threshold_ms: int = 60000,
        extraction_wait_timeout_ms: int = 15000,
    ):
        self.minimum_message_tokens_to_init = minimum_message_tokens_to_init
        self.minimum_tokens_between_update = minimum_tokens_between_update
        self.tool_calls_between_updates = tool_calls_between_updates
        self.extraction_stale_threshold_ms = extraction_stale_threshold_ms
        self.extraction_wait_timeout_ms = extraction_wait_timeout_ms


class SessionMemory:
    """Manages session memory with threshold-based extraction."""

    def __init__(
        self, base_dir: Optional[str] = None, config: Optional[MemoryConfig] = None
    ):
        if base_dir is None:
            base_dir = os.path.join(os.getcwd(), ".agent-os", "memory")
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.config = config or MemoryConfig()
        self.memory_file = self.base_dir / "session-memory.md"
        self.last_token_count: int = 0
        self.last_tool_call_count: int = 0
        self.extraction_in_progress: bool = False
        self.extraction_started_at: Optional[float] = None

    def should_extract_memory(
        self,
        current_token_count: int,
        current_tool_call_count: int,
        has_tool_calls_last_turn: bool,
    ) -> bool:
        """Check if memory extraction should be triggered."""
        # Check minimum token threshold
        if current_token_count < self.config.minimum_message_tokens_to_init:
            return False

        # Check context growth threshold
        token_growth = current_token_count - self.last_token_count
        if token_growth < self.config.minimum_tokens_between_update:
            return False

        # Check tool call threshold
        tool_call_growth = current_tool_call_count - self.last_tool_call_count
        if tool_call_growth >= self.config.tool_calls_between_updates:
            return True

        # Or no tool calls in last turn
        if not has_tool_calls_last_turn:
            return True

        return False

    def read_memory(self) -> str:
        """Read current session memory."""
        if self.memory_file.exists():
            return self.memory_file.read_text(encoding="utf-8")
        return ""

    def write_memory(self, content: str) -> None:
        """Write updated session memory."""
        self.memory_file.write_text(content, encoding="utf-8")

    def update_memory(self, new_content: str) -> None:
        """Update memory with new content after extraction."""
        self.last_token_count = self.last_token_count  # Will be updated by caller
        self.last_tool_call_count = (
            self.last_tool_call_count
        )  # Will be updated by caller
        self.write_memory(new_content)
        self.extraction_in_progress = False
        self.extraction_started_at = None

    def start_extraction(self) -> None:
        """Mark extraction as started."""
        self.extraction_in_progress = True
        self.extraction_started_at = datetime.now(timezone.utc).timestamp() * 1000

    def is_extraction_stale(self) -> bool:
        """Check if extraction is stale (>1min)."""
        if self.extraction_started_at is None:
            return False
        age = datetime.now(timezone.utc).timestamp() * 1000 - self.extraction_started_at
        return age > self.config.extraction_stale_threshold_ms

    def get_memory_template(self) -> str:
        """Get the memory file template."""
        return """# Session Memory

## Session Title
[Brief description]

## Current State
[What's happening right now]

## Task Specification
[What we're working on]

## Files and Functions
[Key files being modified]

## Workflow
[Current workflow phase]

## Errors & Corrections
[Mistakes made and fixes]

## Learnings
[Insights and discoveries]

## Key Results
[What's been accomplished]

## Worklog
[Chronological record of work done]
"""

    def initialize_memory(self) -> None:
        """Initialize memory file if it doesn't exist."""
        if not self.memory_file.exists():
            self.write_memory(self.get_memory_template())

    def get_memory_summary(self) -> Dict[str, Any]:
        """Get a summary of the memory state."""
        content = self.read_memory()
        return {
            "memory_file": str(self.memory_file),
            "exists": self.memory_file.exists(),
            "size_bytes": len(content.encode("utf-8")) if content else 0,
            "last_token_count": self.last_token_count,
            "last_tool_call_count": self.last_tool_call_count,
            "extraction_in_progress": self.extraction_in_progress,
        }
