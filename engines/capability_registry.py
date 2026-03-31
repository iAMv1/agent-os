import json
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class CapabilityType(Enum):
    TOOL = "tool"
    AGENT = "agent"
    SERVICE = "service"
    HOOK = "hook"
    COMMAND = "command"
    SKILL = "skill"


class SDLCStage(Enum):
    REQUIREMENTS = "requirements"
    DESIGN = "design"
    IMPLEMENTATION = "implementation"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    MAINTENANCE = "maintenance"
    COLLABORATION = "collaboration"
    INFRASTRUCTURE = "infrastructure"


@dataclass
class Capability:
    name: str
    cap_type: CapabilityType
    description: str
    stages: List[SDLCStage]
    source_files: List[str]
    inputs: str
    outputs: str
    dependencies: List[str]
    is_always_available: bool
    gating: str  # "always" or feature flag name
    cost_estimate: str  # "low", "medium", "high"
    parallel_safe: bool


class CapabilityRegistry:
    """Registry of all 100+ capabilities extracted from the recovered source code."""

    def __init__(self):
        self.capabilities: Dict[str, Capability] = {}
        self._build_registry()

    def _build_registry(self):
        """Build the complete capability registry from recovered source analysis."""

        # ==================== TOOLS ====================

        # Core File Operations
        self._add(
            Capability(
                name="FileRead",
                cap_type=CapabilityType.TOOL,
                description="Read file contents with range support, binary detection, image handling",
                stages=[
                    SDLCStage.REQUIREMENTS,
                    SDLCStage.DESIGN,
                    SDLCStage.IMPLEMENTATION,
                    SDLCStage.TESTING,
                    SDLCStage.MAINTENANCE,
                ],
                source_files=["tools/FileReadTool/FileReadTool.tsx"],
                inputs="file path, optional line range",
                outputs="file content, metadata",
                dependencies=[],
                is_always_available=True,
                gating="always",
                cost_estimate="low",
                parallel_safe=True,
            )
        )

        self._add(
            Capability(
                name="FileEdit",
                cap_type=CapabilityType.TOOL,
                description="Edit files using SEARCH/REPLACE blocks with diff visualization",
                stages=[SDLCStage.IMPLEMENTATION, SDLCStage.MAINTENANCE],
                source_files=["tools/FileEditTool/FileEditTool.tsx"],
                inputs="file path, search block, replace block",
                outputs="diff, success status",
                dependencies=["FileRead"],
                is_always_available=True,
                gating="always",
                cost_estimate="medium",
                parallel_safe=False,
            )
        )

        self._add(
            Capability(
                name="FileWrite",
                cap_type=CapabilityType.TOOL,
                description="Write new files or overwrite existing files",
                stages=[SDLCStage.IMPLEMENTATION, SDLCStage.DEPLOYMENT],
                source_files=["tools/FileWriteTool/FileWriteTool.tsx"],
                inputs="file path, content",
                outputs="success status",
                dependencies=[],
                is_always_available=True,
                gating="always",
                cost_estimate="medium",
                parallel_safe=False,
            )
        )

        self._add(
            Capability(
                name="Bash",
                cap_type=CapabilityType.TOOL,
                description="Execute shell commands with sandboxing, backgrounding, progress tracking, security analysis",
                stages=[
                    SDLCStage.REQUIREMENTS,
                    SDLCStage.DESIGN,
                    SDLCStage.IMPLEMENTATION,
                    SDLCStage.TESTING,
                    SDLCStage.DEPLOYMENT,
                    SDLCStage.MAINTENANCE,
                    SDLCStage.INFRASTRUCTURE,
                ],
                source_files=[
                    "tools/BashTool/BashTool.tsx",
                    "tools/BashTool/UI.tsx",
                    "tools/BashTool/bashPermissions.tsx",
                ],
                inputs="command string, timeout, description, background flag",
                outputs="stdout, stderr, exit code, background task ID",
                dependencies=[],
                is_always_available=True,
                gating="always",
                cost_estimate="medium",
                parallel_safe=False,
            )
        )

        self._add(
            Capability(
                name="Grep",
                cap_type=CapabilityType.TOOL,
                description="Search file contents using ripgrep with regex support",
                stages=[
                    SDLCStage.REQUIREMENTS,
                    SDLCStage.DESIGN,
                    SDLCStage.IMPLEMENTATION,
                    SDLCStage.TESTING,
                    SDLCStage.MAINTENANCE,
                ],
                source_files=["tools/GrepTool/GrepTool.tsx"],
                inputs="pattern, file filters, context lines",
                outputs="matching lines with file paths and line numbers",
                dependencies=[],
                is_always_available=True,
                gating="always",
                cost_estimate="low",
                parallel_safe=True,
            )
        )

        self._add(
            Capability(
                name="Glob",
                cap_type=CapabilityType.TOOL,
                description="Find files matching glob patterns",
                stages=[
                    SDLCStage.REQUIREMENTS,
                    SDLCStage.DESIGN,
                    SDLCStage.IMPLEMENTATION,
                    SDLCStage.TESTING,
                    SDLCStage.MAINTENANCE,
                ],
                source_files=["tools/GlobTool/GlobTool.tsx"],
                inputs="glob pattern, path",
                outputs="matching file paths",
                dependencies=[],
                is_always_available=True,
                gating="always",
                cost_estimate="low",
                parallel_safe=True,
            )
        )

        self._add(
            Capability(
                name="WebSearch",
                cap_type=CapabilityType.TOOL,
                description="Search the web using Exa AI for current information",
                stages=[
                    SDLCStage.REQUIREMENTS,
                    SDLCStage.DESIGN,
                    SDLCStage.DEPLOYMENT,
                    SDLCStage.MAINTENANCE,
                ],
                source_files=["tools/WebSearchTool/WebSearchTool.tsx"],
                inputs="search query, num results, live crawl mode",
                outputs="search results with content from top websites",
                dependencies=[],
                is_always_available=True,
                gating="always",
                cost_estimate="low",
                parallel_safe=True,
            )
        )

        self._add(
            Capability(
                name="WebFetch",
                cap_type=CapabilityType.TOOL,
                description="Fetch and read webpage content in markdown, text, or HTML",
                stages=[
                    SDLCStage.REQUIREMENTS,
                    SDLCStage.DESIGN,
                    SDLCStage.DEPLOYMENT,
                    SDLCStage.MAINTENANCE,
                ],
                source_files=["tools/WebFetchTool/WebFetchTool.tsx"],
                inputs="URL, format (markdown/text/html)",
                outputs="page content in requested format",
                dependencies=[],
                is_always_available=True,
                gating="always",
                cost_estimate="low",
                parallel_safe=True,
            )
        )

        self._add(
            Capability(
                name="TodoWrite",
                cap_type=CapabilityType.TOOL,
                description="Create and manage todo lists with status tracking",
                stages=[
                    SDLCStage.REQUIREMENTS,
                    SDLCStage.DESIGN,
                    SDLCStage.IMPLEMENTATION,
                    SDLCStage.TESTING,
                    SDLCStage.DEPLOYMENT,
                    SDLCStage.MAINTENANCE,
                ],
                source_files=["tools/TodoWriteTool/TodoWriteTool.ts"],
                inputs="todo items with status (pending/in_progress/completed/cancelled)",
                outputs="updated todo list",
                dependencies=[],
                is_always_available=True,
                gating="always",
                cost_estimate="low",
                parallel_safe=False,
            )
        )

        self._add(
            Capability(
                name="AskUserQuestion",
                cap_type=CapabilityType.TOOL,
                description="Present multiple-choice questions to users for clarification and decision-making",
                stages=[SDLCStage.REQUIREMENTS, SDLCStage.DESIGN],
                source_files=["tools/AskUserQuestionTool/AskUserQuestionTool.tsx"],
                inputs="array of questions with options, labels, descriptions",
                outputs="user answers mapped to questions",
                dependencies=[],
                is_always_available=True,
                gating="always",
                cost_estimate="low",
                parallel_safe=False,
            )
        )

        self._add(
            Capability(
                name="Skill",
                cap_type=CapabilityType.TOOL,
                description="Load and invoke skills (specialized instruction sets) with tool restrictions and model overrides",
                stages=[
                    SDLCStage.REQUIREMENTS,
                    SDLCStage.DESIGN,
                    SDLCStage.IMPLEMENTATION,
                    SDLCStage.TESTING,
                    SDLCStage.DEPLOYMENT,
                    SDLCStage.MAINTENANCE,
                ],
                source_files=["tools/SkillTool/SkillTool.ts"],
                inputs="skill name",
                outputs="loaded skill with allowed tools, model configuration",
                dependencies=[],
                is_always_available=True,
                gating="always",
                cost_estimate="medium",
                parallel_safe=True,
            )
        )

        self._add(
            Capability(
                name="Agent",
                cap_type=CapabilityType.TOOL,
                description="Spawn specialized subagents with configurable models, isolation modes, and tool pools",
                stages=[
                    SDLCStage.DESIGN,
                    SDLCStage.IMPLEMENTATION,
                    SDLCStage.TESTING,
                    SDLCStage.MAINTENANCE,
                ],
                source_files=[
                    "tools/AgentTool/AgentTool.tsx",
                    "tools/AgentTool/builtInAgents.ts",
                    "tools/AgentTool/forkSubagent.ts",
                    "tools/AgentTool/runAgent.ts",
                ],
                inputs="prompt, description, subagent_type, model, background flag, isolation mode",
                outputs="completed result or async launch info",
                dependencies=["LocalAgentTask", "RemoteAgentTask"],
                is_always_available=True,
                gating="always",
                cost_estimate="high",
                parallel_safe=True,
            )
        )

        self._add(
            Capability(
                name="NotebookEdit",
                cap_type=CapabilityType.TOOL,
                description="Edit Jupyter notebook cells with source and outputs",
                stages=[SDLCStage.IMPLEMENTATION],
                source_files=["tools/NotebookEditTool/NotebookEditTool.tsx"],
                inputs="notebook path, cell operations",
                outputs="updated notebook",
                dependencies=["FileRead", "FileWrite"],
                is_always_available=True,
                gating="always",
                cost_estimate="medium",
                parallel_safe=False,
            )
        )

        self._add(
            Capability(
                name="LSP",
                cap_type=CapabilityType.TOOL,
                description="Language Server Protocol operations for code intelligence (go-to-def, references, diagnostics, symbols)",
                stages=[SDLCStage.IMPLEMENTATION, SDLCStage.MAINTENANCE],
                source_files=["tools/LSPTool/LSPTool.ts"],
                inputs="operation type, file path, position",
                outputs="code intelligence results",
                dependencies=[],
                is_always_available=False,
                gating="ENABLE_LSP_TOOL",
                cost_estimate="low",
                parallel_safe=True,
            )
        )

        self._add(
            Capability(
                name="PowerShell",
                cap_type=CapabilityType.TOOL,
                description="Execute PowerShell commands on Windows",
                stages=[
                    SDLCStage.REQUIREMENTS,
                    SDLCStage.DESIGN,
                    SDLCStage.IMPLEMENTATION,
                    SDLCStage.TESTING,
                    SDLCStage.DEPLOYMENT,
                    SDLCStage.MAINTENANCE,
                ],
                source_files=["tools/PowerShellTool/PowerShellTool.ts"],
                inputs="PowerShell command",
                outputs="command output",
                dependencies=[],
                is_always_available=False,
                gating="isPowerShellToolEnabled()",
                cost_estimate="medium",
                parallel_safe=False,
            )
        )

        self._add(
            Capability(
                name="EnterPlanMode",
                cap_type=CapabilityType.TOOL,
                description="Enter structured planning mode with plan file management",
                stages=[SDLCStage.REQUIREMENTS, SDLCStage.DESIGN],
                source_files=["tools/EnterPlanModeTool/EnterPlanModeTool.tsx"],
                inputs="optional description",
                outputs="mode transition, plan file",
                dependencies=[],
                is_always_available=True,
                gating="always",
                cost_estimate="low",
                parallel_safe=False,
            )
        )

        self._add(
            Capability(
                name="ExitPlanMode",
                cap_type=CapabilityType.TOOL,
                description="Exit planning mode and return to implementation",
                stages=[SDLCStage.DESIGN, SDLCStage.IMPLEMENTATION],
                source_files=["tools/ExitPlanModeTool/ExitPlanModeTool.tsx"],
                inputs="none",
                outputs="mode transition",
                dependencies=["EnterPlanMode"],
                is_always_available=True,
                gating="always",
                cost_estimate="low",
                parallel_safe=False,
            )
        )

        self._add(
            Capability(
                name="EnterWorktree",
                cap_type=CapabilityType.TOOL,
                description="Create and enter a git worktree for isolated development",
                stages=[SDLCStage.IMPLEMENTATION],
                source_files=["tools/EnterWorktreeTool/EnterWorktreeTool.tsx"],
                inputs="branch name, optional path",
                outputs="worktree path",
                dependencies=[],
                is_always_available=True,
                gating="always",
                cost_estimate="low",
                parallel_safe=False,
            )
        )

        self._add(
            Capability(
                name="ExitWorktree",
                cap_type=CapabilityType.TOOL,
                description="Exit current git worktree",
                stages=[SDLCStage.IMPLEMENTATION],
                source_files=["tools/ExitWorktreeTool/ExitWorktreeTool.tsx"],
                inputs="none",
                outputs="success status",
                dependencies=["EnterWorktree"],
                is_always_available=True,
                gating="always",
                cost_estimate="low",
                parallel_safe=False,
            )
        )

        self._add(
            Capability(
                name="ScheduleCron",
                cap_type=CapabilityType.TOOL,
                description="Create, list, update, and run cron-triggered tasks",
                stages=[SDLCStage.DEPLOYMENT, SDLCStage.MAINTENANCE],
                source_files=["tools/ScheduleCronTool/ScheduleCronTool.ts"],
                inputs="action (create/list/update/run), cron expression, task config",
                outputs="task status",
                dependencies=[],
                is_always_available=False,
                gating="AGENT_TRIGGERS",
                cost_estimate="medium",
                parallel_safe=True,
            )
        )

        self._add(
            Capability(
                name="RemoteTrigger",
                cap_type=CapabilityType.TOOL,
                description="Create and manage remote-triggered agent sessions via CCR",
                stages=[SDLCStage.DEPLOYMENT, SDLCStage.INFRASTRUCTURE],
                source_files=["tools/RemoteTriggerTool/RemoteTriggerTool.ts"],
                inputs="trigger config, environment ID",
                outputs="trigger status",
                dependencies=[],
                is_always_available=False,
                gating="AGENT_TRIGGERS_REMOTE",
                cost_estimate="medium",
                parallel_safe=True,
            )
        )

        self._add(
            Capability(
                name="ToolSearch",
                cap_type=CapabilityType.TOOL,
                description="Discover deferred tools (MCP + deferred loading tools) on-demand",
                stages=[
                    SDLCStage.REQUIREMENTS,
                    SDLCStage.DESIGN,
                    SDLCStage.IMPLEMENTATION,
                    SDLCStage.TESTING,
                    SDLCStage.DEPLOYMENT,
                    SDLCStage.MAINTENANCE,
                ],
                source_files=["tools/ToolSearchTool/ToolSearchTool.ts"],
                inputs="search query or tool name",
                outputs="matching tool definitions",
                dependencies=[],
                is_always_available=False,
                gating="ENABLE_TOOL_SEARCH",
                cost_estimate="low",
                parallel_safe=True,
            )
        )

        self._add(
            Capability(
                name="Config",
                cap_type=CapabilityType.TOOL,
                description="Read and modify AI Coding Agent configuration",
                stages=[
                    SDLCStage.REQUIREMENTS,
                    SDLCStage.DESIGN,
                    SDLCStage.IMPLEMENTATION,
                    SDLCStage.TESTING,
                    SDLCStage.DEPLOYMENT,
                    SDLCStage.MAINTENANCE,
                ],
                source_files=["tools/ConfigTool/ConfigTool.ts"],
                inputs="config path, value",
                outputs="config value or updated config",
                dependencies=[],
                is_always_available=False,
                gating="USER_TYPE=ant",
                cost_estimate="low",
                parallel_safe=True,
            )
        )

        self._add(
            Capability(
                name="Brief",
                cap_type=CapabilityType.TOOL,
                description="Generate brief summaries of conversation or code changes",
                stages=[
                    SDLCStage.REQUIREMENTS,
                    SDLCStage.DESIGN,
                    SDLCStage.MAINTENANCE,
                ],
                source_files=["tools/BriefTool/BriefTool.ts"],
                inputs="context to summarize",
                outputs="brief summary",
                dependencies=[],
                is_always_available=True,
                gating="always",
                cost_estimate="low",
                parallel_safe=True,
            )
        )

        self._add(
            Capability(
                name="Sleep",
                cap_type=CapabilityType.TOOL,
                description="Delay execution for a specified duration",
                stages=[SDLCStage.IMPLEMENTATION, SDLCStage.TESTING],
                source_files=["tools/SleepTool/SleepTool.ts"],
                inputs="duration in seconds",
                outputs="none",
                dependencies=[],
                is_always_available=False,
                gating="PROACTIVE or KAIROS",
                cost_estimate="low",
                parallel_safe=True,
            )
        )

        self._add(
            Capability(
                name="SyntheticOutput",
                cap_type=CapabilityType.TOOL,
                description="Generate structured synthetic output for testing and simulation",
                stages=[SDLCStage.TESTING],
                source_files=["tools/SyntheticOutputTool/SyntheticOutputTool.ts"],
                inputs="output specification",
                outputs="synthetic content",
                dependencies=[],
                is_always_available=False,
                gating="internal",
                cost_estimate="low",
                parallel_safe=True,
            )
        )

        # Task Management Tools
        self._add(
            Capability(
                name="TaskCreate",
                cap_type=CapabilityType.TOOL,
                description="Create a new background task",
                stages=[
                    SDLCStage.IMPLEMENTATION,
                    SDLCStage.TESTING,
                    SDLCStage.DEPLOYMENT,
                ],
                source_files=["tools/TaskCreateTool/TaskCreateTool.ts"],
                inputs="task type, config",
                outputs="task ID",
                dependencies=[],
                is_always_available=True,
                gating="always",
                cost_estimate="low",
                parallel_safe=True,
            )
        )

        self._add(
            Capability(
                name="TaskGet",
                cap_type=CapabilityType.TOOL,
                description="Get status and output of a task by ID",
                stages=[
                    SDLCStage.IMPLEMENTATION,
                    SDLCStage.TESTING,
                    SDLCStage.DEPLOYMENT,
                ],
                source_files=["tools/TaskGetTool/TaskGetTool.ts"],
                inputs="task ID",
                outputs="task status, output",
                dependencies=["TaskCreate"],
                is_always_available=True,
                gating="always",
                cost_estimate="low",
                parallel_safe=True,
            )
        )

        self._add(
            Capability(
                name="TaskList",
                cap_type=CapabilityType.TOOL,
                description="List all tasks with filtering",
                stages=[
                    SDLCStage.IMPLEMENTATION,
                    SDLCStage.TESTING,
                    SDLCStage.DEPLOYMENT,
                ],
                source_files=["tools/TaskListTool/TaskListTool.ts"],
                inputs="optional filters",
                outputs="list of tasks",
                dependencies=["TaskCreate"],
                is_always_available=True,
                gating="always",
                cost_estimate="low",
                parallel_safe=True,
            )
        )

        self._add(
            Capability(
                name="TaskUpdate",
                cap_type=CapabilityType.TOOL,
                description="Update task status and metadata",
                stages=[
                    SDLCStage.IMPLEMENTATION,
                    SDLCStage.TESTING,
                    SDLCStage.DEPLOYMENT,
                ],
                source_files=["tools/TaskUpdateTool/TaskUpdateTool.ts"],
                inputs="task ID, updates",
                outputs="updated task",
                dependencies=["TaskCreate"],
                is_always_available=True,
                gating="always",
                cost_estimate="low",
                parallel_safe=True,
            )
        )

        self._add(
            Capability(
                name="TaskStop",
                cap_type=CapabilityType.TOOL,
                description="Stop a running task",
                stages=[
                    SDLCStage.IMPLEMENTATION,
                    SDLCStage.TESTING,
                    SDLCStage.DEPLOYMENT,
                ],
                source_files=["tools/TaskStopTool/TaskStopTool.ts"],
                inputs="task ID",
                outputs="stop confirmation",
                dependencies=["TaskCreate"],
                is_always_available=True,
                gating="always",
                cost_estimate="low",
                parallel_safe=True,
            )
        )

        self._add(
            Capability(
                name="TaskOutput",
                cap_type=CapabilityType.TOOL,
                description="Get incremental output from a running task",
                stages=[
                    SDLCStage.IMPLEMENTATION,
                    SDLCStage.TESTING,
                    SDLCStage.DEPLOYMENT,
                ],
                source_files=["tools/TaskOutputTool/TaskOutputTool.ts"],
                inputs="task ID, offset",
                outputs="new output since offset",
                dependencies=["TaskCreate"],
                is_always_available=True,
                gating="always",
                cost_estimate="low",
                parallel_safe=True,
            )
        )

        # Team/Swarm Tools
        self._add(
            Capability(
                name="TeamCreate",
                cap_type=CapabilityType.TOOL,
                description="Create an agent team (swarm) with multiple members",
                stages=[SDLCStage.DESIGN, SDLCStage.IMPLEMENTATION],
                source_files=["tools/TeamCreateTool/TeamCreateTool.ts"],
                inputs="team name, member configs",
                outputs="team ID",
                dependencies=["Agent"],
                is_always_available=False,
                gating="isAgentSwarmsEnabled()",
                cost_estimate="high",
                parallel_safe=True,
            )
        )

        self._add(
            Capability(
                name="TeamDelete",
                cap_type=CapabilityType.TOOL,
                description="Delete an agent team",
                stages=[SDLCStage.DESIGN, SDLCStage.IMPLEMENTATION],
                source_files=["tools/TeamDeleteTool/TeamDeleteTool.ts"],
                inputs="team ID",
                outputs="deletion confirmation",
                dependencies=["TeamCreate"],
                is_always_available=False,
                gating="isAgentSwarmsEnabled()",
                cost_estimate="low",
                parallel_safe=True,
            )
        )

        self._add(
            Capability(
                name="SendMessage",
                cap_type=CapabilityType.TOOL,
                description="Send messages between running agents/teammates",
                stages=[
                    SDLCStage.DESIGN,
                    SDLCStage.IMPLEMENTATION,
                    SDLCStage.COLLABORATION,
                ],
                source_files=["tools/SendMessageTool/SendMessageTool.ts"],
                inputs="target agent name, message content",
                outputs="delivery confirmation",
                dependencies=["Agent"],
                is_always_available=False,
                gating="KAIROS",
                cost_estimate="low",
                parallel_safe=True,
            )
        )

        # ==================== AGENTS ====================

        self._add(
            Capability(
                name="general-purpose-agent",
                cap_type=CapabilityType.AGENT,
                description="All-purpose research and multi-step task execution",
                stages=[
                    SDLCStage.REQUIREMENTS,
                    SDLCStage.DESIGN,
                    SDLCStage.IMPLEMENTATION,
                    SDLCStage.TESTING,
                    SDLCStage.MAINTENANCE,
                ],
                source_files=["tools/AgentTool/builtInAgents.ts"],
                inputs="prompt, description",
                outputs="completed result",
                dependencies=["Agent"],
                is_always_available=True,
                gating="always",
                cost_estimate="high",
                parallel_safe=True,
            )
        )

        self._add(
            Capability(
                name="Explore-agent",
                cap_type=CapabilityType.AGENT,
                description="Read-only file search specialist for codebase exploration",
                stages=[
                    SDLCStage.REQUIREMENTS,
                    SDLCStage.DESIGN,
                    SDLCStage.MAINTENANCE,
                ],
                source_files=["tools/AgentTool/builtInAgents.ts"],
                inputs="exploration prompt",
                outputs="findings report",
                dependencies=["Agent"],
                is_always_available=True,
                gating="always",
                cost_estimate="low",
                parallel_safe=True,
            )
        )

        self._add(
            Capability(
                name="Plan-agent",
                cap_type=CapabilityType.AGENT,
                description="Software architect for implementation planning",
                stages=[SDLCStage.DESIGN],
                source_files=["tools/AgentTool/builtInAgents.ts"],
                inputs="planning prompt",
                outputs="implementation plan",
                dependencies=["Agent"],
                is_always_available=True,
                gating="always",
                cost_estimate="medium",
                parallel_safe=True,
            )
        )

        self._add(
            Capability(
                name="verification-agent",
                cap_type=CapabilityType.AGENT,
                description="Adversarial testing specialist with evidence tracking",
                stages=[SDLCStage.TESTING, SDLCStage.MAINTENANCE],
                source_files=["tools/AgentTool/builtInAgents.ts"],
                inputs="testing prompt",
                outputs="VERDICT: PASS/FAIL/PARTIAL with evidence",
                dependencies=["Agent"],
                is_always_available=False,
                gating="tengu_hive_evidence",
                cost_estimate="medium",
                parallel_safe=True,
            )
        )

        self._add(
            Capability(
                name="agent-code-guide-agent",
                cap_type=CapabilityType.AGENT,
                description="Documentation Q&A agent for AI Coding Agent usage",
                stages=[
                    SDLCStage.REQUIREMENTS,
                    SDLCStage.DESIGN,
                    SDLCStage.IMPLEMENTATION,
                    SDLCStage.TESTING,
                    SDLCStage.DEPLOYMENT,
                    SDLCStage.MAINTENANCE,
                ],
                source_files=["tools/AgentTool/builtInAgents.ts"],
                inputs="question about AI Coding Agent",
                outputs="answer from documentation",
                dependencies=["Agent"],
                is_always_available=True,
                gating="always",
                cost_estimate="low",
                parallel_safe=True,
            )
        )

        self._add(
            Capability(
                name="fork-agent",
                cap_type=CapabilityType.AGENT,
                description="Context-inheriting worker that receives parent's full conversation",
                stages=[SDLCStage.IMPLEMENTATION],
                source_files=["tools/AgentTool/forkSubagent.ts"],
                inputs="directive",
                outputs="structured result (Scope/Result/Key files/Files changed/Issues)",
                dependencies=["Agent"],
                is_always_available=False,
                gating="FORK_SUBAGENT",
                cost_estimate="high",
                parallel_safe=True,
            )
        )

        # ==================== SERVICES ====================

        self._add(
            Capability(
                name="MCP-System",
                cap_type=CapabilityType.SERVICE,
                description="Model Context Protocol server management, OAuth, elicitation, connections",
                stages=[
                    SDLCStage.REQUIREMENTS,
                    SDLCStage.DESIGN,
                    SDLCStage.IMPLEMENTATION,
                    SDLCStage.TESTING,
                    SDLCStage.DEPLOYMENT,
                    SDLCStage.MAINTENANCE,
                ],
                source_files=[
                    "services/mcp/client.ts",
                    "services/mcp/config.ts",
                    "services/mcp/auth.ts",
                    "services/mcp/oauth.ts",
                    "services/mcp/elicitation.ts",
                ],
                inputs="MCP server config",
                outputs="MCP tools and resources",
                dependencies=[],
                is_always_available=True,
                gating="always",
                cost_estimate="medium",
                parallel_safe=True,
            )
        )

        self._add(
            Capability(
                name="Compact-System",
                cap_type=CapabilityType.SERVICE,
                description="Context compaction: auto-compact, micro-compact, reactive compact, snip",
                stages=[
                    SDLCStage.REQUIREMENTS,
                    SDLCStage.DESIGN,
                    SDLCStage.IMPLEMENTATION,
                    SDLCStage.TESTING,
                    SDLCStage.DEPLOYMENT,
                    SDLCStage.MAINTENANCE,
                ],
                source_files=[
                    "services/compact/autoCompact.ts",
                    "services/compact/microCompact.ts",
                    "services/compact/reactiveCompact.ts",
                ],
                inputs="context state",
                outputs="compacted context",
                dependencies=[],
                is_always_available=True,
                gating="always",
                cost_estimate="medium",
                parallel_safe=True,
            )
        )

        self._add(
            Capability(
                name="Memory-System",
                cap_type=CapabilityType.SERVICE,
                description="Session memory, team memory sync, memory extraction, auto-dream",
                stages=[
                    SDLCStage.REQUIREMENTS,
                    SDLCStage.DESIGN,
                    SDLCStage.IMPLEMENTATION,
                    SDLCStage.TESTING,
                    SDLCStage.DEPLOYMENT,
                    SDLCStage.MAINTENANCE,
                ],
                source_files=[
                    "services/SessionMemory/",
                    "services/teamMemorySync/",
                    "services/extractMemories/",
                    "services/autoDream/",
                ],
                inputs="context to remember",
                outputs="retrieved memories",
                dependencies=[],
                is_always_available=True,
                gating="always",
                cost_estimate="low",
                parallel_safe=True,
            )
        )

        self._add(
            Capability(
                name="Plugin-System",
                cap_type=CapabilityType.SERVICE,
                description="Plugin loading, installation, auto-update, policy enforcement",
                stages=[
                    SDLCStage.REQUIREMENTS,
                    SDLCStage.DESIGN,
                    SDLCStage.IMPLEMENTATION,
                    SDLCStage.TESTING,
                    SDLCStage.DEPLOYMENT,
                    SDLCStage.MAINTENANCE,
                ],
                source_files=[
                    "services/plugins/",
                    "plugins/builtinPlugins.ts",
                    "utils/plugins/",
                ],
                inputs="plugin source",
                outputs="loaded plugin capabilities",
                dependencies=[],
                is_always_available=True,
                gating="always",
                cost_estimate="medium",
                parallel_safe=True,
            )
        )

        self._add(
            Capability(
                name="Skill-System",
                cap_type=CapabilityType.SERVICE,
                description="Skill loading, discovery, conditional activation, shell execution",
                stages=[
                    SDLCStage.REQUIREMENTS,
                    SDLCStage.DESIGN,
                    SDLCStage.IMPLEMENTATION,
                    SDLCStage.TESTING,
                    SDLCStage.DEPLOYMENT,
                    SDLCStage.MAINTENANCE,
                ],
                source_files=[
                    "skills/loadSkillsDir.ts",
                    "skills/bundledSkills.ts",
                    "skills/mcpSkillBuilders.ts",
                ],
                inputs="skill name or path",
                outputs="loaded skill content",
                dependencies=[],
                is_always_available=True,
                gating="always",
                cost_estimate="low",
                parallel_safe=True,
            )
        )

        self._add(
            Capability(
                name="Hook-System",
                cap_type=CapabilityType.SERVICE,
                description="PreToolUse, PostToolUse, PermissionRequest, and other lifecycle hooks",
                stages=[
                    SDLCStage.REQUIREMENTS,
                    SDLCStage.DESIGN,
                    SDLCStage.IMPLEMENTATION,
                    SDLCStage.TESTING,
                    SDLCStage.DEPLOYMENT,
                    SDLCStage.MAINTENANCE,
                ],
                source_files=["services/tools/toolHooks.ts", "schemas/hooks.ts"],
                inputs="hook event, hook config",
                outputs="hook result (allow/deny/modify)",
                dependencies=[],
                is_always_available=True,
                gating="always",
                cost_estimate="medium",
                parallel_safe=True,
            )
        )

        self._add(
            Capability(
                name="API-Client",
                cap_type=CapabilityType.SERVICE,
                description="AI Agent API communication with streaming, retry, caching, anti-distillation",
                stages=[
                    SDLCStage.REQUIREMENTS,
                    SDLCStage.DESIGN,
                    SDLCStage.IMPLEMENTATION,
                    SDLCStage.TESTING,
                    SDLCStage.DEPLOYMENT,
                    SDLCStage.MAINTENANCE,
                ],
                source_files=[
                    "services/api/claude.ts",
                    "services/api/withRetry.ts",
                    "services/api/bootstrap.ts",
                ],
                inputs="messages, model, params",
                outputs="streamed response",
                dependencies=[],
                is_always_available=True,
                gating="always",
                cost_estimate="high",
                parallel_safe=True,
            )
        )

        self._add(
            Capability(
                name="Analytics-System",
                cap_type=CapabilityType.SERVICE,
                description="GrowthBook feature flags, Datadog, event logging, telemetry",
                stages=[
                    SDLCStage.REQUIREMENTS,
                    SDLCStage.DESIGN,
                    SDLCStage.IMPLEMENTATION,
                    SDLCStage.TESTING,
                    SDLCStage.DEPLOYMENT,
                    SDLCStage.MAINTENANCE,
                ],
                source_files=[
                    "services/analytics/growthbook.ts",
                    "services/analytics/datadog.ts",
                ],
                inputs="event data",
                outputs="analytics insights",
                dependencies=[],
                is_always_available=True,
                gating="always",
                cost_estimate="low",
                parallel_safe=True,
            )
        )

        self._add(
            Capability(
                name="Voice-System",
                cap_type=CapabilityType.SERVICE,
                description="Voice mode with WebSocket streaming, STT, native audio capture",
                stages=[
                    SDLCStage.REQUIREMENTS,
                    SDLCStage.DESIGN,
                    SDLCStage.IMPLEMENTATION,
                ],
                source_files=["services/voice.ts", "services/voiceStreamSTT.ts"],
                inputs="audio stream",
                outputs="transcribed text",
                dependencies=[],
                is_always_available=False,
                gating="VOICE_MODE",
                cost_estimate="medium",
                parallel_safe=True,
            )
        )

        self._add(
            Capability(
                name="LSP-Service",
                cap_type=CapabilityType.SERVICE,
                description="Language Server Protocol client, manager, diagnostics",
                stages=[SDLCStage.IMPLEMENTATION, SDLCStage.MAINTENANCE],
                source_files=[
                    "services/lsp/client.ts",
                    "services/lsp/manager.ts",
                    "services/lsp/diagnostics.ts",
                ],
                inputs="LSP server config",
                outputs="code intelligence",
                dependencies=[],
                is_always_available=False,
                gating="ENABLE_LSP_TOOL",
                cost_estimate="medium",
                parallel_safe=True,
            )
        )

        self._add(
            Capability(
                name="MagicDocs",
                cap_type=CapabilityType.SERVICE,
                description="Auto-maintained documentation that updates in background",
                stages=[SDLCStage.IMPLEMENTATION, SDLCStage.MAINTENANCE],
                source_files=["services/MagicDocs/magicDocs.ts"],
                inputs="files with # MAGIC DOC: header",
                outputs="updated documentation",
                dependencies=["Agent"],
                is_always_available=True,
                gating="always",
                cost_estimate="medium",
                parallel_safe=True,
            )
        )

        # ==================== TASK TYPES ====================

        self._add(
            Capability(
                name="LocalShellTask",
                cap_type=CapabilityType.AGENT,
                description="Execute shell commands as background tasks",
                stages=[
                    SDLCStage.IMPLEMENTATION,
                    SDLCStage.TESTING,
                    SDLCStage.DEPLOYMENT,
                ],
                source_files=["tasks/LocalShellTask/LocalShellTask.tsx"],
                inputs="shell command",
                outputs="command output",
                dependencies=["Bash"],
                is_always_available=True,
                gating="always",
                cost_estimate="medium",
                parallel_safe=True,
            )
        )

        self._add(
            Capability(
                name="LocalAgentTask",
                cap_type=CapabilityType.AGENT,
                description="Run agents locally with full tool access",
                stages=[
                    SDLCStage.DESIGN,
                    SDLCStage.IMPLEMENTATION,
                    SDLCStage.TESTING,
                    SDLCStage.MAINTENANCE,
                ],
                source_files=["tasks/LocalAgentTask/LocalAgentTask.tsx"],
                inputs="agent config, prompt",
                outputs="agent result",
                dependencies=["Agent"],
                is_always_available=True,
                gating="always",
                cost_estimate="high",
                parallel_safe=True,
            )
        )

        self._add(
            Capability(
                name="RemoteAgentTask",
                cap_type=CapabilityType.AGENT,
                description="Run agents on remote CCR environments",
                stages=[
                    SDLCStage.DESIGN,
                    SDLCStage.DEPLOYMENT,
                    SDLCStage.INFRASTRUCTURE,
                ],
                source_files=["tasks/RemoteAgentTask/RemoteAgentTask.tsx"],
                inputs="agent config, environment ID",
                outputs="remote agent result",
                dependencies=["Agent"],
                is_always_available=False,
                gating="USER_TYPE=ant",
                cost_estimate="high",
                parallel_safe=True,
            )
        )

        self._add(
            Capability(
                name="InProcessTeammateTask",
                cap_type=CapabilityType.AGENT,
                description="Run teammate agents in-process with AsyncLocalStorage isolation",
                stages=[SDLCStage.DESIGN, SDLCStage.IMPLEMENTATION],
                source_files=["tasks/InProcessTeammateTask/InProcessTeammateTask.tsx"],
                inputs="teammate config, prompt",
                outputs="teammate result",
                dependencies=["Agent", "TeamCreate"],
                is_always_available=False,
                gating="isAgentSwarmsEnabled()",
                cost_estimate="high",
                parallel_safe=True,
            )
        )

        self._add(
            Capability(
                name="DreamTask",
                cap_type=CapabilityType.AGENT,
                description="Background dream mode tasks for autonomous exploration",
                stages=[SDLCStage.DESIGN, SDLCStage.IMPLEMENTATION],
                source_files=["tasks/DreamTask/DreamTask.tsx"],
                inputs="dream config",
                outputs="dream result",
                dependencies=["Agent"],
                is_always_available=False,
                gating="KAIROS_DREAM",
                cost_estimate="high",
                parallel_safe=True,
            )
        )

        # ==================== HOOKS ====================

        self._add(
            Capability(
                name="PreToolUse-Hook",
                cap_type=CapabilityType.HOOK,
                description="Intercept tool execution before it runs - can modify input, allow/deny, prevent continuation",
                stages=[
                    SDLCStage.REQUIREMENTS,
                    SDLCStage.DESIGN,
                    SDLCStage.IMPLEMENTATION,
                    SDLCStage.TESTING,
                    SDLCStage.DEPLOYMENT,
                    SDLCStage.MAINTENANCE,
                ],
                source_files=["services/tools/toolHooks.ts"],
                inputs="tool name, tool input",
                outputs="allow/deny/ask/modify",
                dependencies=[],
                is_always_available=True,
                gating="always",
                cost_estimate="low",
                parallel_safe=True,
            )
        )

        self._add(
            Capability(
                name="PostToolUse-Hook",
                cap_type=CapabilityType.HOOK,
                description="Intercept tool execution after completion - can modify output, block continuation",
                stages=[
                    SDLCStage.REQUIREMENTS,
                    SDLCStage.DESIGN,
                    SDLCStage.IMPLEMENTATION,
                    SDLCStage.TESTING,
                    SDLCStage.DEPLOYMENT,
                    SDLCStage.MAINTENANCE,
                ],
                source_files=["services/tools/toolHooks.ts"],
                inputs="tool name, tool output",
                outputs="modified output / block",
                dependencies=["PreToolUse-Hook"],
                is_always_available=True,
                gating="always",
                cost_estimate="low",
                parallel_safe=True,
            )
        )

        self._add(
            Capability(
                name="PermissionRequest-Hook",
                cap_type=CapabilityType.HOOK,
                description="Intercept permission requests before evaluation",
                stages=[
                    SDLCStage.REQUIREMENTS,
                    SDLCStage.DESIGN,
                    SDLCStage.IMPLEMENTATION,
                    SDLCStage.TESTING,
                    SDLCStage.DEPLOYMENT,
                    SDLCStage.MAINTENANCE,
                ],
                source_files=["services/tools/toolHooks.ts"],
                inputs="tool name, tool input",
                outputs="allow/deny/ask",
                dependencies=[],
                is_always_available=True,
                gating="always",
                cost_estimate="low",
                parallel_safe=True,
            )
        )

        self._add(
            Capability(
                name="IDE-Integration-Hook",
                cap_type=CapabilityType.HOOK,
                description="IDE integration for diff viewing, selection sync, logging",
                stages=[SDLCStage.IMPLEMENTATION, SDLCStage.MAINTENANCE],
                source_files=[
                    "hooks/useIDEIntegration.tsx",
                    "hooks/useIdeConnectionStatus.ts",
                    "hooks/useIdeSelection.ts",
                ],
                inputs="IDE events",
                outputs="IDE actions",
                dependencies=[],
                is_always_available=True,
                gating="always",
                cost_estimate="low",
                parallel_safe=True,
            )
        )

        self._add(
            Capability(
                name="Swarm-Permission-Hook",
                cap_type=CapabilityType.HOOK,
                description="Forward permission requests from swarm workers to leader via mailbox",
                stages=[SDLCStage.DESIGN, SDLCStage.IMPLEMENTATION],
                source_files=["hooks/toolPermission/handlers/swarmWorkerHandler.ts"],
                inputs="worker permission request",
                outputs="leader decision",
                dependencies=["Agent", "TeamCreate"],
                is_always_available=False,
                gating="isAgentSwarmsEnabled()",
                cost_estimate="low",
                parallel_safe=True,
            )
        )

        # ==================== COMMANDS ====================

        self._add(
            Capability(
                name="plan-command",
                cap_type=CapabilityType.COMMAND,
                description="Enter/exit planning mode via /plan command",
                stages=[SDLCStage.REQUIREMENTS, SDLCStage.DESIGN],
                source_files=["commands/plan/plan.tsx"],
                inputs="optional description",
                outputs="plan mode state",
                dependencies=["EnterPlanMode", "ExitPlanMode"],
                is_always_available=True,
                gating="always",
                cost_estimate="low",
                parallel_safe=False,
            )
        )

        self._add(
            Capability(
                name="agents-command",
                cap_type=CapabilityType.COMMAND,
                description="View and manage agent teams via /agents command",
                stages=[SDLCStage.DESIGN, SDLCStage.IMPLEMENTATION],
                source_files=["commands/agents/agents.tsx"],
                inputs="none",
                outputs="agent list",
                dependencies=["Agent"],
                is_always_available=True,
                gating="always",
                cost_estimate="low",
                parallel_safe=True,
            )
        )

        self._add(
            Capability(
                name="mcp-command",
                cap_type=CapabilityType.COMMAND,
                description="Manage MCP servers via /mcp command",
                stages=[
                    SDLCStage.REQUIREMENTS,
                    SDLCStage.DESIGN,
                    SDLCStage.IMPLEMENTATION,
                    SDLCStage.DEPLOYMENT,
                ],
                source_files=["commands/mcp/mcp.tsx"],
                inputs="mcp action",
                outputs="mcp status",
                dependencies=["MCP-System"],
                is_always_available=True,
                gating="always",
                cost_estimate="low",
                parallel_safe=True,
            )
        )

        self._add(
            Capability(
                name="plugin-command",
                cap_type=CapabilityType.COMMAND,
                description="Manage plugins via /plugin command",
                stages=[
                    SDLCStage.REQUIREMENTS,
                    SDLCStage.DESIGN,
                    SDLCStage.IMPLEMENTATION,
                    SDLCStage.DEPLOYMENT,
                ],
                source_files=["commands/plugin/ManagePlugins.tsx"],
                inputs="plugin action",
                outputs="plugin status",
                dependencies=["Plugin-System"],
                is_always_available=True,
                gating="always",
                cost_estimate="low",
                parallel_safe=True,
            )
        )

        self._add(
            Capability(
                name="commit-command",
                cap_type=CapabilityType.COMMAND,
                description="Create git commits with AI-generated messages via /commit",
                stages=[SDLCStage.IMPLEMENTATION, SDLCStage.DEPLOYMENT],
                source_files=["commands/commit.ts"],
                inputs="optional message",
                outputs="commit hash",
                dependencies=["Bash"],
                is_always_available=True,
                gating="always",
                cost_estimate="low",
                parallel_safe=False,
            )
        )

        self._add(
            Capability(
                name="diff-command",
                cap_type=CapabilityType.COMMAND,
                description="View git diffs via /diff",
                stages=[
                    SDLCStage.IMPLEMENTATION,
                    SDLCStage.TESTING,
                    SDLCStage.MAINTENANCE,
                ],
                source_files=["commands/diff/diff.tsx"],
                inputs="optional file path",
                outputs="diff content",
                dependencies=["Bash"],
                is_always_available=True,
                gating="always",
                cost_estimate="low",
                parallel_safe=True,
            )
        )

        self._add(
            Capability(
                name="review-command",
                cap_type=CapabilityType.COMMAND,
                description="Review code changes via /review",
                stages=[SDLCStage.TESTING, SDLCStage.MAINTENANCE],
                source_files=["commands/review/review.tsx"],
                inputs="optional PR number",
                outputs="review result",
                dependencies=["Bash", "Agent"],
                is_always_available=True,
                gating="always",
                cost_estimate="medium",
                parallel_safe=True,
            )
        )

        self._add(
            Capability(
                name="compact-command",
                cap_type=CapabilityType.COMMAND,
                description="Trigger context compaction via /compact",
                stages=[
                    SDLCStage.REQUIREMENTS,
                    SDLCStage.DESIGN,
                    SDLCStage.IMPLEMENTATION,
                    SDLCStage.TESTING,
                    SDLCStage.DEPLOYMENT,
                    SDLCStage.MAINTENANCE,
                ],
                source_files=["commands/compact/compact.tsx"],
                inputs="none",
                outputs="compaction confirmation",
                dependencies=["Compact-System"],
                is_always_available=True,
                gating="always",
                cost_estimate="low",
                parallel_safe=True,
            )
        )

        self._add(
            Capability(
                name="model-command",
                cap_type=CapabilityType.COMMAND,
                description="Switch AI models via /model",
                stages=[
                    SDLCStage.REQUIREMENTS,
                    SDLCStage.DESIGN,
                    SDLCStage.IMPLEMENTATION,
                    SDLCStage.TESTING,
                    SDLCStage.DEPLOYMENT,
                    SDLCStage.MAINTENANCE,
                ],
                source_files=["commands/model/model.tsx"],
                inputs="model name",
                outputs="model confirmation",
                dependencies=[],
                is_always_available=True,
                gating="always",
                cost_estimate="low",
                parallel_safe=True,
            )
        )

    def _add(self, cap: Capability):
        self.capabilities[cap.name] = cap

    def get_by_stage(self, stage: SDLCStage) -> List[Capability]:
        """Get all capabilities for a given SDLC stage."""
        return [c for c in self.capabilities.values() if stage in c.stages]

    def get_by_type(self, cap_type: CapabilityType) -> List[Capability]:
        """Get all capabilities of a given type."""
        return [c for c in self.capabilities.values() if c.cap_type == cap_type]

    def get_available(self) -> List[Capability]:
        """Get all always-available capabilities."""
        return [c for c in self.capabilities.values() if c.is_always_available]

    def get_gated(self) -> List[Capability]:
        """Get all gated capabilities."""
        return [c for c in self.capabilities.values() if not c.is_always_available]

    def get_by_name(self, name: str) -> Optional[Capability]:
        """Get a capability by name."""
        return self.capabilities.get(name)

    def get_parallel_safe(self, stage: SDLCStage) -> List[Capability]:
        """Get parallel-safe capabilities for a stage."""
        return [c for c in self.get_by_stage(stage) if c.parallel_safe]

    def get_dependencies(self, cap_name: str) -> List[Capability]:
        """Get dependencies for a capability."""
        cap = self.get_by_name(cap_name)
        if not cap:
            return []
        return [
            self.capabilities[d] for d in cap.dependencies if d in self.capabilities
        ]

    def get_for_workflow(self, stages: List[SDLCStage]) -> List[Capability]:
        """Get all capabilities needed for a workflow spanning multiple stages."""
        caps = set()
        for stage in stages:
            for cap in self.get_by_stage(stage):
                caps.add(cap.name)
                # Add dependencies
                for dep_name in cap.dependencies:
                    if dep_name in self.capabilities:
                        caps.add(dep_name)
        return [self.capabilities[n] for n in caps]

    def to_dict(self) -> dict:
        """Export registry as dictionary."""
        return {
            name: {
                "type": cap.cap_type.value,
                "description": cap.description,
                "stages": [s.value for s in cap.stages],
                "source_files": cap.source_files,
                "inputs": cap.inputs,
                "outputs": cap.outputs,
                "dependencies": cap.dependencies,
                "always_available": cap.is_always_available,
                "gating": cap.gating,
                "cost": cap.cost_estimate,
                "parallel_safe": cap.parallel_safe,
            }
            for name, cap in self.capabilities.items()
        }

    def summary(self) -> str:
        """Generate a human-readable summary."""
        lines = [
            "Capability Registry Summary",
            "=" * 40,
            "Total capabilities: %d" % len(self.capabilities),
            "",
            "By type:",
        ]
        for cap_type in CapabilityType:
            count = len(self.get_by_type(cap_type))
            lines.append("  %s: %d" % (cap_type.value, count))

        lines.append("")
        lines.append("By stage:")
        for stage in SDLCStage:
            count = len(self.get_by_stage(stage))
            lines.append("  %s: %d" % (stage.value, count))

        lines.append("")
        lines.append("Always available: %d" % len(self.get_available()))
        lines.append("Gated: %d" % len(self.get_gated()))

        return "\n".join(lines)
