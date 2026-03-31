---
name: deep-research
description: Use when you need to thoroughly investigate any topic, codebase, system, or problem. Combines web research, codebase analysis, and structured synthesis to produce comprehensive findings.
when_to_use: Researching unfamiliar topics, investigating complex systems, analyzing codebases, gathering comprehensive information before making decisions, or when surface-level answers are insufficient.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - WebFetch
  - WebSearch
arguments:
  - topic
  - depth
  - focus
argument-hint: "[topic-description] [quick|standard|deep] [technical|business|security|architecture]"
---

# Deep Research

Conduct thorough, multi-source research on any topic. Combines systematic investigation with structured synthesis to produce actionable findings.

<HARD-GATE>
Do NOT present conclusions without showing your research process. Do NOT skip primary source verification. Do NOT present speculation as fact.
</HARD-GATE>

## The Iron Law

No research finding without at least TWO independent sources confirming it.

## When to Use

- You need to understand a complex system or codebase
- You're investigating a problem with no obvious solution
- You need comprehensive information before making a decision
- Surface-level answers leave critical questions unanswered
- You need to compare multiple approaches or solutions
- You're analyzing security, architecture, or design patterns

## When NOT to Use

- Simple factual questions with known answers
- Time-critical decisions where speed matters more than thoroughness
- Topics where you already have comprehensive knowledge

## The Process

### Phase 1: Scope Definition

1. **Understand the research question**
   - What exactly are we trying to find out?
   - What would a complete answer look like?
   - What are the critical unknowns?

2. **Define research boundaries**
   - What's in scope?
   - What's out of scope?
   - What's the time budget?

3. **Identify knowledge domains**
   - What areas of expertise does this touch?
   - What existing knowledge applies?
   - What's completely new territory?

### Phase 2: Multi-Source Investigation

```
Research Strategy:
├── Primary Sources (code, docs, specs)
│   ├── Read source code directly
│   ├── Analyze documentation
│   └── Examine configurations
├── Secondary Sources (articles, discussions)
│   ├── WebSearch for current information
│   ├── WebFetch for deep content
│   └── Cross-reference multiple sources
└── Tertiary Sources (summaries, comparisons)
    ├── Synthesize findings
    ├── Identify patterns
    └── Note contradictions
```

4. **Search systematically**
   - Start broad, then narrow
   - Use multiple search strategies
   - Track what you've searched and found

5. **Verify independently**
   - Cross-check findings across sources
   - Note when sources disagree
   - Flag low-confidence findings

6. **Document as you go**
   - Record sources for every finding
   - Note confidence levels
   - Track open questions

### Phase 3: Analysis & Synthesis

7. **Organize findings**
   - Group by theme/category
   - Separate facts from interpretations
   - Identify patterns and contradictions

8. **Evaluate evidence**
   - Strong evidence: multiple independent sources agree
   - Medium evidence: single authoritative source
   - Weak evidence: speculation, single non-authoritative source

9. **Identify gaps**
   - What questions remain unanswered?
   - What would resolve remaining uncertainty?
   - What are the implications of gaps?

### Phase 4: Report Generation

10. **Structure the report**
    ```
    Research Report: [Topic]
    ├── Executive Summary (key findings, confidence level)
    ├── Methodology (how research was conducted)
    ├── Findings (organized by theme)
    │   ├── Finding 1 (evidence, confidence, sources)
    │   ├── Finding 2 (evidence, confidence, sources)
    │   └── ...
    ├── Analysis (patterns, implications, contradictions)
    ├── Open Questions (unanswered, next steps)
    └── Sources (complete bibliography)
    ```

11. **Write with precision**
    - State confidence levels explicitly
    - Cite sources for every claim
    - Distinguish facts from interpretations
    - Note limitations and caveats

## Research Depth Levels

| Level | Time | Sources | Output | Use When |
|-------|------|---------|--------|----------|
| **quick** | 5-10 min | 3-5 sources | Key findings summary | You need fast direction |
| **standard** | 15-30 min | 5-15 sources | Structured report | Normal research needs |
| **deep** | 30-60 min | 15+ sources | Comprehensive analysis | Critical decisions, complex topics |

## Research Focus Areas

| Focus | Emphasis | Tools Used |
|-------|----------|------------|
| **technical** | Code, architecture, implementation | Read, Grep, Glob, Bash |
| **business** | Market, competition, strategy | WebSearch, WebFetch |
| **security** | Vulnerabilities, threats, hardening | Read, Grep, WebSearch |
| **architecture** | Patterns, tradeoffs, scalability | Read, WebSearch, WebFetch |

## Anti-Slop Rules

<Good>
- "Source A states X, Source B confirms X, Source C suggests Y (contradiction noted)"
- "Confidence: High (3 independent sources agree)"
- "This finding is based on direct code analysis at file:line"
</Good>

<Bad>
- "It seems like X might be the case"
- "Probably X"
- "I think X"
- Any finding without a cited source
</Bad>

## Confidence Calibration

| Confidence | Criteria | Language |
|------------|----------|----------|
| **High** | 3+ independent sources agree, or direct code analysis | "Confirmed:", "Verified:" |
| **Medium** | 2 sources agree, or single authoritative source | "Evidence suggests:", "Likely:" |
| **Low** | Single non-authoritative source, or speculation | "Possibly:", "May be:", "Uncertain:" |

## Integration

Related skills: `knowledge-synthesis`, `decision-framework`, `risk-assessment`, `strategic-planning`
