"""
Layer 6: Memory - Store learned knowledge.

Persist knowledge gained from handling unknown tasks so
future similar tasks can be handled more efficiently.
"""

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import json
import os
from datetime import datetime, timezone


class MemoryType(Enum):
    TASK_PATTERN = "task_pattern"
    SOLUTION = "solution"
    CAPABILITY = "capability"
    WORKFLOW = "workflow"
    ERROR = "error"


@dataclass
class MemoryEntry:
    """A single memory entry."""

    entry_id: str
    memory_type: MemoryType
    task_pattern: str
    solution: str
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[str] = None
    access_count: int = 0
    last_accessed: Optional[str] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc).isoformat()


@dataclass
class MemoryLayerResult:
    """Result from memory layer."""

    success: bool
    retrieved_memories: List[MemoryEntry] = field(default_factory=list)
    stored_entry: Optional[MemoryEntry] = None
    knowledge_base_size: int = 0
    error: Optional[str] = None


class MemoryLayer:
    """
    Layer 6: Store and retrieve learned knowledge.

    Persists knowledge from handling unknown tasks and retrieves
    relevant knowledge for future similar tasks.
    """

    def __init__(
        self,
        storage_path: Optional[str] = None,
        max_entries: int = 1000,
    ):
        self.storage_path = storage_path
        self.max_entries = max_entries
        self._knowledge_base: Dict[str, MemoryEntry] = {}
        self._pattern_index: Dict[str, List[str]] = {}
        self._load_from_storage()

    def _load_from_storage(self) -> None:
        """Load knowledge base from storage."""
        if self.storage_path and os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r") as f:
                    data = json.load(f)
                    for entry_data in data.get("entries", []):
                        entry = MemoryEntry(**entry_data)
                        self._knowledge_base[entry.entry_id] = entry
                        self._index_entry(entry)
            except (json.JSONDecodeError, IOError, TypeError):
                self._knowledge_base = {}

    def _save_to_storage(self) -> None:
        """Save knowledge base to storage."""
        if not self.storage_path:
            return

        data = {
            "entries": [
                self._entry_to_dict(entry) for entry in self._knowledge_base.values()
            ],
            "metadata": {
                "total_entries": len(self._knowledge_base),
                "last_updated": datetime.now(timezone.utc).isoformat(),
            },
        }

        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, "w") as f:
            json.dump(data, f, indent=2)

    def _entry_to_dict(self, entry: MemoryEntry) -> Dict[str, Any]:
        """Convert MemoryEntry to dict for serialization."""
        return {
            "entry_id": entry.entry_id,
            "memory_type": entry.memory_type.value,
            "task_pattern": entry.task_pattern,
            "solution": entry.solution,
            "confidence": entry.confidence,
            "metadata": entry.metadata,
            "created_at": entry.created_at,
            "access_count": entry.access_count,
            "last_accessed": entry.last_accessed,
        }

    def can_handle(self, task: str) -> bool:
        """Check if we have relevant knowledge for this task."""
        return self.get_confidence(task) > 0.0

    def get_confidence(self, task: str) -> float:
        """Get confidence based on matching knowledge."""
        matches = self._find_matches(task)
        if not matches:
            return 0.0
        return max(m.confidence for m in matches)

    def handle(
        self, task: str, store_result: Optional[Dict[str, Any]] = None
    ) -> MemoryLayerResult:
        """
        Handle task by retrieving relevant knowledge or storing new knowledge.

        If store_result is provided, stores it as new knowledge.
        Otherwise, retrieves matching knowledge for the task.
        """
        if store_result is not None:
            return self._store_knowledge(task, store_result)
        else:
            return self._retrieve_knowledge(task)

    def _retrieve_knowledge(self, task: str) -> MemoryLayerResult:
        """Retrieve relevant knowledge for the task."""
        matches = self._find_matches(task)

        if not matches:
            return MemoryLayerResult(
                success=False,
                knowledge_base_size=len(self._knowledge_base),
                error="No matching knowledge found",
            )

        for entry in matches:
            entry.access_count += 1
            entry.last_accessed = datetime.now(timezone.utc).isoformat()

        matches.sort(
            key=lambda e: e.confidence * 0.7 + min(e.access_count, 10) * 0.03,
            reverse=True,
        )

        return MemoryLayerResult(
            success=True,
            retrieved_memories=matches,
            knowledge_base_size=len(self._knowledge_base),
        )

    def _store_knowledge(self, task: str, result: Dict[str, Any]) -> MemoryLayerResult:
        """Store new knowledge from handling a task."""
        entry_id = self._generate_entry_id(task)
        memory_type = self._classify_memory_type(task, result)

        entry = MemoryEntry(
            entry_id=entry_id,
            memory_type=memory_type,
            task_pattern=task,
            solution=json.dumps(result, default=str)[:5000],
            confidence=result.get("confidence", 0.5),
            metadata=result.get("metadata", {}),
        )

        if len(self._knowledge_base) >= self.max_entries:
            self._evict_oldest()

        self._knowledge_base[entry_id] = entry
        self._index_entry(entry)
        self._save_to_storage()

        return MemoryLayerResult(
            success=True,
            stored_entry=entry,
            knowledge_base_size=len(self._knowledge_base),
        )

    def _find_matches(self, task: str) -> List[MemoryEntry]:
        """Find matching knowledge entries for the task."""
        task_lower = task.lower()
        task_words = set(task_lower.split())
        matches = []

        for entry_id, entry in self._knowledge_base.items():
            pattern_lower = entry.task_pattern.lower()
            pattern_words = set(pattern_lower.split())

            overlap = len(task_words & pattern_words)
            if overlap > 0:
                similarity = overlap / max(len(task_words | pattern_words), 1)
                if similarity > 0.1:
                    matches.append(entry)

        matches.sort(key=lambda e: e.confidence, reverse=True)
        return matches[:10]

    def _index_entry(self, entry: MemoryEntry) -> None:
        """Index an entry for faster lookup."""
        words = entry.task_pattern.lower().split()
        for word in words:
            if word not in self._pattern_index:
                self._pattern_index[word] = []
            if entry.entry_id not in self._pattern_index[word]:
                self._pattern_index[word].append(entry.entry_id)

    def _generate_entry_id(self, task: str) -> str:
        """Generate a unique entry ID."""
        import hashlib

        timestamp = datetime.now(timezone.utc).isoformat()
        content = f"{task}:{timestamp}"
        return hashlib.md5(content.encode()).hexdigest()[:12]

    def _classify_memory_type(self, task: str, result: Dict[str, Any]) -> MemoryType:
        """Classify the type of memory being stored."""
        if "error" in result:
            return MemoryType.ERROR
        if "solution" in result or "execution_plan" in result:
            return MemoryType.SOLUTION
        if "workflow" in result:
            return MemoryType.WORKFLOW
        if "capability" in result:
            return MemoryType.CAPABILITY
        return MemoryType.TASK_PATTERN

    def _evict_oldest(self) -> None:
        """Evict the least recently accessed entry."""
        if not self._knowledge_base:
            return

        oldest_id = min(
            self._knowledge_base.keys(),
            key=lambda k: (
                self._knowledge_base[k].last_accessed
                or self._knowledge_base[k].created_at
            ),
        )
        entry = self._knowledge_base.pop(oldest_id)
        self._deindex_entry(entry)

    def _deindex_entry(self, entry: MemoryEntry) -> None:
        """Remove an entry from the index."""
        words = entry.task_pattern.lower().split()
        for word in words:
            if word in self._pattern_index:
                self._pattern_index[word] = [
                    eid for eid in self._pattern_index[word] if eid != entry.entry_id
                ]
                if not self._pattern_index[word]:
                    del self._pattern_index[word]

    def get_knowledge_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics."""
        type_counts = {}
        for entry in self._knowledge_base.values():
            type_name = entry.memory_type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1

        return {
            "total_entries": len(self._knowledge_base),
            "max_entries": self.max_entries,
            "type_distribution": type_counts,
            "storage_path": self.storage_path,
        }

    def clear_knowledge(self) -> None:
        """Clear all stored knowledge."""
        self._knowledge_base.clear()
        self._pattern_index.clear()
        self._save_to_storage()
