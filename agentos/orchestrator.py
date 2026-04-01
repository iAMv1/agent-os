"""
AgentOS Main Orchestrator

Ties together all components:
- Session persistence
- Memory system
- Context management
- MCP integration
- Tool system
- Self-healing
- Workflow engine
"""

import os
from typing import Optional, Dict, Any

from agentos.core.session import SessionManager
from agentos.memory.session_memory import SessionMemory, MemoryConfig
from agentos.context.context_manager import ContextManager, ContextConfig
from agentos.mcp.mcp_manager import MCPConfig
from agentos.tools.tool_system import ToolRegistry, ToolExecutor
from agentos.healing.self_healing import (
    SelfHealingSystem,
    RetryConfig,
    CircuitBreakerConfig,
)
from agentos.git.git_system import (
    get_git_state,
    git_status,
    git_diff,
    git_log,
    git_branches,
    create_worktree,
    remove_worktree,
    list_worktrees,
    git_commit,
    git_push,
    git_pull,
    git_remote_base,
    get_git_stats,
    find_git_root,
    is_git_repo,
)


class GitSystem:
    """Git operations wrapper for AgentOS."""

    def get_state(self, path=None):
        return get_git_state(path)

    def status(self, path=None):
        return git_status(path)

    def diff(self, path=None, staged=False):
        return git_diff(path, staged)

    def log(self, path=None, count=10):
        return git_log(path, count)

    def branches(self, path=None):
        return git_branches(path)

    def create_worktree(self, branch, path=None, base_path=None):
        return create_worktree(branch, path, base_path)

    def remove_worktree(self, path, base_path=None):
        return remove_worktree(path, base_path)

    def list_worktrees(self, base_path=None):
        return list_worktrees(base_path)

    def commit(self, message, path=None):
        return git_commit(message, path)

    def push(self, remote="origin", branch=None, path=None):
        return git_push(remote, branch, path)

    def pull(self, remote="origin", branch=None, path=None):
        return git_pull(remote, branch, path)

    def remote_base(self, path=None):
        return git_remote_base(path)

    def stats(self, path=None):
        return get_git_stats(path)

    def is_repo(self, path=None):
        return is_git_repo(path)

    def find_root(self, path=None):
        return find_git_root(path)


class AgentOS:
    """Main AgentOS orchestrator."""

    def __init__(self, base_dir: Optional[str] = None):
        if base_dir is None:
            base_dir = os.path.join(os.getcwd(), ".agent-os")

        self.base_dir = base_dir

        # Initialize all subsystems
        self.session = SessionManager(os.path.join(base_dir, "sessions"))
        self.memory = SessionMemory(os.path.join(base_dir, "memory"))
        self.context = ContextManager(os.path.join(base_dir, "cache"))
        self.mcp = MCPConfig(os.path.join(base_dir, "mcp"))
        self.tools = ToolRegistry()
        self.tool_executor = ToolExecutor(self.tools)
        self.healing = SelfHealingSystem()
        self.git = GitSystem()

        # Initialize memory file if needed
        self.memory.initialize_memory()

    def start_session(self, session_id: Optional[str] = None) -> str:
        """Start a new session or resume the last one."""
        sid = self.session.create_session(session_id)
        self.session.append_turn("system", f"Session started: {sid}")
        return sid

    def continue_session(self) -> str:
        """Resume the last session."""
        sid = self.session.continue_session()
        self.session.append_turn("system", f"Session continued: {sid}")
        return sid

    def resume_session(self, session_id: str) -> str:
        """Resume a specific session."""
        sid = self.session.resume_session(session_id)
        self.session.append_turn("system", f"Session resumed: {sid}")
        return sid

    def fork_session(self, session_id: str, up_to_turn: Optional[int] = None) -> str:
        """Branch from a past conversation."""
        sid = self.session.fork_session(session_id, up_to_turn)
        self.session.append_turn("system", f"Session forked from {session_id}: {sid}")
        return sid

    def add_user_message(self, content: str) -> Dict[str, Any]:
        """Add a user message to the session."""
        turn = self.session.append_turn("user", content)

        # Check if memory extraction should be triggered
        token_count = len(content.split()) * 1.3  # Rough estimate
        if self.memory.should_extract_memory(
            current_token_count=int(token_count),
            current_tool_call_count=0,
            has_tool_calls_last_turn=False,
        ):
            self.memory.start_extraction()

        return turn

    def add_assistant_message(self, content: str, **kwargs) -> Dict[str, Any]:
        """Add an assistant message to the session."""
        return self.session.append_turn("assistant", content, **kwargs)

    def add_tool_result(
        self, tool_name: str, output: str, status: str = "success"
    ) -> Dict[str, Any]:
        """Add a tool result to the session."""
        # Handle large output
        handled = self.context.handle_large_output(output, prefix=f"tool-{tool_name}")

        if handled.get("written_to_disk"):
            content = f"Output written to disk: {handled['file_path']}\nPreview:\n{handled['preview']}"
        else:
            content = handled.get("content", output)

        return self.session.append_turn("tool", content, tool=tool_name, status=status)

    def should_read_file(
        self, file_path: str, current_hash: Optional[str] = None
    ) -> bool:
        """Check if file should be read (deduplication)."""
        return self.context.should_read_file(file_path, current_hash)

    def update_file_hash(self, file_path: str, content: str) -> str:
        """Update file hash after reading/modifying."""
        return self.context.update_file_hash(file_path, content)

    def execute_with_healing(self, name: str, func, fallback=None):
        """Execute a function with self-healing support."""
        return self.healing.execute_with_healing(name, func, fallback)

    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        return {
            "session": {
                "current_id": self.session.current_session_id,
                "turn_count": self.session.turn_count,
                "available_sessions": len(self.session.get_session_ids()),
            },
            "memory": self.memory.get_memory_summary(),
            "context": self.context.get_cache_stats(),
            "mcp": self.mcp.get_server_status(),
            "tools": self.tools.get_tool_stats(),
            "healing": {
                name: cb.get_state()
                for name, cb in self.healing.circuit_breakers.items()
            },
            "git": {
                "is_repo": self.git.is_repo(),
                "root": self.git.find_root(),
                "remote_base": self.git.remote_base(),
            },
        }
