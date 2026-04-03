# Contributing to AgentOS

## How to Contribute

### Adding New Skills

1. Create a directory: `skills/my-skill/`
2. Create `SKILL.md` with the standard format
3. Follow the skill template in `templates/skill-template.md`
4. Submit a PR with a description of what the skill does

### Improving Existing Skills

1. Edit the skill file in `skills/`
2. Test the skill with your agent
3. Submit a PR with before/after examples

### Adding Workflows

Workflows are defined in code in `engines/workflow_composer.py`. To add a new workflow:

1. Add a new template to `_build_templates()` in `workflow_composer.py`
2. Document the workflow in `docs/WORKFLOW.md`
3. Submit a PR

### Reporting Issues

- Use GitHub Issues
- Include: what you expected, what happened, steps to reproduce
- Tag with the appropriate component (skill, workflow, engine, docs)

## Skill Format

Every skill must follow this format:

```yaml
---
name: skill-name
description: When to use this skill (this is the trigger)
when_to_use: Detailed trigger conditions
allowed-tools: List of tools this skill can use
arguments: List of arguments this skill accepts
argument-hint: "[arg1|arg2] [option1|option2]"
---

# Skill Name

<HARD-GATE>
Non-negotiable rules that block progression
</HARD-GATE>

## The Iron Law

Absolute rule that overrides all other instructions

## When to Use

Specific trigger conditions

## When NOT to Use

Boundary conditions

## The Process

Step-by-step instructions with phases

## Integration

Related skills
```

## Code of Conduct

- Be respectful
- Be constructive
- Be helpful
- Share knowledge

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
