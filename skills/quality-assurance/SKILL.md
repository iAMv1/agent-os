---
name: quality-assurance
description: Use when you need to verify quality, correctness, and completeness of anything — code, documents, plans, designs, or processes. Systematic quality checking with explicit standards.
when_to_use: Before shipping anything, reviewing work, validating plans, checking completeness, or when you need to ensure quality standards are met.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
arguments:
  - target
  - standard
argument-hint: "[what-to-check] [strict|standard|light] [functional|security|performance|maintainability]"
---

# Quality Assurance

Systematic quality verification with explicit standards. Catches what rushed work misses.

<HARD-GATE>
Do NOT approve work without checking against every quality criterion. Do NOT skip edge case testing. Do NOT mark something as complete when you know it has issues.
</HARD-GATE>

## The Iron Law

Every quality check must produce specific, actionable findings — never "looks good" without evidence.

## When to Use

- Before shipping, deploying, or delivering anything
- Reviewing someone else's work
- Validating plans or designs before implementation
- When quality is more important than speed
- After making significant changes

## When NOT to Use

- Quick prototypes or throwaway work
- When speed is the only constraint
- For trivial changes with no quality impact

## The Process

### Phase 1: Define Quality Standards

1. **Identify applicable standards**
   ```
   Quality Dimensions:
   ├── Functional: Does it work correctly?
   ├── Security: Is it safe from attacks?
   ├── Performance: Is it fast enough?
   ├── Reliability: Does it handle errors?
   ├── Maintainability: Can others understand it?
   ├── Scalability: Does it handle growth?
   └── Usability: Is it easy to use?
   ```

2. **Set the quality bar**
   - What's the minimum acceptable quality?
   - What's the target quality?
   - What quality dimensions matter most?

### Phase 2: Systematic Review

3. **Check against standards**
   For each quality dimension:
   - What's the criterion?
   - How do we test it?
   - What's the result?
   - What's the evidence?

4. **Test edge cases**
   - Empty inputs
   - Maximum inputs
   - Invalid inputs
   - Concurrent operations
   - Failure scenarios
   - Boundary conditions

5. **Check completeness**
   - Is everything specified implemented?
   - Are all error cases handled?
   - Are all edge cases covered?
   - Is documentation complete?

### Phase 3: Find Issues

6. **Categorize findings**
   ```
   | Severity | Description | Action |
   |----------|-------------|--------|
   | Critical | Broken functionality, security hole | Must fix before shipping |
   | Major | Significant quality issue | Should fix before shipping |
   | Minor | Minor quality issue | Nice to fix |
   | Suggestion | Improvement idea | Consider for future |
   ```

7. **Prioritize**
   - What must be fixed now?
   - What can be fixed later?
   - What's acceptable as-is?

### Phase 4: Report & Verify

8. **Write the QA report**
   ```
   QA Report: [Target]
   ├── Standards Applied
   ├── Findings (by severity)
   │   ├── Critical: [list]
   │   ├── Major: [list]
   │   ├── Minor: [list]
   │   └── Suggestions: [list]
   ├── Coverage (what was checked)
   ├── Gaps (what wasn't checked)
   └── Recommendation (ship/hold/revise)
   ```

9. **Verify fixes**
   - Re-check every finding after fix
   - Check for regressions
   - Confirm no new issues introduced

## Quality Checklists by Type

### Code Quality
- [ ] Functionality: All requirements met
- [ ] Error handling: All error cases covered
- [ ] Edge cases: Boundaries tested
- [ ] Security: No injection, auth bypass, data leaks
- [ ] Performance: No obvious bottlenecks
- [ ] Maintainability: Clear names, comments where needed
- [ ] Testing: Tests cover critical paths
- [ ] Dependencies: No unnecessary dependencies

### Document Quality
- [ ] Accuracy: All facts correct
- [ ] Completeness: Nothing important missing
- [ ] Clarity: Understandable by target audience
- [ ] Consistency: Terminology, formatting consistent
- [ ] Structure: Logical organization
- [ ] Examples: Concrete illustrations provided

### Plan Quality
- [ ] Feasibility: Can this actually be done?
- [ ] Completeness: All phases covered
- [ ] Dependencies: Explicit and correct
- [ ] Risks: Identified with mitigations
- [ ] Milestones: Measurable and realistic
- [ ] Resources: Adequate for the work

## Integration

Related skills: `decision-framework`, `strategic-planning`, `problem-decomposition`
