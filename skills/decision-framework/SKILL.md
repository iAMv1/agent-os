---
name: decision-framework
description: Use when facing any decision that requires structured evaluation of options, tradeoffs, and consequences. Provides a systematic framework for making better decisions.
when_to_use: Choosing between approaches, evaluating tradeoffs, making architectural decisions, prioritizing work, or when you need to justify a decision with clear reasoning.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
arguments:
  - decision
  - criteria
argument-hint: "[decision-description] [speed|quality|cost|risk|balanced]"
---

# Decision Framework

A systematic approach to evaluating options and making decisions. Forces structured thinking over gut feelings.

<HARD-GATE>
Do NOT recommend an option without evaluating at least 3 alternatives. Do NOT skip the "when this is wrong" analysis for any option.
</HARD-GATE>

## The Iron Law

Every decision must have explicit criteria, weighted by importance, with scored alternatives.

## When to Use

- Choosing between technical approaches
- Evaluating tradeoffs in architecture
- Prioritizing features or tasks
- Making build vs buy decisions
- Deciding on tool or framework selection
- Any decision where the wrong choice has meaningful cost

## When NOT to Use

- Trivial decisions with no meaningful consequences
- Time-critical decisions where analysis paralysis is the bigger risk
- Decisions already made that need execution, not re-evaluation

## The Process

### Phase 1: Frame the Decision

1. **State the decision clearly**
   - What exactly are we deciding?
   - Who is affected?
   - What's the time horizon?

2. **Identify the real question**
   - Surface question: "Which framework?"
   - Real question: "Which framework minimizes long-term maintenance cost while meeting performance needs?"

3. **Define success criteria**
   - What would make this decision successful in 6 months?
   - What would make it a failure?

### Phase 2: Generate Options

4. **List all viable alternatives**
   - Minimum 3 options (including "do nothing" or "delay")
   - Include unconventional options
   - Don't filter prematurely

5. **Eliminate dominated options**
   - Remove options that are strictly worse than another on all criteria
   - Keep the survivor

### Phase 3: Evaluate

6. **Define evaluation criteria**
   ```
   Criteria Template:
   - Criterion 1: [name] (weight: X/10)
     - What it measures:
     - How to score:
   - Criterion 2: [name] (weight: X/10)
     - ...
   ```

7. **Score each option**
   ```
   Decision Matrix:
   | Criterion (weight) | Option A | Option B | Option C |
   |-------------------|----------|----------|----------|
   | Speed (8)         | 7 (56)   | 9 (72)   | 5 (40)   |
   | Quality (9)       | 8 (72)   | 6 (54)   | 9 (81)   |
   | Cost (7)          | 6 (42)   | 8 (56)   | 9 (63)   |
   | Risk (6)          | 7 (42)   | 5 (30)   | 8 (48)   |
   | TOTAL             | 212      | 212      | 232      |
   ```

8. **Analyze the results**
   - Which option wins?
   - How close is the race?
   - Which criteria drive the difference?

### Phase 4: Stress Test

9. **Sensitivity analysis**
   - What if weights change by 20%?
   - What if one criterion is removed?
   - Does the winner hold?

10. **Pre-mortem**
    - Imagine it's 6 months later and this decision failed. Why?
    - What assumptions could be wrong?
    - What would you do differently?

11. **Reversibility check**
    - How hard is it to undo this decision?
    - What's the cost of being wrong?
    - Can you make a reversible version first?

### Phase 5: Decide

12. **Make the call**
    - State the decision clearly
    - State the reasoning
    - State the confidence level
    - State the monitoring plan

## Decision Types

| Type | Approach | Time Budget |
|------|----------|-------------|
| **Reversible** | Decide quickly, monitor, adjust | 5-15 min |
| **Irreversible** | Full framework, stress test, pre-mortem | 15-30 min |
| **One-way door** | Maximum rigor, external review | 30-60 min |

## Common Decision Traps

| Trap | Description | Antidote |
|------|-------------|----------|
| **Confirmation bias** | Seeking evidence for preferred option | Actively seek disconfirming evidence |
| **Status quo bias** | Preferring current state | Score "do nothing" as an option |
| **Sunk cost fallacy** | Continuing because of past investment | Evaluate from current state only |
| **Analysis paralysis** | Over-analyzing simple decisions | Match rigor to decision importance |
| **False dichotomy** | Only seeing two options | Force a third option |
| **Anchoring** | First option sets the standard | Evaluate all options independently |

## Integration

Related skills: `strategic-planning`, `risk-assessment`, `problem-decomposition`, `deep-research`
