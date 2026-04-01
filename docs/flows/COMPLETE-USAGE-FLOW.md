# AgentOS — Complete Usage Flow

## What Happens When Someone Clones and Uses AgentOS

This document traces the EXACT step-by-step flow from repo clone to task completion.

---

## Phase 0: Setup (One-Time, 2 Minutes)

### Step 0.1: Clone the Repository
```bash
git clone https://github.com/your-org/agent-os.git
cd agent-os
```

### Step 0.2: Copy Skills to Your Agent
```bash
# For Claude Code
cp -r skills/* ~/.claude/skills/

# For Cursor
cp -r skills/* .cursor/rules/

# For Codex
cp -r skills/* .codex/skills/

# For any other agent
cp -r skills/* <agent-skill-dir>/
```

### Step 0.3: Copy Project Instructions
```bash
cp WORKER.md <project-root>/
# Or rename to your agent's equivalent:
# .cursorrules, .clinerules, .aider.instructions.md, etc.
```

### Step 0.4: (Optional) Install Workflow Engine
```bash
# The workflow engine is Python-based and works standalone
python engines/workflow-engine.py --help
```

**Setup complete.** The agent now has 27 skills, 7 workflow templates, and 71 capabilities cataloged.

---

## Phase 1: User Gives a Prompt

### User Input
```
"Build a REST API for a todo app with user authentication using FastAPI and PostgreSQL"
```

---

## Phase 2: Prompt Enhancer (Automatic)

### Step 2.1: Clarity Assessment
The agent evaluates the prompt against an 8-point checklist:

| Criteria | Score | Status |
|----------|-------|--------|
| Goal is specific and unambiguous | 2/2 | ✅ Clear |
| Scope is defined (files, components) | 2/2 | ✅ Clear |
| Constraints stated (quality, time) | 0/1 | ⚠️ Missing |
| Context sufficient (background) | 1/2 | ⚠️ Partial |
| Success criteria clear | 1/1 | ✅ Clear |
| **Total** | **6/8** | **Good** |

### Step 2.2: Decision
- Score 6/8 → **Self-enhance** (not unclear enough to ask questions)
- Agent fills gaps with reasonable assumptions:
  - Quality: Standard production quality
  - Time: Normal development timeline
  - Context: Standard FastAPI + PostgreSQL patterns

### Step 2.3: Enhanced Specification
```
Enhanced Task Specification:

Original: "Build a REST API for a todo app with user authentication using FastAPI and PostgreSQL"

Enhanced:
- Goal: Build REST API with CRUD operations + JWT auth
- Scope: FastAPI app, PostgreSQL models, auth endpoints
- Constraints: Production quality, standard patterns
- Context: FastAPI + PostgreSQL + JWT
- Success Criteria: Working API with auth, tests pass
- Assumptions: Standard project structure, JWT auth, CRUD for todos

Proceeding with execution.
```

---

## Phase 3: Task Classification

### Step 3.1: Classify Task Type
The agent analyzes the task and classifies it:

| Dimension | Classification | Confidence |
|-----------|---------------|------------|
| **Task Type** | implementation | 85% |
| **SDLC Stages** | implementation, testing | 90% |
| **Complexity** | medium | 75% |
| **Domain** | backend, api | 80% |
| **Estimated Files** | 15-25 | 70% |

### Step 3.2: Select Skills
Based on classification, the agent selects relevant skills:

**Core Skills:**
- `problem-decomposition` — Break into manageable pieces
- `quality-assurance` — Verify quality at each step
- `strategic-planning` — Plan the implementation

**Supporting Skills:**
- `context-manager` — Track state across parallel work
- `ralph-loop` — Iterate and improve
- `superpowers-patterns` — Enforce quality standards

**Domain Skills:**
- `deep-research` — Research FastAPI/PostgreSQL patterns
- `communication-design` — Document the API

---

## Phase 4: Workflow Composition

### Step 4.1: Select Workflow Template
Based on task type (implementation), the agent selects the **Implementation Workflow**:

```
Implementation Workflow
├── Phase 1: Setup (sequential, 5 min, 2 retries)
├── Phase 2: Core Development (parallel, 30 min, 3 retries)
└── Phase 3: Code Quality (parallel, 10 min, 2 retries)
```

### Step 4.2: Adapt for Complexity
Since complexity is "medium", the workflow stays as-is (no simplification or enhancement needed).

### Step 4.3: Adapt for Domain
Since domain is "backend, api", the agent adds:
- `deep-research` for API patterns
- `quality-assurance` for API testing

### Step 4.4: Adapt for Availability
The agent checks which capabilities are available and filters out unavailable ones.

### Step 4.5: Final Workflow
```
Phase 1: Setup
  - Bash (sequential)
  - FileWrite (sequential)
  - FileRead (sequential)
  - TodoWrite (sequential)

Phase 2: Core Development
  - Agent (parallel)
  - FileEdit (parallel)
  - FileWrite (parallel)
  - FileRead (parallel)
  - Bash (parallel)
  - TodoWrite (parallel)
  - general-purpose-agent (parallel)

Phase 3: Code Quality
  - Bash (parallel)
  - Agent (parallel)
  - FileEdit (parallel)
```

---

## Phase 5: Execution (Ralph Loop)

### Step 5.1: Phase 1 — Setup

**Actions:**
1. Create project structure (`Bash`: `mkdir -p app/models app/routes app/schemas`)
2. Initialize FastAPI app (`FileWrite`: `app/main.py`)
3. Set up database connection (`FileWrite`: `app/database.py`)
4. Create requirements.txt (`FileWrite`: `requirements.txt`)
5. Initialize git repo (`Bash`: `git init`)
6. Update todo list (`TodoWrite`)

**Ralph Loop Iteration 1:**
- Plan: Create basic project structure
- Execute: Create files and directories
- Review: Verify structure is correct
- Learn: Note any issues
- Improve: Fix any problems found

**Phase 1 Result:** ✅ Completed

---

### Step 5.2: Phase 2 — Core Development

**Parallel Subagents (5-25 bound enforced):**

The agent spawns **5 parallel subagents** (within the 5-25 bounds):

| Subagent | Task | Model | Isolation |
|----------|------|-------|-----------|
| Agent 1 | User model + database schema | sonnet | worktree |
| Agent 2 | Todo model + database schema | sonnet | worktree |
| Agent 3 | Auth endpoints (login, register) | sonnet | worktree |
| Agent 4 | Todo CRUD endpoints | sonnet | worktree |
| Agent 5 | API schemas + validation | sonnet | worktree |

**Subagent Execution:**
- Each agent works independently in its own worktree
- Agents use their assigned tools (FileEdit, FileWrite, Bash, etc.)
- Results are collected when all agents complete

**Ralph Loop Iteration 1:**
- Plan: Implement core features in parallel
- Execute: 5 agents work simultaneously
- Review: Merge results, check for conflicts
- Learn: Note integration issues
- Improve: Fix conflicts, ensure consistency

**Ralph Loop Iteration 2:**
- Plan: Fix integration issues from Iteration 1
- Execute: Resolve conflicts, ensure consistency
- Review: Verify all endpoints work
- Learn: Note patterns that worked well
- Improve: Refactor for consistency

**Phase 2 Result:** ✅ Completed

---

### Step 5.3: Phase 3 — Code Quality

**Parallel Subagents (3 agents):**

| Subagent | Task | Model |
|----------|------|-------|
| Agent 1 | Run linters + fix issues | haiku |
| Agent 2 | Run type checks + fix issues | haiku |
| Agent 3 | Write unit tests | sonnet |

**Quality Checks:**
- Linting: `ruff check app/`
- Type checking: `mypy app/`
- Testing: `pytest tests/`
- Coverage: `pytest --cov=app tests/`

**Ralph Loop Iteration 1:**
- Plan: Run quality checks, fix issues
- Execute: Run linters, type checks, tests
- Review: Check results, identify failures
- Learn: Note common issues
- Improve: Fix all issues

**Phase 3 Result:** ✅ Completed

---

## Phase 6: Verification (Superpowers)

### Step 6.1: Iron Laws Check
The agent verifies against iron laws:

| Iron Law | Status |
|----------|--------|
| No code changes without understanding existing code | ✅ Passed |
| No deployment without testing | ✅ Passed |
| No conclusions without showing research process | ✅ Passed |
| No decisions without evaluating 3 alternatives | ✅ Passed |

### Step 6.2: Hard Gates Check
The agent verifies all hard gates passed:

| Hard Gate | Status |
|-----------|--------|
| All tests passing | ✅ Passed |
| Linting clean | ✅ Passed |
| Type checking clean | ✅ Passed |
| Documentation complete | ✅ Passed |

### Step 6.3: Anti-Slop Check
The agent checks for anti-slop patterns:

| Pattern | Status |
|---------|--------|
| Vague statements without evidence | ✅ None found |
| "Looks good" without verification | ✅ None found |
| Skipping steps in established processes | ✅ None found |
| Assuming facts without checking | ✅ None found |

---

## Phase 7: Delivery

### Step 7.1: Generate Output
The agent produces:

```
## Task Complete: REST API for Todo App

### What Was Built
- FastAPI application with PostgreSQL backend
- User authentication with JWT
- Todo CRUD endpoints
- Database models and schemas
- Unit tests (90%+ coverage)

### Files Created
- app/main.py — FastAPI application
- app/database.py — Database connection
- app/models/user.py — User model
- app/models/todo.py — Todo model
- app/routes/auth.py — Auth endpoints
- app/routes/todos.py — Todo endpoints
- app/schemas/user.py — User schemas
- app/schemas/todo.py — Todo schemas
- tests/test_auth.py — Auth tests
- tests/test_todos.py — Todo tests
- requirements.txt — Dependencies

### How It Was Verified
- All tests passing (92% coverage)
- Linting clean (ruff)
- Type checking clean (mypy)
- Manual endpoint testing

### What Was Learned
- FastAPI dependency injection patterns
- PostgreSQL async connection pooling
- JWT token refresh implementation

### Next Steps
- Add rate limiting
- Add API documentation (OpenAPI)
- Add deployment configuration
```

### Step 7.2: Update Session Memory
The agent updates `.claude/memory/session-memory.md`:

```markdown
## Session Title
Build REST API for Todo App

## Current State
Task completed successfully

## Key Results
- FastAPI app with auth and CRUD
- 92% test coverage
- All quality checks passed

## Worklog
1. Setup project structure
2. Implemented models and schemas
3. Implemented auth endpoints
4. Implemented todo endpoints
5. Ran quality checks
6. Fixed issues
7. Verified and delivered
```

---

## Phase 8: Context Management (Throughout)

### During Execution
The agent manages context continuously:

| Technique | When Used | Savings |
|-----------|-----------|---------|
| File-read deduplication | Before every file read | 60-80% |
| Large output to disk | When output > 2000 lines | 90% |
| Selective reading | When reading large files | 70-90% |
| Fork agents for side work | For independent tasks | 50-70% |

### When Context Grows
The agent triggers autocompaction:
1. Summarize key findings → write to session memory
2. Trigger `/compact` to clear old context
3. Verify critical context is preserved
4. Resume from session memory

---

## Parallel Subagent Bounds

### Configuration
```python
# In execution_engine.py
MIN_SUBAGENTS = 5   # Minimum parallel subagents
MAX_SUBAGENTS = 25  # Maximum parallel subagents
```

### How It Works
- If a phase has **fewer than 5** parallel-safe capabilities: execute all available (below minimum is acceptable)
- If a phase has **5-25** parallel-safe capabilities: execute all in parallel
- If a phase has **more than 25** parallel-safe capabilities: batch into groups of 25

### Why These Bounds
- **Minimum 5**: Ensures meaningful parallelism for complex tasks
- **Maximum 25**: Prevents resource exhaustion and context overload
- **Batching**: Ensures no capability is skipped when exceeding maximum

---

## Complete Flow Diagram

```
User Prompt
    │
    ▼
┌─────────────────────┐
│  Prompt Enhancer    │  Score 0-2: Ask questions
│  (Auto)             │  Score 3-6: Self-enhance
│                     │  Score 7-8: Execute directly
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│  Task Classifier    │  Type, complexity, domain
│                     │  Selects relevant skills
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│  Workflow Composer  │  Selects workflow template
│                     │  Adapts for complexity/domain
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│  Execution Engine   │  Phase 1: Setup (sequential)
│  (Ralph Loop)       │  Phase 2: Core (parallel, 5-25 agents)
│                     │  Phase 3: Quality (parallel)
│                     │  Each phase: Plan→Execute→Review→Learn→Improve
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│  Verification       │  Iron Laws, Hard Gates, Anti-Slop
│  (Superpowers)      │  Checklists, Quality Standards
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│  Delivery           │  Output, Session Memory Update
│                     │  Context Management Throughout
└─────────────────────┘
```

---

## Key Insights

1. **Prompt Enhancer** prevents wasted effort on unclear tasks
2. **Task Classifier** ensures the right skills are selected
3. **Workflow Composer** adapts to task complexity and domain
4. **Execution Engine** enforces 5-25 subagent bounds
5. **Ralph Loop** ensures iterative improvement
6. **Superpowers** enforces quality standards
7. **Context Management** prevents context bloat throughout
