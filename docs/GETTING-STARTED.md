# Getting Started with AgentOS

Quick start guide to get AgentOS up and running in 5 minutes.

## What is AgentOS?

AgentOS is a universal AI agent operating system that transforms any AI coding agent into a high-performance, self-improving development system. It combines three proven systems:

1. **Ralph Loop** — Iterative self-improvement through continuous feedback
2. **Superpowers** — Iron-law quality enforcement
3. **Workflow Engine** — Dynamic task decomposition

## Prerequisites

- An AI coding agent (Claude Code, Cursor, Codex, etc.)
- Git (for installation)
- Bash shell (Unix/macOS) or PowerShell (Windows)

## Quick Start

### Step 1: Install AgentOS Base

**Unix/macOS:**
```bash
git clone https://github.com/your-org/agent-os.git ~/agent-os
cd ~/agent-os
./scripts/install-base.sh
```

**Windows (PowerShell):**
```powershell
git clone https://github.com/your-org/agent-os.git $env:USERPROFILE\agent-os
cd $env:USERPROFILE\agent-os
.\scripts\install-base.ps1
```

This creates `~/.agent-os/` with:
- Skills directory
- Workflow engines
- Configuration
- Session memory

### Step 2: Install into Your Project

Navigate to your project directory and run:

**Unix/macOS:**
```bash
cd /path/to/your/project
~/.agent-os/scripts/project-install.sh
```

**Windows (PowerShell):**
```powershell
cd \path\to\your\project
$env:USERPROFILE\.agent-os\scripts\project-install.ps1
```

This creates:
- `agent-os/standards/` — Your project's coding standards
- `agent-os/standards/index.yml` — Index for standard matching
- `.agent-os/` — Runtime data (memory, sessions, cache)

### Step 3: Start Using AgentOS

Once installed, you can use the slash commands:

- `/discover-standards` — Extract patterns from your codebase
- `/inject-standards` — Deploy standards into your context
- `/shape-spec` — Create better specifications
- `/ralph-loop` — Start self-improvement cycle
- `/workflow` — Compose and execute workflow

## Next Steps

- Read the [Installation Guide](INSTALLATION.md) for detailed setup options
- Learn about [Profiles](CONCEPTS.md#profiles) for different development contexts
- Explore the [Workflow Engine](WORKFLOW.md) for structured task handling
- Browse the [Skills Catalog](SKILLS.md) for available capabilities

## Troubleshooting

### "Base installation not found"
Run the base installation script first:
```bash
~/.agent-os/scripts/install-base.sh
```

### "Profile not found"
Check your `config.yml` and ensure the profile exists in `~/.agent-os/profiles/`

### Commands not working
Make sure you've run the project installation in your project directory.

## Need Help?

- Check [INSTALLATION.md](INSTALLATION.md) for detailed setup
- Review [CONCEPTS.md](CONCEPTS.md) for understanding the system
- See [FILE-STRUCTURE.md](FILE-STRUCTURE.md) for directory layout reference
