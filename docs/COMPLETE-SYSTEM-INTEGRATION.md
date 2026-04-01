# AgentOS — Complete System Integration

## How Everything Connects

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER PROMPT                                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  1. PROMPT ENHANCER                                                         │
│  - Clarity scoring (0-8)                                                    │
│  - Self-enhance if 3-6, ask questions if 0-2, execute directly if 7-8       │
│  - Output: Enhanced task specification                                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  2. TASK CLASSIFIER                                                         │
│  - Classifies: type, complexity, domain, estimated files                    │
│  - Selects relevant skills from 27 available                                │
│  - Output: Classification result with confidence scores                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  3. WORKFLOW COMPOSER                                                       │
│  - Selects workflow template (7 templates)                                  │
│  - Adapts for complexity, domain, availability                              │
│  - Enforces 5-25 subagent bounds                                            │
│  - Output: Composed workflow with phases, capabilities, dependencies        │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  4. EXECUTION ENGINE (Ralph Loop)                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Phase 1: Setup (sequential)                                         │   │
│  │ Phase 2: Core (parallel, 5-25 subagents)                            │   │
│  │ Phase 3: Quality (parallel)                                         │   │
│  │ Each phase: Plan→Execute→Review→Learn→Improve                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  - Concurrent tools run in parallel (FileRead, Grep, Glob, WebFetch)       │
│  - Serial tools run one at a time (FileEdit, FileWrite, Bash)              │
│  - Output: Phase results with adaptations                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  5. ADAPTATION LAYER                                                        │
│  - Monitors execution for failures                                          │
│  - Substitutes failed capabilities                                          │
│  - Adjusts parallelism based on error rates                                 │
│  - Enriches context with successful outputs                                 │
│  - Switches workflows on persistent failures                                │
│  - Output: Adapted execution plan                                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  6. VERIFICATION (Superpowers)                                              │
│  - Iron Laws: Absolute rules that override all other instructions           │
│  - Hard Gates: XML-tagged checkpoints that block progression                │
│  - Anti-Slop: Specific patterns to avoid with good/bad examples             │
│  - Checklists: Every item must be completed and verified                    │
│  - Output: Verified result or rejection with reasons                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  7. DELIVERY & PERSISTENCE                                                  │
│  - Output: Final result with documentation                                  │
│  - Session JSONL: One line per turn appended to .agent-os/sessions/         │
│  - Session Memory: Updated when thresholds met (tokens ≥10K, growth ≥5K)    │
│  - Session State: Updated after each significant action                     │
│  - File Cache: Updated after each file read/modify                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

## MCP Integration Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MCP SERVER DISCOVERY                               │
│                                                                              │
│  6 Scopes (checked in order):                                                │
│  1. Managed/policy (enterprise-controlled)                                   │
│  2. User-level (~/.claude/mcp.json)                                          │
│  3. Project-level (.claude/mcp.json)                                         │
│  4. Plugin-provided (from plugin manifests)                                  │
│  5. Additional directories (--add-dir paths)                                 │
│  6. Legacy locations (backward compat)                                       │
│                                                                              │
│  Server Formats:                                                             │
│  - .mcp.json files                                                           │
│  - Plugin manifest entries                                                   │
│  - MCPB (MCP Bundle) files                                                   │
│  - Inline server configs                                                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          MCP SERVER LIFECYCLE                                │
│                                                                              │
│  Start:                                                                      │
│  1. Load server config from scope                                            │
│  2. Validate config against schema                                           │
│  3. Check allowlists (enterprise policy)                                     │
│  4. Authenticate (OAuth, API key, none)                                      │
│  5. Start server process (stdio, SSE, HTTP, WebSocket)                       │
│  6. Register tools from server                                               │
│  7. Add tools to tool pool (deferred loading)                                │
│                                                                              │
│  Running:                                                                    │
│  - Keepalive with periodic pings                                             │
│  - OAuth token refresh (15-min cache, session expiry detection)              │
│  - Channel push notifications (6-layer gate chain)                           │
│  - Tool call routing (built-in + MCP merge, deduplication)                   │
│                                                                              │
│  Stop:                                                                       │
│  1. SIGINT → SIGTERM → SIGKILL escalation                                    │
│  2. Exponential backoff on restart                                           │
│  3. Batched state updates                                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          MCP TOOL INTEGRATION                                │
│                                                                              │
│  Tool Assembly Pipeline:                                                     │
│  1. Load all built-in tools                                                  │
│  2. Load all MCP server tools (deferred)                                     │
│  3. Merge: built-in wins over MCP on name collision                          │
│  4. Strip server prefix from MCP tool names                                  │
│  5. Filter by deny rules                                                     │
│  6. Return assembled tool pool                                               │
│                                                                              │
│  Deferred Loading:                                                           │
│  - MCP tools NOT loaded at startup                                           │
│  - Tools loaded on-demand when first needed                                  │
│  - ToolSearch discovers tools agent doesn't know about                       │
│  - Zero performance cost until tools are actually used                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Self-Healing Memory System

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SELF-HEALING MEMORY ARCHITECTURE                      │
│                                                                              │
│  Detection Layer:                                                            │
│  ├── 12-dimensional cache break detection                                   │
│  ├── Stale extraction detection (>1min = stale, >15s = timeout)             │
│  ├── Tool result pairing verification                                       │
│  ├── Message chain continuity (headUuid, anchorUuid, tailUuid)              │
│  └── Circuit breaker at 3 failures                                          │
│                                                                              │
│  Recovery Layer:                                                             │
│  ├── PTL retry with self-healing head truncation (marker-based, 20% fallback)│
│  ├── Retry with exponential backoff + jitter (500ms base, 10 retries)       │
│  ├── OAuth token auto-refresh on 401/403                                    │
│  ├── 90-second idle watchdog on streams                                     │
│  └── Crashed process restart (3-stage shutdown, LSP restart config)         │
│                                                                              │
│  Memory Preservation:                                                        │
│  ├── Session memory updated on thresholds (not intervals)                   │
│  ├── Context preserved across compactions via session memory                │
│  ├── File-read deduplication prevents redundant processing                  │
│  └── JSONL session logs enable exact state reconstruction                   │
│                                                                              │
│  Continuous Improvement:                                                     │
│  ├── Ralph Loop: Each cycle produces better output than last                │
│  ├── Adaptation Layer: Learns from execution failures                       │
│  ├── Session Memory: Accumulates learnings over time                        │
│  └── Execution History: Tracks what worked, what didn't                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

## How AgentOS Keeps Improving Itself

### 1. Ralph Loop (Iterative Self-Improvement)
```
Plan → Execute → Review → Learn → Improve → Plan → ...
```
Each cycle produces better output because the agent learns from its own mistakes. The "Learn" phase extracts lessons, the "Improve" phase applies them to the next cycle.

### 2. Session Memory Accumulation
```
Session 1: Learn X about this codebase
Session 2: Remember X, learn Y
Session 3: Remember X+Y, learn Z
...
Session N: Remember X+Y+Z+...+N, learn N+1
```
Session memory is preserved across compactions and sessions. The agent accumulates knowledge over time — it never starts from scratch.

### 3. Adaptation Layer Learning
```
Execution 1: Capability A failed → substituted with B
Execution 2: Capability B worked → record success
Execution 3: Capability A failed again → prefer B
...
Execution N: Always use B for this scenario
```
The adaptation layer tracks what works and what doesn't, building a knowledge base of successful substitutions.

### 4. Execution History Analysis
```
History:
- Phase 1: Setup → 5 min, 0 failures
- Phase 2: Core → 30 min, 2 failures, 3 adaptations
- Phase 3: Quality → 10 min, 1 failure, 1 adaptation

Insights:
- Phase 2 has highest failure rate → needs more retries
- Capability X fails often → substitute with Y
- Parallel execution saves 60% time → maximize parallelism
```
Execution history is analyzed to identify patterns and optimize future workflows.

### 5. Parameter Optimization
The system continuously optimizes:
- **Subagent count**: Adjusts based on task complexity (5-25 bounds)
- **Retry count**: Adjusts based on failure rates
- **Timeout values**: Adjusts based on execution times
- **Parallelism**: Adjusts based on error rates
- **Tool selection**: Adjusts based on success rates

## Compatibility

### Agent Platforms
| Platform | Compatibility | Notes |
|----------|--------------|-------|
| **Claude Code** | Full | Native integration, all skills work |
| **Cursor** | Full | Skills as rules, WORKER.md as .cursorrules |
| **Codex** | Full | Skills as skills, WORKER.md as project instructions |
| **Cline** | Full | Skills as skills, WORKER.md as .clinerules |
| **Continue** | Full | Skills as instructions |
| **Aider** | Full | Skills as instructions, WORKER.md as .aider.instructions.md |
| **Any LLM Agent** | Full | Skills can be pasted into system prompt |

### MCP Servers
| Server Type | Compatibility | Notes |
|-------------|--------------|-------|
| **stdio** | Full | Standard MCP transport |
| **SSE** | Full | Server-sent events |
| **HTTP** | Full | HTTP transport |
| **WebSocket** | Full | WebSocket transport |
| **OAuth** | Full | OAuth authentication |
| **API Key** | Full | API key authentication |

### External Systems
| System | Integration Method | Notes |
|--------|-------------------|-------|
| **Databases** | MCP servers | Deferred loading, zero cost until used |
| **Cloud Providers** | MCP servers | AWS, GCP, Azure via MCP |
| **CI/CD** | MCP servers | GitHub Actions, GitLab CI, Jenkins |
| **Version Control** | Built-in tools | Git operations via Bash tool |
| **Package Managers** | Built-in tools | npm, pip, cargo, go via Bash tool |
| **Testing Frameworks** | Built-in tools | pytest, jest, cargo test via Bash tool |

## Key Insights

1. **Everything is event-driven** — No timers, no intervals. Updates happen when thresholds are met or events occur.

2. **Context accumulates** — Sessions are never auto-pruned. Knowledge builds over time.

3. **Self-healing is multi-layer** — Detection → Recovery → Preservation → Improvement. Each layer handles different failure modes.

4. **MCP is deferred** — Zero cost until tools are actually needed. Unlimited external capabilities.

5. **Improvement is automatic** — Ralph Loop + Session Memory + Adaptation Layer + Execution History = continuous self-improvement.
