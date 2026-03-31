---
name: ralph-loop
description: Use when you need iterative self-improvement on any task. Implements the Ralph Loop pattern: Plan → Execute → Review → Learn → Improve → Repeat. Each cycle produces better output than the last.
when_to_use: Any task where quality matters, complex work that benefits from iteration, tasks where the first attempt is unlikely to be the best, or when you want systematic improvement over time.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - TodoWrite
arguments:
  - task
  - cycles
  - standard
argument-hint: "[task-description] [1-5] [minimum|standard|high]"
---

# Ralph Loop

Iterative self-improvement through continuous feedback cycles. Each cycle produces better output than the last.

<HARD-GATE>
Do NOT skip the Review phase. Do NOT skip the Learn phase. Do NOT claim improvement without evidence.
</HARD-GATE>

## The Iron Law

Every cycle must produce measurable improvement over the previous cycle.

## When to Use

- Building anything where quality matters
- Complex tasks that benefit from iteration
- When the first attempt is unlikely to be the best
- When you want systematic improvement over time
- Tasks where feedback reveals blind spots

## When NOT to Use

- Trivial tasks where one pass is sufficient
- Time-critical tasks where speed matters more than quality
- Tasks with no clear quality metric

## The Loop

```
┌─────────────────────────────────────────────────────┐
│                    RALPH LOOP                        │
│                                                      │
│  ┌──────┐    ┌──────────┐    ┌────────┐             │
│  │ Plan │───▶│ Execute  │───▶│ Review │             │
│  └──────┘    └──────────┘    └────────┘             │
│      ▲                            │                  │
│      │    ┌──────────┐    ┌────────┘               │
│      └────│ Improve  │◀───│ Learn                  │
│           └──────────┘    └────────┘               │
│                                                      │
│  Each cycle → Better output than previous           │
└─────────────────────────────────────────────────────┘
```

## Phase 1: Plan

1. **Define what you're building**
   - What exactly is the goal?
   - What does success look like?
   - What are the quality criteria?

2. **Define how you'll measure improvement**
   - What metrics will you track?
   - How will you know each cycle is better?
   - What's the baseline?

3. **Plan the approach**
   - What's your strategy?
   - What are the risks?
   - What could go wrong?

## Phase 2: Execute

4. **Build according to plan**
   - Follow the plan
   - Document deviations
   - Track time and effort

5. **Record what you did**
   - What approach did you take?
   - What decisions did you make?
   - What assumptions did you rely on?

## Phase 3: Review

6. **Evaluate against criteria**
   - Does it meet the quality criteria?
   - What works well?
   - What needs improvement?

7. **Find the gaps**
   - What's missing?
   - What's wrong?
   - What could be better?

8. **Score the output**
   ```
   Review Scorecard:
   - Completeness: X/10 (what's missing?)
   - Correctness: X/10 (what's wrong?)
   - Quality: X/10 (what could be better?)
   - Overall: X/10
   ```

## Phase 4: Learn

9. **Extract lessons**
   - What worked well? (keep doing this)
   - What didn't work? (stop doing this)
   - What surprised you? (update mental model)
   - What would you do differently? (improve next time)

10. **Update your approach**
    - What changes for the next cycle?
    - What new knowledge do you have?
    - What assumptions were wrong?

## Phase 5: Improve

11. **Plan the next cycle**
    - What will you do differently?
    - What will you keep the same?
    - What new approach will you try?

12. **Execute the improved approach**
    - Build with the lessons learned
    - Apply the improvements
    - Track the difference

## Cycle Count Guide

| Cycles | When to Use | Expected Improvement |
|--------|-------------|---------------------|
| **1** | Simple tasks, time-critical | Baseline quality |
| **2** | Normal tasks, quality matters | 20-40% improvement |
| **3** | Complex tasks, high quality needed | 40-60% improvement |
| **4-5** | Critical tasks, maximum quality | 60-80% improvement |

## Quality Standards

| Standard | Description |
|----------|-------------|
| **Minimum** | Functional, no critical issues |
| **Standard** | Functional, well-structured, minor issues acceptable |
| **High** | Production-ready, thoroughly tested, documented |

## Tracking Improvement

```
Cycle History:
Cycle 1: Score X/10 — Key issues: [list]
Cycle 2: Score X/10 — Improvements: [list], Remaining: [list]
Cycle 3: Score X/10 — Improvements: [list], Remaining: [list]
...

Improvement Rate: X% per cycle
Target: Y/10
```

## Integration

Related skills: `meta-cognition`, `quality-assurance`, `knowledge-synthesis`, `decision-framework`
