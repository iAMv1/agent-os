# Adaptive Workflow Engine - Complete System Report

## System Overview

The Adaptive Workflow Engine is a Python-based system that analyzes any software development task and dynamically composes the optimal workflow using all 71 capabilities extracted from the AI Coding Agent runtime system.

## Architecture

```
User Task
    │
    ▼
┌─────────────────────────┐
│   Task Classifier       │  Analyzes task type, complexity, domain
│   (task_classifier.py)  │  Maps to SDLC stages
│                         │  8 task types, 10 domains, 3 complexity levels
└─────────────────────────┘
    │
    ▼
┌─────────────────────────┐
│  Capability Registry    │  71 capabilities cataloged
│  (capability_registry)  │  35 tools, 11 agents, 11 services,
│                         │  5 hooks, 9 commands
└─────────────────────────┘
    │
    ▼
┌─────────────────────────┐
│  Workflow Composer      │  7 workflow templates
│  (workflow_composer.py) │  Adapts for complexity, domain, availability
│                         │  Generates phased execution plans
└─────────────────────────┘
    │
    ▼
┌─────────────────────────┐
│  Execution Engine       │  Executes phases with parallel/sequential
│  (execution_engine.py)  │  Handles failures, retries, error recovery
│                         │  Generates execution instructions
└─────────────────────────┘
    │
    ▼
┌─────────────────────────┐
│  Adaptation Layer       │  Monitors execution, adapts dynamically
│  (adaptation_layer.py)  │  Capability substitution, parallelism changes
│                         │  Context enrichment, workflow switching
└─────────────────────────┘
```

## File Structure

```
D:\College\claude\adaptive-workflow/
├── SKILL.md                          # Integration skill for AI Coding Agent
├── main.py                           # Main orchestrator (CLI entry point)
├── classifier/
│   └── task_classifier.py            # Task classification engine
├── registry/
│   └── capability_registry.py        # 71-capability registry
├── engine/
│   ├── workflow_composer.py          # Workflow composition engine
│   ├── execution_engine.py           # Phase execution engine
│   └── adaptation_layer.py           # Dynamic adaptation layer
└── workflows/                        # (future: custom workflow definitions)
```

## Components Detail

### 1. Task Classifier (`classifier/task_classifier.py`)
- **8 task types**: requirements_gathering, architecture_design, implementation, testing_qa, deployment_devops, maintenance_monitoring
- **10 domains**: web, mobile, data_ml, devops, security, general, cli, api, frontend, backend, fullstack
- **3 complexity levels**: simple, medium, complex
- **Pattern-based classification** using regex matching on task descriptions
- **Confidence scoring** based on keyword density and clarity
- **Output**: ClassificationResult with task_type, sdlc_stages, complexity, domain, estimated_files, keywords

### 2. Capability Registry (`registry/capability_registry.py`)
- **71 capabilities** cataloged from recovered source analysis:
  - **35 tools**: Bash, FileRead, FileEdit, FileWrite, Grep, Glob, WebSearch, WebFetch, Agent, TodoWrite, AskUserQuestion, Skill, LSP, PowerShell, EnterPlanMode, ExitPlanMode, EnterWorktree, ExitWorktree, ScheduleCron, RemoteTrigger, ToolSearch, Config, Brief, Sleep, SyntheticOutput, TaskCreate, TaskGet, TaskList, TaskUpdate, TaskStop, TaskOutput, TeamCreate, TeamDelete, SendMessage, NotebookEdit
  - **11 agents**: general-purpose, Explore, Plan, verification, agent-code-guide, fork, LocalShellTask, LocalAgentTask, RemoteAgentTask, InProcessTeammateTask, DreamTask
  - **11 services**: MCP-System, Compact-System, Memory-System, Plugin-System, Skill-System, Hook-System, API-Client, Analytics-System, Voice-System, LSP-Service, MagicDocs
  - **5 hooks**: PreToolUse, PostToolUse, PermissionRequest, IDE-Integration, Swarm-Permission
  - **9 commands**: plan, agents, mcp, plugin, commit, diff, review, compact, model
- **Each capability** has: name, type, description, stages, source_files, inputs, outputs, dependencies, gating, cost, parallel_safe
- **Query methods**: get_by_stage, get_by_type, get_available, get_gated, get_parallel_safe, get_dependencies, get_for_workflow

### 3. Workflow Composer (`engine/workflow_composer.py`)
- **7 workflow templates**:
  - Requirements Gathering (3 phases)
  - Architecture & Design (3 phases)
  - Implementation (3 phases)
  - Testing & QA (3 phases)
  - Deployment & DevOps (3 phases)
  - Maintenance & Monitoring (3 phases)
  - Full SDLC Lifecycle (4 phases)
- **Adaptation rules**:
  - Complexity-based: simple tasks merge phases, complex tasks add planning
  - Domain-based: adds domain-specific capabilities (NotebookEdit for ML, ScheduleCron for DevOps)
  - Availability-based: filters out unavailable capabilities
- **Output**: Workflow with phases, capabilities, timeouts, retry counts, failure handling

### 4. Execution Engine (`engine/execution_engine.py`)
- **Phase execution**: parallel-safe capabilities run together, sequential ones run in order
- **Error handling**: configurable per-phase (abort/continue/skip)
- **Retry logic**: configurable retry count per phase
- **Output generation**: detailed execution instructions for each capability
- **History tracking**: records all executions for analysis

### 5. Adaptation Layer (`engine/adaptation_layer.py`)
- **6 adaptation types**:
  - Capability substitution (find alternatives for failed capabilities)
  - Phase merge (combine phases for simple tasks)
  - Phase split (break phases for complex tasks)
  - Timeout adjustment (increase/decrease based on execution time)
  - Parallelism change (reduce parallelism on high error rates)
  - Workflow switch (switch to simpler workflow on persistent failures)
- **Context enrichment**: adds successful outputs to context for next phases
- **Failure tracking**: tracks success/failure counts per capability

## Test Results

### Test 1: API Implementation
**Task**: "Build a REST API for a todo app with user authentication using FastAPI and PostgreSQL"
- **Classification**: implementation, medium complexity, API domain, 20 files
- **Keywords detected**: fastapi, postgres, api, rest, auth
- **Workflow**: Implementation (3 phases: Setup → Core Development → Code Quality)
- **Capabilities selected**: 6 required, 6 optional
- **Result**: [OK] All 3 phases completed

### Test 2: Requirements Gathering
**Task**: "I need to gather requirements for a new e-commerce platform that sells handmade crafts"
- **Classification**: requirements_gathering, complex, general domain, 100 files
- **Workflow**: Requirements Gathering (3 phases: Context Discovery → Elicitation → Feasibility)
- **Adaptation**: Complex mode added Plan-agent, increased timeouts to 450s, retries to 3
- **Result**: [OK] All 3 phases completed

### Test 3: Bug Fix (JSON output)
**Task**: "Fix the login bug where users get 500 errors after password reset"
- **Classification**: implementation, medium complexity, general domain, 10 files
- **Keywords detected**: login
- **Workflow**: Implementation (3 phases)
- **Output**: JSON format with full classification, workflow, and execution data
- **Result**: [OK] All 3 phases completed

### Test 4: Full Lifecycle
**Task**: Any task spanning 3+ SDLC stages triggers the Full SDLC Lifecycle workflow
- **Workflow**: Requirements & Design → Implementation → Testing → Deployment
- **Capabilities**: 9 required, 7 optional
- **Result**: [OK] All 4 phases completed

## Usage

### CLI Usage
```bash
# Basic usage
python main.py "Build a REST API for a todo app"

# With mode and depth
python main.py "Design the architecture" --mode thorough --depth deep

# JSON output for programmatic use
python main.py "Fix the login bug" --output json

# Fast mode for simple tasks
python main.py "Add a button" --mode fast
```

### Skill Usage (in AI Coding Agent)
```
/adaptive-workflow Build a REST API for a todo app
/adaptive-workflow Design the architecture /thorough
/adaptive-workflow Fix the login bug /fast
```

## How It Works

1. **User describes a task** in natural language
2. **Task Classifier** analyzes the description:
   - Matches against 8 task type patterns
   - Detects domain from technology keywords
   - Estimates complexity from task indicators
   - Extracts relevant technology keywords
3. **Workflow Composer** selects and adapts a workflow:
   - Picks the matching workflow template
   - Adapts phases based on complexity (simple=merge, complex=enhance)
   - Adds domain-specific capabilities
   - Filters out unavailable capabilities
4. **Execution Engine** generates execution instructions:
   - For each phase, generates detailed instructions for each capability
   - Handles parallel vs sequential execution
   - Configures timeouts, retries, failure handling
5. **Adaptation Layer** monitors and adapts:
   - Substitutes failed capabilities with alternatives
   - Adjusts parallelism based on error rates
   - Enriches context with successful outputs
   - Switches workflows on persistent failures

## Key Insights

### 1. Capability Coverage
- **57 capabilities** serve the Implementation stage (most covered)
- **46 capabilities** serve the Design stage
- **39 capabilities** serve the Maintenance stage
- **38 capabilities** serve the Testing stage
- **36 capabilities** serve the Deployment stage
- **34 capabilities** serve the Requirements stage
- **52 capabilities** are always available, **19** are gated

### 2. Workflow Adaptation
- Simple tasks: phases merge, parallelism reduces, timeouts decrease
- Complex tasks: planning phase added, timeouts increase, retries increase
- Domain-specific: capabilities added based on detected domain (ML→NotebookEdit, DevOps→ScheduleCron)

### 3. Execution Strategy
- Parallel-safe capabilities run together for speed
- Sequential capabilities run in order for correctness
- Each phase has configurable timeout, retry count, and failure handling
- Adaptation layer monitors execution and adjusts dynamically

## Next Steps

1. **Add more workflow templates** for specialized scenarios (migration, refactoring, security audit)
2. **Add capability cost estimation** based on token usage and execution time
3. **Add workflow visualization** (Mermaid diagrams of workflow phases)
4. **Add learning system** that improves workflow composition based on execution history
5. **Add multi-agent coordination** for complex workflows that need team-based execution
6. **Add skill integration** that loads specialized skills based on task domain
