---
name: agent-os-master
description: The master orchestrator skill. Automatically enhances vague prompts, decomposes tasks into parallel phases with subagents, selects the right skills, and executes an optimized workflow. Combines Ralph Loop iteration with Superpowers enforcement. This is the universal entry point for any task.
when_to_use: For ANY task — this is the universal entry point. It automatically runs prompt-enhancer first, then task-decomposer, then executes with parallel subagents. You never need to call other skills directly.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - TodoWrite
  - WebFetch
  - WebSearch
arguments:
  - task
  - mode
  - cycles
argument-hint: "[any-task-description] [fast|balanced|thorough] [1-5]"
---

# AgentOS Master Orchestrator

The universal entry point. Automatically enhances prompts, decomposes tasks into parallel subagents, and executes with Ralph Loop iteration and Superpowers enforcement.

<HARD-GATE>
Do NOT skip prompt enhancement. Do NOT skip task decomposition. Do NOT execute without a clear plan. Do NOT skip quality verification. Do NOT claim completion without evidence.
</HARD-GATE>

## The Iron Law

Every task must be: enhanced, classified, decomposed, planned, executed, reviewed, and verified before being marked complete.

## How It Works — The Full Automatic Pipeline

```
User's Raw Prompt
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│  STEP 0: PROMPT ENHANCEMENT (automatic)                 │
│                                                         │
│  1. Analyze: What's missing from the prompt?            │
│  2. Classify: Complete / Partial / Vague / Unclear      │
│  3. Ask: 1-5 clarifying questions (one at a time)       │
│  4. Enhance: Rewrite into precise specification         │
│  5. Confirm: "Does this capture what you want?"         │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│  STEP 1: TASK DECOMPOSITION (automatic)                 │
│                                                         │
│  1. Identify work units and dependencies                │
│  2. Build dependency graph                              │
│  3. Group into parallel phases                          │
│  4. Assign subagents to independent work units          │
│  5. Generate execution plan with handoff points         │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│  STEP 2: SKILL SELECTION (automatic)                    │
│                                                         │
│  Based on task type, select relevant skills:            │
│  - Research → deep-research, knowledge-synthesis        │
│  - Decision → decision-framework, risk-assessment       │
│  - Build → problem-decomposition, quality-assurance     │
│  - Fix → deep-research, problem-decomposition           │
│  - Optimize → optimization-engine, quality-assurance    │
│  - Communicate → communication-design, knowledge-synth  │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│  STEP 3: PARALLEL EXECUTION (automatic)                 │
│                                                         │
│  For each phase:                                        │
│  ├── Dispatch subagents in parallel                     │
│  ├── Each subagent works independently                  │
│  ├── Collect results when all complete                  │
│  └── Pass results to next phase                         │
│                                                         │
│  Subagent types:                                        │
│  - Explore agent: Read-only research                    │
│  - Plan agent: Architecture and design                  │
│  - General-purpose agent: Build and implement           │
│  - Verification agent: Test and validate                │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│  STEP 4: RALPH LOOP ITERATION (automatic)               │
│                                                         │
│  For each cycle (based on mode):                        │
│  1. Plan → 2. Execute → 3. Review → 4. Learn → 5. Improve │
│                                                         │
│  Each cycle produces better output than the last.       │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│  STEP 5: QUALITY VERIFICATION (automatic)               │
│                                                         │
│  Apply Superpowers enforcement:                         │
│  - Iron Laws: Check absolute rules                      │
│  - Hard Gates: Verify all gates passed                  │
│  - Anti-Slop: Check for vague patterns                  │
│  - Checklists: Verify all items complete                │
│  - Pre-mortem: "What could go wrong?"                   │
└─────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│  STEP 6: DELIVER (automatic)                            │
│                                                         │
│  Produce final output:                                  │
│  - What was built/done                                  │
│  - How it was verified                                  │
│  - What was learned                                     │
│  - What remains                                         │
│  - Session memory updated                               │
└─────────────────────────────────────────────────────────┘
```

## The Automatic Flow — No Manual Steps

When you give AgentOS a task, here's what happens automatically:

1. **Your prompt is enhanced** — If it's vague, AgentOS asks clarifying questions and rewrites it into a precise specification
2. **The task is decomposed** — AgentOS breaks it into phases, identifies parallel work, and assigns subagents
3. **Subagents run in parallel** — Independent work units execute simultaneously for maximum speed
4. **Results are synthesized** — The main agent combines all subagent outputs
5. **Quality is verified** — Iron laws, hard gates, and checklists ensure nothing is missed
6. **Output is delivered** — Complete, verified, documented

**You just describe what you want. AgentOS handles the rest.**

## Task Classification Matrix

| If your task involves... | Use these skills |
|-------------------------|-----------------|
| **Research / Investigation** | deep-research, knowledge-synthesis |
| **Making a decision** | decision-framework, risk-assessment |
| **Understanding something** | deep-research, learning-accelerator |
| **Planning something** | strategic-planning, problem-decomposition |
| **Building something** | problem-decomposition, quality-assurance |
| **Fixing something** | deep-research, problem-decomposition, quality-assurance |
| **Optimizing something** | optimization-engine, quality-assurance |
| **Communicating something** | communication-design, knowledge-synthesis |
| **Managing complexity** | context-manager, problem-decomposition |
| **Improving your thinking** | meta-cognition, ralph-loop |

## Execution Modes

| Mode | Cycles | Subagents | Enforcement | When to Use |
|------|--------|-----------|-------------|-------------|
| **fast** | 1 | Minimal | Standard | Quick tasks, time-critical |
| **balanced** | 2 | Moderate | Standard + Hard Gates | Normal tasks, quality matters |
| **thorough** | 3+ | Maximum | Maximum | Complex tasks, high stakes |

## How Parallel Execution Works

### Example: Complex Task Decomposition

**User prompt**: "Reverse-engineer the auth flow, find vulnerabilities, design improvements, create migration plan"

**Automatic decomposition**:
```
Phase 1: Discovery (3 parallel subagents)
├── Subagent A: Map all auth-related files & functions
├── Subagent B: Trace auth flow from entry to completion
└── Subagent C: Identify all auth dependencies & configs

Phase 2: Analysis (2 parallel subagents)
├── Subagent D: Security vulnerability assessment
└── Subagent E: Performance bottleneck analysis

Phase 3: Design (2 parallel subagents)
├── Subagent F: Design improved auth architecture
└── Subagent G: Create migration plan

Phase 4: Synthesis (main agent)
└── Combine all findings into comprehensive report
```

### Subagent Types and When to Use Them

| Subagent Type | Purpose | Tools | When to Use |
|--------------|---------|-------|-------------|
| **Explore** | Read-only research | Read, Grep, Glob, WebSearch | Discovery, investigation |
| **Plan** | Architecture and design | Read, Write | Planning, design |
| **General-purpose** | Build and implement | All tools | Implementation, fixes |
| **Verification** | Test and validate | Read, Bash, Grep | Testing, QA |

## Integration

This skill orchestrates all other AgentOS skills:
- `prompt-enhancer` — Enhances vague prompts (runs first, automatically)
- `task-decomposer` — Breaks tasks into phases and subagents (runs second, automatically)
- `ralph-loop` — Iterative improvement
- `superpowers-patterns` — Quality enforcement
- `deep-research` — Investigation
- `decision-framework` — Decision making
- `knowledge-synthesis` — Understanding
- `strategic-planning` — Planning
- `problem-decomposition` — Breaking down
- `quality-assurance` — Verification
- `communication-design` — Communication
- `learning-accelerator` — Fast learning
- `risk-assessment` — Risk management
- `optimization-engine` — Optimization
- `context-manager` — State management
- `meta-cognition` — Self-reflection
