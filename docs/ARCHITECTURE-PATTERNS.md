# AgentOS Architecture Patterns

> Extracted from Claude Code's internal source code via reverse engineering. Every pattern includes exact file paths, line numbers, step-by-step mechanics, and design rationale.

---

## Table of Contents

1. [Memory System Architecture](#1-memory-system-architecture)
2. [Context Management Architecture](#2-context-management-architecture)
3. [Agentic Orchestration Architecture](#3-agentic-orchestration-architecture)
4. [Agent Swarm Architecture](#4-agent-swarm-architecture)

---

# 1. Memory System Architecture

## 1.1 Session Memory

### Purpose
Per-session memory file that maintains a running summary of the current conversation. Used for compaction and context preservation across long sessions.

### Source Files
| File | Lines | Purpose |
|------|-------|---------|
| `src/src/services/SessionMemory/sessionMemory.ts` | 1-495 | Core implementation — extraction, initialization |
| `src/src/services/SessionMemory/sessionMemoryUtils.ts` | 1-100 | Utilities — config, state management |
| `src/src/services/SessionMemory/prompts.ts` | — | Prompt templates for memory updates |
| `src/src/services/compact/sessionMemoryCompact.ts` | 1-630 | Session memory-based compaction |

### Gating
- **Primary gate**: GrowthBook flag `tengu_session_memory` (default: `false`) at `sessionMemory.ts:81`
- **Secondary gate**: Auto-compact must be enabled
- **Config**: GrowthBook flag `tengu_sm_config` provides config params
- **Compaction gate**: Both `tengu_session_memory` AND `tengu_sm_compact` must be true

### How It Works — Step by Step

```
1. INITIALIZATION (session start)
   initSessionMemory() registers a post-sampling hook
   → Only if auto-compact is enabled
   → Hook fires after each API response completes

2. THRESHOLD CHECKING (each turn)
   shouldExtractMemory() evaluates three conditions:
   a. Token count >= minimumMessageTokensToInit (default: 10,000)
   b. Context growth >= minimumTokensBetweenUpdate (default: 5,000)
      — Uses tokenCountWithEstimation (actual context size, not cumulative API usage)
   c. Tool calls >= toolCallsBetweenUpdates (default: 3) OR no tool calls in last turn

3. EXTRACTION (when thresholds met)
   a. Forks a background agent via runForkedAgent()
   b. Agent receives extraction prompt from prompts.ts
   c. Agent reads current session memory file (if exists)
   d. Agent reads current conversation transcript
   e. Agent produces updated memory content
   f. Agent writes to session memory file on disk
   g. Token usage statistics logged

4. COMPACTION INTEGRATION
   trySessionMemoryCompaction() called during auto-compact:
   a. Reads session memory file as summary context
   b. Uses memory as grounding for summarization
   c. Produces higher-quality compact than raw summarization
```

### Memory File Format
- Stored as a markdown file in the session's working directory
- Contains a running summary of conversation key points
- Updated incrementally (not rewritten from scratch)
- Used as input to `sessionMemoryCompact.ts` compaction path

### Threshold Configuration (`sessionMemoryUtils.ts:18-26`)

```typescript
export type SessionMemoryConfig = {
  minimumMessageTokensToInit: number      // 10,000 default
  minimumTokensBetweenUpdate: number      // 5,000 default
  toolCallsBetweenUpdates: number         // 3 default
}
```

**Design rationale**: Uses `tokenCountWithEstimation` (actual context size) rather than cumulative API usage to prevent double-counting as context grows. Three-threshold gating prevents excessive background agent spawns.

### Stale Extraction Detection (`sessionMemoryUtils.ts:89-100`)

```typescript
export async function waitForSessionMemoryExtraction(): Promise<void> {
  const startTime = Date.now()
  while (extractionStartedAt) {
    const extractionAge = Date.now() - extractionStartedAt
    if (extractionAge > EXTRACTION_STALE_THRESHOLD_MS) return  // >1min = stale
    if (Date.now() - startTime > EXTRACTION_WAIT_TIMEOUT_MS) return  // 15s timeout
    await sleep(100)
  }
}
```

**Design rationale**: Dual timeout prevents blocking. Staleness check (1min) handles crashed extractions. Absolute timeout (15s) prevents waiting too long for legitimate but slow extractions.

---

## 1.2 Team Memory

### Purpose
Shared memory scoped per-repo (identified by git remote hash), synchronized across all authenticated org members. Enables team-wide knowledge sharing.

### Source Files
| File | Purpose |
|------|---------|
| `src/src/services/teamMemorySync/index.ts` | Core sync service (1256 lines) |
| `src/src/services/teamMemorySync/types.ts` | TypeScript types and schemas |
| `src/src/services/teamMemorySync/watcher.ts` | File system watcher for push triggers |
| `src/src/services/teamMemorySync/teamMemSecretGuard.ts` | Secret detection guard |
| `src/src/services/teamMemorySync/secretScanner.ts` | Secret scanning |
| `src/src/memdir/teamMemPaths.ts` | Team memory path utilities |
| `src/src/utils/teamMemoryOps.ts` | Team memory operation detection |

### Gating
- **Primary gate**: `isTeamMemorySyncAvailable()` requires OAuth authentication at `index.ts:762-763`
- **Feature flag**: `feature('TEAMMEM')` for module loading
- **Team memory ops**: Requires team memory feature enabled

### API Contract

```
GET  /api/claude_code/team_memory?repo={owner/repo}            → TeamMemoryData
GET  /api/claude_code/team_memory?repo={owner/repo}&view=hashes → metadata only
PUT  /api/claude_code/team_memory?repo={owner/repo}            → upload entries
```

### How It Works — Step by Step

```
PULL (server → local):
1. Fetch team memory from server API
2. Use ETag for conditional requests (304 Not Modified)
3. Server wins per-key — overwrites local files
4. Write to local .claude/team-memory/ directory
5. Retry with exponential backoff on failure

PUSH (local → server):
1. Scan local .claude/team-memory/ for changes
2. Compare content hashes against server state
3. Delta upload — only keys whose hash differs
4. Secret scanning before upload (secretScanner.ts)
5. Conflict resolution with retries on 412 Precondition Failed

WATCHER:
1. File system watcher monitors .claude/team-memory/
2. Debounced to prevent excessive API calls
3. Triggers push on local changes
4. Suppresses retries on permanent failures
```

### Sync Semantics
- **Server wins**: Pull overwrites local files with server content
- **Delta push**: Only uploads keys whose content hash differs
- **No deletion propagation**: File deletions do NOT propagate (next pull restores deleted files)
- **Secret filtering**: Secret files are skipped and logged
- **Max file size**: 250KB per entry
- **Server-side limits**: GB-tunable per-org

### Team Memory Operations (`teamMemoryOps.ts:1-88`)

```typescript
isTeamMemorySearch()     // checks if a search tool targets team memory files
isTeamMemoryWriteOrEdit() // checks if Write/Edit targets team memory files
appendTeamMemorySummaryParts() // generates human-readable team memory activity summaries
```

**Design rationale**: Team memory is repo-scoped (not user-scoped) to enable team-wide knowledge sharing. Server-wins semantics prevent split-brain. Delta upload minimizes API traffic. Secret scanning prevents credential leakage across team members.

### Directory Structure
```
.claude/team-memory/           # Local team memory directory
├── <key1>.md                  # Team memory entry
├── <key2>.md                  # Team memory entry
└── ...
```

---

## 1.3 Durable Memory Extraction (extractMemories)

### Purpose
Extracts durable memories from the current session transcript and writes them to the auto-memory directory (`~/.claude/projects/<path>/memory/`). Persists knowledge across sessions.

### Source Files
| File | Purpose |
|------|---------|
| `src/src/services/extractMemories/extractMemories.ts` | Core implementation (615 lines) |
| `src/src/services/extractMemories/prompts.ts` | Prompt templates for memory extraction |
| `src/src/memdir/paths.ts` | Memory directory path utilities |
| `src/src/memdir/memoryScan.ts` | Memory file scanning |
| `src/src/query/stopHooks.ts:42-43,102,149` | Module loading and execution |
| `src/src/utils/backgroundHousekeeping.ts:7-8,35` | Initialization |

### Gating
- **Primary gate**: GrowthBook flag `tengu_passport_quail` (default: `false`) at `extractMemories.ts:536`
- **Secondary gate**: `isAutoMemoryEnabled()` from `memdir/paths`
- **Feature flag**: `feature('EXTRACT_MEMORIES')` for module loading
- **Additional gates**: Not in remote mode, not for subagents

### How It Works — Step by Step

```
1. INITIALIZATION
   initExtractMemories() creates extractor and drainer closures
   → Registered as background housekeeping task

2. TRIGGER (end of each query loop — no tool calls)
   executeExtractMemories() runs:
   a. Checks if there are new model-visible messages since last extraction
   b. If no new messages → skip
   c. If extraction already in progress → stash context for trailing run

3. EXTRACTION
   a. Forks agent via runForkedAgent()
   b. Agent receives extraction prompt from prompts.ts
   c. Agent reads session transcript
   d. Agent reads existing memory files in auto-memory directory
   e. Agent creates/updates memory files in auto-memory directory
   f. Token usage statistics logged

4. DRAIN (process exit)
   cli/print.ts:374-375,968 — drains pending memory extraction before exit
   → Ensures no extraction is lost on shutdown
```

### Memory Directory Structure
```
~/.claude/projects/<project-path>/memory/
├── <memory-file-1>.md    # Extracted durable memory
├── <memory-file-2>.md    # Extracted durable memory
└── ...
```

**Design rationale**: Runs only at end of query loops (no tool calls) to avoid interrupting active work. Stashing mechanism prevents concurrent extractions. Drain on exit ensures no data loss.

---

## 1.4 Memory Directory Structure (Complete)

```
~/.claude/
├── projects/
│   └── <project-path>/
│       ├── memory/                    # Auto-memory (durable, per-project)
│       │   └── *.md                   # Extracted memory files
│       └── .claude/
│           └── session-memory.md      # Per-session running summary
│
├── teams/
│   └── <team-name>/
│       └── inboxes/                   # Teammate mailboxes (IPC)
│           └── <agent-name>.json
│
└── team-memory/                       # Team memory (synced, per-repo)
    └── *.md                           # Shared team knowledge entries
```

---

## 1.5 Memory Preservation Across Compactions

### Post-Compaction Cleanup (`postCompactCleanup.ts:31-77`)

```typescript
export function runPostCompactCleanup(querySource?: QuerySource): void {
  const isMainThreadCompact =
    querySource === undefined ||
    querySource.startsWith('repl_main_thread') ||
    querySource === 'sdk'

  resetMicrocompactState()
  if (isMainThreadCompact) {
    require('../contextCollapse/index.js').resetContextCollapse()
    getUserContext.cache.clear?.()
    resetGetMemoryFilesCache('compact')
  }
  clearSystemPromptSections()
  clearClassifierApprovals()
  clearSpeculativeChecks()
  // Intentionally NOT calling resetSentSkillNames() — ~4K tokens saved
  clearBetaTracingState()
  void import('../../utils/attributionHooks.js').then(m => m.sweepFileContentCache())
  clearSessionMessagesCache()
}
```

### Key Design Decisions

1. **Selective cleanup based on query source**: Subagents (agent:*) share module-level state with the main thread. Resetting context-collapse or getUserContext when a SUBAGENT compacts would corrupt the MAIN thread's state.

2. **Skill content survives compaction**: `resetSentSkillNames()` is intentionally NOT called — skill content must survive across multiple compactions so `createSkillAttachmentIfNeeded()` can include the full skill text.

3. **Cache reset for memory files**: `resetGetMemoryFilesCache('compact')` clears the memory file cache so fresh memory files are read after compaction.

---

# 2. Context Management Architecture

## 2.1 Context Window Management

### Context Window Resolution Priority Chain (`context.ts:51-98`)

```
PRIORITY ORDER (first match wins):

1. ENV OVERRIDE (ant-only)
   if USER_TYPE === 'ant' && CLAUDE_CODE_MAX_CONTEXT_TOKENS:
     return parseInt(CLAUDE_CODE_MAX_CONTEXT_TOKENS)

2. EXPLICIT OPT-IN SUFFIX
   if model ends with '[1m]':
     return 1,000,000

3. MODEL CAPABILITY METADATA
   cap = getModelCapability(model)
   if cap.max_input_tokens >= 100,000:
     if cap.max_input_tokens > DEFAULT && is1mContextDisabled():
       return DEFAULT  // HIPAA compliance override
     return cap.max_input_tokens

4. BETA HEADER DETECTION
   if betas includes CONTEXT_1M_BETA_HEADER && modelSupports1M(model):
     return 1,000,000

5. EXPERIMENT TREATMENT
   if getSonnet1mExpTreatmentEnabled(model):
     return 1,000,000

6. ANT MODEL CONFIG
   if USER_TYPE === 'ant':
     antModel = resolveAntModel(model)
     if antModel?.contextWindow:
       return antModel.contextWindow

7. DEFAULT
   return MODEL_CONTEXT_WINDOW_DEFAULT  // 200,000
```

**Design rationale**: Six-layer priority chain with env overrides, explicit opt-in suffixes, capability metadata, beta headers, experiment treatments, and internal configs. Each layer can override the next, with safety checks for HIPAA compliance (`CLAUDE_CODE_DISABLE_1M_CONTEXT`).

### Effective Context Window = Window - Max Output Tokens (`autoCompact.ts:32-49`)

```typescript
export function getEffectiveContextWindowSize(model: string): number {
  const reservedTokensForSummary = Math.min(
    getMaxOutputTokensForModel(model),
    MAX_OUTPUT_TOKENS_FOR_SUMMARY,  // 20,000 (p99.99 of compact summary = 17,387)
  )
  let contextWindow = getContextWindowForModel(model, getSdkBetas())
  const autoCompactWindow = process.env.CLAUDE_CODE_AUTO_COMPACT_WINDOW
  if (autoCompactWindow) {
    contextWindow = Math.min(contextWindow, parseInt(autoCompactWindow, 10))
  }
  return contextWindow - reservedTokensForSummary
}
```

**Design rationale**: The context window must reserve space for the summary output during compaction. Uses p99.99 statistical analysis (17,387 tokens) to set the reserve at 20,000, capped by the model's actual max output tokens. Without this, the compact API call itself would hit prompt-too-long.

### Token Counting with Parallel Tool Call Interleaving (`tokens.ts:226-261`)

```typescript
export function tokenCountWithEstimation(messages: readonly Message[]): number {
  let i = messages.length - 1
  while (i >= 0) {
    const message = messages[i]
    const usage = message ? getTokenUsage(message) : undefined
    if (message && usage) {
      const responseId = getAssistantMessageId(message)
      if (responseId) {
        let j = i - 1
        while (j >= 0) {
          const prior = messages[j]
          const priorId = prior ? getAssistantMessageId(prior) : undefined
          if (priorId === responseId) {
            i = j  // Earlier split of same API response — anchor here instead
          } else if (priorId !== undefined) {
            break  // Hit a different API response — stop walking
          }
          j--  // priorId === undefined: user/tool_result/attachment, keep walking
        }
      }
      return getTokenCountFromUsage(usage) +
        roughTokenCountEstimationForMessages(messages.slice(i + 1))
    }
  }
  return roughTokenCountEstimationForMessages(messages)
}
```

**Edge case**: When the model makes multiple parallel tool calls in one API response, the streaming code emits a SEPARATE assistant record per content block — all sharing the same `message.id` and `usage`. The query loop interleaves each `tool_result` immediately after its `tool_use`. If you stop at the LAST assistant record, you only estimate the one tool_result after it and miss ALL earlier interleaved tool_results.

**Design rationale**: Walks backward past sibling records with the same `message.id` to find the FIRST split from the same API response, ensuring every interleaved tool_result is included in the estimation.

### Max Token Context Overflow Auto-Retry (`withRetry.ts:384-427`)

```typescript
if (error instanceof APIError) {
  const overflowData = parseMaxTokensContextOverflowError(error)
  if (overflowData) {
    const { inputTokens, contextLimit } = overflowData
    const safetyBuffer = 1000
    const availableContext = Math.max(0, contextLimit - inputTokens - safetyBuffer)
    if (availableContext < FLOOR_OUTPUT_TOKENS) throw error
    const minRequired = (retryContext.thinkingConfig.type === 'enabled'
      ? retryContext.thinkingConfig.budgetTokens : 0) + 1
    const adjustedMaxTokens = Math.max(FLOOR_OUTPUT_TOKENS, availableContext, minRequired)
    retryContext.maxTokensOverride = adjustedMaxTokens
    continue  // Retry with adjusted max_tokens
  }
}
```

**Design rationale**: Parses error with regex, computes available context with 1000-token safety buffer, accounts for thinking budget requirements, and retries with adjusted parameters. Prevents permanent stuck state when context is nearly full.

---

## 2.2 Compaction Strategies

### Three-Tier Compaction System

```
TIER 1: Time-Based Microcompact (cold cache)
  → Trigger: User AFK long enough for server cache to expire
  → Action: Content-clear old tool results directly
  → Skips cached MC (assumes warm cache, which is cold)
  → File: microCompact.ts:253-293

TIER 2: Cached Microcompact (warm cache)
  → Trigger: Tool results accumulate, cache still warm
  → Action: Uses cache_edits API to modify cached content
  → Only for main thread (prevents forked agents from registering in global state)
  → File: microCompact.ts (cachedMicrocompactPath)

TIER 3: Auto-Compact (full summarization)
  → Trigger: Context approaches effective window size
  → Action: Full conversation summarization via forked agent
  → Falls back to regular streaming if fork fails
  → File: autoCompact.ts

TIER 4: Session Memory Compact (experimental)
  → Trigger: Same as auto-compact, but with session memory as grounding
  → Uses persisted memory files for higher-quality summaries
  → Gated by tengu_session_memory AND tengu_sm_compact
  → File: sessionMemoryCompact.ts
```

### Time-Based Microcompact: Cold Cache Detection (`microCompact.ts:253-293`)

```typescript
// Time-based trigger runs FIRST and short-circuits. If the gap since the
// last assistant message exceeds the threshold, the server cache has expired
// and the full prefix will be rewritten regardless — so content-clear old
// tool results now, before the request, to shrink what gets rewritten.
// Cached MC is skipped when this fires: editing assumes a warm cache.
const timeBasedResult = maybeTimeBasedMicrocompact(messages, querySource)
if (timeBasedResult) return timeBasedResult

// Only run cached MC for the main thread to prevent forked agents
// from registering their tool_results in the global cachedMCState
if (isCachedMicrocompactEnabled() && isModelSupportedForCacheEditing(model) &&
    isMainThreadSource(querySource)) {
  return await cachedMicrocompactPath(messages, querySource)
}
```

**Design rationale**: Two-path architecture: (1) time-based for cold caches (mutates content directly), (2) cached MC for warm caches (uses cache_edits API). The time-based path also resets cached-MC state to prevent stale tool ID references on the next turn.

### Keep-At-Least-One Invariant (`microCompact.ts:458-463`)

```typescript
// Floor at 1: slice(-0) returns the full array (paradoxically keeps
// everything), and clearing ALL results leaves the model with zero working
// context. Neither degenerate is sensible — always keep at least the last.
const keepRecent = Math.max(1, config.keepRecent)
const keepSet = new Set(compactableIds.slice(-keepRecent))
const clearSet = new Set(compactableIds.filter(id => !keepSet.has(id)))
```

**Design rationale**: Guards against two degenerate cases: JavaScript's `array.slice(-0)` returns the full array (not empty), and clearing ALL tool results leaves the model with zero working context.

### Partial Compaction: Direction-Aware Cache Behavior (`compact.ts:772-1106`)

```typescript
export async function partialCompactConversation(
  allMessages, pivotIndex, context, cacheSafeParams, userFeedback, direction = 'from'
) {
  const messagesToSummarize = direction === 'up_to'
    ? allMessages.slice(0, pivotIndex)
    : allMessages.slice(pivotIndex)

  // 'up_to' must strip old compact boundaries/summaries
  // 'from' keeps them
  const messagesToKeep = direction === 'up_to'
    ? allMessages.slice(pivotIndex).filter(m =>
        m.type !== 'progress' && !isCompactBoundaryMessage(m) &&
        !(m.type === 'user' && m.isCompactSummary))
    : allMessages.slice(0, pivotIndex).filter(m => m.type !== 'progress')

  // 'from': prefix-preserving → boundary; 'up_to': suffix → last summary
  const anchorUuid = direction === 'up_to'
    ? (summaryMessages.at(-1)?.uuid ?? boundaryMarker.uuid)
    : boundaryMarker.uuid
}
```

**Design rationale**: Two directions have fundamentally different cache behavior. `'from'` (summarize after pivot) preserves the cache prefix. `'up_to'` (summarize before pivot) invalidates the cache since the summary precedes kept messages. Direction-aware boundary annotation with `preservedSegment` metadata (headUuid, anchorUuid, tailUuid) for disk relinking.

### Compaction Uses Forked Agent for Cache Sharing (`compact.ts:1178-1248`)

```typescript
if (promptCacheSharingEnabled) {
  try {
    // DO NOT set maxOutputTokens here. The fork piggybacks on the main thread's
    // prompt cache by sending identical cache-key params (system, tools, model,
    // messages prefix, thinking config). Setting maxOutputTokens would clamp
    // budget_tokens via Math.min(budget, maxOutputTokens-1), creating a thinking
    // config mismatch that invalidates the cache.
    const result = await runForkedAgent({
      promptMessages: [summaryRequest],
      cacheSafeParams,
      canUseTool: createCompactCanUseTool(),  // Denies all tool use
      querySource: 'compact',
      forkLabel: 'compact',
      maxTurns: 1,
      skipCacheWrite: true,
      overrides: { abortController: context.abortController },
    })
  } catch (error) {
    // Falls back to regular streaming path
  }
}
```

**Design rationale**: The forked agent reuses the main conversation's cached prefix (system prompt, tools, context messages), saving ~0.76% of fleet cache_creation (~38B tok/day). Falls back to regular streaming on failure.

### Session Memory Compaction: Tool Pair Preservation (`sessionMemoryCompact.ts:232-314`)

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
  // Find the assistant message(s) with matching tool_use blocks
  for (let i = adjustedIndex - 1; i >= 0 && neededToolUseIds.size > 0; i--) {
    if (hasToolUseWithIds(message, neededToolUseIds)) {
      adjustedIndex = i
      neededToolUseIds.delete(block.id)
    }
  }

  // Step 2: Handle thinking blocks that share message.id with kept assistant messages
  const messageIdsInKeptRange = new Set()
  for (let i = adjustedIndex; i < messages.length; i++) {
    if (msg.type === 'assistant' && msg.message.id) {
      messageIdsInKeptRange.add(msg.message.id)
    }
  }
  for (let i = adjustedIndex - 1; i >= 0; i--) {
    if (messageIdsInKeptRange.has(message.message.id)) {
      adjustedIndex = i  // Include thinking blocks
    }
  }
  return adjustedIndex
}
```

**Design rationale**: Two-step index adjustment prevents splitting tool_use/tool_result pairs (causing API errors) and thinking blocks from their sibling tool_use blocks. Handles the streaming-yield pattern where separate messages per content block share a message.id.

### Session Memory Compaction: Boundary Floor Invariant (`sessionMemoryCompact.ts:364-371`)

```typescript
// Floor at the last boundary: the preserved-segment chain has a disk
// discontinuity there (att[0]→summary shortcut from dedup-skip), which
// would let the loader's tail→head walk bypass inner preserved messages
// and then prune them.
const idx = messages.findLastIndex(m => isCompactBoundaryMessage(m))
const floor = idx === -1 ? 0 : idx + 1
for (let i = startIndex - 1; i >= floor; i--) {
  // expand backwards until minimums met
}
```

**Design rationale**: Uses the last compact boundary as a hard floor for backward expansion, matching the same invariant used by reactive compact's `getMessagesAfterCompactBoundary`. Prevents cross-boundary message chain corruption.

### Autocompact Circuit Breaker (`autoCompact.ts:257-265`)

```typescript
// Circuit breaker: stop retrying after N consecutive failures.
// BQ 2026-03-10 found 1,279 sessions had 50+ consecutive failures (up to 3,272)
// in a single session, wasting ~250K API calls/day globally.
if (tracking?.consecutiveFailures !== undefined &&
    tracking.consecutiveFailures >= MAX_CONSECUTIVE_AUTOCOMPACT_FAILURES) {
  return { wasCompacted: false }
}
```

**Design rationale**: Circuit breaker at 3 consecutive failures (not 50+). Tracks failures through the auto-compact tracking state. Logs a warning when the breaker trips. Resets on success. Prevents the ~250K wasted API calls/day seen in production.

### Autocompact: Subagent Recursion Guards (`autoCompact.ts:160-223`)

```typescript
export async function shouldAutoCompact(messages, model, querySource, snipTokensFreed = 0) {
  // Recursion guards. session_memory and compact are forked agents that would deadlock.
  if (querySource === 'session_memory' || querySource === 'compact') return false

  // marble_origami is the ctx-agent — if ITS context blows up and autocompact fires,
  // runPostCompactCleanup calls resetContextCollapse() which destroys the MAIN thread's
  // committed log (module-level state shared across forks).
  if (querySource === 'marble_origami') return false

  // Reactive-only mode: suppress proactive autocompact
  if (getFeatureValue_CACHED_MAY_BE_STALE('tengu_cobalt_raccoon', false)) return false

  // Context-collapse mode: collapse IS the context management system when it's on.
  // Autocompact firing at effective-13k (~93% of effective) sits right between
  // collapse's commit-start (90%) and blocking (95%), so it would race collapse
  // and usually win, nuking granular context that collapse was about to save.
  if (isContextCollapseEnabled()) return false

  // ... token counting and threshold check
}
```

**Design rationale**: Four-layer suppression: recursion guard (session_memory, compact), cross-agent state protection (marble_origami), feature flag (reactive-only mode), and system-level exclusion (context-collapse). Each guard protects a different failure mode.

### PTL Retry: Truncate Head for Compaction Retry (`compact.ts:230-291`)

```typescript
export function truncateHeadForPTLRetry(messages, ptlResponse): Message[] | null {
  // Strip our own synthetic marker from a previous retry before grouping.
  const input = messages[0]?.type === 'user' &&
    messages[0].isMeta &&
    messages[0].message.content === PTL_RETRY_MARKER
    ? messages.slice(1) : messages

  const groups = groupMessagesByApiRound(input)
  if (groups.length < 2) return null

  const tokenGap = getPromptTooLongTokenGap(ptlResponse)
  let dropCount
  if (tokenGap !== undefined) {
    // Precise: drop groups until accumulated tokens cover the gap
    let acc = 0
    dropCount = 0
    for (const g of groups) {
      acc += roughTokenCountEstimationForMessages(g)
      dropCount++
      if (acc >= tokenGap) break
    }
  } else {
    // Fallback: drop 20% of groups (some Vertex/Bedrock error formats)
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

**Design rationale**: Three-layer defense: (1) precise token-gap-based dropping when parseable, (2) 20% fallback for unparseable errors, (3) synthetic user marker to maintain API invariants (first message must be user). Strips its own marker on retry to prevent infinite stall.

### Post-Compaction Message Ordering (`compact.ts:325-338`)

```typescript
export function buildPostCompactMessages(result: CompactionResult): Message[] {
  return [
    result.boundaryMarker,       // First: marks where compaction happened
    ...result.summaryMessages,   // Second: the summary of old messages
    ...(result.messagesToKeep ?? []),  // Third: recent messages preserved
    ...result.attachments,       // Fourth: restored context
    ...result.hookResults,       // Fifth: hook results
  ]
}
```

**Design rationale**: Five-layer ordering ensures: (1) boundary marker is first for UI and parsing, (2) summary messages follow the boundary, (3) kept messages come after summary (preserving their relative order), (4) attachments restore context, (5) hook results are last. Consistent across all compaction paths.

### Post-Compaction Delta Re-Announcement (`compact.ts:567-585`)

```typescript
// Compaction ate prior delta attachments. Re-announce from the current
// state so the model has tool/instruction context on the first post-compact turn.
for (const att of getDeferredToolsDeltaAttachment(context.options.tools,
    context.options.mainLoopModel, [], { callSite: 'compact_full' })) {
  postCompactFileAttachments.push(createAttachmentMessage(att))
}
for (const att of getAgentListingDeltaAttachment(context, [])) {
  postCompactFileAttachments.push(createAttachmentMessage(att))
}
for (const att of getMcpInstructionsDeltaAttachment(
    context.options.mcpClients, context.options.tools,
    context.options.mainLoopModel, [],
)) {
  postCompactFileAttachments.push(createAttachmentMessage(att))
}
```

**Design rationale**: Uses delta attachments with empty history (`[]`) for full compact, and with `messagesToKeep` for partial compact. The delta mechanism diffs against the kept messages, so only new/changed tools are re-announced. Three categories: deferred tools, agent listings, MCP instructions.

### Pre-Compact Discovered Tools Preservation (`compact.ts:606-611`)

```typescript
// Carry loaded-tool state — the summary doesn't preserve tool_reference
// blocks, so the post-compact schema filter needs this to keep sending
// already-loaded deferred tool schemas to the API.
const preCompactDiscovered = extractDiscoveredToolNames(messages)
if (preCompactDiscovered.size > 0) {
  boundaryMarker.compactMetadata.preCompactDiscoveredTools = [...preCompactDiscovered].sort()
}
```

**Design rationale**: Extracts discovered tool names from the pre-compact messages and stores them in the boundary marker's `compactMetadata`. Sorted for deterministic ordering. Used by the post-compact schema filter to restore the correct tool set.

### Post-Compact File Restoration Budget (`compact.ts:122-130`)

```typescript
export const POST_COMPACT_MAX_FILES_TO_RESTORE = 5
export const POST_COMPACT_TOKEN_BUDGET = 50_000
export const POST_COMPACT_MAX_TOKENS_PER_FILE = 5_000
export const POST_COMPACT_MAX_TOKENS_PER_SKILL = 5_000
export const POST_COMPACT_SKILLS_TOKEN_BUDGET = 25_000
```

**Design rationale**: Multi-level budget: per-file cap (5K), total file budget (50K), max files (5), per-skill cap (5K), total skill budget (25K). Per-skill truncation (not dropping) preserves critical instructions at the top of skill files. Budget sized to hold ~5 skills at the per-skill cap.

### Image Stripping Before Compaction (`compact.ts:133-200`)

```typescript
export function stripImagesFromMessages(messages: Message[]): Message[] {
  return messages.map(message => {
    if (message.type !== 'user') return message
    const content = message.message.content
    if (!Array.isArray(content)) return message
    // Replace image blocks with [image] text markers
    // Also strip images/documents nested inside tool_result content arrays
  })
}
```

**Design rationale**: Images are ~2000 tokens each and are not needed for generating a conversation summary. Replaces images with `[image]` text markers so the summary still notes that an image was shared (preserving context about what was discussed).

### Session Metadata Re-Append After Compaction (`compact.ts:706-711`)

```typescript
// Re-append session metadata (custom title, tag) so it stays within
// the 16KB tail window that readLiteMetadata reads for --resume display.
// Without this, enough post-compaction messages push the metadata entry
// out of the window, causing --resume to show the auto-generated title
// instead of the user-set session name.
reAppendSessionMetadata()
```

**Design rationale**: Session metadata (custom title, tag) is stored as a message in the transcript. After compaction, enough new messages are added that the metadata entry gets pushed out of the 16KB tail window that `readLiteMetadata` reads for `--resume` display.

### Compact Boundary Message with Relink Metadata (`compact.ts:340-367`)

```typescript
export function annotateBoundaryWithPreservedSegment(
  boundary: SystemCompactBoundaryMessage,
  anchorUuid: UUID,
  messagesToKeep: readonly Message[] | undefined,
): SystemCompactBoundaryMessage {
  const keep = messagesToKeep ?? []
  if (keep.length === 0) return boundary
  return {
    ...boundary,
    compactMetadata: {
      ...boundary.compactMetadata,
      preservedSegment: {
        headUuid: keep[0]!.uuid,
        anchorUuid,
        tailUuid: keep.at(-1)!.uuid,
      },
    },
  }
}
```

**Design rationale**: Stores a `preservedSegment` with `headUuid`, `anchorUuid`, and `tailUuid` in the boundary marker's metadata. The loader uses this to patch head→anchor and anchor's-other-children→tail on resume. Different anchor computation for 'from' vs 'up_to' partial compact directions.

---

## 2.3 Context Caching

### Two-Phase Cache Break Detection with 12-Dimensional Change Tracking (`promptCacheBreakDetection.ts:1-727`)

```typescript
type PreviousState = {
  systemHash: number
  toolsHash: number
  cacheControlHash: number     // Hash WITH cache_control intact
  toolNames: string[]
  perToolHashes: Record<string, number>  // Per-tool schema hash
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

### Phase 1: Pre-Call State Recording
Records all 12+ dimensions of the API request state before sending.

### Phase 2: Post-Call Cache Read Comparison
After the API response, compares actual cache read tokens against the previous baseline to confirm if a break occurred.

### Edge Cases Covered

| Dimension | What It Catches |
|-----------|----------------|
| `systemHash` | System prompt changed (with character delta tracking) |
| `toolsHash` | Tool schemas changed (aggregate) |
| `cacheControlHash` | Invisible scope/TTL flips (global↔org, 1h↔5m) |
| `perToolHashes` | Individual tool schema changes (77% of tool breaks) |
| `model` | Cross-model cache invalidation |
| `betas` | Beta header changes |
| `autoModeActive` | AFK_MODE_BETA_HEADER presence toggled |
| `isUsingOverage` | Overage state changed (TTL latched, no flip) |
| `cachedMCEnabled` | Cache-editing beta header toggled |
| `effortValue` | Resolved effort goes into output_config |
| `extraBodyHash` | CLAUDE_CODE_EXTRA_BODY changes |
| `fastMode` | Fast mode toggled |
| `globalCacheStrategy` | tool_based vs system_prompt |

### Cache Deletion Notification (`promptCacheBreakDetection.ts:673-682`)

```typescript
export function notifyCacheDeletion(querySource: QuerySource, agentId?: AgentId): void {
  const key = getTrackingKey(querySource, agentId)
  const state = key ? previousStateBySource.get(key) : undefined
  if (state) {
    state.cacheDeletionsPending = true
  }
}
```

**Design rationale**: When cached microcompact sends `cache_edits` deletions, the next API response will legitimately have lower cache read tokens. Without this flag, the break detector would false-positive. The `cacheDeletionsPending` flag resets the baseline when deletions are pending.

### Compaction Notification Resets Cache Baseline (`promptCacheBreakDetection.ts:689-698`)

```typescript
export function notifyCompaction(querySource: QuerySource, agentId?: AgentId): void {
  const key = getTrackingKey(querySource, agentId)
  const state = key ? previousStateBySource.get(key) : undefined
  if (state) {
    state.prevCacheReadTokens = null  // Reset baseline
  }
}
```

**Design rationale**: Called from every compaction path (auto-compact, manual compact, session memory compact, reactive compact) to prevent false-positive cache break detection after context reduction.

### Tracking Key Normalization (`promptCacheBreakDetection.ts:149-158`)

```typescript
function getTrackingKey(querySource: QuerySource, agentId?: AgentId): string | null {
  if (querySource === 'compact') return 'repl_main_thread'  // Compact shares cache with main thread
  for (const prefix of TRACKED_SOURCE_PREFIXES) {
    if (querySource.startsWith(prefix)) return agentId || querySource
  }
  return null  // Untracked: speculation, session_memory, prompt_suggestion
}
```

**Design rationale**: Short-lived forked agents (speculation, session_memory, prompt_suggestion) return `null` — no tracking needed since they run 1-3 turns with a fresh agentId each time. Subagents with tracked prefixes use their unique `agentId` to isolate state, preventing false positives when multiple instances of the same agent type run concurrently.

### Per-Tool Schema Hashing (`promptCacheBreakDetection.ts:187-196`)

```typescript
function computePerToolHashes(strippedTools, names): Record<string, number> {
  const hashes: Record<string, number> = {}
  for (let i = 0; i < strippedTools.length; i++) {
    hashes[names[i] ?? `__idx_${i}`] = computeHash(strippedTools[i])
  }
  return hashes
}
```

**Design rationale**: Only computes per-tool hashes when the aggregate changed (lazy evaluation). Identifies exactly which tool's description changed when `added=removed=0`. AgentTool/SkillTool embed dynamic agent/command lists that change without adding/removing tools. Sanitizes MCP tool names to prevent filepath leakage.

---

## 2.4 Context Deduplication

### LSP Diagnostic Cross-Turn Deduplication (`LSPDiagnosticRegistry.ts:45-335`)

```typescript
const MAX_FILES_FOR_DEDUP = 1000
const deliveredDiagnostics = new LRU<string, Diagnostic[]>(MAX_FILES_FOR_DEDUP)

function deduplicateDiagnosticFiles(files, deliveredDiagnostics): DiagnosticFile[] {
  const dedupedFiles: DiagnosticFile[] = []
  for (const file of files) {
    const previouslyDelivered = deliveredDiagnostics.get(file.uri) ?? []
    for (const diag of file.diagnostics) {
      const isDuplicate = previouslyDelivered.some(prev =>
        prev.message === diag.message && prev.range === diag.range &&
        prev.severity === diag.severity && prev.source === diag.source
      )
      if (!isDuplicate) dedupedFile.diagnostics.push(diag)
    }
  }
  return dedupedFiles.filter(f => f.diagnostics.length > 0)
}
```

**Design rationale**: Two-level deduplication: within-batch (same delivery) and cross-turn (across multiple API calls). Uses LRU cache capped at 1000 files to prevent unbounded memory growth. Falls back to undeduplicated files if deduplication fails (better to show duplicates than lose diagnostics).

### Cache Edits Deduplication (`claude.ts:3110-3151`)

```typescript
// Helper to deduplicate a cache_edits block against already-seen deletions
const deduplicateEdits = (block: CachedMCEditsBlock): CachedMCEditsBlock => { ... }

// For each pinned edit, deduplicate and insert
for (const pinned of pinnedEdits) {
  const dedupedBlock = deduplicateEdits(pinned.block)
  if (dedupedBlock.edits.length > 0) {
    insertBlockAfterToolResults(msg.content, dedupedBlock)
  }
}

// Deduplicate new edits too
const dedupedNewEdits = deduplicateEdits(newCacheEdits)
if (dedupedNewEdits.edits.length > 0) {
  insertBlockAfterToolResults(msg.content, dedupedNewEdits)
}
```

**Design rationale**: Deduplicates both pinned edits (from previous turns) and new edits (from current turn) against already-seen deletions. Only inserts blocks with non-empty edits after deduplication. Prevents API errors from duplicate cache_edits.

### Session-Level Dedup for Nested Memory CLAUDE.md Attachments (`REPL.tsx:2602`)

**Design rationale**: Session-scoped deduplication (not turn-scoped) ensures nested memory attachments are only included once per session, even if the conditions for inclusion are met multiple times.

---

## 2.5 Context Persistence Across Sessions

### Replacement State Reconstruction for Resumed Sessions (`REPL.tsx:2539-2541`)

```typescript
// Reconstruct replacement state for the resumed session. Runs after
// the transcript is loaded and the session's tool-results dir is scanned.
// Content-replacement records from a resumed session's transcript — used to
// reconstruct the replacement state for file editing tools.
```

**Design rationale**: File editing tools use content-replacement records (original content → replacement) for validation. When resuming a session, these records must be reconstructed from the transcript since they're not persisted separately.

### Transcript Segment Writing for Pre-Compaction Messages (`compact.ts:714-717`)

```typescript
// Write a reduced transcript segment for the pre-compaction messages
// (assistant mode only). Fire-and-forget — errors are logged internally.
void sessionTranscriptModule?.writeSessionTranscriptSegment(messages)
```

**Design rationale**: Fire-and-forget pattern — errors don't block the compaction flow. Only runs in assistant mode. Writes a "reduced" segment (not full messages) to minimize storage.

### Agent Definition State Sync Across /resume (`REPL.tsx:967`)

```typescript
// Agent definition is state so /resume can update it mid-session
```

**Design rationale**: Agent definitions are stored as React state so they can be updated mid-session during resume, allowing the resumed session's agent configuration to take effect.

---

## 2.6 Token Counting and Estimation

### Final Context Tokens from Iterations for Task Budget (`tokens.ts:68-112`)

```typescript
export function finalContextTokensFromLastResponse(messages): number {
  // Used for task_budget.remaining computation across compaction boundaries —
  // the server's budget countdown is context-based, so remaining decrements by
  // the pre-compact final window, not billing spend.
  const iterations = (usage as { iterations?: Array<{input_tokens, output_tokens}> }).iterations
  if (iterations && iterations.length > 0) {
    const last = iterations.at(-1)!
    return last.input_tokens + last.output_tokens
  }
  // No iterations → no server tool loop → top-level usage IS the final window.
  return usage.input_tokens + usage.output_tokens
}
```

**Design rationale**: Uses `usage.iterations[-1]` when available (server-side tool loops), falls back to top-level usage. Both paths exclude cache tokens to match the server's `calculate_context_tokens` formula (renderer.py:292).

### Snip Token Adjustment in Autocompact (`autoCompact.ts:164-168`)

```typescript
// Snip removes messages but the surviving assistant's usage still reflects
// pre-snip context, so tokenCountWithEstimation can't see the savings.
// Subtract the rough-delta that snip already computed.
snipTokensFreed = 0,
```

**Design rationale**: The snip operation removes messages from context, but the surviving assistant message's `usage` field still reflects the pre-snip context size. Accepts a `snipTokensFreed` parameter that is subtracted from the token count.

---

# 3. Agentic Orchestration Architecture

## 3.1 Agent Spawning

### Complete Agent Spawning Algorithm (`AgentTool.tsx:239`)

```
PSEUDOCODE: AgentTool.call()
────────────────────────────
INPUT: { description, prompt, subagent_type, model, run_in_background,
         name, team_name, mode: spawnMode, isolation, cwd }

1. PERMISSION CHECK
   if team_name is set AND !isAgentSwarmsEnabled():
     throw "Agent Teams is not yet available on your plan."

2. TEAMMATE NESTING GUARD
   if isTeammate() AND team_name AND name:
     throw "Teammates cannot spawn other teammates"

3. IN-PROCESS TEAMMATE GUARDS
   if isInProcessTeammate() AND team_name AND run_in_background:
     throw "In-process teammates cannot spawn background agents"

4. MULTI-AGENT SPAWN PATH (teammate spawning)
   if team_name AND name:
     → spawnTeammate({ name, prompt, team_name, ... })
     → returns { status: 'teammate_spawned', ... }
     → DONE

5. AGENT TYPE RESOLUTION
   effectiveType = subagent_type ?? (isForkSubagentEnabled() ? undefined : 'general-purpose')
   isForkPath = (effectiveType === undefined)

   if isForkPath:
     if isInForkChild(messages) OR querySource === 'agent:builtin:fork':
       throw "Fork is not available inside a forked worker"
     selectedAgent = FORK_AGENT
   else:
     selectedAgent = find agent by effectiveType from activeAgents
     if not found: throw "Agent type not found"

6. MCP REQUIREMENT CHECK
   if selectedAgent.requiredMcpServers:
     wait up to 30s for pending MCP servers
     if any required server missing: throw error

7. ISOLATION MODE RESOLUTION
   effectiveIsolation = isolation ?? selectedAgent.isolation

8. REMOTE ISOLATION PATH (ant-only, dead-code eliminated for external)
   if effectiveIsolation === 'remote':
     checkRemoteAgentEligibility()
     session = teleportToRemote({ initialMessage: prompt, ... })
     registerRemoteAgentTask({ session, ... })
     return { status: 'remote_launched', sessionUrl, ... }

9. SYSTEM PROMPT CONSTRUCTION
   if isForkPath:
     forkParentSystemPrompt = toolUseContext.renderedSystemPrompt
     promptMessages = buildForkedMessages(prompt, assistantMessage)
   else:
     enhancedSystemPrompt = selectedAgent.getSystemPrompt() + env details
     promptMessages = [createUserMessage(prompt)]

10. WORKTREE SETUP
    if effectiveIsolation === 'worktree':
      worktreeInfo = createAgentWorktree(slug)

11. SYNC vs ASYNC DECISION
    forceAsync = isForkSubagentEnabled()
    assistantForceAsync = appState.kairosEnabled
    shouldRunAsync = (run_in_background || selectedAgent.background ||
                      isCoordinator || forceAsync || assistantForceAsync ||
                      isProactiveActive) && !isBackgroundTasksDisabled

12. TOOL POOL ASSEMBLY
    workerPermissionContext = { mode: selectedAgent.permissionMode ?? 'acceptEdits' }
    workerTools = assembleToolPool(workerPermissionContext, mcpTools)

13. EXECUTION
    if shouldRunAsync:
      → registerAsyncAgent() → creates LocalAgentTaskState
      → register name→agentId mapping if name provided
      → runAsyncAgentLifecycle (fire-and-forget)
      → return { status: 'async_launched', agentId, outputFile }
    else:
      → registerAgentForeground() → creates foreground task
      → iterate runAgent() messages synchronously
      → race against background signal (auto-background or user background)
      → if backgrounded: transition to async path mid-flight
      → return { status: 'completed', content }
```

### Source Files
| File | Lines | Purpose |
|------|-------|---------|
| `src/src/tools/AgentTool/AgentTool.tsx` | 1-1000+ | Central spawn point |
| `src/src/tools/AgentTool/builtInAgents.ts` | 1-100 | Built-in agent definitions |
| `src/src/tools/AgentTool/forkSubagent.ts` | 1-200 | Fork subagent experiment |
| `src/src/tools/AgentTool/runAgent.ts` | 1-1000+ | Agent lifecycle execution |
| `src/src/tools/shared/spawnMultiAgent.ts` | 1-1093 | Multi-agent spawn backends |
| `src/src/tasks/LocalAgentTask/LocalAgentTask.tsx` | 1-683 | Background agent task management |

---

## 3.2 Sync vs Async Agent Determination

### Decision Logic (`AgentTool.tsx:557-567`)

```typescript
const forceAsync = isForkSubagentEnabled();
const assistantForceAsync = feature('KAIROS') ? appState.kairosEnabled : false;
const shouldRunAsync =
  (run_in_background === true ||          // explicit request
   selectedAgent.background === true ||    // agent definition forces it
   isCoordinator ||                        // coordinator mode always async
   forceAsync ||                           // fork experiment
   assistantForceAsync ||                  // assistant/KAIROS mode
   (proactiveModule?.isProactiveActive() ?? false)) // proactive mode
  && !isBackgroundTasksDisabled;           // global killswitch
```

### Sync vs Async Rules

| Condition | Result |
|-----------|--------|
| `run_in_background: true` | Always async |
| Agent has `background: true` in definition | Always async (e.g., Verification Agent) |
| Coordinator mode (`CLAUDE_CODE_COORDINATOR_MODE=1`) | Always async |
| Fork subagent enabled | Always async |
| KAIROS/Assistant mode enabled | Always async |
| Proactive mode active | Always async |
| `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1` | Forces sync (overrides all above) |
| In-process teammate + `run_in_background` | **Error** — not allowed |

### Async Agent Lifecycle (`runAsyncAgentLifecycle`, `agentToolUtils.ts:508`)

```
PSEUDOCODE: runAsyncAgentLifecycle()
─────────────────────────────────────
1. Create progress tracker + activity resolver
2. If summarization enabled: startAgentSummarization() for periodic summaries
3. For each message from makeStream (runAgent generator):
   a. Push to agentMessages array
   b. If UI retains task: append to task.messages for live view
   c. Update progress (toolUseCount, tokenCount, recentActivities)
   d. Emit SDK progress events with last tool name
4. On completion:
   a. Stop summarization
   b. finalizeAgentTool() → extract result
   c. completeAsyncAgent() → mark task completed FIRST (unblocks TaskOutput)
   d. classifyHandoffIfNeeded() → detect if agent handed off to wrong agent
   e. cleanupWorktreeIfNeeded() → remove worktree if no changes
   f. enqueueAgentNotification() → <task-notification> XML to model
5. On abort (AbortError):
   a. killAsyncAgent() → abort controller + cleanup
   b. extractPartialResult() → preserve what was accomplished
   c. enqueueAgentNotification(status: 'killed')
6. On error:
   a. failAsyncAgent() → mark task failed
   b. enqueueAgentNotification(status: 'failed', error)
```

---

## 3.3 Foreground-to-Background Transition

### Mechanism (`AgentTool.tsx:808-999`)

```
PSEUDOCODE: Foreground → Background Transition
─────────────────────────────────────────────────
1. registerAgentForeground() creates:
   - LocalAgentTaskState with isBackgrounded: false
   - backgroundSignal Promise (resolved when backgrounded)
   - Optional auto-background timer (getAutoBackgroundMs() = 120s if enabled)

2. Main loop races:
   raceResult = Promise.race([
     agentIterator.next(),          // next message from agent
     backgroundPromise              // user pressed "background" or timer fired
   ])

3. If background signal fires:
   a. wasBackgrounded = true
   b. Stop foreground summarization
   c. agentIterator.return(undefined) — clean up sync iterator
      (timeout: 1s to prevent blocking on MCP cleanup)
   d. Create NEW progress tracker from accumulated messages
   e. Start NEW runAgent() with isAsync: true
   f. For each new message:
      - Update progress
      - Emit task progress events
   g. On completion:
      - completeAsyncAgent()
      - classifyHandoffIfNeeded()
      - cleanupWorktreeIfNeeded()
      - enqueueAgentNotification()
```

### Auto-Background Timeout (`AgentTool.tsx:72-77`)

```typescript
function getAutoBackgroundMs(): number {
  if (isEnvTruthy(process.env.CLAUDE_AUTO_BACKGROUND_TASKS) ||
      getFeatureValue_CACHED_MAY_BE_STALE('tengu_auto_background_agents', false)) {
    return 120_000; // 2 minutes
  }
  return 0; // disabled
}
```

### Key Files
| File | Lines | Purpose |
|------|-------|---------|
| `src/src/tasks/LocalAgentTask/LocalAgentTask.tsx:526` | — | `registerAgentForeground()` |
| `src/src/tasks/LocalAgentTask/LocalAgentTask.tsx:620` | — | `backgroundAgentTask()` |
| `src/src/tasks/LocalAgentTask/LocalAgentTask.tsx:657` | — | `unregisterAgentForeground()` |

---

## 3.4 Agent Tool Pool Assembly

### Worker Tool Pool (`AgentTool.tsx:572-577`)

```typescript
const workerPermissionContext = {
  ...appState.toolPermissionContext,
  mode: selectedAgent.permissionMode ?? 'acceptEdits'
};
const workerTools = assembleToolPool(workerPermissionContext, appState.mcp.tools);
```

### Tool Pool Resolution (`runAgent.ts:500-502`)

```typescript
const resolvedTools = useExactTools
  ? availableTools  // fork path: use parent's exact tools
  : resolveAgentTools(agentDefinition, availableTools, isAsync).resolvedTools;
```

### Tool Restriction Constants (`tools.ts`)

**ALL_AGENT_DISALLOWED_TOOLS** (`tools.ts:35-46`):
```
TaskOutputTool, ExitPlanModeTool(v2), EnterPlanModeTool,
AgentTool (for non-ant users — prevents recursion),
AskUserQuestionTool, TaskStopTool,
WorkflowTool (if WORKFLOW_SCRIPTS feature enabled)
```

**ASYNC_AGENT_ALLOWED_TOOLS** (`tools.ts:55-71`):
```
FileRead, WebSearch, TodoWrite, Grep, WebFetch, Glob,
All shell tools (Bash), FileEdit, FileWrite, NotebookEdit,
SkillTool, SyntheticOutputTool, ToolSearch,
EnterWorktree, ExitWorktree
```

**IN_PROCESS_TEAMMATE_ALLOWED_TOOLS** (`tools.ts:77-88`):
```
TaskCreate, TaskGet, TaskList, TaskUpdate,
SendMessage,
CronCreate, CronDelete, CronList (if AGENT_TRIGGERS feature enabled)
```

**COORDINATOR_MODE_ALLOWED_TOOLS** (`tools.ts:107-112`):
```
AgentTool, TaskStopTool, SendMessageTool, SyntheticOutputTool
```

### Fork Path: Uses `useExactTools: true`
Fork children receive the **parent's exact tool pool** (not filtered through `resolveAgentTools`) for cache-identical API request prefixes. This is critical for prompt cache sharing between fork siblings.

---

## 3.5 Agent Permission Modes

| Mode | Behavior |
|------|----------|
| `bypassPermissions` | No prompts, all tools auto-approved |
| `acceptEdits` | Prompts for write/edit operations |
| `auto` | Classifier auto-approves safe operations |
| `dontAsk` | Auto-approve without prompts |
| `plan` | Plan mode — requires plan approval |
| `bubble` | Prompts bubble up to parent terminal |

### Permission Mode Inheritance (`spawnMultiAgent.ts:208-260`)

```typescript
function buildInheritedCliFlags(options) {
  if (planModeRequired) {
    // Don't inherit bypass permissions
  } else if (permissionMode === 'bypassPermissions') {
    flags.push('--dangerously-skip-permissions')
  } else if (permissionMode === 'acceptEdits') {
    flags.push('--permission-mode acceptEdits')
  } else if (permissionMode === 'auto') {
    flags.push('--permission-mode auto')
  }
  // Also inherit: --model, --settings, --plugin-dir, --chrome/--no-chrome
}
```

### Permission Mode Override in Agent Definition (`runAgent.ts:415-451`)

```typescript
// Override permission mode if agent defines one
// BUT don't override if parent is in bypassPermissions or acceptEdits mode
if (agentPermissionMode &&
    state.toolPermissionContext.mode !== 'bypassPermissions' &&
    state.toolPermissionContext.mode !== 'acceptEdits' &&
    !(feature('TRANSCRIPT_CLASSIFIER') && state.toolPermissionContext.mode === 'auto')) {
  toolPermissionContext = { ...toolPermissionContext, mode: agentPermissionMode }
}

// Async agents auto-set shouldAvoidPermissionPrompts
if (shouldAvoidPrompts) {
  toolPermissionContext = { ...toolPermissionContext, shouldAvoidPermissionPrompts: true }
}
```

---

## 3.6 Built-In Agents

### Complete Agent Registry

| Agent | Type | Model | Key Properties | File |
|-------|------|-------|----------------|------|
| **general-purpose** | `general-purpose` | default | `tools: ['*']`, all-purpose | `built-in/generalPurposeAgent.ts` |
| **Explore** | `Explore` | haiku/inherit | Read-only, `omitClaudeMd: true` | `built-in/exploreAgent.ts` |
| **Plan** | `Plan` | inherit | Read-only, software architect | `built-in/planAgent.ts` |
| **claude-code-guide** | `claude-code-guide` | haiku | Documentation Q&A, `permissionMode: 'dontAsk'` | `built-in/claudeCodeGuideAgent.ts` |
| **verification** | `verification` | inherit | Adversarial testing, `background: true` | `built-in/verificationAgent.ts` |
| **statusline-setup** | `statusline-setup` | sonnet | Configure status line | `built-in/statuslineSetup.ts` |
| **fork** (synthetic) | `fork` | inherit | `tools: ['*']`, `maxTurns: 200`, `permissionMode: 'bubble'` | `forkSubagent.ts:60` |

### Agent Gating

| Agent | Gate | File |
|-------|------|------|
| Explore/Plan | `feature('BUILTIN_EXPLORE_PLAN_AGENTS')` AND `tengu_amber_stoat` | `builtInAgents.ts:14-20` |
| Verification | `feature('VERIFICATION_AGENT')` AND `tengu_hive_evidence` | `builtInAgents.ts:65-69` |
| Claude Code Guide | Only for non-SDK entrypoints | `builtInAgents.ts` |
| Coordinator agents | `feature('COORDINATOR_MODE')` AND `CLAUDE_CODE_COORDINATOR_MODE` env | `coordinatorMode.ts` |

---

## 3.7 Skill Preloading for Agents (`runAgent.ts:577-646`)

Agents can preload skills from their frontmatter definition:

```yaml
---
name: my-agent
description: My custom agent
skills:
  - commit
  - verify
---
```

### Skill Resolution Strategy (`resolveSkillName`, `runAgent.ts:945-973`)

1. **Exact match** via `hasCommand()` (checks name, userFacingName, aliases)
2. **Prefix with plugin name**: `"my-skill"` → `"pluginName:my-skill"`
3. **Suffix match**: Find any command ending with `":skillName"`

### Skill Loading Process

```
PSEUDOCODE: Skill Preloading
────────────────────────────
1. Get all skills: getSkillToolCommands(projectRoot)
2. For each skillName in agentDefinition.skills:
   a. Resolve skill name (exact → prefix → suffix)
   b. If not found: log warning, skip
   c. If found but not prompt-type: log warning, skip
   d. Get skill content: skill.getPromptForCommand('', toolUseContext)
   e. Add to initialMessages as meta user message
3. All skills loaded concurrently via Promise.all()
```

---

## 3.8 Agent-Specific MCP Servers (`runAgent.ts:95-218`)

Agents can define their own MCP servers in frontmatter, additive to the parent's MCP clients.

### Plugin-Only Policy (`runAgent.ts:117-127`)

```typescript
const agentIsAdminTrusted = isSourceAdminTrusted(agentDefinition.source)
if (isRestrictedToPluginOnly('mcp') && !agentIsAdminTrusted) {
  // Skip MCP servers for user-controlled agents only
  // Plugin, built-in, and policySettings agents are admin-trusted
}
```

---

## 3.9 Agent Hooks (Frontmatter) (`runAgent.ts:557-575`)

```typescript
const hooksAllowedForThisAgent =
  !isRestrictedToPluginOnly('hooks') ||
  isSourceAdminTrusted(agentDefinition.source)
if (agentDefinition.hooks && hooksAllowedForThisAgent) {
  registerFrontmatterHooks(
    rootSetAppState,
    agentId,
    agentDefinition.hooks,
    `agent '${agentDefinition.agentType}'`,
    true, // isAgent - converts Stop to SubagentStop
  )
}
```

---

## 3.10 Subagent Claude.md Omission (`runAgent.ts:388-398`)

```typescript
const shouldOmitClaudeMd =
  agentDefinition.omitClaudeMd &&
  !override?.userContext &&
  getFeatureValue_CACHED_MAY_BE_STALE('tengu_slim_subagent_claudemd', true)
```

**Design rationale**: Read-only agents (Explore, Plan) don't get CLAUDE.md context — saves ~5-15 Gtok/week across 34M+ spawns. Killswitch defaults true.

---

## 3.11 Subagent Git Status Omission (`runAgent.ts:402-410`)

```typescript
const { gitStatus: _omittedGitStatus, ...systemContextNoGit } = baseSystemContext
const resolvedSystemContext =
  agentDefinition.agentType === 'Explore' ||
  agentDefinition.agentType === 'Plan'
    ? systemContextNoGit
    : baseSystemContext
```

**Design rationale**: Explore/Plan agents don't get stale git status in system context — saves ~1-3 Gtok/week. They run `git status` themselves if needed.

---

## 3.12 Agent Thinking Config (`runAgent.ts:681-685`)

```typescript
thinkingConfig: useExactTools
  ? toolUseContext.options.thinkingConfig  // fork: inherit parent's thinking
  : { type: 'disabled' as const },          // regular: thinking disabled
```

**Design rationale**: Fork children inherit parent's thinking config for cache-identical prefixes. Regular sub-agents have thinking disabled to control output token costs.

---

## 3.13 Transcript Classifier for Handoffs (`AgentTool.tsx:961-974`)

```typescript
if (feature('TRANSCRIPT_CLASSIFIER')) {
  const handoffWarning = await classifyHandoffIfNeeded({
    agentMessages,
    tools: toolUseContext.options.tools,
    toolPermissionContext: backgroundedAppState.toolPermissionContext,
    abortSignal: task.abortController!.signal,
    subagentType: selectedAgent.agentType,
    totalToolUseCount: agentResult.totalToolUseCount
  })
  if (handoffWarning) {
    finalMessage = `${handoffWarning}\n\n${finalMessage}`
  }
}
```

**Design rationale**: When enabled, a transcript classifier analyzes agent messages for handoff warnings before sending notifications. Detects when an agent handed off work to the wrong agent type.

---

## 3.14 Agent Color Management (`AgentTool.tsx:286-289, 413-415`)

```typescript
const agentDef = subagent_type ? toolUseContext.options.agentDefinitions.activeAgents.find(a => a.agentType === subagent_type) : undefined;
if (agentDef?.color) {
  setAgentColor(subagent_type!, agentDef.color);
}
```

---

## 3.15 Agent Analytics Events

| Event | When Emitted |
|-------|-------------|
| `tengu_agent_tool_selected` | When an agent is selected |
| `tengu_agent_tool_remote_launched` | When a remote agent is launched |
| `tengu_agent_tool_terminated` | When an agent is terminated |
| `tengu_agent_memory_loaded` | When agent memory is loaded |
| `tengu_fork_agent_query` | When a forked agent query completes |
| `tengu_coordinator_mode_switched` | When coordinator mode is switched |

---

# 4. Agent Swarm Architecture

## 4.1 Swarm Enable/Disable

### Master Gate Function (`agentSwarmsEnabled.ts:24-44`)

```typescript
export function isAgentSwarmsEnabled(): boolean {
  // Ant: always on
  if (process.env.USER_TYPE === 'ant') {
    return true
  }

  // External: require opt-in via env var or --agent-teams flag
  if (
    !isEnvTruthy(process.env.CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS) &&
    !isAgentTeamsFlagSet()
  ) {
    return false
  }

  // Killswitch — always respected for external users
  if (!getFeatureValue_CACHED_MAY_BE_STALE('tengu_amber_flint', true)) {
    return false
  }

  return true
}
```

### Gate Breakdown

| User Type | Requirements |
|-----------|-------------|
| **Ant** (`USER_TYPE === 'ant'`) | Always enabled — no additional checks |
| **External** | BOTH: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` OR `--agent-teams` flag, AND `tengu_amber_flint` GrowthBook gate |

**Design rationale**: This is the MASTER GATE. If ant, ALL swarm features are available with zero additional checks. External users must pass BOTH opt-in AND killswitch. Every component in the system checks this function before enabling swarm-related functionality.

---

## 4.2 Swarm Spawn Modes

### Three Spawn Modes (`spawnMultiAgent.ts`)

#### Mode 1: In-Process (`handleSpawnInProcess`, lines 840-1032)

Runs teammates in the same Node.js process using `AsyncLocalStorage` for isolation.

```typescript
const teammateContextStorage = new AsyncLocalStorage<TeammateContext>()

export function getTeammateContext(): TeammateContext | undefined {
  return teammateContextStorage.getStore()
}

export function runWithTeammateContext<T>(context: TeammateContext, fn: () => T): T {
  return teammateContextStorage.run(context, fn)
}

export function isInProcessTeammate(): boolean {
  return teammateContextStorage.getStore() !== undefined
}
```

**TeammateContext type** (`teammateContext.ts:1-96`):
```typescript
export type TeammateContext = {
  agentId: string
  agentName: string
  teamName: string
  color?: string
  planModeRequired: boolean
  parentSessionId: string
  isInProcess: true
  abortController: AbortController
}
```

**Design rationale**: AsyncLocalStorage provides logical isolation but not security isolation — all in-process teammates share the same Node.js process, memory space, and filesystem access. BQ analysis showed ~20MB RSS per agent at 500+ turn sessions and ~125MB per concurrent agent in swarm bursts.

#### Mode 2: Split-Pane (`handleSpawnSplitPane`, lines 305-539)

Creates teammates in shared tmux/iTerm2 window with leader on left, teammates on right.

#### Mode 3: Separate Window (`handleSpawnSeparateWindow`, lines 545-753)

Creates each teammate in its own tmux window.

### Spawn Routing (`spawnMultiAgent.ts:1040-1078`)

```typescript
async function handleSpawn(input, context) {
  if (isInProcessEnabled()) {
    return handleSpawnInProcess(input, context)
  }
  // ... backend detection, then split-pane or separate window
}
```

---

## 4.3 Teammate Spawn Process (`spawnMultiAgent.ts:1088`)

```
PSEUDOCODE: spawnTeammate()
────────────────────────────
INPUT: { name, prompt, team_name, cwd, use_splitpane, plan_mode_required,
         model, agent_type, description }

1. MODEL RESOLUTION
   model = resolveTeammateModel(inputModel, leaderModel)
   // 'inherit' → leader's model; undefined → default Opus fallback

2. NAME UNIQUENESS
   uniqueName = generateUniqueTeammateName(baseName, teamName)
   sanitizedName = sanitizeAgentName(uniqueName)
   teammateId = formatAgentId(sanitizedName, teamName)

3. BACKEND DETECTION
   detectionResult = detectAndGetBackend()
   // Options: tmux, iTerm2 (it2), in-process

4. SPAWN PATH SELECTION
   if isInProcessEnabled():
     → handleSpawnInProcess() — runs in same Node.js process via AsyncLocalStorage
   else:
     → handleSpawnSplitPane() — tmux/iTerm2 split panes
     → OR handleSpawnSeparateWindow() — separate tmux windows

5. COMMAND CONSTRUCTION
   spawnCommand = "cd <cwd> && env <envVars> <binary> \
     --agent-id <teammateId> \
     --agent-name <sanitizedName> \
     --team-name <teamName> \
     --agent-color <color> \
     --parent-session-id <sessionId> \
     [--plan-mode-required] \
     [--agent-type <agent_type>] \
     <inheritedFlags>"

   inheritedFlags include:
   - --dangerously-skip-permissions (if parent has bypassPermissions)
   - --permission-mode acceptEdits/auto
   - --model <override> (if set)
   - --settings <path>
   - --plugin-dir <dirs>
   - --chrome/--no-chrome

6. EXECUTE SPAWN
   sendCommandToPane(paneId, spawnCommand)

7. MAILBOX DELIVERY
   writeToMailbox(sanitizedName, {
     from: TEAM_LEAD_NAME,
     text: prompt,
     timestamp: ISO timestamp
   }, teamName)
   // Teammate's inbox poller picks this up as first turn

8. REGISTRATION
   - Register in AppState.teamContext
   - Register in team file (CLAUDE.md team roster)
   - Register as background task (visible in tasks pill/dialog)
```

---

## 4.4 Mailbox System for Inter-Agent Communication

### Overview
The mailbox system is the **primary inter-agent communication mechanism** for out-of-process teammates (tmux/iTerm2).

### Source Files
| File | Lines | Purpose |
|------|-------|---------|
| `src/src/utils/teammateMailbox.ts` | 1-1183 | File-based messaging system |

### Mailbox Location
```
.claude/teams/{team_name}/inboxes/{agent_name}.json
```

### Message Types (14 total)

| Message Type | Purpose |
|-------------|---------|
| `TeammateMessage` | General messages between teammates |
| `IdleNotificationMessage` | Sent when a teammate becomes idle |
| `PermissionRequestMessage` | Worker→leader permission requests |
| `PermissionResponseMessage` | Leader→worker permission responses |
| `SandboxPermissionRequestMessage` | Network host permission requests |
| `SandboxPermissionResponseMessage` | Network host permission responses |
| `PlanApprovalRequestMessage` | Plan approval requests |
| `PlanApprovalResponseMessage` | Plan approval responses |
| `ShutdownRequestMessage` | Shutdown requests |
| `ShutdownApprovedMessage` | Shutdown approvals |
| `ShutdownRejectedMessage` | Shutdown rejections |
| `TaskAssignmentMessage` | Task assignments |
| `TeamPermissionUpdateMessage` | Team-wide permission updates |
| `ModeSetRequestMessage` | Mode change requests |

### File Locking (`teammateMailbox.ts:35-41`)

```typescript
const LOCK_OPTIONS = {
  retries: {
    retries: 10,
    minTimeout: 5,
    maxTimeout: 100,
  },
}
```

**Design rationale**: Uses `proper-lockfile` with retries and exponential backoff for concurrent mailbox access. No encryption or authentication — any process with filesystem access could potentially inject messages.

### Writing to Mailbox (`spawnMultiAgent.ts:517-521`)

```typescript
await writeToMailbox(
  sanitizedName,           // recipient agent name
  {
    from: TEAM_LEAD_NAME,  // sender identity
    text: prompt,          // message content (initial instructions)
    timestamp: new Date().toISOString(),
  },
  teamName                 // team context
);
```

### Reading from Mailbox
Teammates poll their inbox on startup. The inbox poller picks up messages and submits them as the teammate's first turn.

### SendMessage Tool for Running Agents
For **in-process** teammates and background agents, the `SendMessage` tool provides direct communication:

```typescript
SendMessage({ to: "agent-id-or-name", message: "Follow-up instructions..." })
```

Messages are queued in `task.pendingMessages` and drained at tool-round boundaries.

---

## 4.5 Permission Forwarding in Swarms

### Swarm Worker Permission Handler (`swarmWorkerHandler.ts:1-159`)

```
PSEUDOCODE: handleSwarmWorkerPermission()
───────────────────────────────────────────
1. Guard: if !isAgentSwarmsEnabled() OR !isSwarmWorker(): return null (fall through to interactive)

2. BASH CLASSIFIER: For bash commands, try classifier auto-approval first
   if feature('BASH_CLASSIFIER'):
     classifierResult = ctx.tryClassifier(pendingClassifierCheck, updatedInput)
     if classifierResult: return classifierResult (auto-approved)

3. FORWARD TO LEADER:
   a. Create permission request:
      { toolName, toolUseId, input, description, permissionSuggestions }

   b. Register callback BEFORE sending (avoid race condition):
      - onAllow(allowedInput, permissionUpdates, feedback, contentBlocks):
        → Merge allowedInput with original input
        → Call ctx.handleUserAllow() to execute the tool
      - onReject(feedback, contentBlocks):
        → Log reject decision
        → Call ctx.cancelAndAbort()

   c. Send request via mailbox:
      sendPermissionRequestViaMailbox(request)

   d. Show visual indicator:
      setAppState({ pendingWorkerRequest: { toolName, toolUseId, description } })

   e. Handle abort signal:
      If parent aborts while waiting: resolve with cancel decision

4. Promise resolves when leader responds (allow or reject)
```

### Swarm Permission Poller (`useSwarmPermissionPoller.ts:1-330`)

Polls every 500ms for permission responses from the team leader when running as a swarm worker.

Key functions:
- `registerPermissionCallback()` — registers callbacks for pending permission requests
- `processMailboxPermissionResponse()` — processes permission responses from mailbox
- `registerSandboxPermissionCallback()` — registers sandbox permission callbacks
- `processSandboxPermissionResponse()` — processes sandbox permission responses
- `useSwarmPermissionPoller()` — the React hook that polls for responses

---

## 4.6 Swarm Initialization Hook (`useSwarmInitialization.ts:1-81`)

```typescript
export function useSwarmInitialization(setAppState, initialMessages, { enabled = true } = {}) {
  useEffect(() => {
    if (!enabled) return
    if (isAgentSwarmsEnabled()) {
      // Check if this is a resumed agent session
      // ... initialize teammate context from stored info
    }
  }, [setAppState, initialMessages, enabled])
}
```

**Design rationale**: Initializes swarm features on session start. Handles both fresh spawns and resumed teammate sessions. Conditionally loaded for dead code elimination.

---

## 4.7 Teammate Identity Resolution (`teammate.ts:1-292`)

### Priority Order

1. **AsyncLocalStorage** (in-process teammates)
2. **dynamicTeamContext** (tmux teammates via CLI args)
3. **Environment variables**

### Key Functions

| Function | Lines | Purpose |
|----------|-------|---------|
| `isTeammate()` | 125-131 | Returns true if running as a teammate |
| `isTeamLead()` | 171-198 | Checks if this session is the team lead |
| `getParentSessionId()` | 34-38 | Returns the leader's session ID |
| `hasActiveInProcessTeammates()` | 205-213 | Checks for running in-process teammates |
| `hasWorkingInProcessTeammates()` | 220-231 | Checks for non-idle teammates |
| `waitForTeammatesToBecomeIdle()` | 238-292 | Returns promise that resolves when all teammates become idle |

---

## 4.8 Team Discovery (`teamDiscovery.ts:1-81`)

Utilities for discovering teams and teammate status. Scans `~/.claude/teams/` to find teams where the current session is the leader.

### Key Types

```typescript
type TeamSummary = {
  name: string
  memberCount: number
  runningCount: number
  idleCount: number
}

type TeammateStatus = {
  name: string
  agentId: string
  model: string
  prompt: string
  status: string
  color: string
  idleSince: string
  tmuxPaneId: string
  cwd: string
  worktreePath: string
  isHidden: boolean
  backendType: string
  mode: string
}
```

---

## 4.9 In-Process Teammate Task State (`InProcessTeammateTask/types.ts:1-121`)

```typescript
InProcessTeammateTaskState includes:
- Identity (agentId, agentName, teamName, color, planModeRequired, parentSessionId)
- Execution state (prompt, model, selectedAgent, abortController)
- Plan mode approval tracking
- Permission mode
- Conversation history (messages capped at 50 via TEAMMATE_MESSAGES_UI_CAP)
- Tool use tracking
- Idle/shutdown state
- Progress tracking
```

### Message Cap Rationale (`types.ts:89-101`)

> "BQ analysis (round 9, 2026-03-20) showed ~20MB RSS per agent at 500+ turn sessions and ~125MB per concurrent agent in swarm bursts. Whale session 9a990de8 launched 292 agents in 2 minutes and reached 36.8GB."

---

## 4.10 Local Agent Task Management (`LocalAgentTask.tsx:1-683`)

| Function | Lines | Purpose |
|----------|-------|---------|
| `registerAsyncAgent()` | 466-515 | Register a background agent task |
| `registerAgentForeground()` | 526-614 | Register a foreground agent that can be backgrounded later |
| `backgroundAgentTask()` | 620-652 | Background a foreground agent |
| `killAsyncAgent()` | 281-303 | Kill an agent task |
| `killAllRunningAgentTasks()` | 309-315 | Kill all running agents (ESC cancellation in coordinator mode) |
| `enqueueAgentNotification()` | 197-262 | Enqueue task completion notifications |
| `updateAgentProgress()` | 339-353 | Update progress tracking |
| `updateAgentSummary()` | 359-407 | Update background summary (for SDK agent progress summaries) |
| `completeAgentTask()` | 412-432 | Mark task as completed |
| `failAgentTask()` | 437-456 | Mark task as failed |

---

## 4.11 Remote Agent Execution

### Remote Task Types
```
['remote-agent', 'ultraplan', 'ultrareview', 'autofix-pr', 'background-pr']
```

### Precondition Checks (`RemoteAgentTask.tsx:146-161`)

| Precondition | Error Code |
|-------------|------------|
| Must be authenticated with Claude.ai | `not_logged_in` |
| Needs a cloud environment | `no_remote_environment` |
| Must be in a git repository | `not_in_git_repo` |
| Needs a GitHub remote | `no_git_remote` |
| Claude GitHub App must be installed | `github_app_not_installed` |
| Org policy must allow remote sessions | `policy_blocked` |

### Teleport to Remote (`teleport.tsx:730-1190`)

Two source modes:
1. **GitHub clone** (default): Backend clones from repo's origin URL
2. **Bundle fallback**: CLI creates `git bundle --all`, uploads via Files API. Gated by `tengu_ccr_bundle_seed_enabled` or `CCR_ENABLE_BUNDLE` env.

### Remote Session Polling (`RemoteAgentTask.tsx:538-799`)

- Polls every **1000ms** via `pollRemoteSessionEvents()`
- Accumulates log from SDK events
- Appends delta text to task output file
- Detects completion via:
  - Session status = `'archived'`
  - `result` message in log
  - Completion checker (for custom remote task types)
  - Remote-review: `<remote-review>` tag in hook_progress stdout
  - Stable idle detection (5 consecutive idle polls)
  - 30-minute timeout for remote-review tasks

### Remote Agent Registration (`RemoteAgentTask.tsx:386-466`)

```typescript
registerRemoteAgentTask({
  remoteTaskType: 'remote-agent',  // or 'ultraplan', 'ultrareview', 'autofix-pr', 'background-pr'
  session: { id, title },
  command: prompt,
  context: toolUseContext,
  toolUseId,
})
```

---

## 4.12 Git Bundle Fallback Mechanism

### When It's Used
1. GitHub preflight fails (CCR can't clone the repo)
2. No GitHub remote exists
3. `CCR_FORCE_BUNDLE=1` env var is set
4. `tengu_ccr_bundle_seed_enabled` GrowthBook gate is on

### Bundle Creation Flow (`teleport/gitBundle.ts`)

```
PSEUDOCODE: createAndUploadGitBundle()
───────────────────────────────────────
1. Check repo has commits (not empty)
2. If uncommitted changes:
   a. Create refs/seed/stash pointing to working tree
   b. bundle.hasWip = true
3. Create git bundle:
   `git bundle create --all <bundle-file>`
4. Check bundle size (reject if too large)
5. Upload via Files API:
   POST to Files API with OAuth token
   Returns fileId
6. Return { success: true, fileId, bundleSizeBytes, scope, hasWip }
```

### Bundle Fail Reasons

| Reason | User Message |
|--------|-------------|
| `empty_repo` | "Repository has no commits — run `git add . && git commit -m \"initial\"` then retry" |
| `too_large` | "Repo is too large to teleport. Please setup GitHub on https://claude.ai/code" |
| `git_error` | "Failed to create git bundle ({error}). Please setup GitHub on https://claude.ai/code" |

### Backend Behavior
When CCR receives `seed_bundle_file_id`:
1. Downloads the bundle from Files API
2. Clones from the bundle instead of GitHub
3. Container gets the caller's exact local state (including uncommitted changes via refs/seed/stash)
4. No GitHub dependency — works for local-only repos

---

## 4.13 Coordinator Mode

### Enable Gate (`coordinatorMode.ts:36-41`)

```typescript
export function isCoordinatorMode(): boolean {
  if (feature('COORDINATOR_MODE')) {
    return isEnvTruthy(process.env.CLAUDE_CODE_COORDINATOR_MODE)
  }
  return false
}
```

### Coordinator System Prompt (`coordinatorMode.ts:111-369`)

Key sections:
1. **Role**: Orchestrate workers for research, implementation, verification
2. **Tools**: Agent, SendMessage, TaskStop, subscribe_pr_activity/unsubscribe_pr_activity
3. **Workers**: Have access to standard tools, MCP tools, project skills via Skill tool
4. **Workflow**: Research (Workers, parallel) → Synthesis (Coordinator) → Implementation (Workers) → Verification (Workers)
5. **Prompt Writing**: Workers can't see coordinator's conversation — every prompt must be self-contained
6. **Synthesis Rule**: Never write "based on your findings" — always synthesize
7. **Continue vs Spawn Decision**:
   | Situation | Mechanism | Why |
   |-----------|-----------|-----|
   | Research explored exactly the files that need editing | Continue (SendMessage) | Worker already has files in context |
   | Research was broad but implementation is narrow | Spawn fresh (Agent) | Avoid exploration noise |
   | Correcting a failure | Continue | Worker has error context |
   | Verifying code a different worker wrote | Spawn fresh | Verifier should see code with fresh eyes |
   | Wrong approach entirely | Spawn fresh | Clean slate avoids anchoring |

### Coordinator User Context (`coordinatorMode.ts:80-109`)

```typescript
function getCoordinatorUserContext(mcpClients, scratchpadDir) {
  const workerTools = isEnvTruthy(CLAUDE_CODE_SIMPLE)
    ? 'Bash, FileEdit, FileRead'  // simple mode
    : Array.from(ASYNC_AGENT_ALLOWED_TOOLS).filter(not internal).join(', ')

  let content = `Workers spawned via the Agent tool have access to these tools: ${workerTools}`

  if (mcpClients.length > 0) {
    content += `\n\nWorkers also have access to MCP tools from: ${serverNames}`
  }

  if (scratchpadDir && isScratchpadGateEnabled()) {
    content += `\n\nScratchpad directory: ${scratchpadDir}\nWorkers can read and write here without permission prompts.`
  }

  return { workerToolsContext: content }
}
```

### Coordinator Mode Activation

When `CLAUDE_CODE_COORDINATOR_MODE=1`:
- `isCoordinatorMode()` returns `true`
- Built-in agents are replaced with coordinator agents (worker type)
- All agent spawns are forced async
- Agent tool prompt is slimmed down (coordinator already knows usage)
- User context includes `workerToolsContext`
- Internal worker tools excluded: `TEAM_CREATE_TOOL_NAME`, `TEAM_DELETE_TOOL_NAME`, `SEND_MESSAGE_TOOL_NAME`, `SYNTHETIC_OUTPUT_TOOL_NAME`

---

## 4.14 Scratchpad Directory

### Gate: `tengu_scratch` (`coordinatorMode.ts:25-27`)

```typescript
function isScratchpadGateEnabled(): boolean {
  return checkStatsigFeatureGate_CACHED_MAY_BE_STALE('tengu_scratch')
}
```

### Purpose
The scratchpad directory is a **durable cross-worker knowledge store** in coordinator mode:
- Workers can read and write without permission prompts
- Used for structured knowledge sharing between workers
- Coordinator can structure files however fits the work
- Passed via `getCoordinatorUserContext`'s `scratchpadDir` parameter (dependency injection from QueryEngine.ts)

---

## 4.15 Scheduled Remote Agents

### Source Files
| File | Purpose |
|------|---------|
| `src/src/skills/bundled/scheduleRemoteAgents.ts` | Skill implementation |
| `src/src/tools/RemoteTriggerTool/RemoteTriggerTool.ts` | RemoteTrigger tool |

### Gates
- `tengu_surreal_dali` GrowthBook gate
- `allow_remote_sessions` policy

### Skill Registration

```typescript
registerBundledSkill({
  name: 'schedule',
  description: 'Create, update, list, or run scheduled remote agents (triggers) that execute on a cron schedule.',
  whenToUse: 'When the user wants to schedule a recurring remote agent...',
  userInvocable: true,
  isEnabled: () => getFeatureValue_CACHED_MAY_BE_STALE('tengu_surreal_dali', false) &&
                   isPolicyAllowed('allow_remote_sessions'),
  allowedTools: [REMOTE_TRIGGER_TOOL_NAME, ASK_USER_QUESTION_TOOL_NAME],
})
```

### Key Constraints
- **Minimum cron interval: 1 hour** (`*/30 * * * *` will be rejected)
- Cron expressions are always in UTC
- Cannot delete triggers via API (direct users to https://claude.ai/code/scheduled)
- MCP connectors attached via `connector_uuid`, `name`, and `url`
- Default model: `claude-sonnet-4-6`
- Requires `environment_id` from CCR environments
- Auth: requires Claude.ai OAuth tokens

---

## 4.16 Fork Subagent Experiment

### Enable Gate (`forkSubagent.ts:32-39`)

```typescript
export function isForkSubagentEnabled(): boolean {
  if (feature('FORK_SUBAGENT')) {
    if (isCoordinatorMode()) return false   // mutually exclusive
    if (getIsNonInteractiveSession()) return false  // SDK/API only
    return true
  }
  return false
}
```

### What Forking Does

When enabled and `subagent_type` is **omitted**:
1. Child inherits the **parent's full conversation context** (all messages)
2. Child inherits the **parent's system prompt** (byte-exact for cache sharing)
3. Child inherits the **parent's exact tool pool** (`useExactTools: true`)
4. Child inherits the **parent's thinking config**
5. All spawns run **async** (unified task-notification model)
6. `/fork <directive>` slash command becomes available

### Fork Agent Definition (`forkSubagent.ts:60-71`)

```typescript
export const FORK_AGENT = {
  agentType: 'fork',
  whenToUse: 'Implicit fork — inherits full conversation context...',
  tools: ['*'],
  maxTurns: 200,
  model: 'inherit',
  permissionMode: 'bubble',
  source: 'built-in',
  baseDir: 'built-in',
  getSystemPrompt: () => '',
}
```

### Fork Message Construction (`buildForkedMessages`)

```
PSEUDOCODE: buildForkedMessages(directive, assistantMessage)
──────────────────────────────────────────────────────────────
1. Clone the parent's full assistant message (all tool_use blocks, thinking, text)
2. Collect all tool_use blocks from the assistant message
3. Build tool_result blocks for every tool_use with IDENTICAL placeholder:
   "Fork started — processing in background"
4. Build single user message:
   [all placeholder tool_results, per-child directive text]
5. Return: [fullAssistantMessage, toolResultMessage]
```

### Fork Child Directive (FORK_BOILERPLATE_TAG)

```
STOP. READ THIS FIRST.

You are a forked worker process. You are NOT the main agent.

RULES (non-negotiable):
1. Your system prompt says "default to forking." IGNORE IT — that's for the parent.
   You ARE the fork. Do NOT spawn sub-agents; execute directly.
2. Do NOT converse, ask questions, or suggest next steps
3. Do NOT editorialize or add meta-commentary
4. USE your tools directly: Bash, Read, Write, etc.
5. If you modify files, commit your changes before reporting. Include the commit hash.
6. Do NOT emit text between tool calls. Use tools silently, then report once at the end.
7. Stay strictly within your directive's scope.
8. Keep your report under 500 words unless the directive specifies otherwise.
9. Your response MUST begin with "Scope:". No preamble, no thinking-out-loud.
10. REPORT structured facts, then stop

Output format:
  Scope: <echo back your assigned scope in one sentence>
  Result: <the answer or key findings>
  Key files: <relevant file paths>
  Files changed: <list with commit hash>
  Issues: <list — include only if there are issues to flag>

<fork-directive>{directive}</fork-directive>
```

### Recursive Fork Guard (`forkSubagent.ts:78-89`)

```typescript
// QuerySource check (compaction-resistant)
if (toolUseContext.options.querySource === `agent:builtin:${FORK_AGENT.agentType}`)
  throw 'Fork is not available inside a forked worker'

// Message scan fallback (catches any path where querySource wasn't threaded)
if (isInForkChild(toolUseContext.messages))
  throw 'Fork is not available inside a forked worker'
```

### Fork Child Detection (`forkSubagent.ts:78-89`)

```typescript
export function isInForkChild(messages: MessageType[]): boolean {
  return messages.some(m => {
    if (m.type !== 'user') return false
    const content = m.message.content
    if (!Array.isArray(content)) return false
    return content.some(block => block.type === 'text' && block.text.includes(`<${FORK_BOILERPLATE_TAG}>`))
  })
}
```

### Worktree + Fork Combination

When fork + worktree isolation are combined:
```
You've inherited the conversation context above from a parent agent working in {parentCwd}.
You are operating in an isolated git worktree at {worktreeCwd} — same repository,
same relative file structure, separate working copy. Paths in the inherited context
refer to the parent's working directory; translate them to your worktree root.
Re-read files before editing if the parent may have modified them.
Your changes stay in this worktree and will not affect the parent's files.
```

### Prompt Cache Sharing for Fork Subagents

```typescript
override: isForkPath ? { systemPrompt: forkParentSystemPrompt } : ...,
availableTools: isForkPath ? toolUseContext.options.tools : workerTools,
forkContextMessages: isForkPath ? toolUseContext.messages : undefined,
...(isForkPath && { useExactTools: true })
```

**Design rationale**: Fork children inherit parent's exact system prompt bytes, tool array, thinking config, and messages prefix for byte-identical API request prefixes. This enables prompt cache hits between fork siblings.

---

## 4.17 Forked Agent Context Sharing (`forkedAgent.ts:1-689`)

### CacheSafeParams

Parameters that must be identical between fork and parent for prompt cache hits.

### State Isolation Strategy (`createSubagentContext`)

| State | Fork Child | Regular Subagent |
|-------|-----------|-----------------|
| readFileState | Cloned from parent | Fresh |
| abortController | New child controller linked to parent | New |
| getAppState | Wrapped to set shouldAvoidPermissionPrompts | Standard |
| setAppState | No-op by default (opt-in via shareSetAppState) | Standard |
| setResponseLength | No-op by default (opt-in via shareSetResponseLength) | Standard |
| nestedMemoryAttachmentTriggers | Fresh | Fresh |
| toolDecisions | Fresh | Fresh |
| discoveredSkillNames | Fresh | Fresh |
| contentReplacementState | Cloned from parent | Fresh |

---

## 4.18 Complete Tool Restriction Matrix

| Tool | General Agent | Async Agent | Fork Child | Coordinator | In-Process Teammate |
|------|--------------|-------------|------------|-------------|---------------------|
| TaskOutputTool | BLOCKED | BLOCKED | — | — | — |
| ExitPlanModeTool | BLOCKED | BLOCKED | — | — | — |
| EnterPlanModeTool | BLOCKED | BLOCKED | — | — | — |
| AgentTool | BLOCKED (non-ant) | BLOCKED | ALLOWED | ALLOWED | BLOCKED |
| AskUserQuestionTool | BLOCKED | BLOCKED | — | — | — |
| TaskStopTool | BLOCKED | BLOCKED | — | ALLOWED | — |
| WorkflowTool | BLOCKED (if WORKFLOW_SCRIPTS) | — | — | — | — |
| TaskCreate | — | — | — | — | ALLOWED |
| TaskGet | — | — | — | — | ALLOWED |
| TaskList | — | — | — | — | ALLOWED |
| TaskUpdate | — | — | — | — | ALLOWED |
| SendMessage | — | — | — | ALLOWED | ALLOWED |
| CronCreate | — | — | — | — | ALLOWED (if AGENT_TRIGGERS) |
| CronDelete | — | — | — | — | ALLOWED (if AGENT_TRIGGERS) |
| CronList | — | — | — | — | ALLOWED (if AGENT_TRIGGERS) |
| FileRead | ALLOWED | ALLOWED | — | — | — |
| FileEdit | ALLOWED | ALLOWED | — | — | — |
| FileWrite | ALLOWED | ALLOWED | — | — | — |
| Bash | ALLOWED | ALLOWED | — | — | — |
| Glob | ALLOWED | ALLOWED | — | — | — |
| Grep | ALLOWED | ALLOWED | — | — | — |
| WebSearch | ALLOWED | ALLOWED | — | — | — |
| WebFetch | ALLOWED | ALLOWED | — | — | — |
| TodoWrite | ALLOWED | ALLOWED | — | — | — |
| SkillTool | ALLOWED | ALLOWED | — | — | — |
| EnterWorktree | ALLOWED | ALLOWED | — | — | — |
| ExitWorktree | ALLOWED | ALLOWED | — | — | — |
| SyntheticOutputTool | ALLOWED | ALLOWED | — | ALLOWED | — |
| ToolSearch | ALLOWED | ALLOWED | — | — | — |
| NotebookEdit | ALLOWED | ALLOWED | — | — | — |
| MCPTool | TBD | TBD | — | — | — |

---

## 4.19 All GrowthBook/Feature Gates

### Feature Flags

| Flag | Purpose | File |
|------|---------|------|
| `FORK_SUBAGENT` | Fork subagent experiment | `forkSubagent.ts:33` |
| `COORDINATOR_MODE` | Coordinator mode feature flag | `coordinatorMode.ts:37` |
| `VERIFICATION_AGENT` | Verification agent feature flag | `builtInAgents.ts:65` |
| `BUILTIN_EXPLORE_PLAN_AGENTS` | Explore/Plan feature flag | `builtInAgents.ts:14` |
| `WORKFLOW_SCRIPTS` | Workflow tool in agents | `tools.ts:44` |
| `AGENT_TRIGGERS` | Cron tools for teammates | `tools.ts:86` |
| `TRANSCRIPT_CLASSIFIER` | Handoff classification | `agentToolUtils.ts:607` |
| `PROMPT_CACHE_BREAK_DETECTION` | Cache break tracking | `runAgent.ts:824` |
| `KAIROS` | Assistant mode force-async | `AgentTool.tsx:563` |
| `PROACTIVE` | Proactive mode | `AgentTool.tsx:59` |
| `BASH_CLASSIFIER` | Auto-approve bash commands | `swarmWorkerHandler.ts:52` |
| `AGENT_MEMORY_SNAPSHOT` | Agent memory snapshots | `loadAgentsDir.ts:348` |
| `MONITOR_TOOL` | Monitor MCP tasks | `runAgent.ts:849` |

### GrowthBook Flags

| Flag | Purpose | File |
|------|---------|------|
| `tengu_amber_flint` | Agent teams killswitch | `agentSwarmsEnabled.ts:39` |
| `tengu_amber_stoat` | Explore/Plan agents | `builtInAgents.ts:17` |
| `tengu_hive_evidence` | Verification agent | `builtInAgents.ts:66` |
| `tengu_surreal_dali` | Scheduled remote agents | `scheduleRemoteAgents.ts:333` |
| `tengu_auto_background_agents` | Auto-background after 120s | `AgentTool.tsx:73` |
| `tengu_scratch` | Scratchpad directory | `coordinatorMode.ts:26` |
| `tengu_ccr_bundle_seed_enabled` | Git bundle fallback | `teleport.tsx:944` |
| `tengu_cobalt_lantern` | /web-setup for GitHub | `scheduleRemoteAgents.ts:400` |
| `tengu_slim_subagent_claudemd` | Omit CLAUDE.md from read-only agents | `runAgent.ts:393` |
| `tengu_agent_list_attach` | Agent list as attachment message | `prompt.ts:63` |
| `tengu_explore_agent` | Explore agent model selection | `exploreAgent.ts:78` |
| `tengu_session_memory` | Session memory feature | `sessionMemory.ts:81` |
| `tengu_sm_compact` | Session memory compaction | `sessionMemoryCompact.ts` |
| `tengu_passport_quail` | Durable memory extraction | `extractMemories.ts:536` |
| `tengu_sm_config` | Session memory config | `sessionMemory.ts` |

### Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` | Enable agent teams (external) | Off |
| `CLAUDE_CODE_COORDINATOR_MODE` | Enable coordinator mode | Off |
| `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS` | Disable all async agents | Off |
| `CLAUDE_AUTO_BACKGROUND_TASKS` | Auto-background agents after 120s | Off |
| `CLAUDE_CODE_SIMPLE` | Simple mode — skip custom agents | Off |
| `CLAUDE_AGENT_SDK_DISABLE_BUILTIN_AGENTS` | Disable all built-in agents (SDK only) | Off |
| `CLAUDE_CODE_AGENT_LIST_IN_MESSAGES` | Agent list as attachment vs inline | Feature-gated |
| `CLAUDE_CODE_ENTRYPOINT` | SDK entrypoint type (`sdk-ts`, `sdk-py`, `sdk-cli`) | — |
| `CCR_FORCE_BUNDLE` | Force git bundle mode for teleport | Off |
| `CCR_ENABLE_BUNDLE` | Enable bundle seed gate | Off |
| `USER_TYPE` | Build type (`ant` or external) | — |
| `TEAMMATE_COMMAND_ENV_VAR` | Override teammate binary path | — |
| `CLAUDE_CODE_MAX_CONTEXT_TOKENS` | Override context window (ant-only) | — |
| `CLAUDE_CODE_DISABLE_1M_CONTEXT` | Disable 1M context (HIPAA compliance) | Off |
| `CLAUDE_CODE_AUTO_COMPACT_WINDOW` | Override auto-compact window size | — |

---

## 4.20 Security Implications

1. **Master Gate Bypass**: Setting `USER_TYPE=ant` bypasses ALL swarm-related checks in one shot — no opt-in, no killswitch, no GrowthBook gates.

2. **Remote Agent Access**: The `isolation: 'remote'` feature is explicitly "Gated ant-only" and delegates to cloud CCR environments. This provides cloud-based agent execution with full isolation.

3. **Permission Delegation**: Swarm workers forward all permission requests to the team leader. A compromised worker could potentially trigger the leader to approve dangerous operations.

4. **Mailbox IPC**: File-based mailbox system has no encryption or authentication — any process with filesystem access could potentially inject messages into a teammate's inbox.

5. **In-Process Isolation**: AsyncLocalStorage provides logical isolation but not security isolation — all in-process teammates share the same Node.js process, memory space, and filesystem access.

6. **Fork Subagent Inheritance**: Fork children inherit the parent's full tool pool, system prompt, and conversation context. A fork child has the same capabilities as the parent.

7. **Coordinator Mode**: The coordinator has a massive system prompt that teaches it to orchestrate workers. The system prompt includes detailed instructions on worker management, prompt writing, and concurrency patterns.

8. **Team File Manipulation**: Team files are stored in `~/.claude/teams/` and are readable/writable by any process with filesystem access.

---

## 4.21 Key Results Summary

| Metric | Value |
|--------|-------|
| Distinct agent capabilities | 38 |
| Feature flags used for build-time gating | 13 |
| GrowthBook flags for runtime feature control | 6+ |
| Environment variables for configuration | 9+ |
| Spawn modes | 3 (split-pane, separate window, in-process) |
| Message types in mailbox IPC | 14 |
| Remote task types | 5 (remote-agent, ultraplan, ultrareview, autofix-pr, background-pr) |
| Built-in agents | 7 (general-purpose, Explore, Plan, claude-code-guide, verification, statusline-setup, fork) |
| Compaction tiers | 4 (time-based microcompact, cached microcompact, auto-compact, session memory compact) |
| Cache break detection dimensions | 12+ |
| Context window resolution layers | 6 |
| Post-compact restoration budgets | 5 levels (per-file, total file, max files, per-skill, total skill) |

---

*This document was extracted from reverse-engineered Claude Code source code. All file paths, line numbers, and code patterns are sourced from the actual codebase. This is the blueprint for AgentOS — a production-grade multi-agent orchestration system.*
