---
description: Enhanced debug skill that extends the built-in /debug with feature flag state dumping, system prompt analysis, capability auditing, and hidden capability detection. Goes beyond the standard debug to reveal gated functionality.
when_to_use: When you need deep debugging that includes feature flag states, hidden capabilities, system prompt analysis, and capability unlocking recommendations.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - WebFetch
arguments:
  - focus
argument-hint: "[full|flags|prompt|capabilities|hooks|mcp|agents|tools]"
---

# Enhanced Debug

Extended debugging that goes beyond the built-in /debug skill to reveal feature flag states, hidden capabilities, system prompt composition, and capability unlocking opportunities.

## Debug Focus Areas

- **full** (default) - Complete debug dump
- **flags** - Feature flag state only
- **prompt** - System prompt analysis only
- **capabilities** - Hidden capability detection only
- **hooks** - Hook system state only
- **mcp** - MCP server state only
- **agents** - Agent system state only
- **tools** - Tool system state only

## Phase 1: Feature Flag State Dump

### Check GrowthBook Cache
```bash
python3 -c "
import json, os
config_path = os.path.expanduser('~/\.agent-os.json')
try:
    with open(config_path) as f:
        config = json.load(f)
    cache = config.get('cachedGrowthBookFeatures', {})
    overrides = config.get('growthBookOverrides', {})
    print('=== GROWTHBOOK CACHED FEATURES ===')
    for flag, value in sorted(cache.items()):
        override = overrides.get(flag, 'N/A')
        marker = ' [OVERRIDE]' if flag in overrides else ''
        print(f'  {flag}: {value}{marker}')
    print(f'\nTotal cached: {len(cache)}, Overrides: {len(overrides)}')
except Exception as e:
    print(f'Error: {e}')
"
```

### Check Environment Variables
```bash
echo "=== FEATURE ENV VARS ==="
for var in USER_TYPE AGENT_CODE_EXPERIMENTAL_AGENT_TEAMS AGENT_CODE_COORDINATOR_MODE AGENT_AUTO_BACKGROUND_TASKS AGENT_CODE_DISABLE_BACKGROUND_TASKS AGENT_CODE_SIMPLE AGENT_CODE_REPL AGENT_INTERNAL_FC_OVERRIDES ENABLE_TOOL_SEARCH AGENT_CODE_VERIFY_PLAN ENABLE_LSP_TOOL AGENT_CODE_ENTRYPOINT; do
  val="${!var}"
  [ -n "$val" ] && echo "  $var=$val" || echo "  $var=(not set)"
done
```

## Phase 2: System Prompt Analysis

### Check Loaded Instructions
```bash
# Check for WORKER.md files that inject into system prompt
echo "=== LOADED INSTRUCTIONS ==="
for f in \
  "$PWD/WORKER.md" \
  "$PWD/CLAUDE.local.md" \
  "$HOME/.agent-os/WORKER.md" \
  "$PWD/.agent-os/WORKER.md"
do
  if [ -f "$f" ]; then
    lines=$(wc -l < "$f")
    echo "  [LOADED] $f ($lines lines)"
  fi
done
```

### Check Memory System State
```bash
echo "=== MEMORY SYSTEM ==="
# Check for memory directory
if [ -d "$HOME/.agent-os/memory" ]; then
  echo "  Memory directory exists"
  ls -la "$HOME/.agent-os/memory/" 2>/dev/null | head -10
fi
# Check for session memory
if [ -d "$HOME/.agent-os/sessions" ]; then
  echo "  Sessions directory exists"
  ls -la "$HOME/.agent-os/sessions/" 2>/dev/null | head -5
fi
```

## Phase 3: Hidden Capability Detection

### Check for Gated Features in Current Build
```bash
echo "=== BUILD CAPABILITY AUDIT ==="
# Check if debug mode is blocked (external builds exit on debug)
echo "  Debug mode: $([ -n "$AGENT_CODE_DEBUG" ] && echo "ENABLED" || echo "UNKNOWN (may be blocked in external builds)")"

# Check coordinator mode availability
echo "  Coordinator mode: $([ "$AGENT_CODE_COORDINATOR_MODE" = "1" ] && echo "ENABLED" || echo "NOT ENABLED (set AGENT_CODE_COORDINATOR_MODE=1)")"

# Check agent teams
echo "  Agent teams: $([ "$AGENT_CODE_EXPERIMENTAL_AGENT_TEAMS" = "1" ] && echo "ENABLED" || echo "NOT ENABLED (set AGENT_CODE_EXPERIMENTAL_AGENT_TEAMS=1)")"

# Check tool search
echo "  Tool search: $([ "$ENABLE_TOOL_SEARCH" = "false" ] && echo "DISABLED (all tools upfront)" || echo "ENABLED (deferred loading)")"

# Check REPL mode
echo "  REPL mode: $([ "$AGENT_CODE_REPL" = "0" ] && echo "DISABLED (primitive tools exposed)" || echo "ENABLED (tools hidden from model)")"
```

### Check for Available but Unused Capabilities
```bash
echo "=== UNUSED CAPABILITIES ==="
# Check MCP servers
python3 -c "
import json, os
config_path = os.path.expanduser('~/\.agent-os/settings.json')
try:
    with open(config_path) as f:
        settings = json.load(f)
    mcp = settings.get('mcpServers', {})
    if mcp:
        print(f'  MCP servers configured: {len(mcp)}')
        for name in mcp:
            print(f'    - {name}')
    else:
        print('  No MCP servers configured')
except Exception as e:
    print(f'  Error: {e}')
"

# Check installed plugins
python3 -c "
import json, os
plugins_path = os.path.expanduser('~/\.agent-os/plugins/installed_plugins.json')
try:
    with open(plugins_path) as f:
        data = json.load(f)
    plugins = data.get('plugins', [])
    print(f'  Installed plugins: {len(plugins)}')
    for p in plugins:
        enabled = p.get('enabled', True)
        status = 'ENABLED' if enabled else 'DISABLED'
        print(f'    - {p.get(\"name\", \"unknown\")} [{status}]')
except FileNotFoundError:
    print('  No installed plugins file')
except Exception as e:
    print(f'  Error: {e}')
"

# Check loaded skills
echo "  Skills directory: $PWD/.agent-os/skills/"
if [ -d "$PWD/.agent-os/skills" ]; then
  skill_count=$(find "$PWD/.agent-os/skills" -name "SKILL.md" | wc -l)
  echo "    Project skills: $skill_count"
fi
user_skill_count=$(find "$HOME/.agent-os/skills" -name "SKILL.md" 2>/dev/null | wc -l)
echo "    User skills: $user_skill_count"
```

## Phase 4: Hook System State

```bash
echo "=== HOOK SYSTEM ==="
# Check for hook configurations
for f in \
  "$HOME/.agent-os/settings.json" \
  "$PWD/.agent-os/settings.json" \
  "$PWD/.agent-os/hooks/hooks.json"
do
  if [ -f "$f" ]; then
    hooks=$(python3 -c "
import json
with open('$f') as fp:
    data = json.load(fp)
hooks = data.get('hooks', {})
for event, hook_list in hooks.items():
    print(f'  {event}: {len(hook_list)} hooks')
" 2>/dev/null)
    if [ -n "$hooks" ]; then
      echo "  Hooks in $f:"
      echo "$hooks"
    fi
  fi
done
```

## Phase 5: Capability Unlock Recommendations

Based on the debug output, generate a prioritized list of capabilities that can be unlocked:

### Immediate (Environment Variables)
1. `AGENT_CODE_COORDINATOR_MODE=1` - Enable coordinator mode
2. `AGENT_CODE_EXPERIMENTAL_AGENT_TEAMS=1` - Enable agent swarms
3. `AGENT_AUTO_BACKGROUND_TASKS=1` - Enable auto-backgrounding
4. `AGENT_CODE_REPL=0` - Expose primitive tools
5. `ENABLE_TOOL_SEARCH=false` - Get all tools upfront

### Quick (GrowthBook Overrides)
6. `tengu_hive_evidence: true` - Verification agent
7. `tengu_surreal_dali: true` - Scheduled remote agents
8. `tengu_scratch: true` - Coordinator scratchpad
9. `tengu_session_memory: true` - Session memory
10. `tengu_glacier_2xr: true` - Tool search enhancements

### Requires Source Modification
11. Magic Docs (USER_TYPE=ant gate)
12. Session Data Uploader (USER_TYPE=ant gate)
13. Anti-Distillation (USER_TYPE=ant gate)
14. Research Data Capture (USER_TYPE=ant gate)
15. All build-time feature flags

## Debug Output Format

```
=== ENHANCED DEBUG REPORT ===
Timestamp: <current time>
Build Type: <ant|external|unknown>
Session ID: <session id>

--- Feature Flags ---
<flag states>

--- Environment ---
<env var states>

--- Loaded Instructions ---
<WORKER.md files>

--- Memory System ---
<memory state>

--- Build Capabilities ---
<capability audit>

--- Unused Capabilities ---
<MCP, plugins, skills>

--- Hook System ---
<hook state>

--- Unlock Recommendations ---
<prioritized list>

=== END DEBUG REPORT ===
```
