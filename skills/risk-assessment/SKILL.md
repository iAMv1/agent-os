---
name: risk-assessment
description: Use when you need to identify, analyze, and mitigate risks in any plan, system, or decision. Systematically finds what could go wrong and how to prevent it.
when_to_use: Before making decisions, reviewing plans, evaluating systems, planning deployments, or when you need to understand what could go wrong.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
arguments:
  - target
  - scope
argument-hint: "[what-to-assess] [technical|business|security|operational|comprehensive]"
---

# Risk Assessment

Find what could go wrong before it goes wrong. Systematic identification, analysis, and mitigation of risks.

<HARD-GATE>
Do NOT assess risks without considering at least 5 categories of risk. Do NOT identify a risk without proposing at least one mitigation strategy.
</HARD-GATE>

## The Iron Law

Every risk must have: a specific scenario, a likelihood estimate, an impact estimate, and at least one mitigation strategy.

## When to Use

- Before deploying or shipping anything
- When evaluating plans or proposals
- When designing systems or architectures
- Before making significant decisions
- When something feels uncertain or risky

## When NOT to Use

- Trivial decisions with no downside
- When the cost of assessment exceeds the potential loss
- When you need to act immediately (assess after)

## Risk Categories

| Category | What It Covers | Examples |
|----------|---------------|----------|
| **Technical** | System failures, bugs, scalability | Performance degradation, data loss, integration failures |
| **Security** | Vulnerabilities, attacks, data breaches | Injection, auth bypass, data exposure |
| **Business** | Market, competition, revenue | Wrong product, missed timing, cost overrun |
| **Operational** | Process, people, infrastructure | Key person dependency, tool failure, vendor lock-in |
| **Compliance** | Legal, regulatory, policy | GDPR violation, license conflict, policy breach |

## The Process

### Phase 1: Identify Risks

1. **Brainstorm risks by category**
   - For each category, ask "What could go wrong?"
   - Think from multiple perspectives (user, attacker, operator)
   - Consider both internal and external risks

2. **Use risk prompts**
   - What if this component fails?
   - What if traffic increases 10x?
   - What if a key person leaves?
   - What if a dependency breaks?
   - What if requirements change?
   - What if we're wrong about our assumptions?
   - What if an attacker targets this?
   - What if the timeline slips?

### Phase 2: Analyze Risks

3. **Assess likelihood**
   - High: Likely to happen (>50%)
   - Medium: Could happen (10-50%)
   - Low: Unlikely but possible (<10%)

4. **Assess impact**
   - High: Catastrophic (system down, data loss, major cost)
   - Medium: Significant (degraded service, moderate cost)
   - Low: Minor (inconvenience, small cost)

5. **Calculate risk score**
   ```
   Risk Score = Likelihood × Impact
   High × High = Critical (act immediately)
   High × Medium = Major (act soon)
   Medium × High = Major (act soon)
   Medium × Medium = Moderate (plan mitigation)
   Low × anything = Monitor (watch for changes)
   ```

### Phase 3: Plan Mitigation

6. **Choose mitigation strategy**
   | Strategy | When to Use | Example |
   |----------|-------------|---------|
   | **Avoid** | Risk is too high | Don't use the risky technology |
   | **Reduce** | Risk can be lowered | Add monitoring, add tests |
   | **Transfer** | Someone else can handle it | Use managed service, get insurance |
   | **Accept** | Risk is low or mitigation is too costly | Monitor and have a response plan |

7. **Create mitigation plan**
   ```
   | Risk | Likelihood | Impact | Score | Strategy | Mitigation | Owner | Deadline |
   |------|-----------|--------|-------|----------|------------|-------|----------|
   | Risk 1 | High | High | Critical | Reduce | Add monitoring, add fallback | Who | When |
   ```

### Phase 4: Monitor

8. **Set up early warning**
   - What signals indicate the risk is materializing?
   - How will we detect it early?
   - Who is responsible for monitoring?

9. **Review and update**
   - Re-assess risks regularly
   - Update based on new information
   - Close risks that are no longer relevant

## Risk Assessment Report Template

```
Risk Assessment: [Target]
Date: [date]
Assessor: [who]

## Executive Summary
- Total risks identified: N
- Critical: N | Major: N | Moderate: N | Low: N
- Overall risk level: [High/Medium/Low]

## Risk Register
[Detailed table of all risks]

## Mitigation Plan
[Specific actions for each risk]

## Monitoring Plan
[How risks will be tracked]

## Residual Risk
[Risk level after mitigation]
```

## Integration

Related skills: `decision-framework`, `strategic-planning`, `quality-assurance`
