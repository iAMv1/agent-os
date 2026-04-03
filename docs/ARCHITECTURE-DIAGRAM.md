# AgentOS Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                         AGENTOS                                          │
│                              Universal AI Agent Operating System                         │
│                                                                                          │
│  ┌───────────────────────────────────────────────────────────────────────────────────┐  │
│  │                              ENTRY POINTS                                          │  │
│  │                                                                                   │  │
│  │  ┌──────────────────────┐              ┌──────────────────────────────┐           │  │
│  │  │  workflow-engine.py  │              │      AgentOS Orchestrator     │           │  │
│  │  │   (CLI / Pipeline)   │              │    (Runtime / Session)        │           │  │
│  │  │                      │              │                               │           │  │
│  │  │  Input: task string  │              │  Input: user messages,        │           │  │
│  │  │  Output: workflow    │              │         tool results,         │           │  │
│  │  │  plan + instructions │              │         git operations        │           │  │
│  │  └──────────┬───────────┘              └───────────────┬───────────────┘           │  │
│  └─────────────┼──────────────────────────────────────────┼───────────────────────────┘  │
│                │                                          │                               │
│  ══════════════╪══════════════════════════════════════════╪═════════════════════════════  │
│  ENGINE LAYER  │  (Task → Workflow → Execution Pipeline)  │                               │
│  ══════════════╪══════════════════════════════════════════╪═════════════════════════════  │
│                │                                          │                               │
│  ┌─────────────▼───────────┐                              │                               │
│  │    TASK CLASSIFIER      │                              │                               │
│  │  (task_classifier.py)   │                              │                               │
│  │                         │                              │                               │
│  │  Input: task string     │                              │                               │
│  │  Output: Classification │                              │                               │
│  │                         │                              │                               │
│  │  ┌───────────────────┐  │                              │                               │
│  │  │ Regex pattern     │  │                              │                               │
│  │  │ matching engine   │  │                              │                               │
│  │  └────────┬──────────┘  │                              │                               │
│  │           │              │                              │                               │
│  │  ┌────────▼──────────┐  │                              │                               │
│  │  │ 6 TASK TYPES      │  │                              │                               │
│  │  │ requirements_     │  │                              │                               │
│  │  │   gathering       │  │                              │                               │
│  │  │ architecture_     │  │                              │                               │
│  │  │   design          │  │                              │                               │
│  │  │ implementation    │  │                              │                               │
│  │  │ testing_qa        │  │                              │                               │
│  │  │ deployment_devops │  │                              │                               │
│  │  │ maintenance_      │  │                              │                               │
│  │  │   monitoring      │  │                              │                               │
│  │  └────────┬──────────┘  │                              │                               │
│  │           │              │                              │                               │
│  │  ┌────────▼──────────┐  │                              │                               │
│  │  │ 11 DOMAINS        │  │                              │                               │
│  │  │ WEB MOBILE DEVOPS │  │                              │                               │
│  │  │ SECURITY API      │  │                              │                               │
│  │  │ FRONTEND BACKEND  │  │                              │                               │
│  │  │ FULLSTACK CLI     │  │                              │                               │
│  │  │ DATA_ML GENERAL   │  │                              │                               │
│  │  └────────┬──────────┘  │                              │                               │
│  │           │              │                              │                               │
│  │  ┌────────▼──────────┐  │                              │                               │
│  │  │ 8 SDLC STAGES     │  │                              │                               │
│  │  │ REQUIREMENTS      │  │                              │                               │
│  │  │ DESIGN            │  │                              │                               │
│  │  │ IMPLEMENTATION    │  │                              │                               │
│  │  │ TESTING           │  │                              │                               │
│  │  │ DEPLOYMENT        │  │                              │                               │
│  │  │ MAINTENANCE       │  │                              │                               │
│  │  │ COLLABORATION     │  │                              │                               │
│  │  │ INFRASTRUCTURE    │  │                              │                               │
│  │  └────────┬──────────┘  │                              │                               │
│  │           │              │                              │                               │
│  │  ┌────────▼──────────┐  │                              │                               │
│  │  │ 3 COMPLEXITY      │  │                              │                               │
│  │  │ SIMPLE MEDIUM     │  │                              │                               │
│  │  │ COMPLEX           │  │                              │                               │
│  │  └────────┬──────────┘  │                              │                               │
│  │           │              │                              │                               │
│  │  ┌────────▼──────────┐  │                              │                               │
│  │  │ Confidence score  │  │                              │                               │
│  │  │ Keywords list     │  │                              │                               │
│  │  │ File count est.   │  │                              │                               │
│  │  └───────────────────┘  │                              │                               │
│  └─────────────┬───────────┘                              │                               │
│                │ ClassificationResult                     │                               │
│                ▼                                          │                               │
│  ┌───────────────────────────┐                            │                               │
│  │   CAPABILITY REGISTRY     │                            │                               │
│  │ (capability_registry.py)  │                            │                               │
│  │                           │                            │                               │
│  │  71 Capabilities:         │                            │                               │
│  │  ┌─────────────────────┐  │                            │                               │
│  │  │ 35 TOOLS            │  │                            │                               │
│  │  │ FileRead FileEdit   │  │                            │                               │
│  │  │ FileWrite Bash Grep │  │                            │                               │
│  │  │ Glob WebSearch      │  │                            │                               │
│  │  │ WebFetch TodoWrite  │  │                            │                               │
│  │  │ AskUserQuestion     │  │                            │                               │
│  │  │ Skill Agent LSP     │  │                            │                               │
│  │  │ NotebookEdit        │  │                            │                               │
│  │  │ PowerShell          │  │                            │                               │
│  │  │ ScheduleCron        │  │                            │                               │
│  │  │ RemoteTrigger       │  │                            │                               │
│  │  │ ToolSearch Config   │  │                            │                               │
│  │  │ Brief Sleep         │  │                            │                               │
│  │  │ SyntheticOutput     │  │                            │                               │
│  │  │ TaskCreate/Get/List │  │                            │                               │
│  │  │ TaskUpdate/Stop/Oup │  │                            │                               │
│  │  │ TeamCreate/Delete   │  │                            │                               │
│  │  │ SendMessage         │  │                            │                               │
│  │  └─────────────────────┘  │                            │                               │
│  │  ┌─────────────────────┐  │                            │                               │
│  │  │ 11 AGENTS           │  │                            │                               │
│  │  │ general-purpose     │  │                            │                               │
│  │  │ Explore/Plan/       │  │                            │                               │
│  │  │ verification/       │  │                            │                               │
│  │  │ fork/code-guide     │  │                            │                               │
│  │  │ LocalShellTask      │  │                            │                               │
│  │  │ LocalAgentTask      │  │                            │                               │
│  │  │ RemoteAgentTask     │  │                            │                               │
│  │  │ InProcessTeammate   │  │                            │                               │
│  │  │ DreamTask           │  │                            │                               │
│  │  └─────────────────────┘  │                            │                               │
│  │  ┌─────────────────────┐  │                            │                               │
│  │  │ 11 SERVICES         │  │                            │                               │
│  │  │ MCP/Compact/Memory  │  │                            │                               │
│  │  │ Plugin/Skill/Hook   │  │                            │                               │
│  │  │ API/Analytics/Voice │  │                            │                               │
│  │  │ LSP/MagicDocs       │  │                            │                               │
│  │  └─────────────────────┘  │                            │                               │
│  │  ┌─────────────────────┐  │                            │                               │
│  │  │ 5 HOOKS             │  │                            │                               │
│  │  │ PreToolUse          │  │                            │                               │
│  │  │ PostToolUse         │  │                            │                               │
│  │  │ PermissionRequest   │  │                            │                               │
│  │  │ IDE-Integration     │  │                            │                               │
│  │  │ Swarm-Permission    │  │                            │                               │
│  │  └─────────────────────┘  │                            │                               │
│  │  ┌─────────────────────┐  │                            │                               │
│  │  │ 9 COMMANDS          │  │                            │                               │
│  │  │ plan/agents/mcp     │  │                            │                               │
│  │  │ plugin/commit/diff  │  │                            │                               │
│  │  │ review/compact/model│  │                            │                               │
│  │  └─────────────────────┘  │                            │                               │
│  │                           │                            │                               │
│  │  Metadata per capability: │                            │                               │
│  │  - SDLC stage membership  │                            │                               │
│  │  - Input/output specs     │                            │                               │
│  │  - Dependency graph       │                            │                               │
│  │  - Cost estimate          │                            │                               │
│  │  - Parallel-safe flag     │                            │                               │
│  │  - Gating flags           │                            │                               │
│  └─────────────┬─────────────┘                            │                               │
│                │ filtered capabilities                    │                               │
│                ▼                                          │                               │
│  ┌───────────────────────────┐                            │                               │
│  │    WORKFLOW COMPOSER      │                            │                               │
│  │  (workflow_composer.py)   │                            │                               │
│  │                           │                            │                               │
│  │  7 Workflow Templates:    │                            │                               │
│  │  ┌─────────────────────┐  │                            │                               │
│  │  │ 1. Requirements     │  │                            │                               │
│  │  │    Gathering        │  │                            │                               │
│  │  │    (3 phases)       │  │                            │                               │
│  │  │ 2. Architecture     │  │                            │                               │
│  │  │    & Design         │  │                            │                               │
│  │  │    (3 phases)       │  │                            │                               │
│  │  │ 3. Implementation   │  │                            │                               │
│  │  │    (3 phases)       │  │                            │                               │
│  │  │ 4. Testing & QA     │  │                            │                               │
│  │  │    (3 phases)       │  │                            │                               │
│  │  │ 5. Deployment       │  │                            │                               │
│  │  │    & DevOps         │  │                            │                               │
│  │  │    (3 phases)       │  │                            │                               │
│  │  │ 6. Maintenance      │  │                            │                               │
│  │  │    & Monitoring     │  │                            │                               │
│  │  │    (3 phases)       │  │                            │                               │
│  │  │ 7. Full SDLC        │  │                            │                               │
│  │  │    Lifecycle        │  │                            │                               │
│  │  │    (4 phases)       │  │                            │                               │
│  │  └─────────────────────┘  │                            │                               │
│  │                           │                            │                               │
│  │  Adaptation Pipeline:     │                            │                               │
│  │  1. Select template       │                            │                               │
│  │     by task_type          │                            │                               │
│  │  2. Adapt for complexity  │                            │                               │
│  │     (merge/split phases)  │                            │                               │
│  │  3. Adapt for domain      │                            │                               │
│  │     (add optional caps)   │                            │                               │
│  │  4. Filter by             │                            │                               │
│  │     availability          │                            │                               │
│  └─────────────┬─────────────┘                            │                               │
│                │ Workflow (phases + capabilities)         │                               │
│                ▼                                          │                               │
│  ┌──────────────────────────────────────────────────────┐ │                               │
│  │               EXECUTION ENGINE                        │ │                               │
│  │            (execution_engine.py)                      │ │                               │
│  │                                                      │ │                               │
│  │  For each WorkflowPhase:                             │ │                               │
│  │  ┌────────────────────────────────────────────────┐  │ │                               │
│  │  │ 1. Resolve capabilities from registry          │  │ │                               │
│  │  │ 2. Split parallel_safe vs sequential           │  │ │                               │
│  │  │ 3. Execute each capability:                    │  │ │                               │
│  │  │    ┌─────────────────────────────────────────┐ │  │ │                               │
│  │  │    │ _execute_tool()     → tool instructions │ │  │ │                               │
│  │  │    │ _execute_agent()    → agent spawn cmds  │ │  │ │                               │
│  │  │    │ _execute_service()  → service usage     │ │  │ │                               │
│  │  │    │ _execute_hook()     → hook setup        │ │  │ │                               │
│  │  │    │ _execute_command()  → command execution │ │  │ │                               │
│  │  │    └─────────────────────────────────────────┘ │  │ │                               │
│  │  │ 4. Call adaptation_layer.adapt_phase()         │  │ │                               │
│  │  │ 5. Track errors, adaptations, outputs          │  │ │                               │
│  │  │ 6. Handle on_failure (abort/continue/skip)     │  │ │                               │
│  │  └────────────────────────────────────────────────┘  │ │                               │
│  │                                                      │ │                               │
│  │  Output: WorkflowResult                              │ │                               │
│  │  - status (PENDING/RUNNING/COMPLETED/FAILED)        │ │                               │
│  │  - phase_results[]                                  │ │                               │
│  │  - adaptations_made[]                               │ │                               │
│  │  - final_output (markdown summary)                  │ │                               │
│  └──────────────────────┬───────────────────────────────┘ │                               │
│                         │                                 │                               │
│  ┌──────────────────────▼───────────────────────────────┐ │                               │
│  │              ADAPTATION LAYER                         │ │                               │
│  │            (adaptation_layer.py)                      │ │                               │
│  │                                                      │ │                               │
│  │  Per-phase adaptation strategies:                    │ │                               │
│  │  ┌────────────────────────────────────────────────┐  │ │                               │
│  │  │ 1. CAPABILITY SUBSTITUTION                     │  │ │                               │
│  │  │    On error → lookup substitute from map       │  │ │                               │
│  │  │    LSP→[Grep,FileRead] WebSearch↔WebFetch      │  │ │                               │
│  │  │    PowerShell→Bash TeamCreate→Agent            │  │ │                               │
│  │  │                                                 │  │ │                               │
│  │  │ 2. CONTEXT ENRICHMENT                          │  │ │                               │
│  │  │    Store successful outputs in context         │  │ │                               │
│  │  │    Key: {cap_name}_output                      │  │ │                               │
│  │  │                                                 │  │ │                               │
│  │  │ 3. PARALLELISM CHANGE                          │  │ │                               │
│  │  │    If error_rate > 50% → reduce_parallelism    │  │ │                               │
│  │  │                                                 │  │ │                               │
│  │  │ 4. WORKFLOW SWITCH                             │  │ │                               │
│  │  │    If failure_rate > 60% over 10+ attempts     │  │ │                               │
│  │  │    → switch_to_simple_workflow                 │  │ │                               │
│  │  │                                                 │  │ │                               │
│  │  │ 5. TIMEOUT TRACKING                            │  │ │                               │
│  │  │    Track execution times per capability        │  │ │                               │
│  │  └────────────────────────────────────────────────┘  │ │                               │
│  │                                                      │ │                               │
│  │  State tracking:                                     │ │                               │
│  │  - failure_counts: Dict[cap_name, int]              │ │                               │
│  │  - success_counts: Dict[cap_name, int]              │ │                               │
│  │  - execution_metrics: Dict[cap_name, List[float]]   │ │                               │
│  │  - adaptations: List[Adaptation]                    │ │                               │
│  └──────────────────────────────────────────────────────┘ │                               │
│                                                           │                               │
│  ════════════════════════════════════════════════════════╪══════════════════════════════  │
│  AGENTOS LAYER  │  (Runtime Infrastructure)              │                               │
│  ════════════════════════════════════════════════════════╪══════════════════════════════  │
│                                                           │                               │
│  ┌───────────────────────────────────────────────────────┼─────────────────────────────┐  │
│  │                    AgentOS Orchestrator               │                             │  │
│  │                   (agentos/orchestrator.py)           │                             │  │
│  │                                                       │                             │  │
│  │  Subsystems:                                          │                             │  │
│  │  ┌──────────────┐ ┌──────────────┐ ┌───────────────┐  │                             │  │
│  │  │   Session    │ │   Memory     │ │   Context     │  │                             │  │
│  │  │  Manager     │ │  Extractor   │ │   Manager     │  │                             │  │
│  │  │              │ │              │ │               │  │                             │  │
│  │  │ JSONL files  │ │ Threshold-   │ │ SHA256 hash   │  │                             │  │
│  │  │ per session  │ │ based memory │ │ dedup cache   │  │                             │  │
│  │  │              │ │ extraction   │ │ Large output  │  │                             │  │
│  │  │ create/      │ │              │ │ → disk write  │  │                             │  │
│  │  │ continue/    │ │ Triggers:    │ │ Preview: 50   │  │                             │  │
│  │  │ resume/fork  │ │ tokens≥10K   │ │ lines         │  │                             │  │
│  │  │              │ │ growth≥5K    │ │ Thresholds:   │  │                             │  │
│  │  │ Format:      │ │ tool_calls≥3 │ │ 2000 lines    │  │                             │  │
│  │  │ {turn,ts,    │ │              │ │ 51200 bytes   │  │                             │  │
│  │  │  role,content}│ │              │ │               │  │                             │  │
│  │  └──────┬───────┘ └──────┬───────┘ └───────┬───────┘  │                             │  │
│  │         │                │                  │          │                             │  │
│  │  ┌──────▼────────────────▼──────────────────▼───────┐  │                             │  │
│  │  │              MESSAGE PIPELINE                     │  │                             │  │
│  │  │                                                   │  │                             │  │
│  │  │  add_user_message() → SessionManager.append_turn()│  │                             │  │
│  │  │                        → SessionMemory.check()    │  │                             │  │
│  │  │                        → maybe extract memory     │  │                             │  │
│  │  │                                                   │  │                             │  │
│  │  │  add_tool_result() → ContextManager.handle_large()│  │                             │  │
│  │  │                        → SessionManager.append()  │  │                             │  │
│  │  │                                                   │  │                             │  │
│  │  │  execute_with_healing() → SelfHealing pipeline    │  │                             │  │
│  │  └──────────────────────┬────────────────────────────┘  │                             │  │
│  │                         │                               │                             │  │
│  │  ┌──────────────────────▼───────────────────────────┐   │                             │  │
│  │  │            SELF-HEALING SYSTEM                    │   │                             │  │
│  │  │         (healing/self_healing.py)                 │   │                             │  │
│  │  │                                                  │   │                             │  │
│  │  │  Retry with Exponential Backoff:                 │   │                             │  │
│  │  │  - max_retries: 10                               │   │                             │  │
│  │  │  - base_delay: 500ms                             │   │                             │  │
│  │  │  - max_delay: 300s (5 min)                       │   │                             │  │
│  │  │  - jitter: ±10%                                  │   │                             │  │
│  │  │  - formula: delay = base × 2^attempt ± jitter    │   │                             │  │
│  │  │                                                  │   │                             │  │
│  │  │  Circuit Breaker Pattern:                        │   │                             │  │
│  │  │  - CLOSED: normal operation                      │   │                             │  │
│  │  │  - OPEN: after 3 failures (60s timeout)          │   │                             │  │
│  │  │  - HALF_OPEN: test with 1 call                   │   │                             │  │
│  │  │                                                  │   │                             │  │
│  │  │  Pipeline:                                       │   │                             │  │
│  │  │  circuit_check → retry_with_backoff → fallback   │   │                             │  │
│  │  └──────────────────────────────────────────────────┘   │                             │  │
│  │                                                         │                             │  │
│  │  ┌───────────────────────────────────────────────────┐  │                             │  │
│  │  │               TOOL SYSTEM                          │  │                             │  │
│  │  │           (tools/tool_system.py)                   │  │                             │  │
│  │  │                                                   │  │                             │  │
│  │  │  ToolRegistry:                                    │  │                             │  │
│  │  │  - register_tool(ToolDefinition)                  │  │                             │  │
│  │  │  - get_concurrent_tools() / get_serial_tools()    │  │                             │  │
│  │  │  - merge_mcp_tools(server_name, tools)            │  │                             │  │
│  │  │                                                   │  │                             │  │
│  │  │  ToolExecutor:                                    │  │                             │  │
│  │  │  - partition_tool_calls() → {concurrent, serial}  │  │                             │  │
│  │  │  - execute_concurrent_tools() → parallel exec     │  │                             │  │
│  │  │  - execute_serial_tools() → sequential exec       │  │                             │  │
│  │  │                                                   │  │                             │  │
│  │  │  Safety Classification:                           │  │                             │  │
│  │  │  - CONCURRENT_SAFE: can run in parallel           │  │                             │  │
│  │  │  - SERIAL_ONLY: must run one at a time            │  │                             │  │
│  │  └───────────────────────┬───────────────────────────┘  │                             │  │
│  │                          │                              │                             │  │
│  │  ┌───────────────────────▼───────────────────────────┐  │                             │  │
│  │  │              MCP MANAGER                           │  │                             │  │
│  │  │           (mcp/mcp_manager.py)                     │  │                             │  │
│  │  │                                                   │  │                             │  │
│  │  │  MCPConfig:                                       │  │                             │  │
│  │  │  - Load/save mcp.json config                      │  │                             │  │
│  │  │  - add_server(name, config)                       │  │                             │  │
│  │  │  - register_tools(server, tools)                  │  │                             │  │
│  │  │  - get_all_tools()                                │  │                             │  │
│  │  │                                                   │  │                             │  │
│  │  │  MCPServer (per server):                          │  │                             │  │
│  │  │  - start() → subprocess.Popen(cmd+args, env)      │  │                             │  │
│  │  │  - call_tool() → JSON-RPC over stdin/stdout       │  │                             │  │
│  │  │  - stop() → SIGINT → SIGTERM → SIGKILL            │  │                             │  │
│  │  │                                                   │  │                             │  │
│  │  │  Transport: stdio (subprocess)                    │  │                             │  │
│  │  │  Protocol: JSON-RPC 2.0                           │  │                             │  │
│  │  └───────────────────────────────────────────────────┘  │                             │  │
│  │                                                         │                             │  │
│  │  ┌───────────────────────────────────────────────────┐  │                             │  │
│  │  │               GIT SYSTEM                           │  │                             │  │
│  │  │           (git/git_system.py)                      │  │                             │  │
│  │  │                                                   │  │                             │  │
│  │  │  Core Pattern:                                    │  │                             │  │
│  │  │  exec_file_no_throw() → never raises              │  │                             │  │
│  │  │  Returns: {stdout, stderr, code}                  │  │                             │  │
│  │  │                                                   │  │                             │  │
│  │  │  Operations:                                      │  │                             │  │
│  │  │  - find_git_root() [LRU-cached, 50 entries]       │  │                             │  │
│  │  │  - git_status() → porcelain parsing               │  │                             │  │
│  │  │  - git_diff() → staged/unified diff               │  │                             │  │
│  │  │  - git_log() → formatted commit history           │  │                             │  │
│  │  │  - git_branches() → all branch names              │  │                             │  │
│  │  │  - create_worktree() / remove_worktree()          │  │                             │  │
│  │  │  - git_commit() / git_push() / git_pull()         │  │                             │  │
│  │  │  - get_git_state() → 6-command aggregation        │  │                             │  │
│  │  │  - get_git_stats() → comprehensive report         │  │                             │  │
│  │  │                                                   │  │                             │  │
│  │  │  Safety: --no-optional-locks on read-only ops     │  │                             │  │
│  │  └───────────────────────────────────────────────────┘  │                             │  │
│  └─────────────────────────────────────────────────────────┘                             │  │
│                                                                                           │  │
│  ┌───────────────────────────────────────────────────────────────────────────────────────┐  │
│  │                              DATA FLOW SUMMARY                                         │  │
│  │                                                                                       │  │
│  │  TASK STRING                                                                          │  │
│  │     │                                                                                 │  │
│  │     ▼                                                                                 │  │
│  │  ┌─────────────┐   ClassificationResult   ┌──────────────────┐                       │  │
│  │  │   CLASSIFY  │ ────────────────────────► │    COMPOSE       │                       │  │
│  │  │  (patterns) │                          │   (templates)    │                       │  │
│  │  └─────────────┘                          └────────┬─────────┘                       │  │
│  │                                                   │ Workflow                         │  │
│  │                                                   ▼                                  │  │
│  │  ┌─────────────────┐   WorkflowResult   ┌──────────────────┐                       │  │
│  │  │    ADAPT        │ ◄───────────────── │    EXECUTE       │                       │  │
│  │  │  (substitute)   │   adaptation dict  │  (instructions)  │                       │  │
│  │  └─────────────────┘                    └──────────────────┘                       │  │
│  │                                                   │                                 │  │
│  │                                                   ▼                                 │  │
│  │  ┌───────────────────────────────────────────────────────────┐                      │  │
│  │  │                    OUTPUT                                  │                      │  │
│  │  │  - JSON: full classification + workflow + execution data  │                      │  │
│  │  │  - TEXT: formatted workflow plan + execution instructions │                      │  │
│  │  │  - Markdown: phase-by-phase capability usage guide        │                      │  │
│  │  └───────────────────────────────────────────────────────────┘                      │  │
│  └───────────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                             │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

## Data Structures

### ClassificationResult (output of TaskClassifier)
```
{
  task_type: str              # "implementation", "bug_fix", "refactor", etc.
  sdlc_stages: List[SDLCStage] # [IMPLEMENTATION], [DESIGN, REQUIREMENTS], etc.
  complexity: TaskComplexity   # SIMPLE, MEDIUM, COMPLEX
  domain: Domain               # WEB, API, DEVOPS, SECURITY, etc.
  estimated_files: int         # 3 (simple), 10 (medium), 50 (complex)
  requires_user_input: bool    # detected from task language
  keywords: List[str]          # ["api", "rest", "python", etc.]
  confidence: float            # 0.0 - 1.0
}
```

### Capability (registry entry)
```
{
  name: str                    # "FileRead", "Bash", "general-purpose-agent"
  cap_type: CapabilityType     # TOOL, AGENT, SERVICE, HOOK, COMMAND
  description: str             # what it does
  stages: List[SDLCStage]      # which SDLC stages it applies to
  source_files: List[str]      # where it was extracted from
  inputs: List[str]            # what it needs
  outputs: List[str]           # what it produces
  dependencies: List[str]      # other capabilities it needs
  is_always_available: bool    # true = no gating
  gating: List[str]            # feature flags that gate this capability
  cost_estimate: str           # "low", "medium", "high"
  parallel_safe: bool          # can run alongside other capabilities
}
```

### Workflow (output of Composer)
```
{
  name: str                    # "Implementation", "Testing & QA", etc.
  description: str             # what this workflow does
  stages: List[str]            # SDLC stages covered
  phases: List[WorkflowPhase]  # ordered execution steps
  estimated_duration: str      # "1-3 hours", "2-8 hours", etc.
  estimated_cost: str          # "low", "medium", "high"
  required_capabilities: List[str]
  optional_capabilities: List[str]
  adaptation_rules: Dict[str, str]
}
```

### WorkflowPhase
```
{
  name: str                    # "Setup", "Core Development", etc.
  description: str             # what this phase does
  capabilities: List[str]      # capability names to use
  parallel: bool               # run capabilities in parallel?
  timeout_seconds: int         # phase timeout
  retry_count: int             # retries on failure
  on_failure: str              # "continue", "abort", "skip"
}
```

### WorkflowResult (output of Execution)
```
{
  workflow_name: str
  status: ExecutionStatus      # PENDING, RUNNING, COMPLETED, FAILED
  phase_results: List[PhaseResult]
  total_duration_seconds: float
  adaptations_made: List[str]
  final_output: str            # markdown summary
}
```

## Execution Flow (End-to-End)

```
1. USER INPUT: "Build a REST API for a todo app"
   │
2. TASK CLASSIFIER:
   │  - Regex match against 6 task type patterns → "implementation"
   │  - Regex match against 11 domain patterns → "api"
   │  - Regex match against complexity patterns → "medium"
   │  - Extract keywords → ["api", "rest", "todo"]
   │  - Calculate confidence → 0.6 (60%)
   │  - Estimate files → 10
   │  Output: ClassificationResult
   │
3. CAPABILITY REGISTRY:
   │  - 71 capabilities loaded
   │  - Filter by SDLC stage (implementation) → subset
   │  - Filter by parallel_safe → for parallel execution
   │  Output: filtered capabilities
   │
4. WORKFLOW COMPOSER:
   │  - Select template: "Implementation" (3 phases)
   │  - Adapt for complexity (medium): standard timeouts
   │  - Adapt for domain (api): add API-specific optional caps
   │  - Filter by availability: remove gated capabilities
   │  Output: Workflow with 3 phases, 6 required + 6 optional capabilities
   │
5. EXECUTION ENGINE:
   │  Phase 1: Setup (sequential)
   │    - Resolve: Bash, FileWrite, FileRead, TodoWrite
   │    - Generate instructions for each
   │    - Track: duration, capabilities used, status
   │  Phase 2: Core Development (parallel-safe split)
   │    - Parallel: FileRead, Grep, Glob
   │    - Sequential: FileEdit, FileWrite
   │    - Call adaptation_layer.adapt_phase()
   │  Phase 3: Code Quality (sequential)
   │    - Resolve: TodoWrite, FileRead, Bash
   │    - Generate instructions
   │  Output: WorkflowResult (COMPLETED, 3/3 phases)
   │
6. ADAPTATION LAYER (during execution):
   │  - Monitor errors per capability
   │  - On error: substitute capability (LSP → Grep)
   │  - Track success/failure counts
   │  - If error_rate > 50%: flag reduce_parallelism
   │  - If failure_rate > 60% over 10+ attempts: flag switch_to_simple_workflow
   │  - Enrich context with successful outputs
   │
7. OUTPUT:
   │  JSON mode: full structured data
   │  TEXT mode: formatted workflow plan + execution instructions
   │  - Phase-by-phase capability usage guide
   │  - Registry summary (counts by type)
```

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Regex-based classification** | Fast, no ML dependency, deterministic |
| **Template-based composition** | Predictable workflows, easy to extend |
| **Instruction generation (not execution)** | Agent-agnostic output; works with any AI coding agent |
| **Capability substitution map** | Graceful degradation when capabilities unavailable |
| **Threshold-based memory extraction** | Prevents constant re-extraction; only on significant growth |
| **SHA256 hash deduplication** | Avoids re-reading unchanged files |
| **Large output → disk write** | Prevents context bloat (>2000 lines or >51KB) |
| **Circuit breaker pattern** | Prevents cascading failures; auto-recovery after timeout |
| **Exponential backoff + jitter** | Prevents thundering herd on retry |
| **exec_file_no_throw for git** | Never crashes; graceful degradation on any error |
| **LRU cache for git root** | Avoids repeated filesystem walks |
| **JSONL session format** | Append-only, crash-safe, easy to parse |
