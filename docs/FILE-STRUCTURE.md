# File Structure Reference

Complete reference for AgentOS directory layout.

## Base Installation (`~/.agent-os/`)

```
~/.agent-os/
├── cache/                    # File hash deduplication cache
│   └── file-hashes.json     # Hash map for read deduplication
├── mcp/                      # MCP server configurations
│   └── servers.yml          # MCP server definitions
├── memory/                   # Session memory files
│   └── session-memory.md    # Current session memory
├── sessions/                 # Session state data
│   └── current-state.md     # Current session state
├── standards/                # Base standards templates
│   └── *.md                 # Standard markdown files
├── skills/                   # Universal skills
│   ├── deep-research/
│   ├── decision-framework/
│   ├── knowledge-synthesis/
│   ├── strategic-planning/
│   ├── problem-decomposition/
│   ├── quality-assurance/
│   ├── communication-design/
│   ├── learning-accelerator/
│   ├── risk-assessment/
│   ├── optimization-engine/
│   ├── context-manager/
│   └── meta-cognition/
├── engines/                  # Workflow engine (Python)
│   ├── workflow-engine.py   # CLI entry point
│   ├── task_classifier.py   # Task classification
│   ├── capability_registry.py # 71 capabilities
│   ├── workflow_composer.py  # Workflow composition
│   ├── execution_engine.py   # Phase execution
│   └── adaptation_layer.py   # Dynamic adaptation
├── commands/                 # Slash commands
│   └── agent-os/
│       ├── discover-standards.md
│       ├── inject-standards.md
│       ├── shape-spec.md
│       ├── ralph-loop.md
│       └── workflow.md
├── profiles/                 # Profile definitions
│   ├── default/
│   │   └── standards/       # Default standards
│   ├── python/
│   │   └── standards/       # Python-specific standards
│   ├── javascript/
│   │   └── standards/       # JavaScript-specific standards
│   ├── web/
│   │   └── standards/       # Web-specific standards
│   └── api/
│       └── standards/       # API-specific standards
└── config.yml               # Configuration file
```

## Project Installation (`your-project/`)

```
your-project/
├── agent-os/                 # Project-specific AgentOS data
│   └── standards/           # Project standards
│       ├── index.yml        # Standards index
│       ├── coding-standards.md
│       ├── git-workflow.md
│       └── testing-standards.md
├── .agent-os/               # Runtime data
│   ├── cache/               # File hash cache
│   ├── memory/              # Session memory
│   │   └── session-memory.md
│   └── sessions/            # Session state
│       └── current-state.md
├── .claude/                 # Claude Code data
│   └── commands/
│       └── agent-os/        # Installed slash commands
│           ├── discover-standards.md
│           ├── inject-standards.md
│           ├── shape-spec.md
│           ├── ralph-loop.md
│           └── workflow.md
└── WORKER.md                # Project instructions
```

## AgentOS Source Repository

```
agent-os/                    # Source repository
├── README.md                # Project README (concise, marketing-focused)
├── LICENSE                  # MIT License
├── WORKER.md                # Project instructions template
├── config.yml               # Configuration with profiles
├── scripts/                 # Installation scripts
│   ├── install-base.sh      # Unix base installation
│   ├── install-base.ps1     # Windows base installation
│   ├── project-install.sh   # Unix project installation
│   └── project-install.ps1  # Windows project installation
├── docs/                    # Documentation
│   ├── GETTING-STARTED.md   # Quick start guide
│   ├── INSTALLATION.md      # Full installation guide
│   ├── WORKFLOW.md          # Workflow engine usage
│   ├── CONCEPTS.md          # Concepts hub
│   ├── STANDARDS.md         # Standards deep dive
│   ├── FILE-STRUCTURE.md    # This file
│   ├── SKILLS.md            # Skills catalog
│   ├── ARCHITECTURE-PATTERNS.md
│   ├── COMPLETE-SYSTEM-INTEGRATION.md
│   ├── CONTRIBUTING.md
│   ├── INTEGRATION.md
│   └── ...                  # Other architecture docs
├── commands/                # Slash commands source
│   └── agent-os/
├── profiles/                # Profile definitions source
│   ├── default/standards/
│   ├── python/standards/
│   ├── javascript/standards/
│   ├── web/standards/
│   └── api/standards/
├── skills/                  # Skills source
│   ├── deep-research/
│   ├── decision-framework/
│   └── ...                  # Other skills
├── engines/                 # Workflow engine source
│   ├── workflow-engine.py
│   ├── task_classifier.py
│   ├── capability_registry.py
│   ├── workflow_composer.py
│   ├── execution_engine.py
│   └── adaptation_layer.py
├── registry/                # Capability registry
│   └── capability-registry.json
└── templates/               # Template files
```

## Key Files

| File | Purpose |
|------|---------|
| `config.yml` | Main configuration with profile definitions |
| `agent-os/standards/index.yml` | Standards index for the project |
| `.agent-os/memory/session-memory.md` | Current session memory |
| `.agent-os/memory/session-memory.md` | Current session memory |
| `WORKER.md` | Project instructions for the agent |

## Directory Purposes

| Directory | Purpose | Created By |
|-----------|---------|------------|
| `~/.agent-os/` | Base installation | `install-base.sh` |
| `agent-os/` | Project standards | `project-install.sh` |
| `.agent-os/` | Runtime data | `project-install.sh` |
| `.claude/commands/agent-os/` | Slash commands | `project-install.sh` |

## Next Steps

- Read about [Concepts](CONCEPTS.md) — profiles, standards, skills
- See the [Installation Guide](INSTALLATION.md) for setup details
- Explore the [Workflow Engine](WORKFLOW.md) for task handling
