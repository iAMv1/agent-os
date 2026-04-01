# MCP + Tool + Self-Healing Architecture

**Blueprint for AgentOS External Integration & Resilience**

Extracted from 9 findings documents covering the Claude Code runtime system (~1900 files, ~500k LOC).

---

## Table of Contents

1. [MCP System Architecture](#1-mcp-system-architecture)
2. [Plugin-MCP Integration](#2-plugin-mcp-integration)
3. [Tool System Architecture](#3-tool-system-architecture)
4. [Self-Healing Patterns](#4-self-healing-patterns)
5. [AgentOS Adaptation Guide](#5-agentos-adaptation-guide)

---

## 1. MCP System Architecture

### 1.1 MCP Server Discovery & Loading

**Sources:** `04-plugin-system-EXPANDED.md`, `ant-internal/categories/12-mcp.md`, `06-tool-execution-EXPANDED.md`

#### Multi-Scope Configuration System

**File:** `src/src/services/mcp/config.ts`

MCP servers are discovered from 6 configuration scopes, evaluated in priority order:

| Scope | Location | Override Behavior |
|-------|----------|-------------------|
| **Enterprise** | `managed-settings.json` | **Exclusive** — blocks ALL other scopes |
| **User** | `~/.claude/.mcp.json` | Global user servers |
| **Project** | `$project/.mcp.json` | Project-shared servers |
| **Local** | `$project/.claude/.mcp.json` | Personal overrides |
| **Dynamic** | Runtime (plugins, CLI) | Session-scoped servers |
| **Claude.ai** | Remote proxy config | Cloud-synced servers |

**Key Pattern — Enterprise Exclusive Control:**
```
if (enterpriseConfigPresent) {
  return enterpriseServers;  // ALL other scopes ignored
}
// Otherwise merge: user → project → local → dynamic → claudeai
```

**Why:** Enterprise admins need absolute control over which MCP servers their organization can use. The exclusive control pattern means if enterprise config exists, no user can add personal MCP servers.

#### Plugin-Provided MCP Servers

**File:** `04-plugin-system-EXPANDED.md` lines 375-444

Plugins provide MCP servers through multiple formats:

```
loadPluginMcpServers(plugin):
  1. Check for .mcp.json in plugin directory (lowest priority)
  2. Process manifest.mcpServers (higher priority):
     a. String ending in .mcpb or .dxt → loadMcpServersFromMcpb()
     b. String (other) → load as JSON file path
     c. Array → mix of paths and inline configs
     d. Object → direct MCP server configs
  3. Merge all servers (last-wins collision)
```

#### MCPB (MCP Bundle) Loading

```
loadMcpServersFromMcpb(plugin, mcpbPath):
  1. If URL → download MCPB file
  2. If local path → read file
  3. Extract MCPB (ZIP format)
  4. Parse DXT manifest
  5. Check if user config needed → return 'needs-config' if so
  6. Convert DXT manifest to MCP server config
  7. Return {serverName: mcpConfig}
```

#### Two-Phase Loading

**File:** `ant-internal/categories/12-mcp.md` lines 98-99

```
Phase 1: Claude Code configs (local files) — FAST, no network
Phase 2: claude.ai configs (remote proxy) — SLOW, network-dependent
```

**Why:** Fast startup by loading local configs first, then fetching remote configs asynchronously. The UI shows local servers immediately while remote servers appear when ready.

### 1.2 MCP Tool Registration & Deferral

**Sources:** `06-tool-execution-EXPANDED.md` lines 460-560, `06-tool-execution-system-audit.md` lines 124-187

#### Deferred Tool Detection

```typescript
isDeferredTool(tool):
  1. If tool.alwaysLoad === true → NOT deferred
  2. If tool.isMcp === true → deferred (default)
  3. If tool.name === TOOL_SEARCH_TOOL_NAME → NOT deferred
  4. If FORK_SUBAGENT enabled AND tool.name === AGENT_TOOL_NAME → NOT deferred
  5. If tool.name === BRIEF_TOOL_NAME → NOT deferred
  6. If tool.name === SEND_USER_FILE_TOOL_NAME → NOT deferred
  7. If tool.shouldDefer === true → deferred
```

#### Tool Search Modes

| Mode | Env Value | Behavior |
|------|-----------|----------|
| `tst` | `true`, `auto:0`, or unset | Always defer MCP and shouldDefer tools |
| `tst-auto` | `auto` or `auto:1-99` | Defer only when tools exceed threshold |
| `standard` | `false`, `auto:100` | No deferral - all tools inline |

#### Deferred Tool Loading Flow

```
1. Initial prompt: Deferred tools sent with defer_loading: true (name only, no schema)
2. Model decides it needs a deferred tool → calls ToolSearchTool
3. ToolSearchTool returns tool_reference blocks with full schemas
4. API expands tool_reference blocks into full tool definitions
5. Model can now call the tool with proper parameters
```

**Why:** Saves context window tokens by not including full MCP tool schemas upfront. MCP servers can have dozens of tools; deferring them until needed saves ~5-20K tokens per turn.

#### Deferred Tools Delta

**File:** `06-tool-execution-EXPANDED.md` lines 527-528

- Tracks which deferred tools have been announced to the model
- Uses `deferred_tools_delta` attachments for incremental updates
- Enabled for ant users or `tengu_glacier_2xr` feature flag
- Avoids per-turn recomputation that busts prompt cache on late MCP connect

### 1.3 MCP Authentication (OAuth, API Keys)

**Sources:** `ant-internal/categories/12-mcp.md` lines 104-125, `04-plugin-system-EXPANDED.md` lines 690-716

#### Transport Types (8 Total)

| Transport | Protocol | Use Case |
|-----------|----------|----------|
| `stdio` | stdin/stdout | Local child processes |
| `sse` | Server-Sent Events | Remote HTTP servers |
| `sse-ide` | SSE (IDE variant) | IDE integrations |
| `http` | HTTP POST | REST-style MCP |
| `ws` | WebSocket | Real-time bidirectional |
| `ws-ide` | WebSocket (IDE variant) | IDE real-time |
| `claudeai-proxy` | OAuth proxy | Cloud-synced servers |
| `sdk` | In-process | Embedded servers |

#### OAuth Token Management

**File:** `ant-internal/categories/12-mcp.md` line 114

- OAuth tokens cached for 15 minutes
- Session expiry detection via HTTP 404 + JSON-RPC error -32001
- `createClaudeAiProxyFetch`: OAuth 401 retry with token change detection

#### OAuth Retry Pattern

```typescript
createClaudeAiProxyFetch():
  1. Make request with current OAuth token
  2. If 401 response:
     a. Detect token change (token was refreshed elsewhere)
     b. Retry with new token
  3. If still 401: propagate error
```

#### Sensitive Plugin Options Storage

**File:** `04-plugin-system-EXPANDED.md` lines 696-709

| Option Type | Storage Location |
|-------------|------------------|
| Non-sensitive | `settings.json` → `pluginConfigs[pluginId].options` |
| Sensitive (`sensitive: true`) | Secure storage (macOS keychain or `.credentials.json`) → `pluginSecrets[pluginId]` |

**Storage Key:** `plugin.source` (always `"${name}@${marketplace}"`)

### 1.4 MCP Channels (Push Notifications)

**Sources:** `ant-internal/categories/12-mcp.md` lines 29-73, `04-plugin-system-supply-chain.md` lines 113-116

#### Channel Notification System

MCP servers can push user messages into the conversation via `notifications/claude/channel`:

```
notifications/claude/channel          — Push user message into conversation
notifications/claude/channel/permission — Structured permission replies
```

#### Multi-Layer Gate Chain (6 Layers)

**File:** `ant-internal/categories/12-mcp.md` lines 58-73

```
Layer 1: Server must declare experimental['claude/channel'] capability
Layer 2: tengu_harbor GrowthBook flag must be enabled
Layer 3: OAuth required (API key users BLOCKED)
Layer 4: Team/Enterprise must set channelsEnabled: true in managed settings
Layer 5: Server must be in --channels list for session
Layer 6: Plugin must be on approved allowlist
```

**Why 6 layers:** Channels allow external systems to inject messages into conversations — a massive security surface. Each layer independently blocks unauthorized access:
- Layer 1: Server self-declaration
- Layer 2: Feature flag rollout control
- Layer 3: Identity verification (OAuth = verified user, API key = service account)
- Layer 4: Organizational policy
- Layer 5: Session-level opt-in
- Layer 6: Plugin-level allowlist

#### Channel Allowlist

**File:** `ant-internal/categories/12-mcp.md` lines 29-44

```typescript
getChannelAllowlist():
  Reads tengu_harbor_ledger from GrowthBook

isChannelAllowlisted(plugin):
  Checks if {marketplace, plugin} tuple is on approved ledger
  // Plugin-level granularity: if plugin approved, ALL its channel servers are
```

**Bypass:** `--dangerously-load-development-channels` for local dev

#### Permission Relay Pattern

```
1. Channel pushes message to conversation
2. Model responds
3. Server parses user reply against regex
4. Server emits structured permission event
5. Meta key sanitization: only [a-zA-Z_][a-zA-Z0-9_]* to prevent XML injection
```

### 1.5 MCP Skills from Servers

**Sources:** `07-skill-loading-system-gated.md` lines 13, `07-skill-system-EXPANDED.md` lines 1036-1074

#### MCP Skill Builders — Write-Once Registry Pattern

**Problem:** MCP skill discovery needs `createSkillCommand` and `parseSkillFrontmatterFields` from `loadSkillsDir.ts`, but:
- Dynamic import fails in Bun-bundled binaries
- Static import creates circular dependency: `client.ts -> mcpSkills.ts -> loadSkillsDir.ts -> ... -> client.ts`

**Solution:**

```typescript
// mcpSkillBuilders.ts — dependency-graph leaf, imports nothing but types
let builders: MCPSkillBuilders | null = null

export function registerMCPSkillBuilders(b: MCPSkillBuilders): void {
  builders = b  // Write once
}

export function getMCPSkillBuilders(): MCPSkillBuilders {
  if (!builders) {
    throw new Error('MCP skill builders not registered')
  }
  return builders
}

// Registration at loadSkillsDir.ts module init (line 1083-1086):
registerMCPSkillBuilders({
  createSkillCommand,
  parseSkillFrontmatterFields,
})
```

**Why:** Breaks circular dependency without dynamic imports. The registry is written once at startup via the static import chain: `main -> commands -> loadSkillsDir`.

#### MCP Skill Sandboxing

**File:** `07-skill-loading-system-gated.md` line 127

MCP skills are sandboxed — they **cannot** execute `!` shell commands:

```typescript
// In createSkillCommand.getPromptForCommand():
IF loadedFrom != 'mcp':
  finalContent = await executeShellCommandsInPrompt(...)
// MCP skills skip shell execution entirely
```

### 1.6 MCP Server Lifecycle Management

**Sources:** `ant-internal/categories/12-mcp.md` lines 77-102, `ABSOLUTE-BEST-EDGE-CASE-TECHNIQUES.md` lines 908-944

#### Connection Management

**File:** `src/src/services/mcp/useManageMCPConnections.ts`

```
Capabilities:
- connect(serverConfig) → establish connection
- reconnect(serverName) → exponential backoff reconnection
- toggle(serverName) → enable/disable
- disconnect(serverName) → clean shutdown
```

#### Exponential Backoff Reconnection

```
5 attempts, 1s-30s backoff:
  Attempt 1: 1s delay
  Attempt 2: 2s delay
  Attempt 3: 4s delay
  Attempt 4: 8s delay
  Attempt 5: 16s delay (capped at 30s)
```

#### Process Shutdown — SIGINT → SIGTERM → SIGKILL Escalation

**File:** `ABSOLUTE-BEST-EDGE-CASE-TECHNIQUES.md` lines 908-944

```typescript
// Stage 1: SIGINT (graceful, like Ctrl+C)
process.kill(childPid, 'SIGINT')

// Stage 2: Wait 100ms, then SIGTERM if still alive
await sleep(100)
if (!resolved) {
  process.kill(childPid, 'SIGTERM')
  await sleep(400)
}

// Stage 3: SIGKILL (force kill)
if (!resolved) {
  process.kill(childPid, 'SIGKILL')
}

// Polling: 50ms intervals to check process existence
// Failsafe: 600ms absolute timeout
```

**Why 3 stages:**
- SIGINT: Gives server chance to clean up (save state, close connections)
- SIGTERM: Standard Unix termination signal
- SIGKILL: Last resort, cannot be caught or ignored

#### Batched State Updates

```
Batched MCP state updates with 16ms flush window
// Batches rapid state changes (connect/disconnect) to avoid UI thrashing
```

#### Stale Plugin Client Cleanup

```
Stale plugin client cleanup:
- Detects when plugin is updated/uninstalled
- Disconnects old MCP client
- Creates new client with updated config
```

#### Stdio stderr Cap

**File:** `ant-internal/categories/12-mcp.md` line 123

```
Stdio stderr cap: 64MB to prevent unbounded memory growth
```

### 1.7 MCP Tool Call Routing

**Sources:** `06-tool-execution-EXPANDED.md` lines 598-649, `06-tool-execution-system-audit.md` lines 59-82

#### Tool Assembly Pipeline

```
assembleToolPool(permissionContext, mcpTools):
  1. Get built-in tools via getTools(permissionContext)
  2. Filter MCP tools by deny rules
  3. Sort each partition by name (prompt-cache stability)
  4. Deduplicate by name (built-in tools take precedence)
  5. Return merged, sorted, deduplicated tool list
```

#### MCP Tool Naming Convention

```
mcp__<serverName>__<toolName>
// Example: mcp__github__create_issue
// Example: mcp__slack__send_message
```

#### Tool Orchestration

**File:** `06-tool-execution-system-audit.md` lines 59-82

```
runTools(toolUseMessages):
  1. Partition tool calls into batches:
     - Consecutive concurrency-safe tools → one batch
     - Each non-concurrency-safe tool → own batch

  2. For each batch:
     If concurrency-safe:
       Run all tools concurrently (up to CLAUDE_CODE_MAX_TOOL_USE_CONCURRENCY)
     Else:
       Run tools serially
```

### 1.8 MCP Error Handling

**Sources:** `ant-internal/categories/12-mcp.md` lines 104-125, `ABSOLUTE-BEST-EDGE-CASE-TECHNIQUES.md` lines 798-836

#### Session Expiry Detection

```
Session expiry detected via:
- HTTP 404 response
- JSON-RPC error code -32001
```

#### MCP Fetch Timeout — Avoiding Stale AbortSignal Memory Leak

**File:** `ABSOLUTE-BEST-EDGE-CASE-TECHNIQUES.md` lines 798-836

```typescript
// PROBLEM: AbortSignal.timeout() creates timer only released on GC
// Bun's lazy GC → ~2.4KB native memory leak per request
// SOLUTION: Manual AbortController + setTimeout

const controller = new AbortController()
const timer = setTimeout(
  c => c.abort(new DOMException('The operation timed out.', 'TimeoutError')),
  MCP_REQUEST_TIMEOUT_MS, controller,
)
timer.unref?.()  // Don't block process exit

const parentSignal = init?.signal
const abort = () => controller.abort(parentSignal?.reason)
parentSignal?.addEventListener('abort', abort)

const cleanup = () => {
  clearTimeout(timer)
  parentSignal?.removeEventListener('abort', abort)
}
```

#### Tool Result Truncation & Validation

- MCP tool results validated against output schema
- Results truncated if exceeding max size
- Truncation indicator shown to model

#### Schema-Not-Sent Detection

**File:** `06-tool-execution-EXPANDED.md` lines 541-550

When a deferred MCP tool is called without its schema being sent:

```
buildSchemaNotSentHint(tool, messages, tools):
  1. If tool search not enabled optimistically → null
  2. If ToolSearchTool not available → null
  3. If tool is not deferred → null
  4. If tool name in discovered tools → null
  5. Otherwise → hint telling model to use ToolSearchTool first
```

### 1.9 MCP Server-to-Agent Communication

**Sources:** `04-plugin-system-EXPANDED.md` lines 407-419, `ant-internal/categories/12-mcp.md` lines 104-125

#### Environment Variable Resolution

```
resolvePluginMcpEnvironment(config, plugin, userConfig):
  For each string value in config (command, args, env, url, headers):
    1. substitutePluginVariables(value, plugin)
       - ${CLAUDE_PLUGIN_ROOT} → plugin.path
       - ${CLAUDE_PLUGIN_DATA} → getPluginDataDir(plugin.source)
    2. substituteUserConfigVariables(value, userConfig)
       - ${user_config.KEY} → saved option value
    3. expandEnvVarsInString(value)
       - ${VAR} → process.env.VAR
       - ${VAR:-default} → process.env.VAR || 'default'
```

#### Server Scoping

Plugin MCP servers are prefixed to avoid conflicts:
- Server name: `plugin:<pluginName>:<serverName>`
- Scope: `'dynamic'`
- `pluginSource` field added for tracking

#### In-Process Servers

**File:** `ant-internal/categories/12-mcp.md` line 112

- Chrome MCP (in-process)
- Computer Use MCP (in-process)

---

## 2. Plugin-MCP Integration

### 2.1 How Plugins Provide MCP Servers

**Sources:** `04-plugin-system-supply-chain.md` lines 16-24, `04-plugin-system-EXPANDED.md` lines 375-444

Plugins can provide MCP servers through their manifest:

```json
{
  "name": "my-plugin",
  "mcpServers": {
    "my-server": {
      "command": "node",
      "args": ["${CLAUDE_PLUGIN_ROOT}/server/index.js"],
      "env": {
        "API_KEY": "${user_config.apiKey}"
      }
    }
  }
}
```

**Multiple formats supported:**
- `.mcp.json` file in plugin directory
- `manifest.mcpServers` field (string, array, or object)
- MCPB files (`.mcpb` / `.dxt`) — ZIP bundles
- Inline config objects

### 2.2 MCP Server Auto-Installation

**Sources:** `04-plugin-system-EXPANDED.md` lines 127-163, 722-757

#### Auto-Update Mechanism

```
autoUpdateMarketplacesAndPluginsInBackground():
  1. Check shouldSkipPluginAutoupdate() → skip if disabled
  2. Get auto-update enabled marketplaces:
     - From known_marketplaces.json autoUpdate field
     - Settings-declared autoUpdate takes precedence
     - Official marketplaces: autoUpdate=true by default
     - Third-party: autoUpdate=false by default
  3. For each auto-update marketplace (parallel):
     refreshMarketplace(name):
       - Git source: git pull in-place (with SSH/HTTPS fallback)
       - URL source: re-download marketplace.json
       - Local source: validate file still exists
       - Official marketplace: try GCS mirror first, then git fallback
  4. For each installed plugin from updated marketplaces:
     updatePluginOp(pluginId, scope):
       - Fetch latest from source
       - Calculate new version
       - If version differs: copy to new versioned cache
       - Update installed_plugins.json (disk only, memory unchanged)
       - Mark old version orphaned if no longer referenced
  5. If any plugins updated → notify via callback (REPL shows restart prompt)
```

#### Non-Inplace Updates

Updates create a NEW versioned cache directory. The running session continues using the old version. On restart, the new version is loaded. This prevents mid-session breakage.

### 2.3 MCP Server Configuration Storage

**Sources:** `ant-internal/categories/12-mcp.md` lines 129-146, `04-plugin-system-EXPANDED.md` lines 690-716

#### Multi-Scope MCP Config

```
Config merge order (later overrides earlier):
1. Enterprise (exclusive if present)
2. User (~/.claude/.mcp.json)
3. Project ($project/.mcp.json)
4. Local ($project/.claude/.mcp.json)
5. Dynamic (runtime, plugins)
6. Claude.ai (remote proxy)
```

#### Policy Filtering

```
Policy filtering: allowlist/denylist by name, command, URL
Server deduplication: plugin vs manual, claude.ai vs manual
Signature-based dedup: stdio:[command] or url:[unwrapped_url]
```

#### Atomic File Writes

```
Atomic file writes with temp file + rename for .mcp.json
// Prevents corruption from interrupted writes
```

#### Plugin Options Storage

**File:** `04-plugin-system-EXPANDED.md` lines 696-709

| Option Type | Storage |
|-------------|---------|
| Non-sensitive | `settings.json` → `pluginConfigs[pluginId].options` |
| Sensitive | Secure storage (macOS keychain or `.credentials.json`) |

### 2.4 MCP Server Updates Management

**Sources:** `04-plugin-system-EXPANDED.md` lines 722-757, 748-757

#### Version Calculation Priority

```
1. manifest.version (from plugin.json)
2. providedVersion (from marketplace entry or installed_plugins.json)
3. Git commit SHA (pre-resolved for git-subdir, or from .git in install path)
4. 'unknown' (last resort)
```

#### Delisting Detection

```
detectAndUninstallDelistedPlugins():
  1. Load flagged plugins cache
  2. Load installed_plugins.json (V2)
  3. For each marketplace in known_marketplaces.json:
     a. Get marketplace catalog
     b. If forceRemoveDeletedPlugins is true:
        - Compare installed plugins vs marketplace plugins
        - For each delisted plugin:
          * Skip if already flagged
          * Skip if only managed-scope installations
          * Auto-uninstall from user/project/local scopes
          * Add to flagged plugins list
```

#### Flagged Plugin Lifecycle

- Stored in `~/.claude/plugins/flagged-plugins.json`
- Format: `{plugins: {pluginId: {flaggedAt: string, seenAt?: string}}}`
- Auto-expire after 48 hours from `seenAt`
- User can dismiss (remove from flagged list)

### 2.5 MCP Server Allowlists

**Sources:** `04-plugin-system-supply-chain.md` lines 118-130, `04-plugin-system-EXPANDED.md` lines 794-838

#### Enterprise Policy Enforcement

```
Policy Sources (from policySettings / managed-settings.json):

| Policy Setting | Type | Effect |
|----------------|------|--------|
| enabledPlugins[pluginId] | false | Force-disables plugin |
| strictKnownMarketplaces | MarketplaceSource[] | Allowlist |
| blockedMarketplaces | MarketplaceSource[] | Blocklist |
| pluginTrustMessage | string | Custom trust message |
```

#### Policy Check Flow

```
isSourceAllowedByPolicy(source):
  1. Check blocklist first (takes precedence):
     - Exact source match
     - GitHub repo vs git URL cross-matching
     - Ref/path constraint matching
     - If blocked → return false
  2. Check allowlist:
     - If null → no restrictions, return true
     - Empty array → deny all, return false
     - For each entry: exact/hostPattern/pathPattern match
     - If any match → return true
  3. No match → return false
```

#### Policy Enforcement Points

1. **Marketplace addition**: Policy check BEFORE any network/filesystem ops
2. **Plugin loading**: If policy active and marketplace config missing → BLOCK (fail-closed)
3. **Plugin installation**: Check `isPluginBlockedByPolicy()` for root AND all transitive deps
4. **Plugin enable**: Check before writing settings
5. **Session plugin override**: Managed settings locked plugins cannot be overridden

#### Fail-Closed Guard

If enterprise policy is active but marketplace config is corrupted/missing, the plugin is BLOCKED rather than loaded unchecked. This prevents silent fail-open.

### 2.6 MCP Channel Allowlists

**Sources:** `ant-internal/categories/12-mcp.md` lines 29-44, `ABSOLUTE-BEST-EDGE-CASE-TECHNIQUES.md` lines 1581-1600

```typescript
// Approved channel plugins allowlist
// --channels plugin:name@marketplace entries only register if
// {marketplace, plugin} is on this list
// server: entries bypass this check (manually configured)

getChannelAllowlist():
  Reads tengu_harbor_ledger from GrowthBook

isChannelsEnabled():
  Reads tengu_harbor GrowthBook flag (default false)

isChannelAllowlisted(plugin):
  Checks if {marketplace, plugin} tuple is on approved ledger
  // Plugin-level granularity: if plugin approved, ALL its channel servers are
```

**Design:** Pure `{marketplace, plugin}` tuple comparison — no wildcards, no patterns, no regex. Impossible to accidentally allow a broader set than intended.

---

## 3. Tool System Architecture

### 3.1 Tool Assembly: Built-in + MCP

**Sources:** `06-tool-execution-system-audit.md` lines 7-26, `06-tool-execution-EXPANDED.md` lines 598-649

#### Tool Interface

**File:** `src/src/Tool.ts:362-695`

```typescript
interface Tool<Input, Output, Progress> {
  // Core
  name: string
  aliases?: string[]
  inputSchema: Zod schema
  outputSchema?: Zod schema
  maxResultSizeChars: number

  // Methods
  call(args, context, canUseTool, parentMessage, onProgress): Promise<ToolResult>
  description(input, options): string
  prompt(options): string
  isEnabled(): boolean
  isReadOnly(input): boolean
  isConcurrencySafe(input): boolean
  isDestructive?(input): boolean
  checkPermissions(input, context): Promise<PermissionResult>
  validateInput?(input, context): void

  // MCP-specific
  shouldDefer?: boolean
  alwaysLoad?: boolean
  isMcp?: boolean
  isLsp?: boolean
  mcpInfo?: { serverName, toolName }
}
```

#### Tool Assembly Pipeline

```
assembleToolPool(permissionContext, mcpTools):
  1. Get built-in tools via getTools(permissionContext)
  2. Filter MCP tools by deny rules
  3. Sort each partition by name (prompt-cache stability)
  4. Deduplicate by name (built-in tools take precedence)
  5. Return merged, sorted, deduplicated tool list
```

#### getTools() Filtering

```
getTools(permissionContext):
  1. If CLAUDE_CODE_SIMPLE:
     → [BashTool, FileReadTool, FileEditTool]
     (+ REPLTool if REPL mode enabled)
     (+ AgentTool, TaskStopTool, SendMessageTool if coordinator mode)

  2. Otherwise:
     a. Get all base tools (getAllBaseTools)
     b. Filter out special tools (ListMcpResources, ReadMcpResource, SyntheticOutput)
     c. Filter by deny rules (filterToolsByDenyRules)
     d. If REPL mode: hide REPL_ONLY_TOOLS
     e. Filter by isEnabled()
```

### 3.2 Tool Deduplication

**Sources:** `06-tool-execution-system-audit.md` line 26, `06-tool-execution-EXPANDED.md` lines 598-606

#### Built-in Wins Over MCP

```
Deduplicate by name (built-in tools take precedence):
  If built-in tool named "Read" exists AND MCP server provides "Read":
    → Use built-in Read, discard MCP Read
```

**Why:** Built-in tools are trusted, optimized, and have full permission integration. MCP tools with the same name could be malicious or incompatible.

#### MCP Server-Prefix Deny Rules

```
filterToolsByDenyRules:
  - Filters tools matching blanket deny rules
  - MCP server-prefix rules strip ALL tools from that server
  // Example: deny rule "mcp__evil_server__*" removes all tools from evil_server
```

### 3.3 Tool Search (Deferred Discovery)

**Sources:** `06-tool-execution-EXPANDED.md` lines 460-528

#### ToolSearchTool Operation

```
Query forms:
  select:Tool1,Tool2  → Direct selection
  keyword search      → Ranked keyword matching
  +required term      → Required term matching

Scoring:
  Exact part match: 10-12 points
  Substring match: 5-6 points
  searchHint match: 4 points
  Description match: 2 points
```

#### Enablement Logic

```
getToolSearchMode():
  1. If CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS → 'standard'
  2. If auto:0 → 'tst'
  3. If auto:100 → 'standard'
  4. If auto:N (1-99) → 'tst-auto'
  5. If truthy → 'tst'
  6. If falsy (defined) → 'standard'
  7. If unset → 'tst' (DEFAULT)

isToolSearchEnabled() (definitive):
  1. Check model supports tool_reference (haiku = no)
  2. Check ToolSearchTool available in tools
  3. Check mode:
     - 'tst' → true
     - 'tst-auto' → check threshold (token count or char heuristic)
     - 'standard' → false
```

#### Threshold Calculation (tst-auto mode)

- Default: 10% of context window
- Configurable: `ENABLE_TOOL_SEARCH=auto:N` where N is percentage
- Uses token counting API if available, falls back to char heuristic (2.5 chars/token)

### 3.4 Tool Permission Checking

**Sources:** `06-tool-execution-system-audit.md` lines 84-103, `06-tool-execution-EXPANDED.md` lines 262-338

#### Permission Resolution Pipeline

```
1. Zod schema validation → rejects invalid input types
2. validateInput() → tool-specific value validation
3. PreToolUse hooks → can modify input, deny, allow, or ask
4. resolveHookPermissionDecision() → merges hook results with rule-based permissions
5. canUseTool() → interactive permission prompt (if needed)
6. PermissionDecision.behavior check:
   - 'allow' → proceed to tool.call()
   - 'deny' → return error message
   - 'ask' → show permission dialog
7. tool.call() → actual execution
8. PostToolUse hooks → can modify output, block continuation
```

#### Rule-Based Permission Matching

```
Rule types:
  Exact:    Bash(git status)        → matches exact command
  Prefix:   Bash(git:*)             → matches command prefix (word boundary)
  Wildcard: Bash(git *)             → matches with glob pattern

Rule sources:
  alwaysAllowRules: ToolPermissionRulesBySource  → Auto-approve
  alwaysDenyRules:  ToolPermissionRulesBySource  → Auto-reject
  alwaysAskRules:   ToolPermissionRulesBySource  → Always prompt
```

#### BashTool Permission Flow (Most Complex)

```
1. Exact match check (deny → ask → allow → passthrough)
2. Prefix match check (deny → ask)
3. Path constraints check (working directory restrictions)
4. Allow rule check
5. Sed constraints check
6. Mode-specific checks (auto mode classifier)
7. Read-only rule check (if BashTool.isReadOnly(input) → auto-allow)
8. Passthrough (triggers permission dialog)
```

#### Read-Only Auto-Allow

If `BashTool.isReadOnly(input)` returns true, the command is auto-allowed without permission prompt. The read-only validation uses:

- `COMMAND_ALLOWLIST`: 40+ commands with flag validation
- `READONLY_COMMANDS`: Simple commands with no dangerous flags
- `READONLY_COMMAND_REGEXES`: Regex patterns for complex commands

### 3.5 Tool Execution Parallelization

**Sources:** `06-tool-execution-system-audit.md` lines 59-82, `06-tool-execution-EXPANDED.md` lines 196-261

#### Partition Algorithm

```
partitionToolCalls(toolUseMessages):
  For each tool call:
    1. Parse input with tool.inputSchema.safeParse()
    2. If parse succeeds: call tool.isConcurrencySafe(parsedInput)
    3. If parse fails: treat as NOT concurrency safe
    4. If current tool is concurrency-safe AND previous batch is also:
       Add to current batch
    5. Else: Start new batch

  Returns: Array of { isConcurrencySafe, blocks[] }
```

#### Execution Flow

```
runTools(toolUseMessages):
  1. Partition tool calls into batches
  2. For each batch:
     If concurrency-safe:
       Run all tools concurrently via all() generator
       Max concurrency: CLAUDE_CODE_MAX_TOOL_USE_CONCURRENCY (default: 10)
       Queue contextModifiers
       Apply modifiers sequentially after ALL tools complete
     Else:
       Run tools serially
       Apply contextModifiers immediately
```

#### StreamingToolExecutor Concurrency Rules

```
canExecuteTool(isConcurrencySafe):
  Can execute if:
    - No tools currently executing, OR
    - This tool is concurrency-safe AND all executing tools are also concurrency-safe

processQueue():
  For each queued tool (in order):
    If canExecuteTool(tool.isConcurrencySafe):
      Start executing
    Else if tool is NOT concurrency-safe:
      Break (maintain order for non-concurrent tools)
```

**Key behaviors:**
- Non-concurrent tools get exclusive access (no other tools can run simultaneously)
- Concurrent-safe tools can run alongside other concurrent-safe tools
- Order is preserved: a non-concurrent tool blocks all subsequent tools until it completes
- **Bash error cascading**: Only Bash errors cancel sibling tools. Read/WebFetch failures don't cascade.

### 3.6 Tool Result Processing

**Sources:** `06-tool-execution-EXPANDED.md` lines 1-70, `06-tool-execution-system-audit.md` lines 7-26

#### Tool Result Size Limits

| Tool | maxResultSizeChars | Notes |
|------|-------------------|-------|
| FileReadTool | Infinity | Never persists (circular read loop) |
| BashTool | 30,000 | Truncated if exceeded |
| GrepTool | 20,000 | Content search results |
| Others | 100,000 | Default limit |

#### Result Truncation

- Results exceeding `maxResultSizeChars` are truncated
- Truncation indicator shown to model
- Model can request more specific output

#### Context Modifiers

```
contextModifier in ToolResult:
  - Tools can return a function that modifies ToolUseContext
  - Only honored for tools that are NOT concurrency safe
  - SkillTool uses this to inject allowed tools and model overrides
  - For concurrent tools: modifiers queued and applied after ALL tools complete
```

#### PostToolUse Hook Processing

```
runPostToolUseHooks():
  - Can modify MCP tool output (updatedMCPToolOutput)
  - Can block continuation (preventContinuation)
  - Can add context messages
  - Can provide stop reason
  - Note: Only modifies MCP tool outputs for non-MCP tools
```

---

## 4. Self-Healing Patterns

### 4.1 Failure Detection & Recovery

**Sources:** `ABSOLUTE-BEST-EDGE-CASE-TECHNIQUES.md` lines 318-359, 636-664, 759-793

#### Prompt-Too-Long (PTL) Retry with Self-Healing Head Truncation

**File:** `src/services/compact/compact.ts:243-291`

```typescript
const PTL_RETRY_MARKER = '[earlier conversation truncated for compaction retry]'

export function truncateHeadForPTLRetry(messages, ptlResponse): Message[] | null {
  // Strip our own synthetic marker from a previous retry
  const input = messages[0]?.type === 'user' &&
    messages[0].isMeta &&
    messages[0].message.content === PTL_RETRY_MARKER
    ? messages.slice(1) : messages

  const groups = groupMessagesByApiRound(input)
  if (groups.length < 2) return null

  const tokenGap = getPromptTooLongTokenGap(ptlResponse)
  let dropCount
  if (tokenGap !== undefined) {
    // Precise: drop exactly enough groups to close the token gap
    let acc = 0; dropCount = 0
    for (const g of groups) {
      acc += roughTokenCountEstimationForMessages(g)
      dropCount++
      if (acc >= tokenGap) break
    }
  } else {
    // Fallback: drop 20% of groups
    dropCount = Math.max(1, Math.floor(groups.length * 0.2))
  }

  dropCount = Math.min(dropCount, groups.length - 1)  // Keep at least one group
  if (dropCount < 1) return null

  const sliced = groups.slice(dropCount).flat()
  if (sliced[0]?.type === 'assistant') {
    return [createUserMessage({ content: PTL_RETRY_MARKER, isMeta: true }), ...sliced]
  }
  return sliced
}
```

**Step by step:**
1. Strip previous retry marker to prevent infinite loops
2. Group messages by API round
3. Parse API error to extract exact token gap
4. Drop groups until gap is closed (or 20% fallback)
5. Keep at least one group (never drop everything)
6. Prepend synthetic user message if needed (API requires user-first)
7. Add retry marker to detect if this retry also fails

**Why designed this way:** The compact request itself can hit prompt-too-long. Without this escape hatch, the user is permanently stuck. The marker prevents infinite retry loops. The 20% fallback handles unparseable API errors.

#### Streaming Idle Timeout Watchdog

**File:** `src/services/api/claude.ts:1868-1928`

```typescript
const STREAM_IDLE_TIMEOUT_MS = 90_000  // 90 seconds
const STREAM_IDLE_WARNING_MS = 45_000  // 45 seconds

function resetStreamIdleTimer(): void {
  clearStreamIdleTimers()
  if (!streamWatchdogEnabled) return
  streamIdleWarningTimer = setTimeout(warnMs => {
    logForDebugging(`Streaming idle warning: no chunks for ${warnMs / 1000}s`)
  }, STREAM_IDLE_WARNING_MS, STREAM_IDLE_WARNING_MS)
  streamIdleTimer = setTimeout(() => {
    streamIdleAborted = true
    streamWatchdogFiredAt = performance.now()
    releaseStreamResources()
  }, STREAM_IDLE_TIMEOUT_MS)
}
```

**Why:** The SDK's request timeout only covers the initial `fetch()`, not the streaming body. A silently dropped TCP connection can hang indefinitely. The watchdog uses a sliding window — reset on every chunk.

### 4.2 Retry Logic with Exponential Backoff

**Sources:** `ABSOLUTE-BEST-EDGE-CASE-TECHNIQUES.md` lines 949-978, `ant-internal/categories/12-mcp.md` lines 91-92

#### API Retry with Persistent Mode

**File:** `src/services/api/withRetry.ts:477-512`

```typescript
// In persistent mode (unattended sessions):
if (persistent) {
  // Chunk long sleeps so the host sees periodic stdout activity
  // and does not mark the session idle
  let remaining = delayMs
  while (remaining > 0) {
    if (options.signal?.aborted) throw new APIUserAbortError()
    if (error instanceof APIError) {
      yield createSystemAPIErrorMessage(error, remaining, reportedAttempt, maxRetries)
    }
    const chunk = Math.min(remaining, HEARTBEAT_INTERVAL_MS)  // 30 seconds
    await sleep(chunk, options.signal, { abortError })
    remaining -= chunk
  }
  if (attempt >= maxRetries) attempt = maxRetries  // Clamp so for-loop never terminates
}
```

**Step by step:**
1. Calculate backoff delay (exponential: 1s, 2s, 4s, 8s, 16s, 30s cap)
2. In persistent mode, chunk the sleep into 30-second intervals
3. Each chunk yields a system message to keep session alive
4. Clamp attempt counter so for-loop never terminates
5. Check abort signal between chunks

**Why:** Long backoff delays (up to 6 hours) would cause the host to mark the session idle. Chunked sleeps with periodic stdout yields keep the session alive and provide progress feedback.

#### MCP Reconnection Backoff

```
5 attempts, 1s-30s exponential backoff:
  Attempt 1: 1s
  Attempt 2: 2s
  Attempt 3: 4s
  Attempt 4: 8s
  Attempt 5: 16s (capped at 30s)
```

### 4.3 Circuit Breakers

**Sources:** `ABSOLUTE-BEST-EDGE-CASE-TECHNIQUES.md` lines 1246-1265

#### Autocompact Circuit Breaker

**File:** `src/services/compact/autoCompact.ts:257-265`

```typescript
// Circuit breaker: stop retrying after N consecutive failures
if (tracking?.consecutiveFailures !== undefined &&
    tracking.consecutiveFailures >= MAX_CONSECUTIVE_AUTOCOMPACT_FAILURES) {
  return { wasCompacted: false }
}
```

**Impact:** BQ 2026-03-10 found 1,279 sessions had 50+ consecutive failures (up to 3,272) in a single session, wasting ~250K API calls/day globally. Circuit breaker at 3 consecutive failures eliminated this waste.

**Step by step:**
1. Track consecutive failures in auto-compact tracking state
2. On each failure, increment counter
3. On success, reset counter to 0
4. If counter >= MAX_CONSECUTIVE_AUTOCOMPACT_FAILURES (3): skip compaction
5. Log warning when breaker trips

**Why designed this way:** Sessions where context is irrecoverably over the limit would hammer the API with doomed compaction attempts. The circuit breaker stops the waste after 3 failures.

### 4.4 Stale Data Detection & Refresh

**Sources:** `ABSOLUTE-BEST-EDGE-CASE-TECHNIQUES.md` lines 1029-1103, 1345-1373

#### Two-Phase Cache Break Detection (12-Dimensional)

**File:** `src/services/api/promptCacheBreakDetection.ts:1-727`

```typescript
type PreviousState = {
  systemHash: number
  toolsHash: number
  cacheControlHash: number
  toolNames: string[]
  perToolHashes: Record<string, number>
  systemCharCount: number
  model: string
  fastMode: boolean
  globalCacheStrategy: string
  betas: string[]
  autoModeActive: boolean
  isUsingOverage: boolean
  cachedMCEnabled: boolean
  effortValue: string
  extraBodyHash: number
  callCount: number
  pendingChanges: PendingChanges | null
  prevCacheReadTokens: number | null
  cacheDeletionsPending: boolean
  buildDiffableContent: () => string
}
```

**Phase 1 (pre-call):** Record state and detect changes
**Phase 2 (post-call):** Check actual cache read tokens to confirm break occurred

**Key features:**
- Per-tool hash tracking identifies which specific tool's schema changed
- 77% of tool breaks are single-tool schema changes
- Sanitizes MCP tool names (collapses to 'mcp') to prevent filepath leakage
- Writes diff files for debugging
- Caps tracked sources at 10 with LRU eviction
- Minimum 2,000 token drop threshold to avoid false positives

#### Time-Based Microcompact: Cold Cache Detection

**File:** `src/services/compact/microCompact.ts:253-293`

```typescript
// Time-based trigger runs FIRST and short-circuits
// If gap since last assistant message exceeds threshold,
// server cache has expired → content-clear old tool results
const timeBasedResult = maybeTimeBasedMicrocompact(messages, querySource)
if (timeBasedResult) return timeBasedResult

// Only run cached MC for warm caches
if (mod.isCachedMicrocompactEnabled() && isMainThreadSource(querySource)) {
  return await cachedMicrocompactPath(messages, querySource)
}
```

**Two-path architecture:**
1. Time-based for cold caches (mutates content directly)
2. Cached MC for warm caches (uses cache_edits API)

### 4.5 Crashed Process Restart

**Sources:** `ABSOLUTE-BEST-EDGE-CASE-TECHNIQUES.md` lines 908-944, `ant-internal/categories/12-mcp.md` lines 77-102

#### MCP Process Shutdown & Restart

**File:** `ABSOLUTE-BEST-EDGE-CASE-TECHNIQUES.md` lines 908-944

```
Shutdown escalation:
  Stage 1: SIGINT (100ms grace)
  Stage 2: SIGTERM (400ms grace)
  Stage 3: SIGKILL (force)

Polling: 50ms intervals to check process existence
Failsafe: 600ms absolute timeout
```

#### LSP Server Restart Configuration

**File:** `04-plugin-system-EXPANDED.md` lines 462-476

```typescript
interface LspServerConfig {
  restartOnCrash?: boolean   // Auto-restart on crash
  maxRestarts?: number       // Max restart attempts
  startupTimeout?: number    // Max ms to wait for startup
  shutdownTimeout?: number   // Max ms to wait for shutdown
}
```

#### Stale Plugin Client Cleanup

```
When plugin is updated/uninstalled:
  1. Detect config change
  2. Disconnect old MCP client
  3. Clean up stale resources
  4. Create new client with updated config
```

### 4.6 Memory Corruption Detection & Repair

**Sources:** `ABSOLUTE-BEST-EDGE-CASE-TECHNIQUES.md` lines 843-867, 993-1026

#### GC-Optimized Write Queue

**File:** `src/utils/task/diskOutput.ts:178-205`

```typescript
#writeAllChunks(): Promise<void> {
  // You MUST NOT add an await here!! That will cause memory to balloon
  return this.#fileHandle!.appendFile(this.#queueToBuffers())
}

#queueToBuffers(): Buffer {
  // Use .splice to in-place mutate the array, informing the GC it can free it
  const queue = this.#queue.splice(0, this.#queue.length)
  const buffer = Buffer.allocUnsafe(totalLength)
  // ... write strings into buffer
  return buffer
}
```

**Why:** Chained `.then()` closures capture their data until the whole chain resolves, causing memory retention. Using `splice` allows immediate GC of queue elements.

#### Tool Result Pairing Repair

**File:** `ABSOLUTE-BEST-EDGE-CASE-TECHNIQUES.md` lines 1195-1242

```typescript
export function adjustIndexToPreserveAPIInvariants(messages, startIndex): number {
  // Step 1: Handle tool_use/tool_result pairs
  const allToolResultIds = []
  for (let i = startIndex; i < messages.length; i++) {
    allToolResultIds.push(...getToolResultIds(messages[i]))
  }

  const neededToolUseIds = new Set(
    allToolResultIds.filter(id => !toolUseIdsInKeptRange.has(id))
  )

  // Walk backward to find matching tool_use blocks
  for (let i = adjustedIndex - 1; i >= 0 && neededToolUseIds.size > 0; i--) {
    if (hasToolUseWithIds(message, neededToolUseIds)) {
      adjustedIndex = i
      neededToolUseIds.delete(block.id)
    }
  }

  // Step 2: Handle thinking blocks that share message.id
  // ...
  return adjustedIndex
}
```

**Why:** When session memory compaction slices messages, it can split tool_use/tool_result pairs (causing API errors). The two-step index adjustment walks backward to find and include orphan tool_uses and sibling thinking blocks.

#### Parallel Tool Call Interleaving Fix

**File:** `ABSOLUTE-BEST-EDGE-CASE-TECHNIQUES.md` lines 986-1026

```typescript
export function tokenCountWithEstimation(messages): number {
  let i = messages.length - 1
  while (i >= 0) {
    const message = messages[i]
    const usage = message ? getTokenUsage(message) : undefined
    if (message && usage) {
      // Walk back past sibling records with same message.id
      const responseId = getAssistantMessageId(message)
      if (responseId) {
        let j = i - 1
        while (j >= 0) {
          const prior = messages[j]
          const priorId = prior ? getAssistantMessageId(prior) : undefined
          if (priorId === responseId) {
            i = j  // Earlier split of same API response
          } else if (priorId !== undefined) {
            break  // Different API response
          }
          j--
        }
      }
      return getTokenCountFromUsage(usage) +
        roughTokenCountEstimationForMessages(messages.slice(i + 1))
    }
  }
  return roughTokenCountEstimationForMessages(messages)
}
```

**Why:** When the model makes multiple parallel tool calls, streaming emits separate assistant records per content block (all sharing the same `message.id`). Stopping at the last assistant record misses interleaved tool_results. Walking backward past sibling records ensures every interleaved tool_result is included.

---

## 5. AgentOS Adaptation Guide

### 5.1 MCP Server Management for AgentOS

#### Server Registry Pattern

Adapt the multi-scope config system:

```python
class MCPServerRegistry:
    scopes = ['enterprise', 'user', 'project', 'local', 'dynamic', 'remote']

    def resolve_servers(self):
        if self.enterprise_config:
            return self.enterprise_config  # Exclusive control
        return self._merge_scopes()  # Later overrides earlier
```

#### Transport Abstraction

Support multiple transport types with a common interface:

```python
class MCPTransport(ABC):
    async def connect(self): ...
    async def disconnect(self): ...
    async def send(self, message): ...
    async def receive(self): ...

class StdioTransport(MCPTransport): ...
class SSETransport(MCPTransport): ...
class WebSocketTransport(MCPTransport): ...
class HTTPTransport(MCPTransport): ...
```

#### Lifecycle Manager

```python
class MCPLifecycleManager:
    async def start_server(self, config):
        # Spawn process, establish connection, discover tools
        pass

    async def stop_server(self, name):
        # SIGINT → SIGTERM → SIGKILL escalation
        pass

    async def restart_on_crash(self, name):
        # Exponential backoff reconnection
        pass
```

### 5.2 Tool System for AgentOS

#### Tool Registry with Deduplication

```python
class ToolRegistry:
    def assemble_tool_pool(self, builtin_tools, mcp_tools):
        # 1. Filter MCP tools by deny rules
        # 2. Sort by name (cache stability)
        # 3. Deduplicate (builtin wins over MCP)
        # 4. Return merged list
        pass
```

#### Permission Pipeline

```python
class PermissionPipeline:
    async def check_permission(self, tool, input, context):
        # 1. Schema validation
        # 2. Input validation
        # 3. PreToolUse hooks
        # 4. Rule-based matching (exact/prefix/wildcard)
        # 5. Interactive prompt (if needed)
        # 6. Execute
        # 7. PostToolUse hooks
        pass
```

#### Parallel Execution Engine

```python
class ToolExecutor:
    MAX_CONCURRENCY = 10

    async def execute_tools(self, tool_calls):
        # Partition into concurrent-safe and serial batches
        # Run concurrent-safe tools in parallel (up to MAX_CONCURRENCY)
        # Run serial tools one at a time
        # Handle error cascading (Bash errors cancel siblings)
        pass
```

### 5.3 Self-Healing Infrastructure for AgentOS

#### Circuit Breaker Pattern

```python
class CircuitBreaker:
    def __init__(self, max_failures=3):
        self.max_failures = max_failures
        self.consecutive_failures = 0

    def record_success(self):
        self.consecutive_failures = 0

    def record_failure(self):
        self.consecutive_failures += 1

    def is_open(self):
        return self.consecutive_failures >= self.max_failures
```

#### Retry with Exponential Backoff

```python
class RetryWithBackoff:
    MAX_DELAY = 30
    HEARTBEAT_INTERVAL = 30

    async def execute_with_retry(self, fn, max_retries=5, persistent=False):
        for attempt in range(max_retries + 1):
            try:
                return await fn()
            except Exception as e:
                delay = min(2 ** attempt, self.MAX_DELAY)
                if persistent:
                    # Chunk sleep with heartbeat yields
                    remaining = delay
                    while remaining > 0:
                        chunk = min(remaining, self.HEARTBEAT_INTERVAL)
                        await self.yield_heartbeat(e, chunk, attempt, max_retries)
                        remaining -= chunk
                else:
                    await asyncio.sleep(delay)
        raise MaxRetriesExceeded()
```

#### Cache Break Detection

```python
class CacheBreakDetector:
    def record_state(self, system_hash, tools_hash, model, ...):
        self.previous_state = {
            'system_hash': system_hash,
            'tools_hash': tools_hash,
            'model': model,
            # ... 12 dimensions
        }

    def detect_break(self, current_state):
        changes = []
        for key, value in current_state.items():
            if value != self.previous_state.get(key):
                changes.append(key)
        return changes
```

#### Process Health Monitor

```python
class ProcessHealthMonitor:
    async def monitor_process(self, pid, config):
        # Watch for crashes
        # Auto-restart with exponential backoff
        # SIGINT → SIGTERM → SIGKILL shutdown
        # Stderr cap to prevent memory growth
        pass
```

### 5.4 Security Patterns for AgentOS

#### Fail-Closed Defaults

```python
# Default to safest option when uncertain
def is_undercover(repo_class):
    if repo_class is None:
        return True  # Unknown → undercover (fail-closed)
    return repo_class != 'internal'
```

#### Defense-in-Depth

```python
class SecurityPipeline:
    async def validate_command(self, command):
        # Layer 1: Schema validation
        # Layer 2: Input validation
        # Layer 3: PreToolUse hooks
        # Layer 4: Rule-based permissions
        # Layer 5: Interactive permission
        # Layer 6: Read-only validation
        # Layer 7: Path constraints
        # Layer 8: Sandbox
        # Layer 9: PostToolUse hooks
        # Layer 10: Auto-mode classifier
        pass
```

#### Fixed-Point Iteration for Env Var Stripping

```python
def strip_all_leading_env_vars(command, blocklist=None):
    """Fixed-point iteration: strip env vars, then wrappers, then env vars again"""
    stripped = command
    previous = ''
    while stripped != previous:
        previous = stripped
        stripped = strip_comment_lines(stripped)
        m = ENV_VAR_PATTERN.match(stripped)
        if not m:
            continue
        if blocklist and blocklist.match(m.group(1)):
            break
        stripped = stripped[len(m.group(0)):]
    return stripped.strip()
```

### 5.5 Key Environment Variables for AgentOS

| Variable | Purpose | Default |
|----------|---------|---------|
| `AGENTOS_MAX_TOOL_CONCURRENCY` | Max parallel tool executions | 10 |
| `AGENTOS_TOOL_SEARCH_MODE` | Tool search mode (tst/tst-auto/standard) | tst |
| `AGENTOS_RETRY_MAX_DELAY` | Max retry backoff delay (seconds) | 30 |
| `AGENTOS_CIRCUIT_BREAKER_THRESHOLD` | Failures before circuit opens | 3 |
| `AGENTOS_STREAM_IDLE_TIMEOUT` | Stream watchdog timeout (ms) | 90000 |
| `AGENTOS_MCP_REQUEST_TIMEOUT` | MCP request timeout (ms) | 60000 |
| `AGENTOS_STDERR_CAP` | MCP stderr cap (bytes) | 67108864 (64MB) |
| `AGENTOS_PLUGIN_CACHE_DIR` | Plugin cache directory | `~/.agentos/plugins` |

---

## Appendix: Source File Reference

| Finding Document | Key Sections |
|-----------------|--------------|
| `04-plugin-system-supply-chain.md` | Plugin sources, capabilities, supply chain risks, channel system |
| `04-plugin-system-EXPANDED.md` | Complete plugin loading algorithm, MCP/LSP integration, auto-update, policy |
| `ant-internal/categories/11-plugin-system.md` | Plugin management hooks, commands, utilities, services |
| `ant-internal/categories/12-mcp.md` | MCP instructions delta, channel allowlist, notifications, connections, client, config |
| `07-skill-loading-system-gated.md` | Skill loading pathways, frontmatter fields, shell execution, conditional skills |
| `07-skill-system-EXPANDED.md` | Complete skill loading algorithm, MCP skill builders, deduplication, bundled skills |
| `06-tool-execution-system-audit.md` | Tool interface, read-only classification, parallelization, permissions, bypass vectors |
| `06-tool-execution-EXPANDED.md` | Complete tool registry, concurrency safety, permission flow, tool search, assembly |
| `ABSOLUTE-BEST-EDGE-CASE-TECHNIQUES.md` | Self-healing patterns, circuit breakers, cache break detection, retry logic, process management |
