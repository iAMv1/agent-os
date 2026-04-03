# AgentOS Concepts

Core concepts that power the AgentOS system.

## Overview

AgentOS is built on several key concepts that work together to create a self-improving development system:

- **Profiles** — Reusable standards sets for different development contexts
- **Standards** — Documented patterns and conventions from your codebase
- **Skills** — Reusable capability modules for specific tasks
- **Workflows** — Structured sequences of phases for handling tasks
- **Ralph Loop** — Iterative self-improvement cycle
- **Superpowers** — Quality enforcement system

---

## Profiles

Profiles are reusable sets of standards tailored to specific development contexts.

### How Profiles Work

A profile defines:
- Which standards to install
- What other profiles to inherit from
- A description of when to use it

### Profile Inheritance

Profiles can inherit from other profiles, creating a chain:

```
web → javascript → default
```

When you install the `web` profile:
1. Standards from `default` are installed first
2. Standards from `javascript` override/add to default
3. Standards from `web` override/add to javascript

### Available Profiles

| Profile | Inherits | Standards |
|---------|----------|-----------|
| `default` | — | coding-standards, git-workflow, testing-standards |
| `python` | default | python-standards, pytest-workflow, type-hinting |
| `javascript` | default | typescript-standards, jest-workflow, eslint-rules |
| `web` | javascript | react-best-practices, component-patterns, accessibility |
| `api` | default | rest-conventions, api-documentation, authentication-patterns |

### Using Profiles

```bash
# Install with specific profile
~/.agent-os/scripts/project-install.sh --profile python

# List available profiles
cat ~/.agent-os/config.yml
```

---

## Standards

Standards are documented patterns and conventions extracted from your codebase.

### What Are Standards?

Standards capture:
- Naming conventions
- Code organization patterns
- Architecture decisions
- Testing approaches
- Git workflows
- Documentation practices

### Standards vs Skills

| Aspect | Standards | Skills |
|--------|-----------|--------|
| **Scope** | Project-specific | Universal |
| **Origin** | Extracted from codebase | Pre-built capabilities |
| **Purpose** | Enforce consistency | Enable capabilities |
| **Location** | `agent-os/standards/` | `skills/` or `~/.agent-os/skills/` |
| **Updates** | Run `/discover-standards` | Update AgentOS base |

### Standards Index

The `index.yml` file catalogs all standards in your project:

```yaml
# Agent OS Standards Index

root:
  coding-standards:
    description: General coding conventions
  git-workflow:
    description: Git branching and commit conventions

testing:
  unit-tests:
    description: Unit testing standards
  integration-tests:
    description: Integration testing approach
```

### Discovering Standards

Run `/discover-standards` to extract patterns from your codebase:

1. Scans your project structure
2. Identifies naming conventions
3. Documents architecture patterns
4. Creates standards files
5. Updates the index

### Injecting Standards

Run `/inject-standards` to deploy relevant standards:

1. Analyzes current task
2. Matches relevant standards
3. Loads them into context
4. Confirms active standards

---

## Skills

Skills are reusable capability modules that extend what your agent can do.

### Core Skills (12 of 27 total)

| Skill | Purpose |
|-------|---------|
| `deep-research` | Multi-source investigation |
| `decision-framework` | Structured decision evaluation |
| `knowledge-synthesis` | Transform facts into understanding |
| `strategic-planning` | Create actionable plans |
| `problem-decomposition` | Break complex problems down |
| `quality-assurance` | Systematic quality verification |
| `communication-design` | Clear communication patterns |
| `learning-accelerator` | Fast learning paths |
| `risk-assessment` | Identify and mitigate risks |
| `optimization-engine` | Make things faster/smaller/cheaper |
| `context-manager` | Track state, manage attention |
| `meta-cognition` | Think about thinking |

### Using Skills

Skills are automatically available after base installation. Reference them by name in your prompts:

```
Use the deep-research skill to investigate this API.
Apply the decision-framework to choose between these options.
```

---

## Ralph Loop

The Ralph Loop is an iterative self-improvement cycle:

```
Plan → Execute → Review → Learn → Improve → Plan → ...
```

### How It Works

1. **Plan** — Define what you're building and how you'll know it's good
2. **Execute** — Build using the best available approach
3. **Review** — Critically evaluate against standards
4. **Learn** — Extract lessons from what worked and what didn't
5. **Improve** — Update approach based on lessons learned
6. **Repeat** — Start next cycle with improved knowledge

### Why It Works

Each cycle produces better output because the agent learns from its own mistakes. The loop creates a continuous improvement cycle that compounds over time.

---

## Superpowers

Superpowers provides non-negotiable quality enforcement:

- **Iron Laws** — Absolute rules that override all other instructions
- **Hard Gates** — XML-tagged gates that block progression until conditions are met
- **Anti-Slop Rules** — Specific patterns to avoid (with good/bad examples)
- **Rationalization Tables** — Preemptive counters for agent self-justification
- **Checklist Enforcement** — TodoWrite items for each step

### Why Enforcement Matters

Without enforcement, agents skip steps when they think they "know better." Superpowers prevent this by making quality gates non-negotiable.

---

## Next Steps

- Read the [Installation Guide](INSTALLATION.md) for setup details
- Explore the [Workflow Engine](WORKFLOW.md) for structured task handling
- Browse the [Skills Catalog](SKILLS.md) for available capabilities
- See [FILE-STRUCTURE.md](FILE-STRUCTURE.md) for directory layout reference
