---
name: superpowers-patterns
description: Use when you need iron-law enforcement, hard gates, and anti-slop patterns for any task. Provides the enforcement layer that ensures quality standards are met.
when_to_use: Any task where quality enforcement matters, when agents tend to skip steps, when you need non-negotiable standards, or when you want to prevent common failure modes.
allowed-tools:
  - Read
  - Write
  - Edit
  - TodoWrite
arguments:
  - task
  - strictness
argument-hint: "[task-description] [standard|strict|maximum]"
---

# Superpowers Patterns

Non-negotiable quality enforcement. Iron laws, hard gates, and anti-slop patterns that prevent agents from cutting corners.

<HARD-GATE>
Do NOT proceed past any hard gate until its conditions are met. Do NOT rationalize skipping steps. Do NOT claim completion without verification.
</HARD-GATE>

## The Iron Law

Every task must pass through all applicable gates before being marked complete.

## Enforcement Mechanisms

### 1. Iron Laws

Iron Laws are absolute rules that override all other instructions. They are written in code blocks and cannot be bypassed.

```
IRON LAW: No [BAD THING] without [GOOD THING] first.
```

**Examples:**
```
IRON LAW: No conclusions without showing your research process.
IRON LAW: No code changes without understanding the existing code.
IRON LAW: No deployment without testing.
IRON LAW: No decisions without evaluating at least 3 alternatives.
```

### 2. Hard Gates

Hard Gates are XML-tagged checkpoints that block progression until conditions are met.

```xml
<HARD-GATE>
Do NOT [ACTION] until [CONDITION] is met.
Do NOT [ACTION] without [REQUIREMENT].
</HARD-GATE>
```

**Examples:**
```xml
<HARD-GATE>
Do NOT write code without first understanding the existing codebase.
Do NOT present conclusions without showing your reasoning process.
Do NOT mark a task complete without verifying all requirements are met.
</HARD-GATE>
```

### 3. Anti-Slop Rules

Anti-Slop Rules define specific patterns to avoid, with good and bad examples.

**Good patterns:**
- "Source A states X, Source B confirms X"
- "The function returns null when the input is empty"
- "Response time: 50ms (target: 100ms)"
- Specific, measurable, verifiable statements

**Bad patterns:**
- "It seems like X might be the case"
- "The function handles edge cases appropriately"
- "The system is fast"
- Vague, unverifiable, speculative statements

### 4. Rationalization Tables

Rationalization Tables preempt agent self-justification by listing excuses and the reality.

| Excuse | Reality |
|--------|---------|
| "I already know this, no need to check" | You might be wrong — verify |
| "This is too simple to need a plan" | Simple tasks fail too — plan briefly |
| "The tests will catch any issues" | Prevention is better than detection |
| "I'll come back and fix this later" | Later never comes — fix it now |
| "This edge case is unlikely" | Unlikely bugs are the hardest to find |

### 5. Red Flag Lists

Red Flags are specific thought patterns that signal rule violations.

| Red Flag | What It Means | What to Do |
|----------|--------------|------------|
| "This looks good" | You haven't verified | Run verification checks |
| "I think this is right" | You're not sure | Verify before proceeding |
| "This is probably fine" | You're guessing | Stop and check |
| "I'll skip this step because..." | You're rationalizing | Don't skip — do the step |
| "This is close enough" | You're lowering standards | Meet the standard or say why |

### 6. Checklist Enforcement

Every checklist item must be completed and verified. Use TodoWrite to track.

```
- [ ] Step 1: [description] — DONE
- [ ] Step 2: [description] — DONE
- [ ] Step 3: [description] — DONE
```

## Enforcement Levels

| Level | Mechanisms Used | When to Use |
|-------|----------------|-------------|
| **Standard** | Iron Laws + Anti-Slop | Normal quality needs |
| **Strict** | + Hard Gates + Checklists | Important work |
| **Maximum** | + Rationalization Tables + Red Flags | Critical work, high stakes |

## Common Failure Modes and Fixes

| Failure Mode | Cause | Fix |
|-------------|-------|-----|
| **Skipping steps** | Agent thinks it "knows better" | Hard gates block progression |
| **Vague output** | Agent avoids specificity | Anti-slop rules with examples |
| **Overconfidence** | Agent doesn't verify | Iron laws require evidence |
| **Rationalization** | Agent justifies shortcuts | Rationalization tables |
| **Incomplete work** | Agent marks done prematurely | Checklist enforcement |

## Integration

Related skills: `ralph-loop`, `meta-cognition`, `quality-assurance`, `decision-framework`
