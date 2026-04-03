# Standards Documentation

Deep dive into AgentOS standards: format, index, examples, and best practices.

## What Are Standards?

Standards are documented patterns and conventions that guide how code should be written in your project. They are:

- **Extracted** from your existing codebase (via `/discover-standards`)
- **Deployed** into context when relevant (via `/inject-standards`)
- **Indexed** for discoverability (in `index.yml`)
- **Maintained** as your codebase evolves

## Standards Format

Each standard is a Markdown file with a consistent structure:

```markdown
# [Standard Name]

## Overview
Brief description of what this standard covers.

## Rules
Specific rules to follow.

### Rule 1: [Name]
- Description
- Good example
- Bad example

### Rule 2: [Name]
- Description
- Good example
- Bad example

## When to Apply
When this standard is relevant.

## Exceptions
Known exceptions to the rules.
```

## Standards Index

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

### Index Structure

- **Top-level keys** are folders (or `root` for root-level files)
- **Second-level keys** are file names (without `.md`)
- **`description`** explains what the standard covers

### Maintaining the Index

The index is automatically updated during project installation. You can also regenerate it manually:

```bash
# The index is in your project's agent-os/standards/index.yml
```

## Good vs Bad Examples

Standards should include clear good/bad examples:

### Good Example

```python
def calculate_total(items: list[Item]) -> float:
    """Calculate total price for a list of items."""
    return sum(item.price * item.quantity for item in items)
```

### Bad Example

```python
def calc(l):
    t = 0
    for i in l:
        t += i.p * i.q
    return t
```

## Standards Discovery

### Automatic Discovery

Run `/discover-standards` to extract patterns from your codebase:

1. Scans project structure
2. Identifies naming conventions
3. Documents architecture patterns
4. Creates standards files
5. Updates the index

### Manual Standards Creation

You can also create standards manually:

1. Create a new `.md` file in `agent-os/standards/`
2. Follow the standard format above
3. Update `index.yml` with the new entry

## Standards Injection

### Automatic Injection

Run `/inject-standards` before starting work:

1. Analyzes current task
2. Matches relevant standards from index
3. Loads them into context
4. Confirms which standards are active

### Manual Standards Loading

You can also reference standards directly:

```
Follow the coding-standards standard for this file.
Apply the git-workflow conventions to this commit.
```

## Standards Profiles

Standards are organized into profiles for different development contexts:

| Profile | Standards |
|---------|-----------|
| `default` | coding-standards, git-workflow, testing-standards |
| `python` | + python-standards, pytest-workflow, type-hinting |
| `javascript` | + typescript-standards, jest-workflow, eslint-rules |
| `web` | + react-best-practices, component-patterns, accessibility |
| `api` | + rest-conventions, api-documentation, authentication-patterns |

## Best Practices

### Writing Good Standards

1. **Be specific** — Vague standards are useless
2. **Include examples** — Show, don't just tell
3. **Keep them updated** — Standards that drift from reality are worse than no standards
4. **Make them actionable** — Standards should be checkable
5. **Document exceptions** — Know when rules don't apply

### Maintaining Standards

1. **Review regularly** — Standards should evolve with your codebase
2. **Remove outdated standards** — Don't keep standards nobody follows
3. **Add new standards** — Capture new patterns as they emerge
4. **Get team buy-in** — Standards only work if everyone follows them

## Next Steps

- Learn about [Profiles](CONCEPTS.md#profiles) for different contexts
- See [Standards vs Skills](CONCEPTS.md#standards-vs-skills) comparison
- Read the [Installation Guide](INSTALLATION.md) for setup details
