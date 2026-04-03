# Skills Catalog

Complete reference for AgentOS universal skills.

## Overview

AgentOS includes 27 universal skills (12 core + 15 specialized) that work with any AI coding agent. The 12 core skills are automatically installed during base installation.

## Core Skills

### 1. Deep Research

**Location:** `skills/deep-research/SKILL.md`

**Purpose:** Multi-source investigation and comprehensive research.

**When to use:**
- Researching complex topics
- Investigating unfamiliar APIs
- Understanding system behavior
- Comparing alternatives

**Key capabilities:**
- Multi-source information gathering
- Cross-referencing and validation
- Synthesis of findings
- Structured research reports

---

### 2. Decision Framework

**Location:** `skills/decision-framework/SKILL.md`

**Purpose:** Structured decision evaluation with weighted scoring.

**When to use:**
- Choosing between options
- Evaluating trade-offs
- Making architectural decisions
- Selecting libraries or tools

**Key capabilities:**
- Weighted scoring matrix
- Pre-mortem analysis
- Sensitivity analysis
- Decision documentation

---

### 3. Knowledge Synthesis

**Location:** `skills/knowledge-synthesis/SKILL.md`

**Purpose:** Transform facts into understanding and actionable insights.

**When to use:**
- After research, before decisions
- Consolidating learnings
- Building mental models
- Creating documentation

**Key capabilities:**
- Pattern recognition
- Concept mapping
- Insight extraction
- Knowledge structuring

---

### 4. Strategic Planning

**Location:** `skills/strategic-planning/SKILL.md`

**Purpose:** Create actionable plans with clear milestones and success criteria.

**When to use:**
- Starting new projects
- Planning major features
- Organizing complex work
- Setting project direction

**Key capabilities:**
- Goal decomposition
- Milestone definition
- Resource planning
- Risk identification

---

### 5. Problem Decomposition

**Location:** `skills/problem-decomposition/SKILL.md`

**Purpose:** Break complex problems into manageable, independent sub-problems.

**When to use:**
- Facing overwhelming complexity
- Planning large refactors
- Designing system architecture
- Organizing work for parallel execution

**Key capabilities:**
- Dependency analysis
- Sub-problem identification
- Interface definition
- Parallel execution planning

---

### 6. Quality Assurance

**Location:** `skills/quality-assurance/SKILL.md`

**Purpose:** Systematic quality verification before shipping.

**When to use:**
- Before shipping anything
- Reviewing completed work
- Validating against requirements
- Final quality gate

**Key capabilities:**
- Checklist enforcement
- Edge case identification
- Regression testing
- Quality metrics

---

### 7. Communication Design

**Location:** `skills/communication-design/SKILL.md`

**Purpose:** Clear, effective communication for docs, explanations, and interfaces.

**When to use:**
- Writing documentation
- Explaining complex concepts
- Designing user interfaces
- Creating API documentation

**Key capabilities:**
- Audience analysis
- Information hierarchy
- Clarity optimization
- Feedback incorporation

---

### 8. Learning Accelerator

**Location:** `skills/learning-accelerator/SKILL.md`

**Purpose:** Fast learning paths for new technologies and concepts.

**When to use:**
- Learning new technologies
- Onboarding to new codebases
- Understanding new domains
- Building expertise quickly

**Key capabilities:**
- Learning path creation
- Concept prioritization
- Practice exercise design
- Progress tracking

---

### 9. Risk Assessment

**Location:** `skills/risk-assessment/SKILL.md`

**Purpose:** Identify and mitigate risks before they become problems.

**When to use:**
- Before decisions
- Reviewing plans
- Evaluating changes
- Pre-deployment checks

**Key capabilities:**
- Risk identification
- Impact analysis
- Mitigation planning
- Risk monitoring

---

### 10. Optimization Engine

**Location:** `skills/optimization-engine/SKILL.md`

**Purpose:** Make things faster, smaller, or cheaper without sacrificing quality.

**When to use:**
- Performance issues
- Cost reduction needs
- Resource optimization
- Efficiency improvements

**Key capabilities:**
- Bottleneck identification
- Optimization strategies
- Trade-off analysis
- Performance measurement

---

### 11. Context Manager

**Location:** `skills/context-manager/SKILL.md`

**Purpose:** Track state, manage attention, and maintain context across complex work.

**When to use:**
- Complex multi-task work
- Long-running investigations
- Context switching
- State restoration

**Key capabilities:**
- State tracking
- Context switching
- Attention management
- Restoration points

---

### 12. Meta-Cognition

**Location:** `skills/meta-cognition/SKILL.md`

**Purpose:** Think about thinking — evaluate your own reasoning and decision-making.

**When to use:**
- Before important decisions
- After unexpected outcomes
- When stuck on a problem
- Reviewing your own work

**Key capabilities:**
- Reasoning evaluation
- Bias identification
- Perspective shifting
- Self-correction

---

## Using Skills

Skills are automatically available after base installation. Reference them by name in your prompts:

```
Use the deep-research skill to investigate this API.
Apply the decision-framework to choose between these options.
Run the quality-assurance skill before we ship this.
```

## Skill Discovery

Skills are organized in the `~/.agent-os/skills/` directory:

```
~/.agent-os/skills/
├── deep-research/
│   └── SKILL.md
├── decision-framework/
│   └── SKILL.md
├── knowledge-synthesis/
│   └── SKILL.md
├── strategic-planning/
│   └── SKILL.md
├── problem-decomposition/
│   └── SKILL.md
├── quality-assurance/
│   └── SKILL.md
├── communication-design/
│   └── SKILL.md
├── learning-accelerator/
│   └── SKILL.md
├── risk-assessment/
│   └── SKILL.md
├── optimization-engine/
│   └── SKILL.md
├── context-manager/
│   └── SKILL.md
└── meta-cognition/
    └── SKILL.md
```

## Next Steps

- Learn about [Concepts](CONCEPTS.md) — profiles, standards, skills
- Explore the [Workflow Engine](WORKFLOW.md) for structured task handling
- See [FILE-STRUCTURE.md](FILE-STRUCTURE.md) for directory layout reference
