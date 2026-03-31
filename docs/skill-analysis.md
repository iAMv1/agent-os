# Comprehensive Skill Structure Analysis

> Analyzed across 5 sources: Bundled Skills (TypeScript), Skills Folder (SKILL.md), Superpowers Skills, KiloCode Skills, and Codex System Skills.

---

## 1. All Skill Format Patterns Found

### 1.1 TypeScript Bundled Skills (src/skills/bundled/)

**Registration Pattern:**
```typescript
registerBundledSkill({
  name: 'skill-name',
  description: 'One-line description',
  whenToUse: 'Detailed trigger conditions',
  allowedTools: ['Read', 'Grep'],
  argumentHint: '[args]',
  userInvocable: true,
  disableModelInvocation: true,
  isEnabled: () => boolean,
  async getPromptForCommand(args, context) {
    // Dynamic prompt generation
    return [{ type: 'text', text: prompt }]
  },
})
```

**Frontmatter-equivalent fields (in code):**
| Field | Purpose | Required |
|-------|---------|----------|
| `name` | Skill identifier | Yes |
| `description` | Short description for triggering | Yes |
| `whenToUse` | Detailed auto-trigger conditions | No |
| `allowedTools` | Tool permission whitelist | No |
| `argumentHint` | CLI argument hint | No |
| `userInvocable` | Can user invoke via /command | No (default false) |
| `disableModelInvocation` | Skip model for description | No |
| `isEnabled` | Runtime visibility gate | No |
| `getPromptForCommand` | Dynamic prompt builder | Yes |
| `files` | Referenced file map | No |

**Key Patterns:**
- **Dynamic content generation**: All prompts are built at runtime with `getPromptForCommand`
- **Runtime detection**: Language detection (`claudeApi.ts`), git repo checks (`batch.ts`), feature flag gates (`scheduleRemoteAgents.ts`)
- **Lazy loading**: Large content loaded on demand via `import()` (`claudeApi.ts`)
- **Template substitution**: `{{var}}` placeholders replaced at runtime (`skillify.ts`, `claudeApi.ts`)
- **Multi-file bundling**: `SKILL_FILES` map for reference docs (`claudeApiContent.ts`, `verifyContent.ts`)
- **Context injection**: Session memory, user messages, environment state passed into prompts

**Sub-patterns by skill type:**
| Type | Example | Pattern |
|------|---------|---------|
| **Command skill** | `/batch`, `/loop`, `/debug` | Parse args → build prompt → return |
| **Auto-trigger skill** | `agent-api` | Description contains TRIGGER conditions |
| **Config skill** | `update-config` | Dynamic schema generation + static docs |
| **Multi-phase skill** | `batch`, `simplify` | Phase-based instructions with agent spawning |
| **Diagnostic skill** | `stuck`, `debug` | Read system state → analyze → report |
| **Meta skill** | `skillify` | Interview → analyze → write SKILL.md |

### 1.2 Skills Folder (skills/)

**Frontmatter format:**
```yaml
---
name: Skill Name
description: One-line description
allowed-tools: Read, Glob, Grep
metadata:
  author: vercel
  version: "1.0.0"
  argument-hint: <file-or-pattern>
---
```

**Body structure patterns:**
| Pattern | Example | Structure |
|---------|---------|-----------|
| **Reference docs** | `01-main-system-prompt` | Sections with code blocks, edge cases, self-improvement protocol |
| **Permission system** | `06-permission-system` | Modes → rules → sources → flow → edge cases |
| **Feature flags** | `19-feature-flags` | Table of flags → access patterns → constants |
| **Hunter skills** | `reverse_engineering_hunter` | Input → Process → Classification → Known database → Output format → Anti-slop rules |
| **Communication** | `brainstorming` | Gates → Dynamic questions → Progress reporting → Error handling → Principles |
| **Guidelines** | `web-design-guidelines` | How it works → Source URL → Usage flow |

**Root-level agent skills (.md files):**
```yaml
---
name: backend-specialist
description: Expert backend architect...
tools: Read, Grep, Glob, Bash, Edit, Write
model: inherit
skills: clean-code, nodejs-best-practices, ...
---
```

These add `tools`, `model`, and `skills` fields for agent composition.

### 1.3 Superpowers Skills

**Frontmatter:**
```yaml
---
name: skill-name
description: Use when [specific triggering conditions]
---
```

Only two fields: `name` and `description`. Max 1024 chars total.

**Body structure:**
```
# Skill Name

## Overview
What + Core principle

## When to Use
Symptoms and use cases

## The Iron Law
NO [BAD THING] WITHOUT [GOOD THING] FIRST

## The Process / Phases
Numbered phases with steps

## Red Flags
Table of rationalizations → reality

## Quick Reference
Table for scanning

## Common Mistakes
Problem → Fix

## Integration
Related skills
```

**Unique enforcement patterns:**
- `<HARD-GATE>` XML tags for non-negotiable gates
- `<Good>` / `<Bad>` comparison blocks
- `digraph` flowcharts in DOT notation
- "Iron Law" code blocks for absolute rules
- Rationalization tables (excuse → reality)
- Red flag lists with STOP instructions

### 1.4 KiloCode Skills

**Frontmatter:**
```yaml
---
name: skill-name
description: Description with triggers
license: Complete terms in LICENSE.txt
metadata:
  category: development
  source:
    repository: https://github.com/...
    path: skill-name
---
```

Adds `license` and `metadata` (category, source repository).

**Body patterns:**
- Phase-based workflows (Phase 1-4)
- Heavy use of emoji section markers (🚀, 🔍, 📋)
- Inline code examples with language variants
- Reference file linking (`[🐍 Python Guide](./reference/...)`)
- XML output formats for evaluations
- Example workflows with user/agent dialogue

### 1.5 Codex System Skills

**Frontmatter:**
```yaml
---
name: "imagegen"
description: "Long comprehensive description..."
metadata:
  short-description: Create or update a skill
---
```

**Directory structure:**
```
skill-name/
├── SKILL.md (required)
├── agents/openai.yaml (UI metadata)
├── scripts/ (executable code)
├── references/ (documentation for context loading)
└── assets/ (output files, templates)
```

**Key concepts:**
- **Progressive Disclosure**: 3-level loading (metadata → SKILL.md → resources)
- **Degrees of Freedom**: High/Medium/Low specificity levels
- **Context window as public good**: Every token has a cost
- **Subagent validation**: Forward-testing without leaking context

---

## 2. Best Practices from Each Source

### 2.1 Bundled Skills (TypeScript)

1. **Dynamic prompt generation**: Build prompts at runtime with actual system state (git status, connected MCP servers, environments)
2. **Lazy loading**: Import large content only when skill is invoked
3. **Template substitution**: Use `{{var}}` placeholders for runtime values
4. **Runtime gating**: `isEnabled()` callbacks for feature flags and environment checks
5. **Context injection**: Pass session memory, user messages, and environment into prompts
6. **Multi-file bundling**: Bundle reference docs as string maps for selective inclusion
7. **Error messages as prompts**: Return user-friendly error messages when preconditions fail
8. **Argument parsing**: Built-in parsing logic for complex command formats (e.g., `/loop`)

### 2.2 Skills Folder (SKILL.md)

1. **Self-improvement protocol**: Skills that document their own improvement triggers and feedback format
2. **Edge cases & gotchas**: Dedicated sections for known pitfalls
3. **Dynamic sections**: Document how content is assembled from multiple sources
4. **Model-specific adaptations**: Document behavior differences across models
5. **Prompt composition pipeline**: Document the order and conditions for section assembly
6. **Cross-referencing**: Skills reference other skills by number/name
7. **Comprehensive tables**: Permission modes, feature flags, hook events as reference tables

### 2.3 Superpowers Skills

1. **Iron Law enforcement**: Absolute rules in code blocks that override all other instructions
2. **Rationalization prevention**: Tables of excuses → realities that preempt agent self-justification
3. **Red flag lists**: Specific thought patterns that signal rule violations
4. **Hard gates**: XML-tagged gates that block progression until conditions met
5. **Good/Bad examples**: Side-by-side code comparisons with explanations
6. **Flowchart visualization**: DOT notation for non-obvious decision trees
7. **Checklist enforcement**: TodoWrite items for each checklist step
8. **Two-stage review**: Spec compliance → code quality as separate review gates
9. **Model selection guidance**: Use least powerful model that can handle the role
10. **Subagent context curation**: Never inherit session history; construct exactly what's needed

### 2.4 KiloCode Skills

1. **Phase-based workflows**: Clear numbered phases with sub-steps
2. **Evaluation-driven development**: Create evaluations to test effectiveness
3. **Language-specific branches**: Separate guides for Python vs TypeScript
4. **Agent-centric design**: Optimize for LLM context constraints (concise returns, actionable errors)
5. **Quality checklists**: Per-language quality verification lists
6. **Reference file organization**: Structured reference directory with clear loading triggers

### 2.5 Codex System Skills

1. **Progressive disclosure**: Three-level loading to minimize context usage
2. **Degrees of freedom**: Match specificity to task fragility
3. **Context window economy**: "The context window is a public good"
4. **Variant-specific files**: Organize by framework/variant to avoid loading irrelevant context
5. **Script bundling**: Executable scripts for deterministic, token-efficient operations
6. **Forward-testing**: Subagent validation without leaking expected answers
7. **No extraneous files**: Only essential files that support agent execution
8. **Description completeness**: All "when to use" info in description, not body

---

## 3. Common Structural Elements

### 3.1 Universal Components

| Component | Present In | Purpose |
|-----------|-----------|---------|
| **Name** | All | Unique identifier |
| **Description** | All | Triggering conditions |
| **Overview/Introduction** | All except bundled | What + core principle |
| **When to Use** | All except bundled | Trigger conditions |
| **When NOT to Use** | Superpowers, Codex | Boundary definition |
| **Process/Phases** | All | Step-by-step instructions |
| **Examples** | All | Concrete illustrations |
| **Anti-patterns/Mistakes** | All | What to avoid |
| **Reference files** | All except simple bundled | Supporting documentation |

### 3.2 Frontmatter Field Union

| Field | Bundled | Skills | Superpowers | KiloCode | Codex |
|-------|---------|--------|-------------|----------|-------|
| `name` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `description` | ✓ | ✓ | ✓ | ✓ | ✓ |
| `allowed-tools` | ✓ (code) | ✓ | ✗ | ✗ | ✗ |
| `whenToUse` | ✓ (code) | ✗ | ✗ | ✗ | ✗ |
| `argumentHint` | ✓ (code) | ✓ | ✗ | ✗ | |
| `userInvocable` | ✓ (code) | ✗ | ✗ | ✗ | ✗ |
| `isEnabled` | ✓ (code) | ✗ | ✗ | ✗ | ✗ |
| `metadata` | ✗ | ✓ | ✗ | ✓ | ✓ |
| `tools` | ✗ | ✓ | ✗ | ✗ | ✗ |
| `model` | ✗ | ✓ | ✗ | ✗ | ✗ |
| `skills` | ✗ | ✓ | ✗ | ✗ | ✗ |
| `license` | ✗ | ✗ | ✗ | ✓ | ✗ |

### 3.3 Body Section Patterns

| Section | Superpowers | KiloCode | Codex | Skills | Bundled |
|---------|-------------|----------|-------|--------|---------|
| Overview | ✓ | ✓ | ✓ | ✓ | ✓ (implicit) |
| When to Use | ✓ | ✓ | ✓ | ✓ | ✓ (code) |
| Core Principle/Iron Law | ✓ | ✗ | ✗ | ✗ | ✗ |
| Phases/Steps | ✓ | ✓ | ✓ | ✓ | ✓ |
| Examples | ✓ | ✓ | ✓ | ✓ | ✓ |
| Anti-patterns | ✓ | ✗ | ✗ | ✓ | ✗ |
| Red Flags | ✓ | ✗ | ✗ | ✗ | ✗ |
| Rationalization Table | ✓ | ✗ | ✗ | ✗ | ✗ |
| Quick Reference | ✓ | ✓ | ✗ | ✗ | ✗ |
| Common Mistakes | ✓ | ✓ | ✗ | ✓ | ✗ |
| Integration/Related | ✓ | ✗ | ✗ | ✗ | ✗ |
| Edge Cases | ✗ | ✗ | ✗ | ✓ | ✗ |
| Flowcharts | ✓ | ✗ | ✗ | ✗ | ✗ |
| Good/Bad Examples | ✓ | ✓ | ✗ | ✗ | ✗ |

---

## 4. Unique Patterns Worth Adopting

### 4.1 From Superpowers

1. **Iron Law Code Blocks**: Absolute rules formatted as code blocks for visual emphasis
   ```
   NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
   ```

2. **Rationalization Tables**: Preemptive counter-arguments to agent self-justification
   | Excuse | Reality |
   |--------|---------|
   | "Issue is simple" | Simple issues have root causes too |

3. **Red Flag Lists**: Specific thought patterns that signal violations
   - "Quick fix for now, investigate later" → STOP. Return to Phase 1.

4. **HARD-GATE XML Tags**: Non-negotiable gates that block progression
   ```xml
   <HARD-GATE>
   Do NOT invoke any implementation skill until design is approved.
   </HARD-GATE>
   ```

5. **Good/Bad Comparison Blocks**: Side-by-side with explanations
   ```
   <Good>Clear code</Good>
   <Bad>Over-engineered code</Bad>
   ```

6. **DOT Flowcharts**: Visual decision trees for non-obvious flows

7. **Two-Stage Review**: Spec compliance → code quality as separate gates

8. **Model Selection Guidance**: Use least powerful model per role

### 4.2 From Codex

1. **Progressive Disclosure**: 3-level loading system (metadata → body → resources)

2. **Degrees of Freedom Framework**:
   - High freedom: Text-based instructions
   - Medium freedom: Pseudocode with parameters
   - Low freedom: Specific scripts, few parameters

3. **Variant-Specific Organization**: Split by framework to avoid loading irrelevant context

4. **Script Bundling**: Executable scripts for token-efficient, deterministic operations

5. **Forward-Testing**: Subagent validation without leaking expected answers

6. **Context Window Economy**: "The context window is a public good"

### 4.3 From Bundled Skills

1. **Dynamic Prompt Generation**: Build prompts with real system state

2. **Runtime Detection**: Language detection, git checks, feature flag gates

3. **Lazy Loading**: Import large content only when invoked

4. **Template Substitution**: `{{var}}` placeholders for runtime values

5. **Multi-File Bundling**: Reference docs as string maps for selective inclusion

6. **Context Injection**: Session memory, user messages, environment state

### 4.4 From KiloCode

1. **Phase-Based Workflows**: Clear numbered phases with sub-steps

2. **Evaluation-Driven Development**: Create evaluations to test effectiveness

3. **Language-Specific Branches**: Separate guides per language

4. **Agent-Centric Design**: Optimize for LLM context constraints

### 4.5 From Skills Folder

1. **Self-Improvement Protocol**: Skills document their own improvement triggers

2. **Edge Cases & Gotchas**: Dedicated sections for known pitfalls

3. **Dynamic Section Documentation**: How content is assembled from sources

4. **Model-Specific Adaptations**: Behavior differences across models

5. **Comprehensive Reference Tables**: Permission modes, feature flags, events

---

## 5. Recommendations for New Skill Design

### 5.1 Frontmatter Standard

```yaml
---
name: skill-name-with-hyphens
description: Use when [specific triggering conditions, symptoms, situations]. Do NOT summarize workflow.
allowed-tools: [patterns like Bash(npm:*)]
when-to-use: Detailed trigger conditions (if description is too short)
argument-hint: "[args]"
---
```

**Rules:**
- Only `name` and `description` are required
- Description must start with "Use when..."
- Description must NOT summarize workflow (causes agent to shortcut)
- Max 1024 chars for frontmatter
- Name uses only letters, numbers, hyphens

### 5.2 Body Structure Template

```markdown
# Skill Name

## Overview
What is this? Core principle in 1-2 sentences.

## When to Use
- Symptom 1
- Symptom 2
- When NOT to use

<HARD-GATE>
Non-negotiable gate if applicable
</HARD-GATE>

## The Iron Law (if discipline-enforcing)
NO [BAD THING] WITHOUT [GOOD THING] FIRST

## The Process

### Phase 1: [Name]
1. Step with clear action
2. Step with clear action

**Success criteria**: [How to know phase is complete]

### Phase 2: [Name]
...

## Good/Bad Examples (if applicable)
<Good>Good example</Good>
<Bad>Bad example</Bad>

## Red Flags (if discipline-enforcing)
- Thought pattern 1 → STOP
- Thought pattern 2 → STOP

## Rationalization Table (if discipline-enforcing)
| Excuse | Reality |
|--------|---------|
| "..." | ... |

## Quick Reference
| Situation | Action |

## Common Mistakes
| Mistake | Fix |

## Integration
- **Required sub-skill**: superpowers:skill-name
- **Called by**: skill-name
```

### 5.3 Key Design Principles

1. **Progressive Disclosure**: Keep SKILL.md under 500 lines. Split heavy reference into `references/` files.

2. **Description = Triggers Only**: Never summarize workflow in description. The agent will follow description instead of reading skill body.

3. **Keyword Coverage**: Include error messages, symptoms, synonyms, tool names for search discovery.

4. **One Excellent Example**: Better than many mediocre ones. Choose most relevant language.

5. **Active Voice, Verb-First Names**: `creating-skills` not `skill-creation`, `condition-based-waiting` not `async-test-helpers`

6. **Cross-Reference by Name**: Use `superpowers:skill-name` syntax, NOT `@file/path` (force-loads context)

7. **Token Efficiency**: Every token counts. Move details to tool help, use cross-references, compress examples.

8. **Degrees of Freedom**: Match specificity to task fragility. Narrow bridges need guardrails; open fields allow many routes.

9. **Rationalization Prevention**: For discipline-enforcing skills, close every loophole explicitly. Build rationalization tables from baseline testing.

10. **Dynamic Content for Bundled Skills**: Use runtime detection, template substitution, and context injection for maximum relevance.

### 5.4 File Organization Decision Tree

```
Skill content fits in 500 lines?
├── Yes → Self-contained: skill-name/SKILL.md
├── No, has heavy reference → Split: skill-name/SKILL.md + references/
├── No, has reusable scripts → Split: skill-name/SKILL.md + scripts/
└── No, has output templates → Split: skill-name/SKILL.md + assets/
```

### 5.5 Quality Checklist

- [ ] Name uses only letters, numbers, hyphens
- [ ] Description starts with "Use when..."
- [ ] Description does NOT summarize workflow
- [ ] Overview has core principle in 1-2 sentences
- [ ] When to Use includes specific symptoms/triggers
- [ ] When NOT to Use is documented
- [ ] Process has clear phases with success criteria
- [ ] At least one concrete example
- [ ] Common mistakes section exists
- [ ] SKILL.md body under 500 lines
- [ ] Reference files have table of contents if >100 lines
- [ ] No narrative storytelling
- [ ] Cross-references use skill-name syntax, not @file paths
- [ ] Keywords for search discovery included throughout
- [ ] If discipline-enforcing: Iron Law, Red Flags, Rationalization Table present
