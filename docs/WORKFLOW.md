# Workflow Engine Guide

The AgentOS workflow engine analyzes any task and composes an optimal workflow using available capabilities.

## Overview

```
User Task → Task Classifier → Capability Registry → Workflow Composer → Execution Engine → Adaptation Layer
```

The workflow engine provides:

1. **Task Classification** — Analyzes task type, complexity, and domain
2. **Workflow Composition** — Selects and orders the right capabilities
3. **Execution** — Runs phases with parallel/sequential handling
4. **Adaptation** — Adjusts based on execution feedback

## Using the Workflow Engine

### CLI Usage

```bash
# Basic usage
python engines/workflow-engine.py "Build a REST API for a todo app"

# Fast mode (skip optional phases)
python engines/workflow-engine.py "Fix the login bug" --mode fast

# Thorough mode with JSON output
python engines/workflow-engine.py "Design the architecture" --mode thorough --output json
```

### Slash Command

In Claude Code or compatible agents:

```
/workflow Build a REST API for a todo app
```

## Workflow Templates

### 1. Requirements Gathering

**When to use:** Understanding what to build, clarifying ambiguous requirements

**Phases:**
1. Analyze existing context and codebase
2. Identify stakeholders and constraints
3. Define success criteria
4. Document requirements

### 2. Architecture & Design

**When to use:** Planning system structure, making technical decisions

**Phases:**
1. Analyze requirements
2. Identify components and relationships
3. Evaluate design alternatives
4. Document architecture decisions

### 3. Implementation

**When to use:** Building features, writing code

**Phases:**
1. Review specifications
2. Set up development environment
3. Implement core functionality
4. Add error handling and edge cases
5. Write tests
6. Review and refactor

### 4. Testing & QA

**When to use:** Quality verification, bug hunting

**Phases:**
1. Review test coverage
2. Write missing tests
3. Run test suite
4. Manual testing of critical paths
5. Performance testing
6. Document test results

### 5. Deployment & DevOps

**When to use:** Shipping code, infrastructure changes

**Phases:**
1. Review deployment checklist
2. Update dependencies
3. Run pre-deployment tests
4. Deploy to staging
5. Verify staging deployment
6. Deploy to production
7. Post-deployment verification

### 6. Maintenance & Monitoring

**When to use:** Bug fixes, performance improvements, ongoing support

**Phases:**
1. Analyze issue or metric
2. Identify root cause
3. Implement fix or improvement
4. Test the fix
5. Deploy and monitor

### 7. Full SDLC

**When to use:** End-to-end project work, greenfield development

**Phases:**
1. Requirements gathering
2. Architecture & design
3. Implementation
4. Testing & QA
5. Deployment
6. Maintenance planning

## Task Classification

The engine classifies tasks along three dimensions:

### Task Type
- **requirements_gathering** — Understanding what to build
- **architecture_design** — Planning system structure
- **implementation** — Building features and writing code
- **testing_qa** — Quality verification and bug hunting
- **deployment_devops** — Shipping code and infrastructure
- **maintenance_monitoring** — Bug fixes and ongoing support

### Complexity
- **Simple** — Clear task, known approach, < 1 hour
- **Medium** — Some unknowns, standard patterns, 1-4 hours
- **Complex** — Multiple unknowns, novel approach, > 4 hours

### Domain
- **Web** — Web applications, frontend frameworks
- **Mobile** — iOS, Android, React Native
- **Data ML** — Analytics, ML, data processing
- **DevOps** — Infrastructure, CI/CD, deployment
- **Security** — Auth, encryption, vulnerabilities
- **General** — Uncategorized tasks
- **CLI** — Command-line tools
- **API** — REST APIs, GraphQL, gRPC
- **Frontend** — UI, components, styling
- **Backend** — APIs, databases, services
- **Fullstack** — Multiple layers

## Adaptation Types

The engine can adapt workflows during execution:

1. **Capability Substitution** — Replace unavailable capability with alternative
2. **Phase Merge** — Combine phases for simple tasks
3. **Phase Split** — Break complex phases into sub-phases
4. **Timeout Adjustment** — Extend or reduce phase timeouts
5. **Retry Adjustment** — Change retry count on repeated failures
6. **Parallelism Change** — Adjust which phases run in parallel
7. **Workflow Switch** — Switch to a different workflow template
8. **Context Enrichment** — Add relevant context to phases

## Capability Registry

The registry catalogs 71 capabilities:

| Category | Count | Examples |
|----------|-------|---------|
| Tools | 35 | Bash, Read, Edit, Write, Grep, Glob, WebSearch |
| Agents | 11 | general-purpose, Explore, Plan, verification |
| Services | 11 | MCP, Compact, Memory, Plugin, Skill |
| Hooks | 5 | PreToolUse, PostToolUse, PermissionRequest |
| Commands | 9 | plan, agents, mcp, plugin, commit |

See `registry/capability-registry.json` for the complete registry.

## Next Steps

- Learn about [Concepts](CONCEPTS.md) — profiles, standards, skills
- Browse the [Skills Catalog](SKILLS.md) for available capabilities
- Read the [Installation Guide](INSTALLATION.md) for setup details
