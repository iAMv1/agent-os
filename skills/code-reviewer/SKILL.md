---
name: code-reviewer
description: Use when you need automated code review with security, performance, maintainability, and correctness checks. Systematic code analysis that catches bugs, vulnerabilities, and design issues before they ship.
when_to_use: After writing or modifying code, before merging PRs, during code review sessions, when evaluating third-party code, or when you need objective quality assessment of code changes.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
arguments:
  - target
  - depth
  - focus
argument-hint: "[file-or-directory] [quick|standard|deep] [security|performance|maintainability|correctness|comprehensive]"
---

# Code Reviewer

Automated, systematic code review that checks for security vulnerabilities, performance issues, maintainability problems, and correctness bugs. Catches what human reviewers miss.

<HARD-GATE>
Do NOT approve code without checking every review dimension. Do NOT skip security checks even for "internal" code. Do NOT provide vague feedback — every finding must include the exact location, the problem, and a concrete fix.
</HARD-GATE>

## The Iron Law

Every finding must include: exact file:line, the specific problem, why it matters, and a concrete fix with code.

## When to Use

- After writing new code or modifying existing code
- Before merging pull requests or branches
- When reviewing someone else's code
- When integrating third-party libraries or copied code
- When refactoring and you need to verify nothing broke
- Before deploying to production

## When NOT to Use

- Trivial changes (typos, formatting only)
- Throwaway prototypes or exploratory code
- When you need to ship an emergency hotfix (review after)
- Generated code you didn't write and won't maintain

## The Process

### Phase 1: Scope & Context

1. **Identify what changed**
   - Run `git diff` or compare against base branch
   - List all modified, added, and deleted files
   - Understand the purpose of the changes

2. **Understand the context**
   - What is the code supposed to do?
   - What are the requirements or user story?
   - What existing patterns does this codebase use?

3. **Set review depth**
   - **quick**: Security + obvious bugs only
   - **standard**: All dimensions, focused on changed code
   - **deep**: All dimensions including surrounding code and architecture

### Phase 2: Security Review

4. **Check for injection vulnerabilities**
   - SQL injection: parameterized queries, ORM usage
   - XSS: output encoding, template escaping
   - Command injection: shell escaping, avoid `eval`/`exec`
   - Path traversal: input validation on file paths

5. **Check authentication & authorization**
   - Are protected endpoints checking auth?
   - Is authorization enforced at the data layer?
   - Are tokens/secrets handled securely?
   - No hardcoded credentials or API keys

6. **Check data handling**
   - Sensitive data not logged or exposed in errors
   - PII encrypted at rest and in transit
   - Input validated and sanitized
   - Output encoded appropriately

7. **Check dependency security**
   - No known vulnerable dependencies
   - Dependencies from trusted sources
   - Lock files committed and up to date

### Phase 3: Performance Review

8. **Check for performance anti-patterns**
   - N+1 query problems
   - Missing database indexes
   - Unnecessary data fetching or over-fetching
   - Memory leaks (unclosed resources, growing caches)
   - Blocking operations in async code

9. **Check algorithmic efficiency**
   - O(n²) or worse in hot paths
   - Unnecessary iterations or transformations
   - Missing caching for expensive operations
   - Large payloads transferred unnecessarily

10. **Check resource management**
    - Connections, files, streams properly closed
    - Timeouts configured for external calls
    - Rate limiting for external APIs
    - Proper cleanup in error paths

### Phase 4: Maintainability Review

11. **Check code structure**
    - Functions are small and single-purpose
    - Clear, descriptive naming
    - Consistent code style with project conventions
    - No deep nesting (max 3 levels)
    - DRY — no duplicated logic

12. **Check documentation**
    - Complex logic has explanatory comments
    - Public APIs have docstrings/JSDoc
    - Non-obvious decisions are documented
    - No commented-out code left behind

13. **Check testability**
    - Code is structured for testing
    - Dependencies are injectable
    - No hidden global state
    - Edge cases have test coverage

### Phase 5: Correctness Review

14. **Check logic correctness**
    - Off-by-one errors in loops and ranges
    - Null/undefined handling
    - Error cases handled (not just happy path)
    - Race conditions in concurrent code
    - State management correctness

15. **Check edge cases**
    - Empty inputs, null values
    - Maximum values, overflow
    - Invalid or malformed input
    - Concurrent access patterns
    - Network failures, timeouts

### Phase 6: Report

16. **Generate review report**
    ```
    Code Review: [Target]
    ├── Summary
    │   ├── Files reviewed: N
    │   ├── Lines changed: N
    │   └── Overall assessment: [Pass/Pass with comments/Needs work]
    ├── Findings by Severity
    │   ├── Critical (must fix): [count]
    │   ├── Major (should fix): [count]
    │   ├── Minor (nice to fix): [count]
    │   └── Suggestions: [count]
    ├── Detailed Findings
    │   ├── [file:line] Severity: Problem
    │   │   ├── Why it matters
    │   │   └── Suggested fix
    │   └── ...
    └── Positive Observations
        └── What was done well
    ```

## Anti-Slop Rules

<Good>
- "src/auth.ts:42 — CRITICAL: User input concatenated into SQL query. Use parameterized query: `db.query('SELECT * FROM users WHERE id = $1', [userId])`"
- "src/handler.py:15 — MAJOR: No timeout on HTTP request. Add `timeout=30` to requests.get() call."
- "src/utils.js:8 — MINOR: Function name `doStuff` is not descriptive. Rename to `formatUserDisplayName`."
</Good>

<Bad>
- "The code looks good overall"
- "Maybe add some error handling?"
- "Check for security issues"
- "Performance could be better"
- Any finding without a specific file:line reference
- Any finding without a concrete suggested fix
</Bad>

## Severity Definitions

| Severity | Definition | Action |
|----------|-----------|--------|
| **Critical** | Security vulnerability, data loss, or crash | Must fix before merge |
| **Major** | Significant bug, performance issue, or maintainability problem | Should fix before merge |
| **Minor** | Style issue, minor improvement, or documentation gap | Fix when convenient |
| **Suggestion** | Optional improvement or alternative approach | Consider for future |

## Language-Specific Checks

| Language | Key Checks |
|----------|-----------|
| **JavaScript/TypeScript** | Type safety, async/await errors, prototype pollution, XSS |
| **Python** | SQL injection, pickle deserialization, mutable defaults |
| **Go** | Error handling, goroutine leaks, context cancellation |
| **Rust** | Unwrap/expect in production, clone overuse, lifetime issues |
| **Java** | Null handling, resource leaks, serialization issues |

## Integration

Related skills: `quality-assurance`, `security-auditor`, `risk-assessment`, `api-designer`
