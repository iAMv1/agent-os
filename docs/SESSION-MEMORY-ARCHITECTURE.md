# AgentOS Session Persistence & Memory System

## Architecture

### Where Data Lives

**AgentOS Repository** (what you clone):
```
agent-os/
├── skills/           ← Skill definitions
├── engines/          ← Workflow engines
├── docs/             ← Documentation
└── WORKER.md         ← Project instructions
```

**User's Project** (created at runtime):
```
<project>/.agent-os/
├── sessions/         ← JSONL session logs (accumulated)
│   └── {sessionId}.jsonl
├── memory/           ← Session memory (updated on thresholds)
│   └── session-memory.md
├── session/          ← Current session state (updated every turn)
│   └── current-state.md
└── cache/            ← File hashes (updated on file changes)
    └── file-hashes.json
```

### How Updates Work — Event-Driven, NOT Interval-Based

#### 1. Session JSONL — Updated EVERY Turn
```
When: After every user message and agent response
What: One JSON line appended to .agent-os/sessions/{sessionId}.jsonl
Why: Complete audit trail, enables --continue/--resume/--fork-session
```

Format:
```jsonl
{"turn": 1, "timestamp": "2026-04-01T10:00:00Z", "role": "user", "content": "Build X"}
{"turn": 2, "timestamp": "2026-04-01T10:00:05Z", "role": "assistant", "content": "Enhanced spec..."}
{"turn": 3, "timestamp": "2026-04-01T10:00:10Z", "role": "assistant", "tool": "FileRead", "input": {"path": "main.py"}}
{"turn": 4, "timestamp": "2026-04-01T10:00:12Z", "role": "tool", "tool": "FileRead", "output": "...", "status": "success"}
```

#### 2. Session Memory — Updated on Thresholds (NOT intervals)
```
When: ALL of these conditions must be met:
  - Token count >= 10,000 (minimum to start tracking)
  - Context growth >= 5,000 tokens since last update
  - Tool calls >= 3 since last update OR no tool calls in last turn
What: Forked agent reads current memory + conversation, writes updated memory
Why: Preserves key context across compactions without wasting tokens every turn
```

This is from the source code's `sessionMemory.ts` — it uses a **forked background agent** to update memory only when thresholds are met, not on a timer.

#### 3. Current Session State — Updated Every Significant Action
```
When: After each significant action or decision
What: Updates .agent-os/session/current-state.md
Why: Quick reference for what's happening right now
```

#### 4. File Hash Cache — Updated on File Changes
```
When: After any file is read or modified
What: Updates .agent-os/cache/file-hashes.json
Why: Enables file-read deduplication (skip re-reading unchanged files)
```

### Session Commands

| Command | What It Does |
|---------|-------------|
| `--continue` | Resume last session from `.agent-os/sessions/` |
| `--resume {sessionId}` | Pick specific past session |
| `--fork-session {sessionId}` | Branch from past conversation (new session, same history up to fork point) |

### Session Rotation

**No auto-pruning.** Sessions accumulate indefinitely. Users manually clean up if needed. This matches the source code's design philosophy: context is valuable, don't destroy it automatically.

### Memory Preservation Across Compactions

When context gets compacted, the session memory file preserves:
- Task specifications
- File lists being worked on
- Workflow state (what phase, what's done, what's next)
- Errors and corrections
- Learnings and insights
- Key results

This means even after compaction destroys most of the conversation history, the agent can reconstruct the essential context from the memory file.
