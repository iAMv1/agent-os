---
description: Enables and configures the Magic Docs auto-documentation system. Creates magic doc files that auto-update in the background, providing living documentation that stays current with code changes.
when_to_use: When you want automatic documentation that updates as you work, or need to set up the magic documentation system.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
arguments:
  - action
  - target
argument-hint: "[enable|create|list|update] [file-path|all]"
---

# Magic Docs Enabler

Enables and configures the Magic Docs auto-documentation system. This system automatically maintains documentation files that update in the background as you work.

## Understanding Magic Docs

Based on source code analysis (`src/src/services/MagicDocs/magicDocs.ts`), Magic Docs is an auto-documentation system that:

1. **Detects** files with `# MAGIC DOC: [title]` header
2. **Monitors** conversation turns for relevant changes
3. **Updates** magic doc files in the background via forked subagent
4. **Preserves** documentation accuracy as code evolves

**Note**: In the original implementation, this is gated behind `USER_TYPE === 'ant'`. This skill implements the same functionality without the gate.

## Phase 1: Enable Magic Docs System

### Create Magic Docs Configuration

```bash
# Create magic docs configuration directory
mkdir -p ~/\.agent-os/magic-docs

# Create configuration
cat > ~/\.agent-os/magic-docs/config.json << 'EOF'
{
  "magicDocs": {
    "enabled": true,
    "autoUpdate": true,
    "updateTrigger": "on-conversation-turn",
    "maxDocs": 50,
    "updateInterval": "per-turn",
    "backgroundAgent": {
      "model": "haiku",
      "timeout": 300,
      "permissionMode": "acceptEdits"
    }
  }
}
EOF
```

## Phase 2: Create Magic Doc Files

### Magic Doc File Format

Magic doc files use a special header format:

```markdown
# MAGIC DOC: [Document Title]

## Purpose
[What this document tracks]

## Last Updated
[Timestamp]

## Content
[Auto-maintained content]
```

### Create a Magic Doc for Architecture

```bash
cat > "$PWD/ARCHITECTURE.md" << 'EOF'
# MAGIC DOC: System Architecture

## Purpose
Auto-maintained documentation of the system architecture, including components, data flow, and dependencies.

## Last Updated
$(date -u +%Y-%m-%dT%H:%M:%SZ)

## Components
[This section is auto-updated as components are added/modified]

## Data Flow
[This section is auto-updated as data flow changes]

## Dependencies
[This section is auto-updated as dependencies change]
EOF
```

### Create a Magic Doc for API

```bash
cat > "$PWD/API.md" << 'EOF'
# MAGIC DOC: API Documentation

## Purpose
Auto-maintained API documentation that stays current with code changes.

## Last Updated
$(date -u +%Y-%m-%dT%H:%M:%SZ)

## Endpoints
[This section is auto-updated as API endpoints change]

## Request/Response Formats
[This section is auto-updated as formats change]

## Authentication
[This section is auto-updated as auth changes]
EOF
```

### Create a Magic Doc for Changelog

```bash
cat > "$PWD/CHANGELOG.md" << 'EOF'
# MAGIC DOC: Changelog

## Purpose
Auto-maintained changelog that tracks all significant changes.

## Last Updated
$(date -u +%Y-%m-%dT%H:%M:%SZ)

## Recent Changes
[This section is auto-updated as changes are made]
EOF
```

## Phase 3: Magic Doc Update Instructions

### How Magic Docs Update

When working with magic doc files, instruct the AI to update them:

> "After making changes, update all MAGIC DOC files to reflect the current state."

The AI will:
1. Identify which magic docs are affected by the changes
2. Update the content to reflect the current state
3. Update the "Last Updated" timestamp
4. Preserve the magic doc header

### Manual Update Command

To manually update all magic docs:

> "Update all MAGIC DOC files in this project to reflect the current state of the codebase."

### Update Specific Magic Doc

To update a specific magic doc:

> "Update the MAGIC DOC file at [path] to reflect recent changes."

## Phase 4: Magic Doc Detection Script

Create a script to find all magic docs in a project:

```bash
cat > ~/\.agent-os/scripts/find-magic-docs.sh << 'SCRIPT'
#!/bin/bash
# Find all Magic Doc files in the current directory tree

echo "=== MAGIC DOCS ==="
found=0

while IFS= read -r -d '' file; do
  if head -1 "$file" | grep -q "^# MAGIC DOC:"; then
    title=$(head -1 "$file" | sed 's/^# MAGIC DOC: //')
    updated=$(grep "^## Last Updated" -A1 "$file" | tail -1)
    echo "  [MAGIC DOC] $title"
    echo "    Path: $file"
    echo "    Last Updated: $updated"
    echo ""
    found=$((found + 1))
  fi
done < <(find . -name "*.md" -type f -print0 2>/dev/null)

if [ $found -eq 0 ]; then
  echo "  No magic docs found."
  echo ""
  echo "To create a magic doc, add this header to any .md file:"
  echo "  # MAGIC DOC: [Document Title]"
fi

echo "Total: $found magic doc(s)"
SCRIPT
chmod +x ~/\.agent-os/scripts/find-magic-docs.sh
```

## Phase 5: Integration with Hooks

### Auto-Update Magic Docs on File Changes

Create a hook that triggers magic doc updates after file modifications:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "type": "prompt",
        "prompt": "If any files were modified, check if any MAGIC DOC files need updating. List any magic docs that should be updated and why.",
        "tools": ["Read", "Glob", "Grep"]
      }
    ]
  }
}
```

## Magic Doc Best Practices

1. **Use descriptive titles** - Make the title clear about what the doc tracks
2. **Keep scope focused** - Each magic doc should track one aspect of the project
3. **Update regularly** - Update magic docs after significant changes
4. **Use structured sections** - Organize content in clear sections for easy updating
5. **Preserve the header** - Always keep the `# MAGIC DOC:` header intact
6. **Include timestamps** - Track when docs were last updated
7. **Link to source** - Reference the source files the doc tracks

## Common Magic Doc Types

| Type | Purpose | Update Trigger |
|------|---------|----------------|
| Architecture | System structure | Component changes |
| API | API documentation | Endpoint changes |
| Changelog | Change history | Any significant change |
| Dependencies | Package dependencies | Dependency changes |
| Configuration | Config documentation | Config changes |
| Deployment | Deployment procedures | Deployment changes |
| Testing | Test coverage | Test changes |
| Security | Security posture | Security changes |

## Verification

```bash
# Find all magic docs
~/\.agent-os/scripts/find-magic-docs.sh

# Check magic docs config
cat ~/\.agent-os/magic-docs/config.json
```
