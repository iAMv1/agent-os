"""
AgentOS Context Management System

Multi-layer context management:
- File-read deduplication via hash caching
- Large output handling (write to disk when >2000 lines)
- Context budget prioritization
- Autocompaction triggers
"""

import hashlib
import json
import os
from pathlib import Path
from typing import Optional, Dict, Any, List


class ContextConfig:
    """Configuration for context management."""

    def __init__(
        self,
        max_output_lines: int = 2000,
        max_output_bytes: int = 51200,
        preview_lines: int = 50,
        context_budget_priority: Optional[List[str]] = None,
    ):
        self.max_output_lines = max_output_lines
        self.max_output_bytes = max_output_bytes
        self.preview_lines = preview_lines
        self.context_budget_priority = context_budget_priority or [
            "current_task",
            "session_memory",
            "relevant_code",
            "reference_docs",
        ]


class ContextManager:
    """Manages context with deduplication, large output handling, and budget prioritization."""

    def __init__(
        self, base_dir: Optional[str] = None, config: Optional[ContextConfig] = None
    ):
        if base_dir is None:
            base_dir = os.path.join(os.getcwd(), ".agent-os", "cache")
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.config = config or ContextConfig()
        self.hash_file = self.base_dir / "file-hashes.json"
        self.output_dir = self.base_dir / "outputs"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.file_hashes: Dict[str, str] = self._load_hashes()

    def _load_hashes(self) -> Dict[str, str]:
        """Load file hash cache from disk."""
        if self.hash_file.exists():
            try:
                with open(self.hash_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def _save_hashes(self) -> None:
        """Save file hash cache to disk."""
        with open(self.hash_file, "w", encoding="utf-8") as f:
            json.dump(self.file_hashes, f, indent=2)

    def compute_hash(self, content: str) -> str:
        """Compute SHA256 hash of content."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def should_read_file(
        self, file_path: str, current_hash: Optional[str] = None
    ) -> bool:
        """Check if file should be read (hash changed or not cached)."""
        if current_hash is None:
            return True
        cached_hash = self.file_hashes.get(file_path)
        return cached_hash != current_hash

    def update_file_hash(self, file_path: str, content: str) -> str:
        """Update file hash after reading/modifying."""
        file_hash = self.compute_hash(content)
        self.file_hashes[file_path] = file_hash
        self._save_hashes()
        return file_hash

    def should_write_to_disk(self, content: str) -> bool:
        """Check if content should be written to disk instead of context."""
        lines = content.count("\n") + 1
        bytes_size = len(content.encode("utf-8"))
        return (
            lines > self.config.max_output_lines
            or bytes_size > self.config.max_output_bytes
        )

    def write_to_disk(self, content: str, prefix: str = "output") -> str:
        """Write large content to disk and return file path."""
        import uuid

        filename = f"{prefix}-{uuid.uuid4().hex[:8]}.txt"
        output_path = self.output_dir / filename
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        return str(output_path)

    def generate_preview(self, content: str) -> str:
        """Generate a preview of large content."""
        lines = content.split("\n")
        if len(lines) <= self.config.preview_lines:
            return content

        preview = "\n".join(lines[: self.config.preview_lines])
        preview += f"\n\n... [{len(lines) - self.config.preview_lines} more lines]"
        preview += f"\nFull content written to disk. Use Read <path> to view."
        return preview

    def handle_large_output(
        self, content: str, prefix: str = "output"
    ) -> Dict[str, Any]:
        """Handle large output: write to disk if needed, return preview."""
        if self.should_write_to_disk(content):
            file_path = self.write_to_disk(content, prefix)
            preview = self.generate_preview(content)
            return {
                "written_to_disk": True,
                "file_path": file_path,
                "preview": preview,
                "total_lines": content.count("\n") + 1,
                "total_bytes": len(content.encode("utf-8")),
            }
        return {
            "written_to_disk": False,
            "content": content,
        }

    def get_context_budget(self) -> List[str]:
        """Get context budget priorities."""
        return self.config.context_budget_priority

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "cached_files": len(self.file_hashes),
            "cache_file": str(self.hash_file),
            "output_dir": str(self.output_dir),
            "output_files": len(list(self.output_dir.glob("*.txt")))
            if self.output_dir.exists()
            else 0,
        }

    def clear_cache(self) -> None:
        """Clear all cached hashes."""
        self.file_hashes = {}
        self._save_hashes()
