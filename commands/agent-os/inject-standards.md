# /inject-standards — Deploy standards into your context

## Description
Intelligently inject relevant coding standards into your working context based on the current task.

## Usage
Run this command when you want to:
- Load relevant standards before starting work
- Ensure the agent follows project conventions
- Switch context between different parts of the codebase

## Process
1. Analyze the current task and files being modified
2. Match relevant standards from agent-os/standards/index.yml
3. Inject matching standards into the agent's context
4. Confirm which standards are active

## Output
- Active standards loaded into context
- Confirmation of which conventions will be enforced
