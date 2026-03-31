---
name: prompt-enhancer
description: Use when a user provides any task or request. Enhances vague prompts into precise, actionable specifications by asking clarifying questions and adding missing context. Always runs before any other skill.
when_to_use: At the start of every interaction, before executing any task. When a user prompt is vague, incomplete, or lacks critical context. When you need to understand what the user actually wants vs what they said.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - TodoWrite
arguments:
  - prompt
  - mode
argument-hint: "[user-prompt] [auto|interactive]"
---

# Prompt Enhancer

Transform vague user requests into precise, actionable specifications. Never execute a poorly-defined task.

<HARD-GATE>
Do NOT execute a task until the prompt has been enhanced and clarified. Do NOT assume context the user didn't provide. Do NOT skip asking questions when critical information is missing.
</HARD-GATE>

## The Iron Law

Every task must have: a clear goal, success criteria, constraints, and scope before execution begins.

## When to Use

- **Always** — as the first step before any task execution
- User provides a vague or one-line request
- Task has ambiguous requirements
- Missing critical context (scope, constraints, success criteria)
- Multiple interpretations are possible

## When NOT to Use

- User has already provided a detailed, complete specification
- Task is trivially simple and unambiguous

## The Process

### Phase 1: Analyze the Prompt

1. **Identify what's missing**
   Check each dimension:
   - **Goal**: What exactly are we trying to achieve?
   - **Scope**: What's in/out of scope?
   - **Constraints**: Time, resources, technology, dependencies?
   - **Success criteria**: How do we know it's done and correct?
   - **Context**: What existing code/system does this touch?
   - **Audience**: Who is this for?
   - **Format**: What should the output look like?

2. **Classify prompt quality**
   | Quality | Description | Action |
   |---------|-------------|--------|
   | **Complete** | All dimensions covered | Execute directly |
   | **Partial** | Some dimensions missing | Ask 1-3 questions |
   | **Vague** | Most dimensions missing | Ask 3-5 questions |
   | **Unclear** | Can't determine intent | Ask clarifying questions |

### Phase 2: Ask Clarifying Questions

3. **Ask questions strategically**
   - Ask **one question at a time** (don't overwhelm)
   - Ask the **most critical question first** (the one that changes everything)
   - Provide **suggested answers** (multiple choice when possible)
   - Explain **why you're asking** (so the user understands the impact)

4. **Question priority order**
   1. What's the actual goal? (if unclear)
   2. What's the scope? (if unbounded)
   3. What are the constraints? (if unconstrained)
   4. What does success look like? (if undefined)
   5. What existing context should I know? (if unknown)

### Phase 3: Enhance the Prompt

5. **Rewrite the prompt**
   Take the user's original request + answers → produce an enhanced specification:

   ```
   Enhanced Task Specification:
   ├── Original Request: [what the user said]
   ├── Enhanced Goal: [precise, measurable goal]
   ├── Scope: [what's in, what's out]
   ├── Constraints: [time, tech, resources]
   ├── Success Criteria: [how we know it's done]
   ├── Context: [existing code/system info]
   ├── Output Format: [what deliverables]
   └── Execution Plan: [phases, subagents, workflow]
   ```

6. **Confirm with the user**
   - Present the enhanced specification
   - Ask "Does this capture what you want?"
   - Adjust based on feedback

### Phase 4: Hand Off to Workflow

7. **Pass enhanced spec to task-decomposer**
   - The task-decomposer will break it into phases
   - Subagents will be assigned to parallel work
   - The workflow engine will execute

## Question Templates

### For Research Tasks
- "What's the depth you need? (quick overview / standard analysis / deep dive)"
- "What specific aspects are most important?"
- "What will you use this research for?"

### For Build Tasks
- "What's the tech stack?"
- "Are there existing systems to integrate with?"
- "What's the minimum viable version vs full version?"
- "Any performance or scalability requirements?"

### For Fix Tasks
- "What's the exact symptom?"
- "When did it start happening?"
- "What changed recently?"
- "What's the impact (blocking / annoying / cosmetic)?"

### For Design Tasks
- "Who is the target audience?"
- "What are the key user flows?"
- "Are there existing design patterns to follow?"
- "What's the timeline?"

## Anti-Slop Rules

<Good>
- "To make sure I build exactly what you need: should this be a quick prototype or production-ready?"
- "I see three possible interpretations. Which matches your intent: A, B, or C?"
- "Before I start: what's the most important outcome from this task?"
</Good>

<Bad>
- Starting execution without clarifying
- Assuming the user's intent
- Asking 10 questions at once
- Asking questions whose answers are obvious from context
</Bad>

## Integration

This skill runs **automatically before every task**. It feeds into:
- `task-decomposer` — breaks enhanced spec into phases and subagents
- `agent-os-master` — orchestrates the full workflow
- `ralph-loop` — provides clear success criteria for iteration
