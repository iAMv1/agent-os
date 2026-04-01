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
- Unknown task handling (7-layer system)
"""

import os
import asyncio
from typing import Optional, Dict, Any

from agentos.core.session import SessionManager
from agentos.memory.session_memory import SessionMemory, MemoryConfig
from agentos.context.context_manager import ContextManager, ContextConfig
from agentos.mcp.mcp_manager import MCPConfig
from agentos.mcp.connectors.registry import ConnectorRegistry, create_default_registry
from agentos.tools.tool_system import ToolRegistry, ToolExecutor
from agentos.healing.self_healing import (
    SelfHealingSystem,
    RetryConfig,
    CircuitBreakerConfig,
)
from agentos.unknown_task.orchestrator import UnknownTaskOrchestrator
from agentos.unknown_task.layer1_skills import SkillsLayer
from agentos.unknown_task.layer2_mcp import MCPLayer
from agentos.unknown_task.layer3_toolsearch import ToolSearchLayer
from agentos.unknown_task.layer4_research import ResearchLayer
from agentos.unknown_task.layer5_adaptation import AdaptationLayer
from agentos.unknown_task.layer6_memory import MemoryLayer
from agentos.unknown_task.layer7_fallback import FallbackLayer
from agentos.unknown_task.orchestrator import LayerResult, TaskOutcome
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
from agentos.github.github_integration import (
    gh_auth_status,
    create_pr,
    get_pr,
    list_prs,
    merge_pr,
    close_pr,
    get_pr_reviews,
    add_pr_review,
    request_pr_changes,
    approve_pr,
    add_pr_comment,
    reply_to_pr_comment,
    get_pr_comments,
    get_pr_diff,
    get_pr_files,
    get_pr_checks,
    create_issue,
    get_issue,
    list_issues,
    close_issue,
    reopen_issue,
    add_issue_comment,
    update_issue,
    search_issues,
    analyze_pr_diff,
    generate_pr_review_suggestions,
    auto_review_pr,
    get_repo_info,
    get_github_state,
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


class GitHubSystem:
    """GitHub operations wrapper for AgentOS."""

    def auth_status(self):
        return gh_auth_status()

    def create_pr(
        self,
        title,
        body,
        base="main",
        head=None,
        repo=None,
        draft=False,
        labels=None,
        assignees=None,
        reviewers=None,
        cwd=None,
    ):
        return create_pr(
            title, body, base, head, repo, draft, labels, assignees, reviewers, cwd
        )

    def get_pr(self, pr_number=None, repo=None, cwd=None):
        return get_pr(pr_number, repo, cwd)

    def list_prs(
        self, state="open", base=None, head=None, limit=20, repo=None, cwd=None
    ):
        return list_prs(state, base, head, limit, repo, cwd)

    def merge_pr(
        self, pr_number, method="merge", delete_branch=False, repo=None, cwd=None
    ):
        return merge_pr(pr_number, method, delete_branch, repo, cwd)

    def close_pr(self, pr_number, repo=None, cwd=None):
        return close_pr(pr_number, repo, cwd)

    def get_pr_reviews(self, pr_number, repo=None, cwd=None):
        return get_pr_reviews(pr_number, repo, cwd)

    def add_pr_review(
        self, pr_number, action="approve", body=None, repo=None, cwd=None
    ):
        return add_pr_review(pr_number, action, body, repo, cwd)

    def request_changes(self, pr_number, reason=None, repo=None, cwd=None):
        return request_pr_changes(pr_number, reason, repo, cwd)

    def approve_pr(self, pr_number, comment=None, repo=None, cwd=None):
        return approve_pr(pr_number, comment, repo, cwd)

    def add_pr_comment(self, pr_number, body, repo=None, cwd=None):
        return add_pr_comment(pr_number, body, repo, cwd)

    def reply_to_comment(self, pr_number, comment_id, body, repo=None, cwd=None):
        return reply_to_pr_comment(pr_number, comment_id, body, repo, cwd)

    def get_pr_comments(self, pr_number, repo=None, cwd=None):
        return get_pr_comments(pr_number, repo, cwd)

    def get_pr_diff(self, pr_number, repo=None, cwd=None):
        return get_pr_diff(pr_number, repo, cwd)

    def get_pr_files(self, pr_number, repo=None, cwd=None):
        return get_pr_files(pr_number, repo, cwd)

    def get_pr_checks(self, pr_number, repo=None, cwd=None):
        return get_pr_checks(pr_number, repo, cwd)

    def create_issue(
        self,
        title,
        body=None,
        labels=None,
        assignees=None,
        milestone=None,
        repo=None,
        cwd=None,
    ):
        return create_issue(title, body, labels, assignees, milestone, repo, cwd)

    def get_issue(self, issue_number, repo=None, cwd=None):
        return get_issue(issue_number, repo, cwd)

    def list_issues(
        self, state="open", labels=None, assignee=None, limit=20, repo=None, cwd=None
    ):
        return list_issues(state, labels, assignee, limit, repo, cwd)

    def close_issue(self, issue_number, repo=None, cwd=None):
        return close_issue(issue_number, repo, cwd)

    def reopen_issue(self, issue_number, repo=None, cwd=None):
        return reopen_issue(issue_number, repo, cwd)

    def add_issue_comment(self, issue_number, body, repo=None, cwd=None):
        return add_issue_comment(issue_number, body, repo, cwd)

    def update_issue(
        self,
        issue_number,
        title=None,
        body=None,
        labels=None,
        add_labels=None,
        remove_labels=None,
        assignees=None,
        add_assignees=None,
        remove_assignees=None,
        milestone=None,
        repo=None,
        cwd=None,
    ):
        return update_issue(
            issue_number,
            title,
            body,
            labels,
            add_labels,
            remove_labels,
            assignees,
            add_assignees,
            remove_assignees,
            milestone,
            repo,
            cwd,
        )

    def search_issues(self, query, limit=20, repo=None, cwd=None):
        return search_issues(query, limit, repo, cwd)

    def analyze_pr(self, pr_number, repo=None, cwd=None):
        return analyze_pr_diff(pr_number, repo, cwd)

    def generate_review_suggestions(self, pr_number, repo=None, cwd=None):
        return generate_pr_review_suggestions(pr_number, repo, cwd)

    def auto_review_pr(self, pr_number, approve_if_clean=False, repo=None, cwd=None):
        return auto_review_pr(pr_number, approve_if_clean, repo, cwd)

    def get_repo_info(self, repo=None, cwd=None):
        return get_repo_info(repo, cwd)

    def get_state(self, cwd=None):
        return get_github_state(cwd)


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
        self.mcp_connectors = create_default_registry(
            config_path=os.path.join(base_dir, "mcp", "connectors.json")
        )
        self.tools = ToolRegistry()
        self.tool_executor = ToolExecutor(self.tools)
        self.healing = SelfHealingSystem()
        self.git = GitSystem()
        self.github = GitHubSystem()

        # Initialize unknown task handling system
        self.unknown_task = self._init_unknown_task_system(base_dir)

        # Initialize memory file if needed
        self.memory.initialize_memory()

    def _init_unknown_task_system(self, base_dir: str) -> UnknownTaskOrchestrator:
        """Initialize the 7-layer unknown task handling system."""
        memory_path = os.path.join(base_dir, "unknown_task_knowledge.json")

        skills_layer = SkillsLayer()
        mcp_layer = MCPLayer(mcp_config={})
        tool_search_layer = ToolSearchLayer(search_enabled=True)
        research_layer = ResearchLayer(max_agents=3, timeout_seconds=300)
        adaptation_layer = AdaptationLayer(available_capabilities={})
        memory_layer = MemoryLayer(storage_path=memory_path, max_entries=1000)
        fallback_layer = FallbackLayer(max_fallback_depth=5)

        return UnknownTaskOrchestrator(
            skills_layer=skills_layer,
            mcp_layer=mcp_layer,
            tool_search_layer=tool_search_layer,
            research_layer=research_layer,
            adaptation_layer=adaptation_layer,
            memory_layer=memory_layer,
            fallback_layer=fallback_layer,
            confidence_threshold=0.5,
        )

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

    async def connect_mcp_connector(self, name: str):
        """Connect a specific MCP connector."""
        return await self.mcp_connectors.connect(name)

    async def disconnect_mcp_connector(self, name: str):
        """Disconnect a specific MCP connector."""
        return await self.mcp_connectors.disconnect(name)

    async def connect_all_mcp_connectors(self):
        """Connect all registered MCP connectors."""
        return await self.mcp_connectors.connect_all()

    async def disconnect_all_mcp_connectors(self):
        """Disconnect all registered MCP connectors."""
        return await self.mcp_connectors.disconnect_all()

    async def call_mcp_tool(
        self, tool_name: str, arguments: Dict[str, Any], connector: Optional[str] = None
    ):
        """Call an MCP tool across any connected connector."""
        return await self.mcp_connectors.call_tool(
            tool_name, arguments, connector_name=connector
        )

    async def get_mcp_tools(self):
        """Get all available MCP tools from connected connectors."""
        return await self.mcp_connectors.get_all_tools()

    def get_mcp_connector_status(self):
        """Get status of all MCP connectors."""
        return self.mcp_connectors.get_status()

    async def get_mcp_health(self):
        """Health check for All MCP connectors."""
        return await self.mcp_connectors.health_check()

    async def handle_unknown_task(self, task: str) -> LayerResult:
        """Handle an unknown task through the 7-layer system."""
        return await self.unknown_task.handle_task(task)

    def get_unknown_task_confidence(self, task: str) -> Dict[str, float]:
        """Get confidence scores for all unknown task layers."""
        return self.unknown_task.get_layer_confidence(task)

    def get_recommended_layer(self, task: str) -> Optional[str]:
        """Get the recommended layer for an unknown task."""
        layer = self.unknown_task.get_recommended_layer(task)
        return layer.value if layer else None

    def get_unknown_task_stats(self) -> Dict[str, Any]:
        """Get unknown task handling statistics."""
        return self.unknown_task.get_stats()

    def register_skill(self, name: str, metadata: Dict[str, Any]) -> None:
        """Register a skill for unknown task handling."""
        self.unknown_task.skills.register_skill(name, metadata)

    def register_capability(self, name: str, metadata: Dict[str, Any]) -> None:
        """Register a capability for adaptation layer."""
        self.unknown_task.adaptation.register_capability(name, metadata)

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
            "github": {
                "authenticated": self.github.auth_status().get("authenticated", False),
                "state": self.github.get_state(),
            },
            "mcp_connectors": self.mcp_connectors.get_status(),
            "unknown_task": self.unknown_task.get_stats(),
        }
