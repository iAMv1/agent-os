# AgentOS

> **Universal AI Agent Operating System** — A complete framework for transforming any AI coding agent into a high-performance, self-improving development system.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-21-blue)](skills/)
[![Workflows](https://img.shields.io/badge/workflows-7-green)](workflows/)
[![Capabilities](https://img.shields.io/badge/capabilities-71-orange)](registry/capability-registry.json)

## What Is This?

AgentOS is a **complete operating system for AI coding agents**. It combines three proven systems into one unified framework:

1. **Ralph Loop** — Iterative self-improvement through continuous feedback cycles
2. **Superpowers** — Iron-law enforcement, hard gates, and anti-slop patterns
3. **Adaptive Workflow Engine** — Dynamic task decomposition and capability composition

The result: **any AI coding agent** (AI Coding Agent, Cursor, Codex, Devin, Aider, or any LLM-based agent) can be upgraded to operate at the level of the most advanced internal systems.

## Quick Start

### For Any AI Coding Agent

1. **Copy the skills** to your agent's skill directory
2. **Copy the WORKER.md** (or equivalent system prompt) to your project root
3. **Start using** — no configuration needed

```bash
# For AI Coding Agent
cp -r skills/* ~/\.agent-os/skills/
cp WORKER.md .

# For Cursor
cp -r skills/* .cursor/rules/

# For Codex
cp -r skills/* .codex/skills/

# For any agent with skill support
cp -r skills/* <agent-skill-dir>/
```

### For Developers

```bash
git clone https://github.com/your-org/agent-os.git
cd agent-os
python engines/workflow-engine.py --help
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        AGENT OS                                  │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Ralph Loop   │  │ Superpowers  │  │ Adaptive Workflow    │  │
│  │              │  │              │  │                      │  │
│  │ • Iterate    │  │ • Iron Laws  │  │ • Task Classifier    │  │
│  │ • Improve    │  │ • Hard Gates │  │ • Capability Registry│  │
│  │ • Self-Correct│ │ • Anti-Slop  │  │ • Workflow Composer  │  │
│  │ • Learn      │  │ • Checklists │  │ • Execution Engine   │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    Universal Skills                       │   │
│  │                                                           │   │
│  │  deep-research │ decision-framework │ knowledge-synthesis │   │
│  │  strategic-planning │ problem-decomposition │ quality-assurance │   │
│  │  communication-design │ learning-accelerator │ risk-assessment │   │
│  │  optimization-engine │ context-manager │ meta-cognition │   │
│  │  + 9 capability-unlocker skills                           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Agent-Agnostic Protocol                     │   │
│  │                                                           │   │
│  │  Works with: AI Coding Agent, Cursor, Codex, Devin, Aider,   │   │
│  │  Continue, Cline, Roo Code, and any LLM-based agent      │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Ralph Loop (Iterative Self-Improvement)

The Ralph Loop pattern creates a **continuous improvement cycle**:

```
Plan → Execute → Review → Learn → Improve → Plan → ...
```

**How it works:**
1. **Plan**: Define what you're building and how you'll know it's good
2. **Execute**: Build it using the best available approach
3. **Review**: Critically evaluate the output against standards
4. **Learn**: Extract lessons from what worked and what didn't
5. **Improve**: Update your approach based on lessons learned
6. **Repeat**: Start the next cycle with improved knowledge

**Key insight**: Each cycle produces better output than the last because the agent learns from its own mistakes.

### 2. Superpowers (Enforcement System)

Superpowers provides **non-negotiable quality enforcement**:

- **Iron Laws**: Absolute rules that override all other instructions
- **Hard Gates**: XML-tagged gates that block progression until conditions are met
- **Anti-Slop Rules**: Specific patterns to avoid (with good/bad examples)
- **Rationalization Tables**: Preemptive counters for agent self-justification
- **Red Flag Lists**: Specific thought patterns that signal rule violations
- **Checklist Enforcement**: TodoWrite items for each step

**Key insight**: Without enforcement, agents skip steps when they think they "know better." Superpowers prevent this.

### 3. Adaptive Workflow Engine (Dynamic Task Handling)

The workflow engine **analyzes any task and composes the optimal workflow**:

```
User Task → Task Classifier → Capability Registry → Workflow Composer → Execution Engine → Adaptation Layer
```

**7 workflow templates:**
- Requirements Gathering
- Architecture & Design
- Implementation
- Testing & QA
- Deployment & DevOps
- Maintenance & Monitoring
- Full SDLC Lifecycle

**Key insight**: Instead of one-size-fits-all, the engine adapts its approach based on task type, complexity, domain, and available capabilities.

## Universal Skills (21 Total)

### Core Skills (12)

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| [deep-research](skills/deep-research/SKILL.md) | Multi-source investigation | Researching complex topics |
| [decision-framework](skills/decision-framework/SKILL.md) | Structured decision evaluation | Choosing between options |
| [knowledge-synthesis](skills/knowledge-synthesis/SKILL.md) | Transform facts into understanding | After research, before decisions |
| [strategic-planning](skills/strategic-planning/SKILL.md) | Create actionable plans | Starting new projects |
| [problem-decomposition](skills/problem-decomposition/SKILL.md) | Break complex problems down | Facing overwhelming complexity |
| [quality-assurance](skills/quality-assurance/SKILL.md) | Systematic quality verification | Before shipping anything |
| [communication-design](skills/communication-design/SKILL.md) | Clear communication | Writing docs, explaining concepts |
| [learning-accelerator](skills/learning-accelerator/SKILL.md) | Fast learning paths | Learning new technologies |
| [risk-assessment](skills/risk-assessment/SKILL.md) | Identify and mitigate risks | Before decisions, reviewing plans |
| [optimization-engine](skills/optimization-engine/SKILL.md) | Make things faster/smaller/cheaper | Performance issues, cost reduction |
| [context-manager](skills/context-manager/SKILL.md) | Track state, manage attention | Complex multi-task work |
| [meta-cognition](skills/meta-cognition/SKILL.md) | Think about thinking | Before important decisions |

### Capability Unlocker Skills (9)

| Skill | Purpose |
|-------|---------|
| [capability-unlocker](skills/capability-unlocker/SKILL.md) | Automate unlocking all available capabilities |
| [feature-flag-dumper](skills/feature-flag-dumper/SKILL.md) | Dump complete feature flag state |
| [system-prompt-extractor](skills/system-prompt-extractor/SKILL.md) | Extract full system prompt |
| [hook-interceptor](skills/hook-interceptor/SKILL.md) | Intercept tool execution via hooks |
| [tool-permission-manipulator](skills/tool-permission-manipulator/SKILL.md) | Maximize tool access |
| [agent-capability-enhancer](skills/agent-capability-enhancer/SKILL.md) | Maximize agent capabilities |
| [magic-docs-enabler](skills/magic-docs-enabler/SKILL.md) | Auto-documentation system |
| [plugin-capability-injector](skills/plugin-capability-injector/SKILL.md) | Inject capabilities via plugins |
| [enhanced-debug](skills/enhanced-debug/SKILL.md) | Extended debugging capabilities |

## Integration Guide

### AI Coding Agent

```bash
# Copy skills
cp -r skills/* ~/\.agent-os/skills/

# Copy project instructions
cp WORKER.md .

# Copy workflow engine
cp -r engines/ .agent-os/engines/
```

### Cursor

```bash
# Copy as rules
cp -r skills/* .cursor/rules/

# Copy project instructions
cp WORKER.md .cursorrules
```

### Codex (OpenAI)

```bash
# Copy as skills
cp -r skills/* .codex/skills/

# Copy project instructions
cp WORKER.md .codex/WORKER.md
```

### Any Agent with Skill Support

```bash
# Copy skills to agent's skill directory
cp -r skills/* <agent-skill-dir>/

# Copy project instructions
cp WORKER.md <project-root>/
```

### Agents Without Skill Support

For agents that don't support external skills:
1. **Paste the skill content** directly into your system prompt
2. **Use the WORKER.md** as your project-level instructions
3. **Reference skills by name** — the agent will follow the patterns

## Capability Registry

The registry catalogs **71 capabilities** that any agent can use:

- **35 tools**: Bash, Read, Edit, Write, Grep, Glob, WebSearch, WebFetch, Agent, etc.
- **11 agents**: general-purpose, Explore, Plan, verification, agent-code-guide, etc.
- **11 services**: MCP, Compact, Memory, Plugin, Skill, Hook, API, Analytics, etc.
- **5 hooks**: PreToolUse, PostToolUse, PermissionRequest, IDE-Integration, Swarm-Permission
- **9 commands**: plan, agents, mcp, plugin, commit, diff, review, compact, model

See [registry/capability-registry.json](registry/capability-registry.json) for the complete registry.

## Workflow Engine

The workflow engine is a Python-based system that:
1. **Classifies** any task by type, complexity, and domain
2. **Composes** an optimal workflow from available capabilities
3. **Executes** the workflow with parallel/sequential phases
4. **Adapts** dynamically based on execution feedback

```bash
python engines/workflow-engine.py "Build a REST API for a todo app"
python engines/workflow-engine.py "Fix the login bug" --mode fast
python engines/workflow-engine.py "Design the architecture" --mode thorough --output json
```

## Why This Works

### The Research Behind AgentOS

This system is built on **deep reverse-engineering** of the most advanced AI coding agent runtime system (~1900 files, ~500k LOC). We:

1. **Recovered 552 original source files** from compiled artifacts
2. **Audited ~90 feature flags** and ~100+ capability gates
3. **Modified 48+ source files** to unlock hidden capabilities
4. **Analyzed every skill format** across 5 different agent systems
5. **Built and tested** the adaptive workflow engine on real tasks

### What Makes This Different

| Feature | Typical Agent | AgentOS |
|---------|--------------|---------|
| **Task handling** | One-size-fits-all | Adapts to task type, complexity, domain |
| **Quality enforcement** | Hope the agent does well | Iron laws, hard gates, checklists |
| **Self-improvement** | None | Ralph Loop: iterate, learn, improve |
| **Context management** | Loses track of state | Structured memory, dedup, restoration points |
| **Parallel execution** | Sequential only | Fork agents for independent tasks |
| **Tool usage** | Bash for everything | Dedicated tools with proper permissions |
| **Decision making** | Gut feeling | Weighted scoring, pre-mortem, sensitivity analysis |

## License

MIT — Use freely, modify freely, distribute freely.

## Contributing

Contributions welcome! See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

## Acknowledgments

- **Ralph Loop** — Inspired by the iterative self-improvement pattern
- **Superpowers** — Inspired by the iron-law enforcement system
- **AI Coding Agent** — The runtime system that inspired this research
- **The open-source AI agent community** — For pushing the boundaries of what's possible
