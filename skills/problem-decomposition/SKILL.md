---
name: problem-decomposition
description: Use when facing a complex problem that needs to be broken into manageable pieces. Systematically decomposes any problem into solvable sub-problems.
when_to_use: Facing overwhelming complexity, designing system architecture, planning large projects, debugging complex issues, or when a problem seems too big to tackle directly.
allowed-tools:
  - Read
  - Write
  - Edit
  - TodoWrite
arguments:
  - problem
  - strategy
argument-hint: "[problem-description] [top-down|bottom-up|divide-conquer|dependency-based]"
---

# Problem Decomposition

Break complex problems into manageable pieces. Every big problem is just many small problems waiting to be solved in the right order.

<HARD-GATE>
Do NOT start solving until decomposition is complete. Do NOT create sub-problems that aren't independently solvable. Do NOT skip dependency mapping between sub-problems.
</HARD-GATE>

## The Iron Law

Every sub-problem must be independently testable — you must be able to verify it's solved without solving other sub-problems.

## When to Use

- A problem feels overwhelming or unclear
- You need to plan work across multiple people or phases
- Debugging a complex issue with many potential causes
- Designing a system with multiple components
- Estimating effort for a large initiative

## When NOT to Use

- Simple problems with obvious solutions
- Problems that are already at the right granularity
- When you need to act immediately (decompose after)

## Decomposition Strategies

### Strategy 1: Top-Down (Goal → Steps)
Start with the end goal and work backward:
```
Goal: Build X
├── Sub-goal 1: What must exist for X to work?
│   ├── Sub-goal 1.1: What must exist for 1 to work?
│   └── Sub-goal 1.2: ...
├── Sub-goal 2: What else must exist?
└── Sub-goal 3: ...
```

### Strategy 2: Bottom-Up (Components → System)
Start with what you have and build up:
```
Existing: A, B, C
├── Combine A + B → AB
├── Combine AB + C → ABC
└── ABC + new component → Goal
```

### Strategy 3: Divide & Conquer (Independent Parts)
Split into independent pieces:
```
Problem P
├── Part P1 (independent of P2, P3)
├── Part P2 (independent of P1, P3)
└── Part P3 (independent of P1, P2)
```

### Strategy 4: Dependency-Based (Order Matters)
Order by what must come first:
```
Layer 1: Foundation (no dependencies)
├── Task 1.1
└── Task 1.2

Layer 2: Depends on Layer 1
├── Task 2.1 (needs 1.1)
└── Task 2.2 (needs 1.1, 1.2)

Layer 3: Depends on Layer 2
└── Task 3.1 (needs 2.1, 2.2)
```

## The Process

### Phase 1: Understand the Problem

1. **State the problem clearly**
   - What exactly is the problem?
   - What would a solution look like?
   - What are the constraints?

2. **Identify the boundaries**
   - What's inside the problem?
   - What's outside (assumed solved)?
   - What interfaces connect inside to outside?

### Phase 2: Decompose

3. **Choose a decomposition strategy**
   - Top-down: if you know the goal but not the path
   - Bottom-up: if you have components but not the system
   - Divide & conquer: if the problem has natural boundaries
   - Dependency-based: if order matters

4. **Create the decomposition tree**
   - Break into 3-7 sub-problems (Miller's Law)
   - Each sub-problem should be independently solvable
   - Stop when sub-problems are small enough to solve directly

5. **Map dependencies**
   - Which sub-problems depend on which?
   - What's the critical path?
   - What can be done in parallel?

### Phase 3: Validate

6. **Check completeness**
   - Do all sub-problems together solve the original problem?
   - Is anything missing?
   - Is anything duplicated?

7. **Check granularity**
   - Are sub-problems small enough to solve directly?
   - Are any too small (over-decomposed)?
   - Are any too large (under-decomposed)?

8. **Check independence**
   - Can each sub-problem be solved independently?
   - Are dependencies explicit and minimal?
   - Are there circular dependencies?

### Phase 4: Plan Execution

9. **Order the sub-problems**
   - Start with foundation (no dependencies)
   - Build up layer by layer
   - Parallelize independent branches

10. **Create the execution plan**
    - Assign each sub-problem to a phase
    - Define success criteria for each
    - Set up checkpoints between phases

## Decomposition Quality Checklist

- [ ] Problem is stated clearly
- [ ] Strategy is appropriate for the problem type
- [ ] Sub-problems are independently solvable
- [ ] Dependencies are explicit
- [ ] No circular dependencies
- [ ] Granularity is appropriate
- [ ] Nothing is missing or duplicated
- [ ] Execution order is defined

## Integration

Related skills: `strategic-planning`, `decision-framework`, `quality-assurance`
