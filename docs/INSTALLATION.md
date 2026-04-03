# Installation Guide

Complete guide for installing AgentOS on your system and in your projects.

## Two-Part Installation

AgentOS has two parts:

1. **Base Installation** — Lives in your home directory (`~/.agent-os/`). Holds your profiles, scripts, commands, and configuration.
2. **Project Installation** — Lives in your project (`your-project/agent-os/`). Holds standards, specs, and runtime data specific to that project.

This separation lets you maintain standards across multiple projects while keeping each project self-contained.

---

## Step 1: Base Installation

Get AgentOS into your home directory using one of these methods:

### Option A: Git Clone (Recommended)

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

### Option B: Download ZIP

1. Download the ZIP from GitHub (Code → Download ZIP)
2. Extract the contents
3. Move the extracted folder to your home directory and rename it to `agent-os`
4. Run the installation script

### What Gets Installed

The base installation creates `~/.agent-os/` with:

| Directory | Purpose |
|-----------|---------|
| `cache/` | File hash deduplication cache |
| `mcp/` | MCP server configurations |
| `memory/` | Session memory files |
| `sessions/` | Session state data |
| `standards/` | Base standards templates |
| `skills/` | Universal skills (27 total) |
| `engines/` | Workflow engine (Python) |
| `commands/agent-os/` | Slash commands |
| `config.yml` | Configuration with profiles |

### Installation Script Options

```bash
# Show verbose output
./scripts/install-base.sh --verbose

# Show help
./scripts/install-base.sh --help
```

---

## Step 2: Project Installation

Navigate to your project directory and run the installation script:

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

**Windows Users Note:** Use the PowerShell script `project-install.ps1` for native Windows support. No WSL or Git Bash required.

### What Gets Installed

The project installation creates:

| Directory/File | Purpose |
|----------------|---------|
| `agent-os/standards/` | Your project's coding standards |
| `agent-os/standards/index.yml` | Index for standard matching |
| `.agent-os/` | Runtime data (memory, sessions, cache) |
| `.claude/commands/agent-os/` | Slash commands for Claude Code |
| `WORKER.md` | Project instructions (if not exists) |

### Using a Specific Profile

To install with a specific profile:

```bash
~/.agent-os/scripts/project-install.sh --profile python
```

Available profiles (from `config.yml`):
- `default` — General development
- `python` — Python development
- `javascript` — JavaScript/TypeScript development
- `web` — Web development (inherits from javascript)
- `api` — API development

### Commands Only

To update only the commands (preserving existing standards):

```bash
~/.agent-os/scripts/project-install.sh --commands-only
```

### Verbose Output

To see detailed installation output:

```bash
~/.agent-os/scripts/project-install.sh --verbose
```

---

## Configuration

### config.yml

The configuration file controls AgentOS behavior:

```yaml
default_profile: default

profiles:
  default:
    description: "Default profile for general development"
    inherits: []
    standards:
      - coding-standards
      - git-workflow
      - testing-standards
  
  python:
    description: "Python development profile"
    inherits:
      - default
    standards:
      - python-standards
      - pytest-workflow
      - type-hinting
```

### Profile Inheritance

Profiles can inherit from other profiles, creating a chain:

```
web → javascript → default
```

When you install the `web` profile, you get standards from:
1. `default` (base)
2. `javascript` (inherits from default)
3. `web` (inherits from javascript)

Later profiles override earlier ones if there are conflicts.

---

## Updating AgentOS

### Update Base Installation

```bash
cd ~/agent-os
git pull
./scripts/install-base.sh
```

### Update Project Installation

```bash
cd /path/to/your/project
~/.agent-os/scripts/project-install.sh --commands-only
```

### Update Standards

To refresh standards from your profile:

```bash
~/.agent-os/scripts/project-install.sh --profile default
```

Note: This will prompt before overwriting existing standards.

---

## Manual Installation

If you prefer not to use the scripts, you can install manually:

### Manual Base Installation

```bash
# Create base structure
mkdir -p ~/.agent-os/{cache,mcp,memory,sessions,standards,skills}

# Copy skills
cp -r agent-os/skills/deep-research ~/.agent-os/skills/
cp -r agent-os/skills/decision-framework ~/.agent-os/skills/
# ... copy other skills

# Copy engines
cp -r agent-os/engines ~/.agent-os/engines

# Copy config
cp agent-os/config.yml ~/.agent-os/config.yml
```

### Manual Project Installation

```bash
# Create project structure
mkdir -p agent-os/standards
mkdir -p .agent-os/{memory,sessions,cache}

# Copy standards from profile
cp -r ~/.agent-os/profiles/default/standards/* agent-os/standards/

# Create index
echo "# Agent OS Standards Index" > agent-os/standards/index.yml
```

---

## Next Steps

- Run `/discover-standards` to extract patterns from your codebase
- Run `/inject-standards` to deploy standards into your context
- Read about [Profiles and Standards](CONCEPTS.md)
- Explore the [Workflow Engine](WORKFLOW.md)
