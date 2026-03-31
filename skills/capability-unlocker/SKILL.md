---
description: Unlocks hidden capabilities by configuring environment variables, GrowthBook overrides, and settings. Automates the process of enabling all available feature flags and runtime gates.
when_to_use: When you want to enable all available hidden capabilities, unlock feature-flag gated tools, or maximize AI Coding Agent's capabilities.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
arguments:
  - scope
argument-hint: "[all|agents|tools|ui|memory|bridge]"
---

# Capability Unlocker

Unlocks hidden capabilities by configuring environment variables, GrowthBook overrides, and settings. This skill automates the process of enabling all available feature flags and runtime gates.

## Unlock Scope

- **all** (default) - Unlock everything possible
- **agents** - Unlock agent-related capabilities
- **tools** - Unlock tool-related capabilities
- **ui** - Unlock UI-related capabilities
- **memory** - Unlock memory-related capabilities
- **bridge** - Unlock bridge/remote capabilities

## Phase 1: Environment Variable Configuration

Create or update the environment configuration file:

```bash
# Create environment file
cat > ~/\.agent-os/env-unlock.sh << 'EOF'
#!/bin/bash
# Capability Unlocker - Environment Variables
# Source this file before starting AI Coding Agent: source ~/\.agent-os/env-unlock.sh

# Agent Capabilities
export AGENT_CODE_EXPERIMENTAL_AGENT_TEAMS=1
export AGENT_AUTO_BACKGROUND_TASKS=1
export AGENT_CODE_COORDINATOR_MODE=1

# Tool Capabilities
export ENABLE_TOOL_SEARCH=false
export ENABLE_LSP_TOOL=1
export AGENT_CODE_VERIFY_PLAN=true

# UI Capabilities
export AGENT_CODE_REPL=0

# Memory Capabilities
# (configured via GrowthBook overrides)

# Debug/Development
# export AGENT_CODE_DISABLE_EXPERIMENTAL_BETAS=1  # Uncomment to disable betas

echo "Capability unlocker environment variables set."
echo "Run: source ~/\.agent-os/env-unlock.sh"
EOF
chmod +x ~/\.agent-os/env-unlock.sh
```

## Phase 2: GrowthBook Override Configuration

Update `~/\.agent-os.json` with GrowthBook overrides to enable runtime-gated features:

```bash
# Read current config and add overrides
python3 << 'PYEOF'
import json
import os

config_path = os.path.expanduser("~/\.agent-os.json")

# Read existing config
try:
    with open(config_path, 'r') as f:
        config = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    config = {}

# GrowthBook overrides to enable hidden capabilities
overrides = {
    # Agent capabilities
    "tengu_hive_evidence": True,           # Verification agent + evidence tracking
    "tengu_surreal_dali": True,            # Scheduled remote agents
    "tengu_auto_background_agents": True,  # Auto-background after 120s
    "tengu_cobalt_harbor": True,           # CCR harbor auto-connect
    "tengu_ccr_mirror": True,              # CCR mirror mode
    "tengu_bridge_repl_v2": True,          # Bridge REPL v2 (env-less)
    "tengu_scratch": True,                 # Coordinator scratchpad
    "tengu_onyx_plover": True,             # Auto-dream scheduling

    # Tool capabilities
    "tengu_glacier_2xr": True,             # Tool search enhancements
    "tengu_quartz_lantern": True,          # File edit/write enhancements
    "tengu_tool_search": True,             # Deferred tool loading

    # UI capabilities
    "tengu_terminal_panel": True,          # Terminal panel
    "tengu_terminal_sidebar": True,        # Terminal sidebar
    "tengu_chomp_inflection": True,        # Prompt suggestion
    "tengu_marble_sandcastle": True,       # Fast mode
    "tengu_destructive_command_warning": True,  # Destructive command warnings

    # Memory capabilities
    "tengu_session_memory": True,          # Session memory
    "tengu_coral_fern": True,              # Memory directory system
    "tengu_passport_quail": True,          # Memory directory (passport)
    "tengu_slate_thimble": True,           # Memory paths extension

    # Other capabilities
    "tengu_amber_prism": True,             # Message formatting
    "tengu_copper_panda": True,            # Skill improvement
    "tengu_lapis_finch": True,             # Plugin hint recommendation
    "tengu_basalt_3kr": True,              # MCP instructions delta
    "tengu_trace_lantern": True,           # Beta session tracing
    "tengu_lodestone_enabled": True,       # Deep link protocol
    "tengu_moth_copse": True,              # Attachment feature
    "tengu_marble_fox": True,              # Attachment feature
    "tengu_amber_json_tools": True,        # JSON tools beta
    "tengu_immediate_model_command": True, # Immediate model command
    "tengu_fgts": True,                    # First-gen token streaming
    "tengu_otk_slot_v1": True,             # OTK slot management
}

# Merge with existing overrides
existing = config.get("growthBookOverrides", {})
existing.update(overrides)
config["growthBookOverrides"] = existing

# Also update cached features to ensure they persist
cached = config.get("cachedGrowthBookFeatures", {})
cached.update(overrides)
config["cachedGrowthBookFeatures"] = cached

# Write back
with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)

print(f"Updated {config_path} with {len(overrides)} GrowthBook overrides")
print(f"Total overrides: {len(config['growthBookOverrides'])}")
PYEOF
```

## Phase 3: Settings Configuration

Update settings to enable additional capabilities:

```bash
# Update settings.json
python3 << 'PYEOF'
import json
import os

settings_path = os.path.expanduser("~/\.agent-os/settings.json")

try:
    with open(settings_path, 'r') as f:
        settings = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    settings = {}

# Enable capabilities
updates = {
    # Enable all permission modes
    "permissionMode": "default",

    # Enable experimental features
    "enableAllTools": True,

    # Enable MCP channel permissions if available
    "mcp": settings.get("mcp", {}),
}

settings.update(updates)

with open(settings_path, 'w') as f:
    json.dump(settings, f, indent=2)

print(f"Updated {settings_path}")
PYEOF
```

## Phase 4: Verification

After applying unlocks, verify the current state:

```bash
echo "=== CAPABILITY UNLOCK STATUS ==="
echo ""
echo "Environment Variables:"
for var in \
  AGENT_CODE_EXPERIMENTAL_AGENT_TEAMS \
  AGENT_AUTO_BACKGROUND_TASKS \
  AGENT_CODE_COORDINATOR_MODE \
  ENABLE_TOOL_SEARCH \
  ENABLE_LSP_TOOL \
  AGENT_CODE_VERIFY_PLAN \
  AGENT_CODE_REPL
do
  val="${!var}"
  if [ -n "$val" ]; then
    echo "  [SET] $var=$val"
  else
    echo "  [NOT SET] $var"
  fi
done

echo ""
echo "GrowthBook Overrides:"
python3 -c "
import json, os
config_path = os.path.expanduser('~/\.agent-os.json')
try:
    with open(config_path) as f:
        config = json.load(f)
    overrides = config.get('growthBookOverrides', {})
    for flag, value in sorted(overrides.items()):
        status = 'ENABLED' if value else 'disabled'
        print(f'  [{status}] {flag}')
except Exception as e:
    print(f'  Error reading config: {e}')
"

echo ""
echo "=== UNLOCK COMPLETE ==="
echo "Restart AI Coding Agent for changes to take effect."
```

## Capabilities Unlocked by This Skill

### Agent Capabilities
- Agent swarms (if build has flag)
- Auto-background agents
- Verification agent
- Scheduled remote agents
- Coordinator mode (if build has flag)
- Coordinator scratchpad
- Auto-dream scheduling

### Tool Capabilities
- Tool search enhancements
- File edit/write enhancements
- LSP tool
- Plan verification tool
- All tools upfront (no deferral)

### UI Capabilities
- Terminal panel
- Terminal sidebar
- Prompt suggestion
- Fast mode
- Destructive command warnings

### Memory Capabilities
- Session memory
- Memory directory system
- Memory paths extension

### Other Capabilities
- Message formatting
- Skill improvement
- Plugin hint recommendation
- MCP instructions delta
- Beta session tracing
- Deep link protocol
- Enhanced attachments
- JSON tools beta
- Immediate model command
- First-gen token streaming
- OTK slot management

## Limitations

This skill can only unlock capabilities that are:
1. Present in the build (not compiled out by feature flags)
2. Gated by runtime flags (GrowthBook) or environment variables
3. Not gated by `USER_TYPE === 'ant'` (build-time string replacement)

Capabilities that require source modification are documented in the findings but cannot be unlocked by this skill alone.
