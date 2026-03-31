---
description: Dumps complete feature flag state including GrowthBook flags, build-time features, env var overrides, and cached values. Reveals all gated capabilities and their current status.
when_to_use: When you need to understand what features are enabled/disabled, debug feature flag issues, or discover hidden capabilities.
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
arguments:
  - scope
  - format
argument-hint: "[all|runtime|buildtime|env|cache] [json|table|markdown]"
---

# Feature Flag State Dumper

Dump the complete feature flag state across all layers: GrowthBook runtime flags, build-time features, environment variable overrides, and cached values.

## Scope Options

- **all** (default) - Dump everything
- **runtime** - GrowthBook flags only
- **buildtime** - feature() flags only
- **env** - Environment variable overrides only
- **cache** - Cached GrowthBook features from disk

## Format Options

- **markdown** (default) - Human-readable tables
- **json** - Machine-readable JSON output
- **table** - Compact terminal tables

## Step 1: Read GrowthBook Cache

Read the cached GrowthBook features from the user config:

```bash
# Read GrowthBook cached features
cat ~/\.agent-os.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
cache = data.get('cachedGrowthBookFeatures', {})
overrides = data.get('growthBookOverrides', {})
print('=== CACHED GROWTHBOOK FEATURES ===')
for flag, value in sorted(cache.items()):
    print(f'  {flag}: {value}')
print(f'\n=== GROWTHBOOK OVERRIDES ===')
for flag, value in sorted(overrides.items()):
    print(f'  {flag}: {value}')
" 2>/dev/null || echo "No GrowthBook cache found"
```

## Step 2: Check Environment Variables

Check all feature-related environment variables:

```bash
echo "=== FEATURE-RELATED ENVIRONMENT VARIABLES ==="
for var in \
  USER_TYPE \
  AGENT_CODE_EXPERIMENTAL_AGENT_TEAMS \
  AGENT_CODE_COORDINATOR_MODE \
  AGENT_AUTO_BACKGROUND_TASKS \
  AGENT_CODE_DISABLE_BACKGROUND_TASKS \
  AGENT_CODE_SIMPLE \
  AGENT_CODE_REPL \
  AGENT_INTERNAL_FC_OVERRIDES \
  AGENT_CODE_DISABLE_POLICY_SKILLS \
  AGENT_CODE_DISABLE_EXPERIMENTAL_BETAS \
  ENABLE_TOOL_SEARCH \
  AGENT_CODE_VERIFY_PLAN \
  ENABLE_LSP_TOOL \
  AGENT_AGENT_SDK_DISABLE_BUILTIN_AGENTS \
  AGENT_CODE_PLUGIN_SEED_DIR \
  AGENT_CODE_PLUGIN_USE_ZIP_CACHE \
  AGENT_CODE_USE_COWORK_PLUGINS \
  AGENT_CODE_ENTRYPOINT \
  AGENT_CODE_REMOTE \
  AGENT_CODE_GB_BASE_URL
do
  val="${!var}"
  if [ -n "$val" ]; then
    echo "  $var=$val"
  fi
done
echo "(empty = not set)"
```

## Step 3: Enumerate All Known Feature Flags

### Build-Time Flags (feature() from bun:bundle)

| Flag | Status | Purpose |
|------|--------|---------|
| CHICAGO_MCP | Build-dependent | Computer Use MCP server |
| KAIROS | Build-dependent | Assistant mode |
| KAIROS_CHANNELS | Build-dependent | MCP channel push notifications |
| KAIROS_BRIEF | Build-dependent | Brief mode / SendUserMessage |
| KAIROS_DREAM | Build-dependent | Dream mode |
| TEAMMEM | Build-dependent | Team memory sync |
| CACHED_MICROCOMPACT | Build-dependent | Cache editing |
| TRANSCRIPT_CLASSIFIER | Build-dependent | Auto permission mode |
| CONNECTOR_TEXT | Build-dependent | MCP connector text blocks |
| PROMPT_CACHE_BREAK_DETECTION | Build-dependent | Cache break analytics |
| CONTEXT_COLLAPSE | Build-dependent | Context window collapse |
| REACTIVE_COMPACT | Build-dependent | Reactive compaction |
| PROACTIVE | Build-dependent | Autonomous proactive mode |
| MCP_SKILLS | Build-dependent | MCP skill system |
| EXPERIMENTAL_SKILL_SEARCH | Build-dependent | Experimental skill search |
| EXTRACT_MEMORIES | Build-dependent | Memory extraction |
| TEMPLATES | Build-dependent | Job classifier/templates |
| BASH_CLASSIFIER | Build-dependent | Bash command auto-approval |
| UNATTENDED_RETRY | Build-dependent | Unattended retry |
| ANTI_DISTILLATION_CC | Build-dependent | Anti-model-distillation |
| UPLOAD_USER_SETTINGS | Build-dependent | Settings upload |
| DOWNLOAD_USER_SETTINGS | Build-dependent | Settings download |
| VOICE_MODE | Build-dependent | Voice mode |
| BG_SESSIONS | Build-dependent | Background sessions |
| BRIDGE_MODE | Build-dependent | Remote control bridge |
| COORDINATOR_MODE | Build-dependent | Multi-agent coordination |
| COMMIT_ATTRIBUTION | Build-dependent | Git commit attribution |
| REVIEW_ARTIFACT | Build-dependent | Review artifact |
| AGENT_TRIGGERS | Build-dependent | Agent triggers |
| AGENT_TRIGGERS_REMOTE | Build-dependent | Remote agent triggers |
| BUILDING_AGENT_APPS | Build-dependent | Claude Apps skill |
| RUN_SKILL_GENERATOR | Build-dependent | Skill generator |
| FORK_SUBAGENT | Build-dependent | Fork subagent experiment |
| TERMINAL_PANEL | Build-dependent | Terminal panel UI |
| COWORKER_TYPE_TELEMETRY | Build-dependent | Coworker type telemetry |

### Runtime GrowthBook Flags

| Flag | Default | Purpose | Unlock Method |
|------|---------|---------|---------------|
| tengu_amber_flint | true | Agent swarms killswitch | Already enabled |
| tengu_amber_stoat | true | Explore/Plan agents | Already enabled |
| tengu_hive_evidence | false | Evidence + verification agent | Set in growthBookOverrides |
| tengu_surreal_dali | false | Scheduled remote agents | Set in growthBookOverrides |
| tengu_auto_background_agents | false | Auto-background after 120s | Set AGENT_AUTO_BACKGROUND_TASKS=1 |
| tengu_ccr_bridge | false | CCR bridge mode | Requires agent\.ai subscription |
| tengu_cobalt_harbor | false | CCR harbor auto-connect | Set in growthBookOverrides |
| tengu_ccr_mirror | false | CCR mirror mode | Set in growthBookOverrides |
| tengu_bridge_repl_v2 | false | Bridge REPL v2 | Set in growthBookOverrides |
| tengu_scratch | false | Coordinator scratchpad | Set in growthBookOverrides |
| tengu_onyx_plover | false | Auto-dream scheduling | Set in growthBookOverrides |
| tengu_glacier_2xr | false | Tool search enhancements | Set in growthBookOverrides |
| tengu_quartz_lantern | false | File edit/write enhancements | Set in growthBookOverrides |
| tengu_session_memory | false | Session memory | Set in growthBookOverrides |
| tengu_coral_fern | false | Memory directory system | Set in growthBookOverrides |
| tengu_terminal_panel | false | Terminal panel | Set in growthBookOverrides |
| tengu_terminal_sidebar | false | Terminal sidebar | Set in growthBookOverrides |
| tengu_chomp_inflection | false | Prompt suggestion | Set in growthBookOverrides |
| tengu_marble_sandcastle | false | Fast mode | Set in growthBookOverrides |
| tengu_turtle_carbon | true | Thinking mode | Already enabled |
| tengu_collage_kaleidoscope | true | Image paste support | Already enabled |
| tengu_slate_prism | true | Print/CLI formatting | Already enabled |
| tengu_attribution_header | true | Attribution header | Already enabled |
| tengu_birch_trellis | true | Bash permission enhancements | Already enabled |
| tengu_amber_quartz_disabled | false | Voice mode disable | Already disabled (voice enabled) |

## Step 4: Identify Gated Capabilities

### Currently Locked (Requires Source Modification)
These capabilities are gated by `USER_TYPE === 'ant'` and are **compiled out** of public builds:

1. **Magic Docs** - Auto-documentation system
2. **Session Data Uploader** - Git/filesystem state capture
3. **Event Loop Stall Detector** - Performance monitoring
4. **SDK Heap Dump Monitor** - Memory monitoring
5. **Asciicast Recorder** - Terminal recording
6. **Research Data Capture** - API research field extraction
7. **Numeric Effort Override** - Internal effort_override param
8. **Anti-Distillation** - Model distillation prevention
9. **CCShare** - Internal session sharing
10. **Ant Model Aliases** - capybara-fast etc.
11. **Debug Mode** - External builds can't be debugged
12. **Hidden CLI Flags** - --delegate-permissions, --afk, --tasks, --agent-teams

### Unlockable via Environment Variables
1. **Coordinator Mode** - `AGENT_CODE_COORDINATOR_MODE=1` (if build has flag)
2. **Agent Swarms** - `AGENT_CODE_EXPERIMENTAL_AGENT_TEAMS=1`
3. **Auto-Background** - `AGENT_AUTO_BACKGROUND_TASKS=1`
4. **Simple Mode** - `AGENT_CODE_SIMPLE=1` (restricts tools)
5. **Disable REPL** - `AGENT_CODE_REPL=0` (exposes primitive tools)
6. **Disable Tool Search** - `ENABLE_TOOL_SEARCH=false`
7. **Enable LSP Tool** - `ENABLE_LSP_TOOL=1`
8. **Verify Plan** - `AGENT_CODE_VERIFY_PLAN=true`

### Unlockable via GrowthBook Overrides
Edit `~/\.agent-os.json` and add:
```json
{
  "growthBookOverrides": {
    "tengu_hive_evidence": true,
    "tengu_surreal_dali": true,
    "tengu_auto_background_agents": true,
    "tengu_cobalt_harbor": true,
    "tengu_ccr_mirror": true,
    "tengu_bridge_repl_v2": true,
    "tengu_scratch": true,
    "tengu_onyx_plover": true,
    "tengu_glacier_2xr": true,
    "tengu_quartz_lantern": true,
    "tengu_session_memory": true,
    "tengu_coral_fern": true,
    "tengu_terminal_panel": true,
    "tengu_terminal_sidebar": true,
    "tengu_chomp_inflection": true,
    "tengu_marble_sandcastle": true
  }
}
```

## Step 5: Generate Capability Report

Based on the current state, produce a report showing:
1. Which capabilities are currently available
2. Which are locked but unlockable (with instructions)
3. Which require source modification
4. Priority ranking by value vs effort
