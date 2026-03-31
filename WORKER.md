# WORKER.md — AgentOS Project Instructions

<!-- STATIC-CONTENT-BOUNDARY -->

## What Is AgentOS

AgentOS is a universal AI agent operating system that combines:
1. **Ralph Loop** — Iterative self-improvement
2. **Superpowers** — Quality enforcement
3. **Adaptive Workflow** — Dynamic task handling

See `README.md` for full documentation.

<!-- Everything below this line is dynamic and rebuilt per session. -->

## Operating Instructions

### 1. Live Repo Context

At session start, always load:
- **Git state**: Check current branch, recent commits, uncommitted changes
- **File changes**: Track what's been modified since last interaction
- **Project structure**: Use Glob and Grep (not Bash) for file discovery
- **Session memory**: Read `.agent-os/memory/session-memory.md` at session start
- **Session state**: Read `.agent-os/session/current-state.md` for ongoing context

### 2. Aggressive Prompt Cache Reuse

**Static/dynamic content boundary:**
- Everything above `<!-- STATIC-CONTENT-BOUNDARY -->` is static — globally cached
- Everything below is dynamic — rebuilt per session
- Keep static content above the boundary, dynamic content below

### 3. Tool Usage Priority

| Instead of Bash(...) | Use | Why |
|---------------------|-----|-----|
| `grep`, `rg` | `Grep` | Better permission handling, structured results |
| `find`, `ls` | `Glob` | Faster, structured file discovery |
| `cat`, `head`, `tail` | `Read` | Proper encoding handling, range support |
| `sed`, `awk` | `Edit` | SEARCH/REPLACE blocks, safer mutations |
| `echo >`, `cat <<EOF` | `Write` | Proper file creation |

### 4. Minimizing Context Bloat

**File-read deduplication:**
- Check `.agent-os/cache/file-hashes.json` before reading any file
- If file hash matches cached hash, skip re-reading
- Update hash after any file modification

**Large output handling:**
- If tool output > 2000 lines or > 50KB, write to disk
- Return first 50 lines + line count + file path reference
- Never dump massive outputs directly into context

**Autocompaction:**
- Trigger `/compact` when context grows large
- Before compacting: summarize key findings to session memory

### 5. Structured Session Memory

Maintain structured session memory at `.agent-os/memory/session-memory.md`:

```markdown
# Session Memory

## Session Title
[Brief description]

## Current State
[What's happening right now]

## Task Specification
[What we're working on]

## Files and Functions
[Key files being modified]

## Workflow
[Current workflow phase]

## Errors & Corrections
[Mistakes made and fixes]

## Learnings
[Insights and discoveries]

## Key Results
[What's been accomplished]

## Worklog
[Chronological record of work done]
```

### 6. Forks and Subagents

**Use subagents/forks for:**
- Independent research tasks
- Parallel file analysis
- Background summarization
- Memory extraction
- Verification tasks

**Rules:**
- Dispatch independent tasks in parallel, not sequentially
- Fork agents reuse parent's cache
- Don't contaminate main agent loop with side work

### 7. Quality Standards

**Before completing any task:**
1. Verify the work is correct
2. Check for edge cases
3. Ensure no regressions
4. Update session memory
5. Document what was done

**Anti-slop rules:**
- No vague statements without evidence
- No "looks good" without verification
- No skipping steps in established processes
- No assuming facts without checking
