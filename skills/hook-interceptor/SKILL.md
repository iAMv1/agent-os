---
description: Intercepts tool execution using PreToolUse and PostToolUse hooks to log, modify, or block tool calls. Reveals the complete tool execution pipeline and enables custom tool behavior modification.
when_to_use: When you need to monitor tool execution, modify tool inputs/outputs, block specific tools, or understand the hook interception system.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
arguments:
  - action
  - target
argument-hint: "[monitor|modify|block|log] [tool-name|all]"
---

# Hook Interceptor

Intercept tool execution using the PreToolUse and PostToolUse hook system. This skill demonstrates how hooks can monitor, modify, or block any tool call.

## Hook System Architecture

Based on analysis of `src/src/services/tools/toolHooks.ts`, the hook system supports:

### Hook Events (in execution order)
1. **PermissionRequest** - Before permission check
2. **PreToolUse** - Before tool execution (can modify input)
3. **PostToolUse** - After successful tool execution (can modify output)
4. **PostToolUseFailure** - After tool execution failure
5. **Notification** - When notifications are emitted
6. **Stop** - When session is stopping
7. **PreCompact** - Before context compaction
8. **PostCompact** - After context compaction
9. **UserPromptSubmit** - Before user prompt is submitted
10. **SessionStart** - When session starts

### Hook Types
1. **command** - Executes a shell command
2. **prompt** - LLM evaluation
3. **agent** - Spawns an agent with tools
4. **http** - POSTs to a URL

## Interception Capabilities

### PreToolUse Hook
Can:
- **Allow** - Skip permission check
- **Deny** - Block tool execution
- **Ask** - Force permission prompt
- **Modify Input** - Change tool arguments before execution
- **Add Context** - Inject additional context messages
- **Prevent Continuation** - Stop execution entirely

### PostToolUse Hook
Can:
- **Modify Output** - Change tool results before model sees them
- **Add Context** - Inject additional context
- **Block Continuation** - Stop execution after tool completes
- **Add Blocking Error** - Treat success as failure

### PostToolUseFailure Hook
Can:
- **Add Context** - Provide additional error context
- **Block Continuation** - Stop execution on failure

## Implementation: Tool Execution Logger

Create a hooks configuration that logs all tool execution:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "type": "command",
        "command": "echo '[HOOK] PreToolUse: ${AGENT_TOOL_NAME} with input: ${AGENT_TOOL_INPUT}' >> ~/\.agent-os/hook-log.jsonl"
      }
    ],
    "PostToolUse": [
      {
        "type": "command",
        "command": "echo '[HOOK] PostToolUse: ${AGENT_TOOL_NAME} completed' >> ~/\.agent-os/hook-log.jsonl"
      }
    ],
    "PostToolUseFailure": [
      {
        "type": "command",
        "command": "echo '[HOOK] PostToolUseFailure: ${AGENT_TOOL_NAME} failed: ${AGENT_TOOL_ERROR}' >> ~/\.agent-os/hook-log.jsonl"
      }
    ]
  }
}
```

## Implementation: Tool Input Modifier

Modify tool inputs before execution:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "type": "prompt",
        "prompt": "Review this tool input and modify it if needed. Tool: ${AGENT_TOOL_NAME}, Input: ${AGENT_TOOL_INPUT}",
        "tools": ["Read", "Write", "Edit"]
      }
    ]
  }
}
```

## Implementation: Tool Output Modifier

Modify tool outputs before the model sees them:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "type": "prompt",
        "prompt": "Review and summarize this tool output. Tool: ${AGENT_TOOL_NAME}, Output: ${AGENT_TOOL_OUTPUT}",
        "tools": ["Read", "Write"]
      }
    ]
  }
}
```

## Implementation: Tool Blocker

Block specific tools from executing:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "type": "prompt",
        "prompt": "Should this tool be blocked? Tool: ${AGENT_TOOL_NAME}. If yes, return DENY. If no, return ALLOW.",
        "tools": []
      }
    ]
  }
}
```

## Hook Variable Substitution

Hooks support these variables:
- `${AGENT_TOOL_NAME}` - Name of the tool being executed
- `${AGENT_TOOL_INPUT}` - JSON input to the tool
- `${AGENT_TOOL_OUTPUT}` - Output from the tool
- `${AGENT_TOOL_ERROR}` - Error message if tool failed
- `${AGENT_SESSION_ID}` - Current session ID
- `${AGENT_SKILL_DIR}` - Skill directory path

## Installing Hooks

Hooks can be installed via:

1. **settings.json** - Add to user or project settings:
```json
{
  "hooks": {
    "PreToolUse": [...],
    "PostToolUse": [...]
  }
}
```

2. **Plugin hooks** - Include in plugin's `hooks/hooks.json`

3. **Skill frontmatter** - Include in skill's `hooks` field:
```yaml
---
hooks:
  PreToolUse:
    - type: command
      command: "echo 'Tool executed' >> ~/\.agent-os/hook-log.jsonl"
---
```

## Hook Execution Order

1. User requests tool execution
2. **PermissionRequest** hooks fire
3. Permission rules evaluated
4. **PreToolUse** hooks fire (can modify input)
5. Hook results merged with permission decision
6. Tool executes (if allowed)
7. **PostToolUse** hooks fire (on success)
8. **PostToolUseFailure** hooks fire (on failure)
9. Model receives final output

## Monitoring Tool Execution

To monitor all tool execution without modifying behavior:

```bash
# Create a monitoring hook configuration
cat > ~/\.agent-os/hooks/monitor.json << 'EOF'
{
  "hooks": {
    "PreToolUse": [
      {
        "type": "command",
        "command": "echo '{\"event\":\"PreToolUse\",\"tool\":\"${AGENT_TOOL_NAME}\",\"time\":\"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'\"}' >> ~/\.agent-os/tool-monitor.jsonl"
      }
    ],
    "PostToolUse": [
      {
        "type": "command",
        "command": "echo '{\"event\":\"PostToolUse\",\"tool\":\"${AGENT_TOOL_NAME}\",\"time\":\"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'\"}' >> ~/\.agent-os/tool-monitor.jsonl"
      }
    ],
    "PostToolUseFailure": [
      {
        "type": "command",
        "command": "echo '{\"event\":\"PostToolUseFailure\",\"tool\":\"${AGENT_TOOL_NAME}\",\"error\":\"${AGENT_TOOL_ERROR}\",\"time\":\"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'\"}' >> ~/\.agent-os/tool-monitor.jsonl"
      }
    ]
  }
}
EOF
```

## Analysis: Hook Interception Points

Based on source code analysis, the key interception points are:

1. **toolExecution.ts:599-1104** - Main execution pipeline
2. **toolHooks.ts:435-650** - PreToolUse hook processing
3. **toolHooks.ts:39-191** - PostToolUse hook processing
4. **toolHooks.ts:193-319** - PostToolUseFailure hook processing
5. **resolveHookPermissionDecision()** - Merges hook results with permissions

The hook system is the most powerful extension mechanism in AI Coding Agent - it can intercept, modify, or block any tool execution at any point in the pipeline.
