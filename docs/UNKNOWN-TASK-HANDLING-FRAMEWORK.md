# UNKNOWN TASK HANDLING FRAMEWORK

**Version:** 1.0.0  
**Date:** 2026-04-02  
**Status:** Authoritative Blueprint  
**Scope:** How AgentOS handles ANY task with zero prior context

---

## TABLE OF CONTENTS

1. [THE PROBLEM](#1-the-problem)
2. [THE SOLUTION ARCHITECTURE](#2-the-solution-architecture)
3. [LAYER 1: SKILL SYSTEM](#3-layer-1-skill-system)
4. [LAYER 2: MCP SERVER ECOSYSTEM](#4-layer-2-mcp-server-ecosystem)
5. [LAYER 3: TOOL SEARCH & DEFERRED DISCOVERY](#5-layer-3-tool-search--deferred-discovery)
6. [LAYER 4: RESEARCH & FORKED AGENTS](#6-layer-4-research--forked-agents)
7. [LAYER 5: ADAPTATION & SUBSTITUTION](#7-layer-5-adaptation--substitution)
8. [LAYER 6: SESSION MEMORY & KNOWLEDGE ACCUMULATION](#8-layer-6-session-memory--knowledge-accumulation)
9. [LAYER 7: FALLBACK CHAINS](#9-layer-7-fallback-chains)
10. [SPECIFIC TASK PATTERNS](#10-specific-task-patterns)
11. [THE COMPLETE FLOW](#11-the-complete-flow)
12. [MCP SERVER DISCOVERY ALGORITHM](#12-mcp-server-discovery-algorithm)
13. [PLUGIN SYSTEM DYNAMICS](#13-plugin-system-dynamics)
14. [EDGE CASE HANDLING](#14-edge-case-handling)

---

## 1. THE PROBLEM

### What Is an "Unknown Task"?

An unknown task is any request where the agent has **zero prior context** about:
- The domain (e.g., "Create a Google Apps Script for Gmail automation")
- The tooling (e.g., "Scrape this dynamic JavaScript-rendered page")
- The methodology (e.g., "Convert this research paper into a working implementation")
- The infrastructure (e.g., "Set up a Kubernetes operator for my custom resource")

### Why Prior Systems Fail

Traditional agents fail on unknown tasks because:
1. **Fixed tool sets** — They only know tools they were trained with
2. **No discovery mechanism** — They can't find new tools at runtime
3. **No learning loop** — Each session starts from scratch
4. **No substitution logic** — If the primary approach fails, they're stuck
5. **No memory accumulation** — Knowledge gained isn't preserved

### The Core Challenge

```
User: "Build me a web scraper that handles Cloudflare challenges"
Agent with no context:
  ❌ Doesn't know what MCP servers exist for web scraping
  ❌ Doesn't know about Cloudflare bypass techniques
  ❌ Doesn't know which tools can handle JavaScript rendering
  ❌ Has no memory of previous scraping attempts
  ❌ Can't discover new capabilities at runtime
```

---

## 2. THE SOLUTION ARCHITECTURE

### Multi-Layer Defense-in-Depth

The unknown task handling system uses **7 layers**, each progressively more capable but also more expensive:

```
                    ┌─────────────────────────────────────┐
                    │    LAYER 7: FALLBACK CHAINS         │  ← Last resort
                    │    (graceful degradation)           │
                    ├─────────────────────────────────────┤
                    │    LAYER 6: SESSION MEMORY          │  ← Learn & store
                    │    (accumulate knowledge)           │
                    ├─────────────────────────────────────┤
                    │    LAYER 5: ADAPTATION              │  ← Substitute
                    │    (find alternatives)              │
                    ├─────────────────────────────────────┤
                    │    LAYER 4: FORKED AGENTS           │  ← Deep research
                    │    (parallel investigation)         │
                    ├─────────────────────────────────────┤
                    │    LAYER 3: TOOL SEARCH             │  ← Find tools
                    │    (deferred discovery)             │
                    ├─────────────────────────────────────┤
                    │    LAYER 2: MCP SERVERS             │  ← Connect servers
                    │    (dynamic capabilities)           │
                    ├─────────────────────────────────────┤
                    │    LAYER 1: SKILL SYSTEM            │  ← Check first
                    │    (known capabilities)             │
                    └─────────────────────────────────────┘
```

### Decision Flow

```
User gives unknown task
         │
         ▼
   ┌─────────────┐
   │ Layer 1:    │  Check skills directory for matching skills
   │ Skills?     │  → Found? Execute skill instructions
   └──────┬──────┘
          │ No match
          ▼
   ┌─────────────┐
   │ Layer 2:    │  Search for MCP servers that handle this domain
   │ MCP?        │  → Found? Connect and use MCP tools
   └──────┬──────┘
          │ No servers
          ▼
   ┌─────────────┐
   │ Layer 3:    │  Use ToolSearch to find deferred tools
   │ ToolSearch? │  → Found? Use discovered tools
   └──────┬──────┘
          │ Nothing found
          ▼
   ┌─────────────┐
   │ Layer 4:    │  Fork agents to research the domain
   │ Research?   │  → Results? Apply findings
   └──────┬──────┘
          │ Still stuck
          ▼
   ┌─────────────┐
   │ Layer 5:    │  Substitute with alternative approaches
   │ Adapt?      │  → Alternative? Try it
   └──────┬──────┘
          │ No alternatives
          ▼
   ┌─────────────┐
   │ Layer 6:    │  Store what we learned for next time
   │ Learn?      │  → Create skill/memory for future
   └──────┬──────┘
          │
          ▼
   ┌─────────────┐
   │ Layer 7:    │  Gracefully degrade, explain limitations
   │ Fallback?   │  → Provide best partial answer
   └─────────────┘
```

### Key Principles

1. **Cheapest first** — Skills are free (already loaded), MCP costs connection time, research costs tokens
2. **Progressive disclosure** — Each layer reveals more about the problem space
3. **Knowledge accumulation** — Every layer feeds back into Layer 6 (memory)
4. **No dead ends** — Layer 7 ensures the agent always provides SOMETHING useful

---

## 3. LAYER 1: SKILL SYSTEM

### How Skills Work

Skills are the **first and cheapest** layer. They are markdown files with YAML frontmatter that provide structured instructions for specific tasks.

### Skill Discovery Algorithm

From `loadSkillsDir.ts`, the complete loading algorithm:

```
FUNCTION getSkillDirCommands(cwd):
  // Resolve all skill directory paths
  userSkillsDir     = ~/.claude/skills/                    ← Global user skills
  managedSkillsDir  = getManagedFilePath()/.claude/skills/ ← Policy-managed
  projectSkillsDirs = .claude/skills/ walking up to ~      ← Project-local
  additionalDirs    = --add-dir paths                      ← Explicit adds

  // Load from all sources in parallel
  [managedSkills, userSkills, projectSkills, additionalSkills, legacyCommands] =
    PARALLEL_LOAD(all directories)

  // Deduplicate by realpath (first wins)
  // Priority: managed > user > project > additional > legacy

  // Separate conditional skills (with paths: frontmatter)
  // Store unconditional skills for immediate use
  // Store conditional skills for activation when matching files touched

  RETURN unconditional skills
```

### Skill Directory Priority

| Priority | Location | Scope | Example |
|----------|----------|-------|---------|
| 1 | `getManagedFilePath()/.claude/skills/` | Policy-enforced | Enterprise-wide skills |
| 2 | `~/.claude/skills/` | User-global | Personal skills across all projects |
| 3 | `.claude/skills/` (walks up to ~) | Project-local | Project-specific skills |
| 4 | `--add-dir` paths → `.claude/skills/` | Explicit | Manually added directories |
| 5 | `.claude/commands/` (DEPRECATED) | Legacy | Old command format |

### Skill Format

```markdown
---
name: web-scraper
description: Scrape websites with various techniques
when_to_use: When the user asks to scrape, extract, or harvest data from websites
allowed-tools:
  - Bash(curl:*)
  - Bash(python:*)
  - WebFetch
  - WebSearch
  - Read
  - Write
model: sonnet
effort: high
---

# Web Scraping Skill

## Approach

1. First, try WebFetch for static pages
2. If JavaScript-rendered, use Python with Playwright
3. Handle anti-bot measures with...

## Tools Required

- Primary: WebFetch (static content)
- Secondary: Python + Playwright (dynamic content)
- Fallback: Selenium with stealth plugins

## Common Patterns

### Cloudflare Protection
...
```

### Dynamic Skill Discovery

Skills can be discovered **at runtime** when the agent operates on files:

```
FUNCTION discoverSkillDirsForPaths(filePaths, cwd):
  FOR each filePath being operated on:
    Walk up from file's directory to cwd
    Check for .claude/skills/ at each level
    Skip gitignored directories (node_modules protection)
    Load any newly discovered skills
    Deeper skills override shallower ones
```

### Conditional Skill Activation

Skills with `paths:` frontmatter activate when matching files are touched:

```markdown
---
name: react-review
description: Review React component code
paths:
  - src/components/**
  - src/**/*.tsx
---
```

These are stored separately and activated via `activateConditionalSkillsForPaths()` when the model touches matching files.

### Skill Execution Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| **Inline** (default) | Skill content expands into current conversation | Simple tasks, needs user interaction |
| **Fork** (`context: fork`) | Runs as a sub-agent with its own context | Self-contained research tasks |
| **Model-only** (`user-invocable: false`) | Only the model can invoke | Internal helper skills |
| **User-only** (`disable-model-invocation: true`) | Only users can invoke via slash command | Sensitive operations |

### Shell Command Execution in Skills

Skills can execute shell commands **at load time** using two syntaxes:

```markdown
# Block syntax
```!
git diff --stat HEAD
```

# Inline syntax
The current branch is !`git branch --show-current`.
```

Commands go through permission checks and the skill's `allowed-tools` are injected as `alwaysAllowRules`.

### How Skills Handle Unknown Tasks

When a skill encounters an unknown sub-task, it can:

1. **Reference other skills** via the `skills:` frontmatter field
2. **Fork a sub-agent** with `context: fork` to research
3. **Use WebSearch/WebFetch** to find information
4. **Execute shell commands** to discover tools (`npm search`, `pip search`)
5. **Create conditional skills** for future activation

---

## 4. LAYER 2: MCP SERVER ECOSYSTEM

### What Is MCP?

The Model Context Protocol (MCP) is a standard for connecting AI models to external tools and data sources. MCP servers expose tools, resources, and prompts that the agent can use dynamically.

### MCP Connection Management

From `useManageMCPConnections.ts`:

```
MCP Lifecycle:
  1. Load configs from multiple scopes:
     - Enterprise config (exclusive control)
     - User config (~/.claude/mcp.json)
     - Project config (.claude/mcp.json)
     - Local config (.claude.local/mcp.json)
     - Dynamic configs (runtime-added)
     - Claude.ai configs (network-fetched)

  2. Dedup by signature:
     - stdio:[command] for stdio servers
     - url:[unwrapped_url] for HTTP servers

  3. Connect with exponential backoff:
     - 5 attempts, 1s-30s backoff
     - Channel notification handler registration
     - Batched state updates (16ms flush window)

  4. Transport types supported:
     - stdio (local process)
     - SSE (Server-Sent Events)
     - SSE-IDE
     - HTTP (Streamable HTTP)
     - WS (WebSocket)
     - WS-IDE
     - claudeai-proxy
     - SDK (in-process)
```

### MCP Tool Integration

MCP tools appear in the tool registry as:
- `mcp__serverName__toolName`
- `isMcp: true` — marks them as MCP tools
- `shouldDefer: true` — deferred by default (unless `alwaysLoad: true`)
- Discovered via ToolSearch when needed

### MCP Skill Builders

MCP servers can provide skills through a write-once registry pattern:

```typescript
// mcpSkillBuilders.ts — dependency-graph leaf
let builders: MCPSkillBuilders | null = null

export function registerMCPSkillBuilders(b: MCPSkillBuilders): void {
  builders = b  // Called once at startup
}

export function getMCPSkillBuilders(): MCPSkillBuilders {
  if (!builders) throw new Error('MCP skill builders not registered')
  return builders
}
```

This avoids circular imports while allowing MCP servers to create skill commands.

### MCP Instructions Delta

From `mcpInstructionsDelta.ts`:
- Delta-based MCP instruction announcements avoid per-turn recomputation
- Scans message history for `mcp_instructions_delta` attachments
- Supports both server-authored instructions and client-side synthesized blocks
- Prevents prompt cache bust on late MCP connect

### Key MCP Servers for Unknown Tasks

| MCP Server | Purpose | Transport | Tools Provided |
|------------|---------|-----------|----------------|
| **mem0** | Memory management | stdio | Store/retrieve memories, context |
| **examcp** | Example MCP servers | stdio | Reference implementations |
| **Playwright** | Browser automation | stdio | Navigate, scrape, screenshot |
| **Puppeteer** | Headless browser | stdio | Page control, data extraction |
| **Firecrawl** | Web scraping API | HTTP | Crawl, scrape, extract |
| **Jina Reader** | URL to markdown | HTTP | Clean content extraction |
| **GitHub** | Git operations | stdio | Repos, PRs, issues |
| **PostgreSQL** | Database access | stdio | Query, schema, migrations |
| **Filesystem** | File operations | stdio | Read, write, search files |
| **Google Workspace** | G Suite APIs | HTTP | Gmail, Sheets, Docs, Apps Script |
| **Slack** | Communication | HTTP | Messages, channels, search |
| **Linear** | Project management | HTTP | Issues, projects, teams |

### How to Discover the Best MCP Server

```
ALGORITHM: DiscoverBestMCPServer(task):
  1. Parse task for domain keywords
  2. Search MCP marketplace/plugin registry
  3. Check installed MCP servers for matching tools
  4. If none found:
     a. WebSearch for "MCP server <domain>"
     b. Check GitHub for MCP server implementations
     c. Evaluate server quality (stars, maintenance, tool count)
  5. Connect best match via stdio or HTTP
  6. List available tools via ListMcpResourcesTool
  7. Use ReadMcpResourceTool to understand capabilities
```

### MCP Connection Configuration

```json
// .claude/mcp.json
{
  "mcpServers": {
    "firecrawl": {
      "command": "npx",
      "args": ["-y", "firecrawl-mcp"],
      "env": {
        "FIRECRAWL_API_KEY": "${FIRECRAWL_API_KEY}"
      }
    },
    "mem0": {
      "command": "python",
      "args": ["-m", "mem0.mcp_server"],
      "env": {
        "MEM0_API_KEY": "${MEM0_API_KEY}"
      }
    }
  }
}
```

---

## 5. LAYER 3: TOOL SEARCH & DEFERRED DISCOVERY

### How ToolSearch Works

From `toolSearch.ts`, ToolSearch enables **dynamic discovery of deferred tools** to save context window tokens.

### Tool Search Modes

| Mode | Env Value | Behavior |
|------|-----------|----------|
| `tst` | `true`, `auto:0`, or unset | Always defer MCP and shouldDefer tools |
| `tst-auto` | `auto` or `auto:1-99` | Defer only when tools exceed threshold |
| `standard` | `false`, `auto:100` | No deferral — all tools inline |

### Deferred Tool Detection

```typescript
isDeferredTool(tool):
  1. If tool.alwaysLoad === true → NOT deferred
  2. If tool.isMcp === true → deferred
  3. If tool.name === TOOL_SEARCH_TOOL_NAME → NOT deferred
  4. If FORK_SUBAGENT enabled AND tool.name === AGENT_TOOL_NAME → NOT deferred
  5. If tool.name === BRIEF_TOOL_NAME → NOT deferred
  6. If tool.name === SEND_USER_FILE_TOOL_NAME → NOT deferred
  7. If tool.shouldDefer === true → deferred
```

### ToolSearch Query Forms

| Form | Example | Behavior |
|------|---------|----------|
| Direct select | `select:Tool1,Tool2` | Returns exact tools by name |
| Keyword search | `web scraping browser` | Ranked match against tool names, searchHints, descriptions |
| Required term | `+required term` | Only tools containing the required term |

### Scoring Algorithm

```
Score = exact part match (10-12pts)
      + substring match (5-6pts)
      + searchHint match (4pts)
      + description match (2pts)
```

### How ToolSearch Handles Unknown Tools

When the agent encounters an unknown task:

1. **Model decides** it needs a tool it doesn't know about
2. **Calls ToolSearchTool** with a keyword query derived from the task
3. **ToolSearchTool** searches all deferred tools (MCP tools, shouldDefer tools)
4. **Returns tool_reference blocks** with full schemas
5. **API expands** tool_reference blocks into full tool definitions
6. **Model can now call** the discovered tool

### Schema-Not-Sent Detection

If a deferred tool is called without its schema being sent:

```
buildSchemaNotSentHint(tool, messages, tools):
  1. If tool search not enabled → null
  2. If ToolSearchTool not available → null
  3. If tool is not deferred → null
  4. If tool name in discovered tools → null
  5. Otherwise → hint telling model to use ToolSearchTool first
```

### Tools with `shouldDefer: true`

- WebFetchTool
- WebSearchTool
- TodoWriteTool
- TaskStopTool
- All MCP tools (by default)

---

## 6. LAYER 4: RESEARCH & FORKED AGENTS

### Forked Agent Architecture

From the AgentTool implementation, forked agents are the **research engine** for unknown tasks:

```
Forked Agent Properties:
  - Inherits parent's cache-safe params (system, tools, model)
  - Has its own agentId for state isolation
  - Cannot fork again (recursive fork guard)
  - Runs with limited tool set (no AskUserQuestion, no Agent)
  - Returns results to parent via structured output
```

### Recursive Fork Guard

```typescript
if (isForkPath && toolUseContext.agentId) {
  return {
    data: { status: 'error', error:
      'Fork is not available inside a forked worker. Complete your task directly using your tools.'
    }
  }
}
```

### Research Agent Pattern

For unknown tasks, the agent spawns research sub-agents:

```
ALGORITHM: ResearchUnknownTask(task):
  1. Decompose task into research questions
  2. For each question:
     a. Fork an Explore agent (read-only research)
     b. Agent uses WebSearch, WebFetch, Glob, Grep
     c. Agent returns structured findings
  3. Synthesize findings from all agents
  4. Determine best approach based on research
  5. Execute using discovered tools/approaches
```

### Agent Types for Research

| Agent Type | Purpose | Tool Set | Best For |
|------------|---------|----------|----------|
| **Explore** | Read-only research | Read, Grep, Glob, WebSearch, WebFetch | Understanding codebases, finding patterns |
| **Plan** | Architecture planning | Read, Grep, Glob, WebSearch | Designing solutions, evaluating options |
| **general-purpose** | Full capability | All async agent tools | Implementation, debugging |
| **verification** | Adversarial testing | Read, Grep, Glob, Bash | Finding flaws, testing assumptions |

### Parallel Research Strategy

```
ALGORITHM: ParallelResearch(task):
  1. Identify independent research questions
  2. Spawn N Explore agents in parallel (up to CLAUDE_CODE_MAX_TOOL_USE_CONCURRENCY)
  3. Each agent researches one question independently
  4. Collect and synthesize results
  5. Identify gaps → spawn follow-up agents if needed
```

### Concurrency Safety for Research

Research agents use only concurrency-safe tools:
- FileReadTool (always safe)
- GlobTool (always safe)
- GrepTool (always safe)
- WebFetchTool (always safe)
- WebSearchTool (always safe)

This allows maximum parallelism during the research phase.

---

## 7. LAYER 5: ADAPTATION & SUBSTITUTION

### The Adaptation Layer

From `adaptation_layer.py` in the workflow engine:

### 8 Adaptation Types

| Type | Trigger | Action |
|------|---------|--------|
| **Capability substitution** | Tool/server unavailable | Find alternative capability with similar output |
| **Phase merge** | Task simpler than expected | Combine workflow phases |
| **Phase split** | Task more complex than expected | Break phase into sub-phases |
| **Timeout adjustment** | Execution taking longer | Increase/decrease timeout |
| **Retry adjustment** | Repeated failures | Change retry count |
| **Parallelism change** | High error rate | Reduce parallelism |
| **Workflow switch** | Persistent failures | Switch to simpler workflow |
| **Context enrichment** | Successful outputs | Add outputs to context for next phases |

### Capability Substitution Algorithm

```
ALGORITHM: SubstituteCapability(failed_capability, context):
  1. Get failed capability's outputs and dependencies
  2. Query registry for alternatives with matching output types
  3. Filter by availability (installed, connected, enabled)
  4. Rank by:
     - Output similarity (exact match > partial > different format)
     - Cost (cheaper preferred)
     - Reliability (historical success rate)
  5. Return best alternative or null if none found
```

### Substitution Examples

| Failed Capability | Substitution | Trade-off |
|-------------------|-------------|-----------|
| Playwright MCP | Selenium + stealth plugins | Slower but works |
| Firecrawl MCP | WebFetch + manual parsing | Less structured output |
| GitHub MCP | Bash(git:*) commands | More manual work |
| PostgreSQL MCP | Bash(psql:*) commands | Less convenient |
| Google Apps Script MCP | WebFetch + manual API calls | More complex auth |

### Adaptation Triggers

The adaptation layer monitors execution and triggers adaptations based on:

```
TRIGGER CONDITIONS:
  - Tool call fails with "tool not found" → capability substitution
  - Tool call fails with "connection refused" → MCP reconnection or substitution
  - Tool call times out → timeout adjustment or parallelism reduction
  - 3+ consecutive failures → workflow switch
  - Context window pressure → phase merge or compaction
  - User provides new constraints → workflow recomposition
```

---

## 8. LAYER 6: SESSION MEMORY & KNOWLEDGE ACCUMULATION

### Memory Systems

The system has multiple memory layers that accumulate knowledge:

### 1. Session Memory

From `sessionMemory.ts`:
- Per-session running summary of the conversation
- Updated via forked agent when token/tool-call thresholds met
- Used for compaction and context preservation
- GrowthBook flag: `tengu_session_memory`

### 2. Auto-Memory (Durable Memory)

From `extractMemories.ts`:
- Extracts durable memories from session transcript
- Writes to `~/.claude/projects/<path>/memory/`
- Runs at end of each complete query loop
- GrowthBook flag: `tengu_passport_quail`

### 3. Team Memory

From `teamMemorySync/index.ts`:
- Shared across team members (per-repo, identified by git remote hash)
- Syncs between local filesystem and server API
- Pull: server wins per-key
- Push: delta upload (only changed content hashes)
- Requires OAuth authentication

### 4. Memory Directory System

From `memdir/paths.ts`:
- Organized memory files per project path
- Scanned for relevant memories at session start
- GrowthBook flag: `tengu_coral_fern`

### How Memory Accumulates Knowledge About New Domains

```
ALGORITHM: AccumulateDomainKnowledge(task, findings):
  1. Extract domain from task classification
  2. For each finding:
     a. Create memory entry with:
        - domain: identified domain
        - technique: what was learned
        - tools: which tools worked
        - mcp_servers: which servers were useful
        - confidence: how reliable the finding is
        - timestamp: when learned
     b. Write to auto-memory directory
  3. On next session with same domain:
     a. Scan memory directory for matching entries
     b. Inject relevant memories into context
     c. Agent starts with prior knowledge
```

### Skill Creation from Learned Knowledge

The skill creation process captures session knowledge into reusable skills:

```
Skill Creation Process (4-round interview):
  1. Confirm: What process should be captured?
  2. Details: What are the key steps and decisions?
  3. Step breakdown: Detailed procedure with conditions
  4. Final: Generate complete SKILL.md with frontmatter
```

### Memory Promotion

The `/remember` skill reviews auto-memory entries and proposes promotions:
- Detect duplicates
- Identify outdated entries
- Find conflicts
- Promote to CLAUDE.md or CLAUDE.local.md

---

## 9. LAYER 7: FALLBACK CHAINS

### When Everything Else Fails

The fallback chain ensures the agent always provides value:

```
FALLBACK HIERARCHY:
  1. Primary approach (best tool/server for the task)
  2. Alternative approach (substituted capability)
  3. Manual approach (bash commands, direct API calls)
  4. Research approach (find documentation, create plan)
  5. Partial approach (do what's possible, explain gaps)
  6. Explanation approach (explain what would be needed)
```

### Graceful Degradation Patterns

| Scenario | Fallback |
|----------|----------|
| No MCP server available | Use WebSearch to find alternatives, then bash commands |
| Tool not found | ToolSearch to discover, or use equivalent bash command |
| API rate limited | Retry with backoff, or use cached data |
| Context overflow | Compact, then continue with summary |
| Agent timeout | Reduce parallelism, retry sequentially |
| Permission denied | Explain what's needed, ask user to approve |
| Network unavailable | Use local tools only, explain limitations |

### Error Recovery via Hooks

PostToolUseFailure hooks provide structured error recovery:

```
PostToolUseFailure Hook Flow:
  1. Tool execution fails
  2. Hook analyzes error type
  3. Hook can:
     - Add context messages explaining the failure
     - Block continuation if error is critical
     - Suggest alternative approaches
  4. Agent receives failure context and adapts
```

### The "Stuck" Detection System

From the `stuck` skill:
- Detects when the agent is making no progress
- Scans for repeated patterns, circular reasoning
- Posts diagnostic report
- Suggests alternative approaches

---

## 10. SPECIFIC TASK PATTERNS

### Pattern 1: Web Scraping

**Task:** "Scrape product data from an e-commerce site"

```
LAYER 1 (Skills):
  → Check for web-scraper skill in .claude/skills/
  → If found, follow skill instructions

LAYER 2 (MCP):
  → Search for scraping MCP servers:
    - firecrawl-mcp (best for structured extraction)
    - playwright-mcp (best for dynamic JS pages)
    - jina-reader-mcp (best for clean markdown)
  → Connect best match
  → List available tools
  → Execute scrape

LAYER 3 (ToolSearch):
  → Query: "scrape web browser extract"
  → Discover deferred tools matching the query
  → Use discovered tools

LAYER 4 (Research):
  → Fork Explore agent to research:
    - "best web scraping techniques 2026"
    - "how to bypass Cloudflare scraping"
    - "MCP servers for web scraping"
  → Synthesize findings

LAYER 5 (Adaptation):
  → If firecrawl fails → try playwright
  → If playwright fails → try selenium
  → If all fail → use curl + regex parsing

LAYER 6 (Memory):
  → Store which servers worked for this domain
  → Create memory entry: "scraping ecommerce sites"
  → Note anti-bot measures encountered

LAYER 7 (Fallback):
  → If nothing works: provide manual curl commands
  → Explain what tools would be needed
  → Create a scraping plan for the user
```

**MCP Servers for Web Scraping:**

| Server | Best For | Setup |
|--------|----------|-------|
| firecrawl | Structured data extraction | `npx -y firecrawl-mcp` |
| playwright | Dynamic JS rendering | `npx -y @anthropic/mcp-playwright` |
| jina-reader | Clean markdown from URLs | HTTP with API key |
| puppeteer | Headless browser control | `npx -y @modelcontextprotocol/server-puppeteer` |
| selenium | Legacy browser automation | Python + selenium |

---

### Pattern 2: Google Apps Script

**Task:** "Create a Google Apps Script that auto-replies to Gmail"

```
LAYER 1 (Skills):
  → Check for google-apps-script skill
  → If found, follow instructions

LAYER 2 (MCP):
  → Search for Google Workspace MCP servers:
    - google-workspace-mcp (Gmail, Sheets, Docs)
    - gmail-mcp (email-specific)
    - google-apps-script-mcp (script deployment)
  → Connect Google Workspace MCP
  → Authenticate via OAuth
  → Use tools to create and deploy script

LAYER 3 (ToolSearch):
  → Query: "google apps script gmail"
  → Discover any deferred Google-related tools

LAYER 4 (Research):
  → Fork Explore agent:
    - "Google Apps Script Gmail auto-reply tutorial"
    - "Google Apps Script MCP server"
    - "Gmail API Apps Script examples"
  → Fork Plan agent:
    - Design the script architecture
  → Synthesize: create script from research

LAYER 5 (Adaptation):
  → If no Google MCP → use Gmail REST API directly
  → If API auth fails → provide manual setup instructions
  → If deployment fails → provide step-by-step guide

LAYER 6 (Memory):
  → Store Google Apps Script patterns learned
  → Note OAuth setup steps for future
  → Record which API endpoints worked

LAYER 7 (Fallback):
  → Provide raw Apps Script code
  → Give manual deployment instructions
  → Link to Google Apps Script documentation
```

**MCP Servers for Google Apps Script:**

| Server | Purpose | Setup |
|--------|---------|-------|
| google-workspace-mcp | Full G Suite access | OAuth + service account |
| gmail-mcp | Email operations | OAuth |
| google-sheets-mcp | Spreadsheet operations | OAuth |
| google-drive-mcp | File management | OAuth |
| google-apps-script-mcp | Script deployment | OAuth + Apps Script API |

---

### Pattern 3: Research Tasks

**Task:** "Research the best approach to implement real-time collaboration"

```
LAYER 1 (Skills):
  → Check for research skill
  → If found, use research methodology

LAYER 2 (MCP):
  → Search for research-oriented MCP servers:
    - academic-search-mcp (papers)
    - arxiv-mcp (preprints)
    - semantic-scholar-mcp (research database)
  → Connect if available

LAYER 3 (ToolSearch):
  → Query: "research papers search academic"
  → Discover research tools

LAYER 4 (Research):
  → Fork 3+ Explore agents in parallel:
    Agent 1: "CRDT vs OT for real-time collaboration"
    Agent 2: "WebSocket vs WebRTC for real-time sync"
    Agent 3: "existing real-time collaboration libraries 2026"
  → Fork Plan agent: synthesize and recommend
  → Generate comprehensive research report

LAYER 5 (Adaptation):
  → If academic MCP unavailable → use WebSearch + WebFetch
  → If papers are paywalled → find open access alternatives
  → If too many results → narrow scope with additional agents

LAYER 6 (Memory):
  → Store research findings in auto-memory
  → Create "real-time collaboration" knowledge base
  → Link to key papers and libraries

LAYER 7 (Fallback):
  → Provide best-known approaches from training
  → Acknowledge knowledge cutoff
  → Suggest where to find latest information
```

**MCP Servers for Research:**

| Server | Purpose | Setup |
|--------|---------|-------|
| semantic-scholar | Academic paper search | HTTP, free API |
| arxiv | Preprint search | HTTP, free |
| pubmed | Medical literature | HTTP, free |
| crossref | DOI/metadata lookup | HTTP, free |
| exa | Web search with content extraction | HTTP, API key |

---

### Pattern 4: Learning Roadmaps

**Task:** "Create a learning roadmap for Rust systems programming"

```
LAYER 1 (Skills):
  → Check for learning-roadmap skill
  → If found, use structured approach

LAYER 2 (MCP):
  → Search for education MCP servers:
    - curriculum-mcp
    - learning-path-mcp
  → Connect if available

LAYER 3 (ToolSearch):
  → Query: "learning roadmap curriculum"
  → Discover education-related tools

LAYER 4 (Research):
  → Fork Explore agents:
    Agent 1: "Rust systems programming learning path"
    Agent 2: "best Rust books and courses 2026"
    Agent 3: "Rust projects for learning progression"
  → Fork Plan agent: structure the roadmap
  → Generate progressive curriculum

LAYER 5 (Adaptation):
  → If no education MCP → use WebSearch for resources
  → If too many resources → filter by quality metrics
  → If outdated resources → find recent alternatives

LAYER 6 (Memory):
  → Store the generated roadmap
  → Note resource quality ratings
  → Track learning progression patterns

LAYER 7 (Fallback):
  → Provide general learning methodology
  → Suggest starting points
  → Create a self-study framework
```

---

### Pattern 5: Research Paper to Code

**Task:** "Implement the attention mechanism from this paper: [URL]"

```
LAYER 1 (Skills):
  → Check for paper-implementation skill
  → If found, follow methodology

LAYER 2 (MCP):
  → Search for academic MCP servers:
    - paper-reader-mcp (PDF parsing)
    - arxiv-mcp (paper access)
  → Connect paper-reader if available

LAYER 3 (ToolSearch):
  → Query: "paper pdf parse extract code"
  → Discover paper processing tools

LAYER 4 (Research):
  → Fork Explore agent: fetch and parse the paper
  → Fork Plan agent: design implementation architecture
  → Fork general-purpose agent: implement the code
  → Fork verification agent: test the implementation
  → Synthesize: paper → design → code → tests

LAYER 5 (Adaptation):
  → If paper is paywalled → find preprint version
  → If math is unclear → research supplementary materials
  → If implementation too complex → break into phases

LAYER 6 (Memory):
  → Store paper implementation patterns
  → Note which approaches worked
  → Link paper to implementation

LAYER 7 (Fallback):
  → Explain the paper's key concepts
  → Provide pseudocode
  → Point to existing implementations
```

---

### Pattern 6: Code Visualization

**Task:** "Create an interactive visualization of this algorithm's execution"

```
LAYER 1 (Skills):
  → Check for visualization skill
  → If found, follow visualization guidelines

LAYER 2 (MCP):
  → Search for visualization MCP servers:
    - mermaid-mcp (diagrams)
    - d3-mcp (interactive charts)
    - plotly-mcp (data visualization)
  → Connect best match

LAYER 3 (ToolSearch):
  → Query: "visualization chart diagram interactive"
  → Discover visualization tools

LAYER 4 (Research):
  → Fork Explore agent: "best JS visualization libraries 2026"
  → Fork Plan agent: design the visualization
  → Fork general-purpose agent: implement
  → Fork verification agent: test rendering

LAYER 5 (Adaptation):
  → If D3 too complex → use Chart.js
  → If interactive not possible → create static SVG
  → If web not available → create terminal ASCII art

LAYER 6 (Memory):
  → Store visualization techniques learned
  → Note which libraries work best for which data types
  → Record implementation patterns

LAYER 7 (Fallback):
  → Create ASCII diagram
  → Describe the visualization in text
  → Provide code for user to render themselves
```

---

### Pattern 7: Any Unknown Task (General Pattern)

**Task:** [Anything the agent has never seen before]

```
ALGORITHM: HandleUnknownTask(task):
  // PHASE 1: Assess
  1. Classify the task (domain, complexity, type)
     → Use task_classifier.py patterns
     → Identify what's known vs unknown

  // PHASE 2: Check Known Capabilities
  2. Check skills directory for matching skills
     → Found? Execute skill
     → Not found? Continue

  3. Check installed MCP servers for relevant tools
     → Found? Use MCP tools
     → Not found? Continue

  4. Use ToolSearch for deferred tools
     → Found? Use discovered tools
     → Not found? Continue

  // PHASE 3: Research
  5. Fork Explore agents to research the domain
     → Parallel research of key questions
     → Synthesize findings

  6. Fork Plan agent to design approach
     → Based on research findings
     → Create implementation plan

  // PHASE 4: Execute
  7. Execute using discovered tools/approaches
     → Monitor for failures
     → Adapt as needed

  // PHASE 5: Learn
  8. Store knowledge gained
     → Create memory entries
     → Optionally create new skill
     → Update domain knowledge base

  // PHASE 6: Report
  9. Report results and limitations
     → What was accomplished
     → What couldn't be done
     → What would be needed for full solution
```

---

## 11. THE COMPLETE FLOW

### End-to-End Example: "Build a Slack bot that summarizes daily standups"

```
TURN 1: User Request
  User: "Build a Slack bot that summarizes daily standups"

TURN 2: Layer 1 — Skill Check
  Agent: Checks .claude/skills/ for "slack" or "bot" skills
  Result: No matching skills found

TURN 3: Layer 2 — MCP Server Search
  Agent: Checks installed MCP servers
  Result: No Slack MCP server connected
  Agent: Searches for Slack MCP servers
  Found: @modelcontextprotocol/server-slack (stdio)
  Agent: Connects Slack MCP server
  Result: Connected! Tools available: slack_post_message, slack_list_channels, slack_get_messages

TURN 4: Layer 3 — ToolSearch
  Agent: Queries ToolSearch for "summarize text meeting"
  Result: Found WebSearch, WebFetch (for research)

TURN 5: Layer 4 — Research
  Agent: Forks 2 Explore agents:
    Agent A: "Slack bot architecture best practices 2026"
    Agent B: "How to summarize standup messages in Slack"
  Agent: Forks Plan agent: "Design Slack standup summarizer bot"

TURN 6: Synthesis
  Agent: Combines research findings:
    - Use Slack MCP for message operations
    - Use cron scheduling for daily triggers
    - Summarization via LLM API call
    - Store summaries in a file or database

TURN 7: Execution
  Agent: Implements the bot:
    1. Creates bot script (FileWriteTool)
    2. Sets up cron trigger (ScheduleCronTool)
    3. Tests with Slack MCP tools
    4. Verifies functionality (verification agent)

TURN 8: Layer 6 — Memory Storage
  Agent: Creates memory entries:
    - "Slack bot development patterns"
    - "Standup summarization approach"
    - "Slack MCP server capabilities"

TURN 9: Layer 6 — Skill Creation
  Agent: Creates slack-bot-builder skill:
    ---
    name: slack-bot-builder
    description: Build Slack bots with MCP integration
    allowed-tools: [Bash, FileWrite, Skill, WebSearch]
    ---
    # Slack Bot Builder
    ...

NEXT TIME: Same Domain
  User: "Build a Slack bot for code review notifications"
  Agent: Finds slack-bot-builder skill → uses it immediately
  Agent: Recalls Slack MCP connection → reconnects
  Agent: Much faster execution (no research needed)
```

### The Learning Loop

```
First encounter with domain:
  Skills: ❌ → MCP: ❌ → ToolSearch: ❌ → Research: ✅ → Execute → Learn → Store

Second encounter with domain:
  Skills: ✅ (created last time) → Execute immediately

This is the key insight: the system GETS SMARTER over time.
```

---

## 12. MCP SERVER DISCOVERY ALGORITHM

### Complete Discovery Algorithm

```
ALGORITHM: DiscoverAndConnectMCPServer(task_domain):
  // Step 1: Check existing connections
  connected_servers = ListMcpResources()
  FOR server IN connected_servers:
    IF server.domain MATCHES task_domain:
      RETURN server

  // Step 2: Check local MCP configs
  configs = LoadMCPConfigs()  // enterprise, user, project, local, dynamic
  FOR config IN configs:
    IF config.domain MATCHES task_domain:
      Connect(config)
      RETURN config

  // Step 3: Search MCP marketplace
  marketplace_results = WebSearch("MCP server <task_domain>")
  FOR result IN marketplace_results:
    Evaluate server:
      - GitHub stars / downloads
      - Last update date
      - Tool count and quality
      - Transport type compatibility
    IF server looks good:
      Download and install
      Connect server
      RETURN server

  // Step 4: Check plugin registry
  plugins = DiscoverPlugins()
  FOR plugin IN plugins:
    IF plugin.provides_mcp AND plugin.domain MATCHES task_domain:
      Install plugin
      Connect MCP server from plugin
      RETURN server

  // Step 5: Manual setup
  IF no server found:
    Research: "how to build MCP server for <task_domain>"
    Provide user with setup instructions
    RETURN null
```

### MCP Server Evaluation Criteria

| Criterion | Weight | How to Evaluate |
|-----------|--------|-----------------|
| Tool relevance | 40% | Do the tools match the task? |
| Maintenance | 20% | Last commit, issue response time |
| Popularity | 15% | GitHub stars, npm downloads |
| Documentation | 15% | README quality, examples |
| Security | 10% | OAuth support, permission model |

### MCP Connection Lifecycle

```
Connection Lifecycle:
  1. LOAD: Parse config from all scopes
  2. DEDUP: Prevent duplicate connections by signature
  3. CONNECT: Establish transport (stdio/HTTP/SSE/WS)
  4. INITIALIZE: Send initialize request, get server info
  5. DISCOVER: List tools, resources, prompts
  6. USE: Call tools as needed via ToolSearch
  7. MONITOR: Watch for connection drops
  8. RECONNECT: Exponential backoff on failure (5 attempts, 1s-30s)
  9. DISCONNECT: Clean shutdown when done
```

---

## 13. PLUGIN SYSTEM DYNAMICS

### Plugin Loading

From `pluginLoader.ts`:

```
Plugin Loading Pipeline:
  1. Discover plugin directories:
     - Bundled plugins (shipped with Claude Code)
     - User-installed plugins (~/.claude/plugins/)
     - Project plugins (.claude/plugins/)
     - Marketplace plugins (downloaded)

  2. For each plugin:
     a. Parse plugin manifest (plugin.json)
     b. Validate signature and trust level
     c. Load components:
        - MCP servers
        - LSP servers
        - Skills/commands
        - Agents
        - Hooks
     d. Resolve dependencies
     e. Initialize plugin

  3. Deduplicate components by name
  4. Apply policy filters (allowlist/denylist)
  5. Register all components with the runtime
```

### Plugin Components

| Component | Purpose | Discovery |
|-----------|---------|-----------|
| MCP servers | External tool integration | Plugin manifest |
| LSP servers | Language intelligence | Plugin manifest |
| Skills | Task-specific instructions | .claude/skills/ in plugin |
| Agents | Specialized sub-agents | .claude/agents/ in plugin |
| Hooks | Event interception | Plugin manifest |

### Plugin-Plugin Communication

Plugins can communicate through:
1. **Shared MCP servers** — multiple plugins can use the same server
2. **Hook chaining** — PostToolUse hooks from different plugins chain
3. **Skill references** — skills can reference other skills across plugins

---

## 14. EDGE CASE HANDLING

### Edge Case 1: MCP Server Crashes Mid-Task

```
Detection: Tool call fails with "connection reset" or "process terminated"
Response:
  1. Attempt reconnection (exponential backoff, 5 attempts)
  2. If reconnection fails → capability substitution
  3. Log the failure for future reference
  4. Continue with alternative approach
```

### Edge Case 2: ToolSearch Returns No Results

```
Detection: ToolSearch query returns empty result set
Response:
  1. Broaden the query (remove specific terms)
  2. Try synonym queries
  3. If still empty → fall back to research agents
  4. Research agents may discover tools to install
```

### Edge Case 3: All Research Agents Return Conflicting Information

```
Detection: Synthesis step finds contradictions
Response:
  1. Identify the contradiction points
  2. Fork verification agent to resolve conflicts
  3. Use confidence scoring (source quality, recency)
  4. Present both options with tradeoffs to user
```

### Edge Case 4: Context Window Overflow During Research

```
Detection: Token count approaches context limit
Response:
  1. Trigger microcompact to clear old tool results
  2. If still over limit → partial compact (summarize old messages)
  3. Preserve research findings in memory before compacting
  4. Continue with compacted context
```

### Edge Case 5: Skill Has Wrong Information (Outdated)

```
Detection: Skill instructions reference deprecated tools/APIs
Response:
  1. Follow skill instructions but verify each step
  2. If verification fails → research current approach
  3. Update the skill with new information
  4. Store correction in memory
```

### Edge Case 6: Forked Agent Gets Stuck

```
Detection: Agent exceeds timeout or enters loop
Response:
  1. Abort the forked agent
  2. Analyze what went wrong
  3. Try with different approach or narrower scope
  4. If persistent → handle directly in main thread
```

### Edge Case 7: User Interrupts Mid-Research

```
Detection: User sends new message while agents are running
Response:
  1. Abort running research agents (sibling error cascade)
  2. Preserve any completed research
  3. Address user's new request
  4. Resume research if still relevant
```

### Edge Case 8: No Network Access

```
Detection: WebSearch, WebFetch, and MCP connections all fail
Response:
  1. Fall back to local tools only (Read, Grep, Glob, Bash)
  2. Use training knowledge for the domain
  3. Check local memory for prior knowledge
  4. Explain what network access would enable
```

---

## SUMMARY: THE UNKNOWN TASK HANDLING MATRIX

| Layer | Mechanism | Cost | Speed | Coverage |
|-------|-----------|------|-------|----------|
| 1. Skills | Check skill files | Free | Instant | Low (only pre-written skills) |
| 2. MCP | Connect servers | Low | Fast | Medium (depends on ecosystem) |
| 3. ToolSearch | Discover deferred tools | Free | Fast | Medium (only installed tools) |
| 4. Research | Fork agents | High | Slow | High (can learn anything) |
| 5. Adaptation | Substitute capabilities | Medium | Medium | High (always has alternatives) |
| 6. Memory | Store & recall | Free | Instant | Grows over time |
| 7. Fallback | Graceful degradation | Low | Fast | Always provides SOMETHING |

### The Golden Rule

> **Every unknown task is just a known task waiting to be discovered, researched, and remembered.**

The system transforms unknown tasks into known tasks through:
1. **Discovery** (find the right tools/servers)
2. **Research** (learn what you don't know)
3. **Execution** (do the task with discovered capabilities)
4. **Memory** (remember for next time)

After the first encounter, the task moves from "unknown" to "known" via skills and memory. The second encounter is always faster than the first.
