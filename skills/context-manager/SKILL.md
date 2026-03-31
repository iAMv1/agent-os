---
name: context-manager
description: Use when working on complex tasks that require tracking multiple pieces of information, maintaining state across sessions, or managing attention across parallel work streams.
when_to_use: Working on large projects, managing multiple tasks simultaneously, switching between contexts, or when you need to maintain awareness of the big picture while working on details.
allowed-tools:
  - Read
  - Write
  - Edit
  - TodoWrite
  - Glob
  - Grep
arguments:
  - scope
  - mode
argument-hint: "[project-or-task] [track|restore|summarize|switch]"
---

# Context Manager

Maintain awareness, track state, and manage attention across complex work. Never lose the thread.

<HARD-GATE>
Do NOT start new work without documenting the current state of existing work. Do NOT switch contexts without saving a restoration point.
</HARD-GATE>

## The Iron Law

Every context switch must have a restoration point — enough information to pick up exactly where you left off.

## When to Use

- Working on large, multi-phase projects
- Managing multiple tasks or work streams
- Switching between different types of work
- When you need to maintain awareness of the big picture
- After interruptions or breaks in work

## When NOT to Use

- Single-task work with no context switching
- Trivial tasks that don't require state tracking
- When the work fits entirely in working memory

## The Process

### Phase 1: Capture Current State

1. **Document what you're working on**
   ```
   Context Snapshot:
   ├── Current Task: [what you're doing right now]
   ├── Progress: [what's done, what's next]
   ├── Open Questions: [unresolved items]
   ├── Decisions Made: [key decisions and rationale]
   ├── Files Modified: [what's changed]
   ├── Dependencies: [what you're waiting on]
   └── Next Action: [the very next thing to do]
   ```

2. **Track open loops**
   - What's started but not finished?
   - What questions need answers?
   - What decisions are pending?

### Phase 2: Manage Attention

3. **Prioritize work streams**
   ```
   Attention Map:
   ├── Active: [what you're working on now]
   ├── Pending: [what's next]
   ├── Blocked: [what's waiting on something]
   └── Backlog: [what could be done later]
   ```

4. **Set context boundaries**
   - What's in scope for this session?
   - What's explicitly out of scope?
   - What's the time budget?

### Phase 3: Context Switching

5. **Save restoration point**
   Before switching to a different task:
   - Document current state (Phase 1)
   - Note where you left off
   - List what you need to resume

6. **Load new context**
   When starting a different task:
   - Review the restoration point
   - Re-establish mental model
   - Confirm the next action

7. **Return to saved context**
   When returning to a previous task:
   - Read the restoration point
   - Verify nothing has changed
   - Resume from the documented next action

### Phase 4: Big Picture Maintenance

8. **Regular context reviews**
   - Every 30-60 minutes: review progress
   - Every session start: review open loops
   - Every session end: save restoration point

9. **Maintain the project map**
   ```
   Project Map:
   ├── Goal: [what we're building]
   ├── Current Phase: [where we are]
   ├── Completed: [what's done]
   ├── In Progress: [what's happening now]
   ├── Next: [what's coming]
   └── Risks: [what could go wrong]
   ```

## Context Management Tools

| Tool | Purpose | When to Use |
|------|---------|-------------|
| **TodoWrite** | Track tasks and status | Always |
| **Context Snapshot** | Save state before switching | Before any context switch |
| **Project Map** | Maintain big picture | Every session start/end |
| **Open Loops List** | Track unresolved items | When questions arise |
| **Decision Log** | Record decisions and rationale | When making decisions |

## Integration

Related skills: `strategic-planning`, `problem-decomposition`, `quality-assurance`
