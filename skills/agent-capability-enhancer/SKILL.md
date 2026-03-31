---
description: Maximizes agent capabilities by enabling all agent types, configuring optimal agent settings, and unlocking hidden agent features like fork subagents, swarms, and remote isolation.
when_to_use: When you need maximum agent capabilities, want to use all available agent types, or unlock hidden agent features.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
arguments:
  - focus
argument-hint: "[all|swarms|fork|remote|background|coordinator]"
---

# Agent Capability Enhancer

Maximizes agent capabilities by enabling all agent types, configuring optimal settings, and unlocking hidden agent features.

## Agent Focus Areas

- **all** (default) - Enhance all agent capabilities
- **swarms** - Enable agent swarms/teams
- **fork** - Enable fork subagent experiment
- **remote** - Enable remote agent execution
- **background** - Enable background agent features
- **coordinator** - Enable coordinator mode

## Phase 1: Agent Environment Configuration

```bash
# Create agent capability environment file
cat > ~/\.agent-os/agent-env.sh << 'EOF'
#!/bin/bash
# Agent Capability Enhancer - Environment Variables

# Enable agent swarms/teams
export AGENT_CODE_EXPERIMENTAL_AGENT_TEAMS=1

# Enable coordinator mode (if build has the flag)
export AGENT_CODE_COORDINATOR_MODE=1

# Enable auto-backgrounding (agents auto-background after 120s)
export AGENT_AUTO_BACKGROUND_TASKS=1

# Do NOT disable background tasks
unset AGENT_CODE_DISABLE_BACKGROUND_TASKS

# Do NOT disable built-in agents
unset AGENT_AGENT_SDK_DISABLE_BUILTIN_AGENTS

# Do NOT use simple mode (restricts tools)
unset AGENT_CODE_SIMPLE

echo "Agent capability environment variables set."
echo "Run: source ~/\.agent-os/agent-env.sh"
EOF
chmod +x ~/\.agent-os/agent-env.sh
```

## Phase 2: GrowthBook Agent Overrides

```bash
# Update GrowthBook overrides for agent capabilities
python3 << 'PYEOF'
import json
import os

config_path = os.path.expanduser("~/\.agent-os.json")

try:
    with open(config_path, 'r') as f:
        config = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    config = {}

# Agent-related GrowthBook overrides
agent_overrides = {
    # Agent swarms
    "tengu_amber_flint": True,           # Agent swarms killswitch (keep enabled)
    "tengu_amber_stoat": True,           # Explore/Plan agents (keep enabled)

    # Advanced agent features
    "tengu_hive_evidence": True,         # Verification agent + evidence tracking
    "tengu_auto_background_agents": True, # Auto-background after 120s
    "tengu_slim_subagent_claudemd": True, # Slim subagent WORKER.md
    "tengu_agent_list_attach": True,     # Agent list attachment

    # Remote agents
    "tengu_surreal_dali": True,          # Scheduled remote agents
    "tengu_cobalt_lantern": True,        # Web setup / GitHub integration

    # Coordinator mode
    "tengu_scratch": True,               # Coordinator scratchpad directory

    # Remote session
    "tengu_ccr_bundle_seed_enabled": True, # Git bundle fallback for remote sessions
}

# Merge with existing overrides
existing = config.get("growthBookOverrides", {})
existing.update(agent_overrides)
config["growthBookOverrides"] = existing

# Also update cached features
cached = config.get("cachedGrowthBookFeatures", {})
cached.update(agent_overrides)
config["cachedGrowthBookFeatures"] = cached

with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)

print(f"Updated {len(agent_overrides)} agent-related GrowthBook overrides")
PYEOF
```

## Phase 3: Agent Configuration

### Configure Agent Settings in settings.json

```bash
python3 << 'PYEOF'
import json
import os

settings_path = os.path.expanduser("~/\.agent-os/settings.json")

try:
    with open(settings_path, 'r') as f:
        settings = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    settings = {}

# Agent configuration
agent_config = {
    # Default agent settings
    "agent": {
        # Allow all tools for agents
        "allowed_tools": ["*"],
        # Use inherit model (same as parent)
        "model": "inherit",
        # Allow agents to run in background
        "run_in_background": True,
    }
}

# Merge agent config
existing_agent = settings.get("agent", {})
existing_agent.update(agent_config.get("agent", {}))
settings["agent"] = existing_agent

with open(settings_path, 'w') as f:
    json.dump(settings, f, indent=2)

print("Updated agent configuration in settings.json")
PYEOF
```

## Phase 4: Agent Capability Audit

```bash
echo "=== AGENT CAPABILITY STATUS ==="
echo ""
echo "Environment Variables:"
echo "  Agent teams: ${AGENT_CODE_EXPERIMENTAL_AGENT_TEAMS:-not set}"
echo "  Coordinator mode: ${AGENT_CODE_COORDINATOR_MODE:-not set}"
echo "  Auto-background: ${AGENT_AUTO_BACKGROUND_TASKS:-not set}"
echo "  Disable background: ${AGENT_CODE_DISABLE_BACKGROUND_TASKS:-not set}"
echo "  Disable built-in agents: ${AGENT_AGENT_SDK_DISABLE_BUILTIN_AGENTS:-not set}"
echo "  Simple mode: ${AGENT_CODE_SIMPLE:-not set}"

echo ""
echo "GrowthBook Agent Flags:"
python3 -c "
import json, os
config_path = os.path.expanduser('~/\.agent-os.json')
try:
    with open(config_path) as f:
        config = json.load(f)
    overrides = config.get('growthBookOverrides', {})
    agent_flags = [k for k in overrides if 'amber' in k or 'hive' in k or 'auto_background' in k or 'slim_subagent' in k or 'agent_list' in k or 'surreal' in k or 'cobalt_lantern' in k or 'scratch' in k or 'ccr_bundle' in k]
    for flag in sorted(agent_flags):
        status = 'ENABLED' if overrides[flag] else 'disabled'
        print(f'  [{status}] {flag}')
except Exception as e:
    print(f'  Error: {e}')
"

echo ""
echo "Agent Configuration:"
python3 -c "
import json, os
settings_path = os.path.expanduser('~/\.agent-os/settings.json')
try:
    with open(settings_path) as f:
        settings = json.load(f)
    agent = settings.get('agent', {})
    if agent:
        for k, v in agent.items():
            print(f'  {k}: {v}')
    else:
        print('  No agent configuration found')
except Exception as e:
    print(f'  Error: {e}')
"
```

## Available Agent Types

### Built-In Agents (Always Available)
| Agent | Model | Purpose |
|-------|-------|---------|
| general-purpose | default | All-purpose research and multi-step tasks |
| Explore | haiku | Read-only file search specialist |
| Plan | inherit | Software architect for implementation planning |
| agent-code-guide | haiku | Documentation Q&A agent |

### Gated Agents (Unlockable)
| Agent | Gate | Purpose |
|-------|------|---------|
| verification | tengu_hive_evidence | Adversarial testing specialist |
| coordinator workers | COORDINATOR_MODE | Worker agents in coordinator mode |
| fork subagent | FORK_SUBAGENT | Context-inheriting workers |
| remote agents | USER_TYPE=ant | Cloud-executed agents |

### Agent Isolation Modes
| Mode | Availability | Description |
|------|-------------|-------------|
| none (default) | All builds | No isolation |
| worktree | All builds | Git worktree isolation |
| remote | USER_TYPE=ant only | Cloud environment isolation |

## Agent Tool Restrictions

### All Agent Disallowed Tools
- TaskOutput
- ExitPlanMode
- EnterPlanMode
- Agent (for non-ant users - agents can't spawn agents)
- AskUserQuestion
- TaskStop
- Workflow (if WORKFLOW_SCRIPTS feature is on)

### Async Agent Allowed Tools
- Read, WebSearch, TodoWrite, Grep, WebFetch, Glob
- Shell tools (Bash, PowerShell)
- FileEdit, FileWrite, NotebookEdit
- Skill, SyntheticOutput, ToolSearch
- EnterWorktree, ExitWorktree

### Coordinator Mode Allowed Tools
- Agent, TaskStop, SendMessage, SyntheticOutput

## Step-by-Step Agent Unlock

1. **Enable agent swarms**: `AGENT_CODE_EXPERIMENTAL_AGENT_TEAMS=1`
2. **Enable coordinator mode**: `AGENT_CODE_COORDINATOR_MODE=1` (if build has flag)
3. **Enable auto-background**: `AGENT_AUTO_BACKGROUND_TASKS=1`
4. **Enable verification agent**: Set `tengu_hive_evidence: true` in GrowthBook overrides
5. **Enable scheduled remote agents**: Set `tengu_surreal_dali: true` in GrowthBook overrides
6. **Enable coordinator scratchpad**: Set `tengu_scratch: true` in GrowthBook overrides
7. **Enable fork subagent**: Requires build with `FORK_SUBAGENT` flag
8. **Enable remote isolation**: Requires ant build (USER_TYPE=ant)
