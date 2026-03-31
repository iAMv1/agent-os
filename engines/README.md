# AgentOS — Core Workflow Engine

Agent-agnostic workflow engine that analyzes any task and composes the optimal workflow.

## Usage

```bash
python workflow-engine.py "Build a REST API for a todo app"
python workflow-engine.py "Fix the login bug" --mode fast
python workflow-engine.py "Design the architecture" --mode thorough --output json
```

## Architecture

```
Task → Classifier → Registry → Composer → Engine → Adaptation → Output
```

## Components

- `task_classifier.py` — Classifies tasks by type, complexity, domain
- `capability_registry.py` — 71-capability catalog
- `workflow_composer.py` — Composes workflows from capabilities
- `execution_engine.py` — Executes workflows with adaptation
- `adaptation_layer.py` — Dynamic adaptation during execution

## Integration

This engine works with any AI agent that can:
- Execute Python scripts
- Read/write files
- Run shell commands
- Use tools (Bash, Read, Write, etc.)

The engine generates **execution instructions** that any agent can follow.
