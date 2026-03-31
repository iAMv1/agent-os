---
name: task-decomposer
description: Use after prompt-enhancer to break any enhanced task specification into phases, parallel subagents, and execution plan. Automatically divides work across independent subagents for maximum parallelism.
when_to_use: After a task has been clarified by prompt-enhancer. Before any execution begins. When you need to plan how a complex task will be executed with parallel subagents.
allowed-tools:
  - Read
  - Write
  - Edit
  - TodoWrite
  - Glob
  - Grep
  - Bash
arguments:
  - spec
  - mode
argument-hint: "[enhanced-task-spec] [fast|balanced|thorough]"
---

# Task Decomposer

Break any enhanced task specification into phases, parallel subagents, and an execution plan. Automatically maximizes parallelism.

<HARD-GATE>
Do NOT start execution until the decomposition is complete. Do NOT create subagents that share mutable state. Do NOT skip dependency mapping between phases.
</HARD-GATE>

## The Iron Law

Every task must be decomposed into independently executable phases with explicit dependencies before any work begins.

## When to Use

- After prompt-enhancer produces an enhanced task specification
- Before executing any multi-step task
- When a task can benefit from parallel subagent execution
- When you need to plan complex work

## When NOT to Use

- Trivial single-step tasks
- Tasks already decomposed by a previous run

## The Process

### Phase 1: Analyze Dependencies

1. **Identify work units**
   - What are the distinct pieces of work?
   - Which pieces depend on others?
   - Which pieces are independent?

2. **Build dependency graph**
   ```
   Work Unit A (no dependencies)
   ├── Work Unit B (depends on A)
   ├── Work Unit C (depends on A)
   └── Work Unit D (depends on B, C)
   ```

### Phase 2: Design Parallel Execution

3. **Group into parallel phases**
   ```
   Phase 1: [A] — Run in parallel (no dependencies)
   Phase 2: [B, C] — Run in parallel (both depend on A)
   Phase 3: [D] — Run after Phase 2 (depends on B, C)
   ```

4. **Assign subagents**
   - Each independent work unit → one subagent
   - Subagents in the same phase → run in parallel
   - Subagents in different phases → run sequentially

### Phase 3: Create Execution Plan

5. **Generate the plan**
   ```
   Execution Plan: [Task Name]
   ├── Phase 1: [Name]
   │   ├── Subagent 1: [Task] — Parallel
   │   ├── Subagent 2: [Task] — Parallel
   │   └── Subagent 3: [Task] — Parallel
   ├── Phase 2: [Name]
   │   ├── Subagent 4: [Task] — Parallel
   │   └── Subagent 5: [Task] — Parallel
   └── Phase 3: [Name]
       └── Main Agent: Synthesize results
   ```

6. **Define handoff points**
   - What does each subagent produce?
   - What does the next phase need as input?
   - How are results combined?

### Phase 4: Execute

7. **Run phases sequentially**
   - Within each phase: run subagents in parallel
   - Between phases: wait for all subagents to complete
   - Collect results and pass to next phase

8. **Synthesize results**
   - Main agent combines all subagent outputs
   - Produces final deliverable
   - Verifies against success criteria

## Decomposition Patterns

### Pattern 1: Research → Analyze → Synthesize
```
Phase 1: Research (3 parallel subagents)
Phase 2: Analyze (2 parallel subagents)
Phase 3: Synthesize (main agent)
```

### Pattern 2: Discover → Design → Build → Test
```
Phase 1: Discover (3 parallel subagents)
Phase 2: Design (2 parallel subagents)
Phase 3: Build (N parallel subagents)
Phase 4: Test (2 parallel subagents)
Phase 5: Synthesize (main agent)
```

### Pattern 3: Investigate → Fix → Verify
```
Phase 1: Investigate (2 parallel subagents)
Phase 2: Fix (1 subagent)
Phase 3: Verify (2 parallel subagents)
```

### Pattern 4: Parallel Exploration
```
Phase 1: Explore (N parallel subagents, each with different approach)
Phase 2: Compare (main agent evaluates all approaches)
Phase 3: Execute best approach (1 subagent)
```

## Subagent Assignment Rules

| Work Unit Type | Subagent Type | Tools |
|---------------|---------------|-------|
| Research/Discovery | Explore agent | Read, Grep, Glob, WebSearch |
| Analysis | General-purpose agent | Read, Grep, Bash |
| Design | Plan agent | Read, Write |
| Build | General-purpose agent | Read, Write, Edit, Bash |
| Test | Verification agent | Read, Bash, Grep |
| Synthesis | Main agent | All tools |

## Integration

This skill is the bridge between:
- `prompt-enhancer` — receives enhanced task specification
- `agent-os-master` — provides execution plan
- `ralph-loop` — provides phases for iteration
- `superpowers-patterns` — enforces quality gates between phases
