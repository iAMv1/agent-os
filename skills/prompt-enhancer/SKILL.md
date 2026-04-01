---
name: prompt-enhancer
description: Use when a task description is vague, ambiguous, incomplete, or lacks critical context. Automatically enhances unclear prompts by filling gaps with reasonable assumptions. Only asks questions when context is truly impossible to infer. Never touches prompts that are already detailed enough.
when_to_use: Any time the user's request is unclear, missing details, ambiguous, or could be interpreted multiple ways. Activates automatically when you detect insufficient context. Self-enhances first, asks questions only as last resort.
allowed-tools:
  - Read
  - Write
  - Edit
  - TodoWrite
arguments:
  - prompt
  - mode
argument-hint: "[original-prompt] [auto|ask-first|enhance-only]"
---

# Prompt Enhancer

Transform vague requests into precise, actionable specifications. Self-enhances first. Asks questions only when truly stuck. Never touches clear prompts.

<HARD-GATE>
Do NOT enhance prompts that are already clear and detailed. Do NOT ask questions if you can reasonably infer the intent. Do NOT execute unclear tasks without first enhancing or clarifying.
</HARD-GATE>

## The Iron Law

If the prompt is clear — execute directly. If unclear — enhance it yourself first. Only ask questions when enhancement is impossible.

## Decision Flow

```
User Prompt
    │
    ▼
┌─────────────────────┐
│  Is it clear and    │
│  detailed enough?   │
└─────────────────────┘
    │
    ├── YES → Execute directly (skip enhancement entirely)
    │
    └── NO
         │
         ▼
    ┌─────────────────────┐
    │  Can I reasonably   │
    │  infer the intent   │
    │  and fill gaps?     │
    └─────────────────────┘
         │
         ├── YES → Self-enhance the prompt, show enhanced version, execute
         │
         └── NO
              │
              ▼
         ┌─────────────────────┐
         │  Ask 1-3 targeted   │
         │  questions with     │
         │  multiple-choice    │
         │  options            │
         └─────────────────────┘
```

## Step 1: Clarity Check

Evaluate the prompt against this checklist:

```
Clarity Score (8 points):
[ ] Goal is specific and unambiguous (0-2 points)
[ ] Scope is defined — files, components, areas (0-2 points)
[ ] Constraints stated — quality, time, resources (0-1 points)
[ ] Context sufficient — background, related info (0-2 points)
[ ] Success criteria clear (0-1 points)

Total: X/8
```

| Score | Decision |
|-------|----------|
| **7-8** | CLEAR → Execute directly. No enhancement. No questions. |
| **5-6** | ENHANCEABLE → Self-enhance with reasonable assumptions. Show enhanced version. Execute. |
| **3-4** | AMBIGUOUS → Try to self-enhance. If you can't, ask 1-3 questions. |
| **0-2** | UNCLEAR → Ask 1-3 targeted questions with options. |

## Step 2: Self-Enhance (If Score 3-6)

If the prompt is unclear but you can reasonably infer intent:

1. **Fill gaps with reasonable assumptions**
   - Use project context to infer missing details
   - Use common patterns to fill in specifics
   - Use existing codebase structure to determine scope

2. **Create the enhanced specification**
   ```
   Enhanced Task Specification:

   Original: "[user's original request]"

   Enhanced:
   - Goal: [specific, unambiguous goal]
   - Scope: [files, components, areas involved]
   - Constraints: [quality, time, resource limits]
   - Context: [relevant background information]
   - Success Criteria: [how we'll know it's done right]
   - Assumptions Made: [what I inferred and why]

   Proceeding with this understanding. Let me know if anything is wrong.
   ```

3. **Execute immediately** — don't wait for confirmation unless the assumptions are risky

## Step 3: Ask Questions (Only If Score 0-2 OR Self-Enhance Failed)

Only ask questions when you truly cannot infer the intent:

**Question Format:**
```
I need to clarify a few things before I proceed:

1. [Specific question about the critical gap]
   - Option A: [most likely interpretation]
   - Option B: [alternative interpretation]
   - Other: [let me specify]

[Max 3 questions — only ask about critical gaps]
```

**Question Rules:**
- Ask MAX 3 questions — only about critical gaps
- Provide options — don't make the user write from scratch
- Be specific — "Which file?" not "What do you mean?"
- Explain WHY you're asking — "I need to know X so I can Y"
- If user doesn't respond, proceed with best assumption

## Modes

| Mode | Behavior | When to Use |
|------|----------|-------------|
| **auto** (default) | Self-enhances unclear prompts, asks only if stuck | Normal use |
| **ask-first** | Always asks questions before enhancing | When precision is critical |
| **enhance-only** | Only self-enhances, never asks questions | When you want fast execution |

## Examples

### Example 1: Clear Prompt (Score 8/8) — Skip Entirely

**User**: "Refactor src/auth/login.ts to use the new JWT library from src/auth/jwt.ts. Keep the same API surface. Add unit tests in src/auth/__tests__/login.test.ts. Target: 90% coverage."

**Enhancer**: Score 8/8 — Clear and detailed. Executing directly.

### Example 2: Vague but Enhanceable (Score 4/8) — Self-Enhance

**User**: "Fix the auth bug"

**Enhancer**: Score 4/8 — Vague but I can infer from context.

```
Enhanced Task Specification:

Original: "Fix the auth bug"

Enhanced:
- Goal: Fix the authentication bug causing login failures
- Scope: src/auth/login.ts and related auth files
- Constraints: Maintain existing API, no breaking changes
- Context: Based on recent changes to auth flow
- Success Criteria: Login works, tests pass, no regressions
- Assumptions Made: Assuming this refers to the recent login timeout issue. If it's a different bug, let me know.

Proceeding with investigation and fix.
```

### Example 3: Too Ambiguous (Score 1/8) — Ask Questions

**User**: "Make it faster"

**Enhancer**: Score 1/8 — Cannot infer what "it" refers to or what "faster" means.

```
I need to clarify before I proceed:

1. What should be faster?
   - The page load time?
   - The API response time?
   - The database queries?
   - Something else?

2. What's the current performance and what's the target?
   - Current: [unknown] → Target: [unknown]

2 questions — I need these to optimize the right thing.
```

### Example 4: Partially Clear (Score 6/8) — Self-Enhance

**User**: "Add rate limiting to the API endpoints"

**Enhancer**: Score 6/8 — Clear goal, missing specifics. Self-enhancing.

```
Enhanced Task Specification:

Original: "Add rate limiting to the API endpoints"

Enhanced:
- Goal: Add rate limiting to prevent API abuse
- Scope: All API endpoint handlers in src/api/
- Constraints: Use sliding window algorithm, configurable limits
- Context: Standard rate limiting patterns
- Success Criteria: Rate limits enforced, tests pass, no impact on legitimate traffic
- Assumptions Made: Using 100 requests/minute per IP as default. Configurable via environment variables.

Proceeding with implementation.
```

## Anti-Slop Rules

<Good>
- "Score 8/8 — Clear. Executing directly."
- "Score 5/8 — Self-enhancing with reasonable assumptions: [list]. Proceeding."
- "Score 2/8 — Cannot infer intent. Asking 2 questions: [questions]"
</Good>

<Bad>
- "What do you mean?" (too vague, no options)
- Enhancing a prompt that's already clear (waste of time)
- Asking 5+ questions (overwhelming)
- Executing without checking clarity on vague prompts
- "I think you mean X" without showing the enhanced spec
</Bad>

## Integration

Related skills: `agent-os-master`, `deep-research`, `problem-decomposition`, `context-manager`, `communication-design`
