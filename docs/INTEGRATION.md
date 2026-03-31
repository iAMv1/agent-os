# Integration Guide

How to integrate AgentOS with any AI coding agent.

## Universal Integration (Works with Any Agent)

### Method 1: Copy Skills (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-org/agent-os.git
cd agent-os

# Copy skills to your agent's skill directory
cp -r skills/* <your-agent-skill-dir>/

# Copy the master orchestrator
cp skills/agent-os-master/SKILL.md <your-agent-skill-dir>/
```

### Method 2: Paste into System Prompt

If your agent doesn't support external skills:
1. Open the skill files you need
2. Paste their content into your system prompt
3. Reference them by name in your instructions

### Method 3: Project-Level Instructions

Copy `WORKER.md` (or equivalent) to your project root. Most agents read project-level instructions automatically.

## Agent-Specific Integration

### AI Coding Agent

```bash
# Skills
cp -r skills/* ~/\.agent-os/skills/

# Project instructions
cp WORKER.md .

# Workflow engine (optional)
cp -r engines/ .agent-os/engines/

# Session memory
mkdir -p .agent-os/memory .agent-os/session .agent-os/cache
```

### Cursor

```bash
# Rules (Cursor reads .cursor/rules/)
cp -r skills/* .cursor/rules/

# Project instructions
cp WORKER.md .cursorrules
```

### Codex (OpenAI)

```bash
# Skills
cp -r skills/* .codex/skills/

# Project instructions
cp WORKER.md .codex/WORKER.md
```

### Cline / Roo Code

```bash
# Custom instructions
cp WORKER.md .clinerules

# Skills (if supported)
cp -r skills/* .cline/skills/
```

### Continue

```bash
# Custom instructions
cp WORKER.md .continue/instructions.md
```

### Aider

```bash
# Aider reads .aider.conf.yml for instructions
# Add skill content to your .aider.instructions.md
cp WORKER.md .aider.instructions.md
```

### Devin / Other Cloud Agents

For cloud-based agents:
1. Create a `.agent-os/` directory in your project
2. Copy skills there
3. Reference them in your project instructions

## Workflow Engine Integration

The workflow engine is a Python script that works with any agent:

```bash
# Install Python 3.8+
python --version

# Run the workflow engine
python engines/workflow-engine.py "Build a REST API"

# Get JSON output for programmatic use
python engines/workflow-engine.py "Build a REST API" --output json
```

### Using with Any Agent

1. **Run the engine** to get a workflow plan
2. **Give the plan** to your agent as instructions
3. **Agent executes** the workflow phases
4. **Engine adapts** based on execution feedback

## Skill Format Compatibility

AgentOS skills use a universal format compatible with all major agents:

```yaml
---
name: skill-name
description: When to use this skill
allowed-tools: Read, Write, Edit, Bash
arguments:
  - arg1
  - arg2
---

# Skill Name

## The Iron Law
[Absolute rule]

## When to Use
[Trigger conditions]

## The Process
[Step-by-step instructions]
```

### Compatibility Matrix

| Agent | Frontmatter | Body | Hooks | Shell Exec |
|-------|-------------|------|-------|------------|
| **AI Coding Agent** | Full support | Full support | Full | Full |
| **Cursor** | Partial | Full support | No | No |
| **Codex** | Partial | Full support | No | No |
| **Cline** | Partial | Full support | No | No |
| **Aider** | No | Full support | No | No |
| **Continue** | No | Full support | No | No |

**Note**: All agents support the body content. Frontmatter support varies but is not required — skills work even without frontmatter.

## Customization

### Adding Your Own Skills

1. Create a directory: `skills/my-skill/`
2. Create `SKILL.md` with the standard format
3. Copy to your agent's skill directory

### Modifying Existing Skills

1. Edit the skill file in `skills/`
2. Copy to your agent's skill directory
3. Changes take effect on next session

### Creating Skill Packs

Group related skills into packs:
```bash
mkdir -r skills/my-pack/
cp skills/deep-research skills/my-pack/
cp skills/knowledge-synthesis skills/my-pack/
cp skills/decision-framework skills/my-pack/
```

## Troubleshooting

### Skills Not Loading
- Check that the skill file is named `SKILL.md`
- Check that the skill is in the correct directory
- Check that your agent supports skill loading

### Skills Not Triggering
- Check the `description` field — it should contain trigger conditions
- Check the `when_to_use` field — it should describe when to use the skill
- Try invoking the skill manually by name

### Workflow Engine Not Running
- Check Python version: `python --version` (need 3.8+)
- Check that all engine files are present
- Check file permissions: `chmod +x engines/workflow-engine.py`
