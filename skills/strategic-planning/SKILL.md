---
name: strategic-planning
description: Use when you need to create a strategic plan for any project, initiative, or goal. Transforms vague objectives into actionable, sequenced plans with milestones and risk mitigation.
when_to_use: Starting new projects, planning complex initiatives, setting roadmaps, aligning teams, or when you have a goal but no clear path.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - TodoWrite
arguments:
  - goal
  - horizon
argument-hint: "[goal-description] [short-term|medium-term|long-term]"
---

# Strategic Planning

Transform vague objectives into actionable, sequenced plans. Forces clarity on what matters, what comes first, and what could go wrong.

<HARD-GATE>
Do NOT create a plan without identifying dependencies between phases. Do NOT set milestones without defining how success is measured. Do NOT skip the risk section.
</HARD-GATE>

## The Iron Law

Every plan must have: clear phases, explicit dependencies, measurable milestones, and identified risks with mitigation strategies.

## When to Use

- Starting a new project or initiative
- Planning complex multi-phase work
- Setting quarterly or annual roadmaps
- Aligning multiple stakeholders on direction
- When you have a goal but no clear path

## When NOT to Use

- Simple tasks that don't need planning
- When you need to act immediately (plan after)
- When the situation is too uncertain for meaningful planning

## The Process

### Phase 1: Define the Objective

1. **State the goal precisely**
   - What exactly are we trying to achieve?
   - What does success look like?
   - What does failure look like?
   - Who benefits? Who is affected?

2. **Define constraints**
   - Time: When must this be done?
   - Resources: What's available?
   - Dependencies: What must happen first?
   - Non-negotiables: What can't change?

### Phase 2: Analyze the Current State

3. **Assess where we are**
   - What exists today?
   - What's working? What's broken?
   - What's the gap between current and desired state?

4. **Identify forces**
   ```
   Force Analysis:
   ├── Driving forces (push toward goal)
   │   - Force 1: strength, reliability
   │   - Force 2: strength, reliability
   ├── Restraining forces (push away from goal)
   │   - Force 1: strength, reliability
   │   - Force 2: strength, reliability
   └── Net force: toward or away from goal?
   ```

### Phase 3: Design the Strategy

5. **Identify strategic approaches**
   - What are the viable paths to the goal?
   - What are the tradeoffs of each path?
   - Which path has the best risk/reward ratio?

6. **Sequence the work**
   ```
   Strategic Sequence:
   Phase 1: Foundation (what must exist first)
   ├── Deliverable 1.1
   ├── Deliverable 1.2
   └── Milestone: [measurable outcome]

   Phase 2: Core (the main work)
   ├── Deliverable 2.1
   ├── Deliverable 2.2
   └── Milestone: [measurable outcome]

   Phase 3: Polish (refinement and optimization)
   ├── Deliverable 3.1
   └── Milestone: [measurable outcome]
   ```

7. **Map dependencies**
   - What must happen before what?
   - What can happen in parallel?
   - What's the critical path?

### Phase 4: Risk & Mitigation

8. **Identify risks**
   ```
   Risk Register:
   | Risk | Likelihood | Impact | Mitigation | Owner |
   |------|-----------|--------|------------|-------|
   | Risk 1 | High/Med/Low | High/Med/Low | Strategy | Who |
   ```

9. **Plan contingencies**
   - If X goes wrong, what's Plan B?
   - What are the early warning signs?
   - When do we pivot vs. persist?

### Phase 5: Execution Plan

10. **Create actionable steps**
    - Break phases into specific tasks
    - Assign priorities
    - Set deadlines
    - Define success criteria for each step

11. **Set up monitoring**
    - What metrics track progress?
    - How often do we check?
    - When do we adjust the plan?

## Plan Quality Checklist

- [ ] Objective is specific and measurable
- [ ] Current state is honestly assessed
- [ ] Strategy has clear rationale
- [ ] Phases are sequenced logically
- [ ] Dependencies are explicit
- [ ] Milestones are measurable
- [ ] Risks are identified with mitigations
- [ ] Contingencies are defined
- [ ] Monitoring plan is in place

## Integration

Related skills: `decision-framework`, `problem-decomposition`, `risk-assessment`, `quality-assurance`
