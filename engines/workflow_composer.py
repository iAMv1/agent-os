import json
import time
import copy
import hashlib
from typing import Dict, List, Optional, Tuple, Set, Any
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

from workflow_validator import WorkflowValidator, ValidationResult
from workflow_metrics import WorkflowMetricsCollector
from workflow_rollback import RollbackManager


# Re-export for use by other modules
@dataclass
class WorkflowPhase:
    name: str
    description: str
    capabilities: List[str]
    parallel: bool
    timeout_seconds: int
    retry_count: int
    on_failure: str


@dataclass
class Workflow:
    name: str
    description: str
    stages: List[str]
    phases: List[WorkflowPhase]
    estimated_duration: str
    estimated_cost: str
    required_capabilities: List[str]
    optional_capabilities: List[str]
    adaptation_rules: Dict[str, str]


class DependencyEdge:
    """Represents a dependency between two phases."""

    def __init__(self, from_phase: str, to_phase: str, condition: Optional[str] = None):
        self.from_phase = from_phase
        self.to_phase = to_phase
        self.condition = condition  # Optional condition for conditional dependencies

    def __repr__(self):
        return "%s -> %s" % (self.from_phase, self.to_phase)


class WorkflowDAG:
    """Directed Acyclic Graph for workflow phase dependencies."""

    def __init__(self):
        self.adjacency: Dict[str, List[str]] = defaultdict(list)
        self.in_degree: Dict[str, int] = defaultdict(int)
        self.nodes: Set[str] = set()
        self.edges: List[DependencyEdge] = []

    def add_node(self, name: str):
        self.nodes.add(name)
        if name not in self.in_degree:
            self.in_degree[name] = 0

    def add_edge(self, from_phase: str, to_phase: str, condition: Optional[str] = None):
        self.adjacency[from_phase].append(to_phase)
        self.in_degree[to_phase] += 1
        self.nodes.add(from_phase)
        self.nodes.add(to_phase)
        self.edges.append(DependencyEdge(from_phase, to_phase, condition))

    def has_cycle(self) -> bool:
        visited = set()
        rec_stack = set()

        def dfs(node):
            visited.add(node)
            rec_stack.add(node)
            for neighbor in self.adjacency.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            rec_stack.discard(node)
            return False

        for node in self.nodes:
            if node not in visited:
                if dfs(node):
                    return True
        return False

    def topological_sort(self) -> List[str]:
        in_deg = dict(self.in_degree)
        queue = [n for n in self.nodes if in_deg.get(n, 0) == 0]
        result = []

        while queue:
            queue.sort()
            node = queue.pop(0)
            result.append(node)
            for neighbor in self.adjacency.get(node, []):
                in_deg[neighbor] -= 1
                if in_deg[neighbor] == 0:
                    queue.append(neighbor)

        if len(result) != len(self.nodes):
            raise ValueError("Cycle detected in workflow DAG")
        return result

    def get_parallel_groups(self) -> List[List[str]]:
        in_deg = dict(self.in_degree)
        groups = []
        remaining = set(self.nodes)

        while remaining:
            ready = [n for n in remaining if in_deg.get(n, 0) == 0]
            if not ready:
                raise ValueError("Cycle detected - cannot resolve parallel groups")
            groups.append(sorted(ready))
            for node in ready:
                remaining.discard(node)
                for neighbor in self.adjacency.get(node, []):
                    in_deg[neighbor] -= 1

        return groups

    def get_dependencies(self, phase_name: str) -> List[str]:
        deps = []
        for edge in self.edges:
            if edge.to_phase == phase_name:
                deps.append(edge.from_phase)
        return deps

    def get_dependents(self, phase_name: str) -> List[str]:
        return list(self.adjacency.get(phase_name, []))


@dataclass
class DynamicPhaseConfig:
    """Configuration for dynamically generated phases."""

    name: str
    description: str
    capabilities: List[str]
    dependencies: List[str]
    parallel: bool = False
    timeout_seconds: int = 300
    retry_count: int = 2
    on_failure: str = "continue"
    condition: Optional[str] = None
    resource_estimate: Dict[str, float] = field(default_factory=dict)
    rollback_strategy: str = "checkpoint"


@dataclass
class GeneratedWorkflow:
    """A dynamically generated workflow with DAG structure."""

    name: str
    description: str
    phases: List[WorkflowPhase]
    dag: WorkflowDAG
    validation_result: Optional[ValidationResult] = None
    estimated_duration_seconds: float = 0.0
    critical_path: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class WorkflowComposer:
    """Composes workflows from capabilities based on task classification."""

    def __init__(self, capability_registry):
        self.registry = capability_registry
        self.workflow_templates = self._build_templates()
        self.validator = WorkflowValidator(capability_registry)
        self.metrics = WorkflowMetricsCollector()
        self.rollback_manager = RollbackManager()
        self.generated_workflows: Dict[str, GeneratedWorkflow] = {}

    def _build_templates(self) -> Dict[str, Workflow]:
        """Build workflow templates for each SDLC stage combination."""
        return {
            "requirements_gathering": Workflow(
                name="Requirements Gathering",
                description="Discover, document, and validate requirements",
                stages=["requirements"],
                phases=[
                    WorkflowPhase(
                        name="Context Discovery",
                        description="Analyze existing codebase and documentation",
                        capabilities=[
                            "FileRead",
                            "Grep",
                            "Glob",
                            "Bash",
                            "Explore-agent",
                        ],
                        parallel=True,
                        timeout_seconds=300,
                        retry_count=2,
                        on_failure="continue",
                    ),
                    WorkflowPhase(
                        name="Requirements Elicitation",
                        description="Gather and document requirements",
                        capabilities=["AskUserQuestion", "FileWrite", "TodoWrite"],
                        parallel=False,
                        timeout_seconds=600,
                        retry_count=1,
                        on_failure="abort",
                    ),
                    WorkflowPhase(
                        name="Feasibility Analysis",
                        description="Research and assess technical feasibility",
                        capabilities=[
                            "WebSearch",
                            "WebFetch",
                            "Skill",
                            "Explore-agent",
                        ],
                        parallel=True,
                        timeout_seconds=300,
                        retry_count=2,
                        on_failure="continue",
                    ),
                ],
                estimated_duration="30-60 minutes",
                estimated_cost="low",
                required_capabilities=[
                    "FileRead",
                    "Grep",
                    "Glob",
                    "AskUserQuestion",
                    "FileWrite",
                ],
                optional_capabilities=[
                    "WebSearch",
                    "WebFetch",
                    "Explore-agent",
                    "Skill",
                ],
                adaptation_rules={
                    "simple_task": "Skip feasibility analysis, go straight to elicitation",
                    "complex_task": "Add Plan-agent for structured requirements analysis",
                    "unknown_domain": "Add WebSearch/WebFetch for domain research",
                },
            ),
            "architecture_design": Workflow(
                name="Architecture & Design",
                description="Design system architecture and create implementation plan",
                stages=["design"],
                phases=[
                    WorkflowPhase(
                        name="Context Analysis",
                        description="Analyze existing architecture and constraints",
                        capabilities=[
                            "FileRead",
                            "Grep",
                            "Glob",
                            "Explore-agent",
                            "Bash",
                        ],
                        parallel=True,
                        timeout_seconds=300,
                        retry_count=2,
                        on_failure="continue",
                    ),
                    WorkflowPhase(
                        name="Design Exploration",
                        description="Research patterns and generate alternatives",
                        capabilities=["WebSearch", "WebFetch", "Plan-agent"],
                        parallel=True,
                        timeout_seconds=600,
                        retry_count=1,
                        on_failure="continue",
                    ),
                    WorkflowPhase(
                        name="Architecture Documentation",
                        description="Document architecture and generate diagrams",
                        capabilities=["FileWrite", "Bash", "Plan-agent"],
                        parallel=False,
                        timeout_seconds=300,
                        retry_count=1,
                        on_failure="abort",
                    ),
                ],
                estimated_duration="1-2 hours",
                estimated_cost="medium",
                required_capabilities=[
                    "FileRead",
                    "Grep",
                    "Glob",
                    "Plan-agent",
                    "FileWrite",
                ],
                optional_capabilities=[
                    "WebSearch",
                    "WebFetch",
                    "Bash",
                    "Explore-agent",
                ],
                adaptation_rules={
                    "greenfield": "Skip context analysis, start with design exploration",
                    "brownfield": "Extend context analysis with deep codebase exploration",
                    "migration": "Add feasibility analysis phase for migration strategy",
                },
            ),
            "implementation": Workflow(
                name="Implementation",
                description="Build the feature or system",
                stages=["implementation"],
                phases=[
                    WorkflowPhase(
                        name="Setup",
                        description="Create project structure and configure tooling",
                        capabilities=["Bash", "FileWrite", "FileRead", "TodoWrite"],
                        parallel=False,
                        timeout_seconds=300,
                        retry_count=2,
                        on_failure="abort",
                    ),
                    WorkflowPhase(
                        name="Core Development",
                        description="Implement the feature using parallel agents",
                        capabilities=[
                            "Agent",
                            "FileEdit",
                            "FileWrite",
                            "FileRead",
                            "Bash",
                            "TodoWrite",
                            "general-purpose-agent",
                        ],
                        parallel=True,
                        timeout_seconds=1800,
                        retry_count=3,
                        on_failure="continue",
                    ),
                    WorkflowPhase(
                        name="Code Quality",
                        description="Run linters, type checks, and fix issues",
                        capabilities=["Bash", "Agent", "FileEdit", "LSP"],
                        parallel=True,
                        timeout_seconds=600,
                        retry_count=2,
                        on_failure="continue",
                    ),
                ],
                estimated_duration="2-8 hours",
                estimated_cost="high",
                required_capabilities=[
                    "Bash",
                    "FileEdit",
                    "FileWrite",
                    "FileRead",
                    "Agent",
                    "TodoWrite",
                ],
                optional_capabilities=[
                    "LSP",
                    "NotebookEdit",
                    "EnterWorktree",
                    "general-purpose-agent",
                    "Plan-agent",
                ],
                adaptation_rules={
                    "simple_task": "Skip parallel development, implement directly",
                    "complex_task": "Add Plan-agent phase, use worktree isolation, spawn multiple agents",
                    "team_available": "Use TeamCreate for coordinated multi-agent development",
                    "fork_available": "Use fork-agent for context-inheriting parallel work",
                },
            ),
            "testing_qa": Workflow(
                name="Testing & QA",
                description="Test the implementation and ensure quality",
                stages=["testing"],
                phases=[
                    WorkflowPhase(
                        name="Test Planning",
                        description="Analyze coverage and identify test gaps",
                        capabilities=[
                            "Bash",
                            "Explore-agent",
                            "FileWrite",
                            "TodoWrite",
                        ],
                        parallel=True,
                        timeout_seconds=300,
                        retry_count=1,
                        on_failure="continue",
                    ),
                    WorkflowPhase(
                        name="Test Generation",
                        description="Generate unit, integration, and E2E tests",
                        capabilities=["Agent", "FileWrite", "FileRead", "Bash"],
                        parallel=True,
                        timeout_seconds=600,
                        retry_count=2,
                        on_failure="continue",
                    ),
                    WorkflowPhase(
                        name="Test Execution",
                        description="Run test suite and analyze failures",
                        capabilities=["Bash", "Agent", "FileEdit", "TodoWrite"],
                        parallel=False,
                        timeout_seconds=900,
                        retry_count=3,
                        on_failure="continue",
                    ),
                ],
                estimated_duration="1-4 hours",
                estimated_cost="medium",
                required_capabilities=[
                    "Bash",
                    "Agent",
                    "FileWrite",
                    "FileRead",
                    "TodoWrite",
                ],
                optional_capabilities=["Explore-agent", "verification-agent", "LSP"],
                adaptation_rules={
                    "simple_task": "Skip test planning, generate and run tests directly",
                    "complex_task": "Use verification-agent for adversarial testing",
                    "existing_tests": "Focus on test gaps, extend existing test suite",
                    "no_existing_tests": "Start with critical path tests, expand coverage",
                },
            ),
            "deployment_devops": Workflow(
                name="Deployment & DevOps",
                description="Deploy the system and set up infrastructure",
                stages=["deployment", "infrastructure"],
                phases=[
                    WorkflowPhase(
                        name="Infrastructure Analysis",
                        description="Analyze current infrastructure and requirements",
                        capabilities=[
                            "Bash",
                            "FileRead",
                            "AskUserQuestion",
                            "WebSearch",
                        ],
                        parallel=True,
                        timeout_seconds=300,
                        retry_count=1,
                        on_failure="continue",
                    ),
                    WorkflowPhase(
                        name="CI/CD Setup",
                        description="Create pipeline configuration and environments",
                        capabilities=["FileWrite", "Bash", "FileRead"],
                        parallel=False,
                        timeout_seconds=600,
                        retry_count=2,
                        on_failure="abort",
                    ),
                    WorkflowPhase(
                        name="Deployment",
                        description="Build, deploy, and verify",
                        capabilities=["Bash", "Agent", "TodoWrite"],
                        parallel=False,
                        timeout_seconds=900,
                        retry_count=3,
                        on_failure="abort",
                    ),
                ],
                estimated_duration="2-6 hours",
                estimated_cost="medium",
                required_capabilities=["Bash", "FileWrite", "FileRead", "TodoWrite"],
                optional_capabilities=[
                    "Agent",
                    "ScheduleCron",
                    "RemoteTrigger",
                    "AskUserQuestion",
                    "WebSearch",
                ],
                adaptation_rules={
                    "first_deployment": "Add infrastructure analysis phase, use staging first",
                    "existing_pipeline": "Update existing pipeline instead of creating new",
                    "multi_environment": "Add environment-specific configuration phase",
                },
            ),
            "maintenance_monitoring": Workflow(
                name="Maintenance & Monitoring",
                description="Diagnose issues, fix bugs, and optimize",
                stages=["maintenance"],
                phases=[
                    WorkflowPhase(
                        name="Diagnosis",
                        description="Analyze logs, reproduce issue, identify root cause",
                        capabilities=[
                            "Bash",
                            "Grep",
                            "FileRead",
                            "Agent",
                            "Explore-agent",
                        ],
                        parallel=True,
                        timeout_seconds=300,
                        retry_count=2,
                        on_failure="continue",
                    ),
                    WorkflowPhase(
                        name="Resolution",
                        description="Develop, test, and deploy fix",
                        capabilities=["Agent", "FileEdit", "Bash", "FileWrite"],
                        parallel=False,
                        timeout_seconds=600,
                        retry_count=3,
                        on_failure="abort",
                    ),
                    WorkflowPhase(
                        name="Prevention",
                        description="Add regression tests, update monitoring, document fix",
                        capabilities=["Agent", "FileWrite", "Bash", "TodoWrite"],
                        parallel=True,
                        timeout_seconds=300,
                        retry_count=1,
                        on_failure="continue",
                    ),
                ],
                estimated_duration="1-4 hours",
                estimated_cost="medium",
                required_capabilities=["Bash", "Grep", "FileRead", "Agent", "FileEdit"],
                optional_capabilities=[
                    "Explore-agent",
                    "verification-agent",
                    "TodoWrite",
                    "FileWrite",
                ],
                adaptation_rules={
                    "known_issue": "Skip diagnosis, go straight to resolution",
                    "performance_issue": "Add profiling and benchmarking to diagnosis",
                    "security_issue": "Add security scanning and audit to prevention",
                },
            ),
            "full_lifecycle": Workflow(
                name="Full SDLC Lifecycle",
                description="End-to-end software development from requirements to deployment",
                stages=[
                    "requirements",
                    "design",
                    "implementation",
                    "testing",
                    "deployment",
                ],
                phases=[
                    WorkflowPhase(
                        name="Requirements & Design",
                        description="Gather requirements and design architecture",
                        capabilities=[
                            "FileRead",
                            "Grep",
                            "Glob",
                            "AskUserQuestion",
                            "Plan-agent",
                            "Explore-agent",
                            "FileWrite",
                            "WebSearch",
                        ],
                        parallel=True,
                        timeout_seconds=900,
                        retry_count=2,
                        on_failure="continue",
                    ),
                    WorkflowPhase(
                        name="Implementation",
                        description="Build the system using parallel agents",
                        capabilities=[
                            "Agent",
                            "FileEdit",
                            "FileWrite",
                            "FileRead",
                            "Bash",
                            "TodoWrite",
                            "general-purpose-agent",
                        ],
                        parallel=True,
                        timeout_seconds=1800,
                        retry_count=3,
                        on_failure="continue",
                    ),
                    WorkflowPhase(
                        name="Testing",
                        description="Test thoroughly and fix issues",
                        capabilities=[
                            "Bash",
                            "Agent",
                            "FileEdit",
                            "FileWrite",
                            "TodoWrite",
                        ],
                        parallel=True,
                        timeout_seconds=900,
                        retry_count=3,
                        on_failure="continue",
                    ),
                    WorkflowPhase(
                        name="Deployment",
                        description="Deploy and verify",
                        capabilities=["Bash", "FileWrite", "TodoWrite"],
                        parallel=False,
                        timeout_seconds=600,
                        retry_count=2,
                        on_failure="abort",
                    ),
                ],
                estimated_duration="4-16 hours",
                estimated_cost="high",
                required_capabilities=[
                    "FileRead",
                    "Grep",
                    "Glob",
                    "Agent",
                    "Bash",
                    "FileEdit",
                    "FileWrite",
                    "TodoWrite",
                    "Plan-agent",
                ],
                optional_capabilities=[
                    "Explore-agent",
                    "verification-agent",
                    "WebSearch",
                    "WebFetch",
                    "LSP",
                    "TeamCreate",
                    "general-purpose-agent",
                ],
                adaptation_rules={
                    "simple_task": "Merge requirements+design, skip parallel implementation",
                    "complex_task": "Use TeamCreate for coordinated multi-agent development",
                    "fork_available": "Use fork-agent for context-inheriting parallel work",
                    "team_available": "Use swarm teams for coordinated development",
                },
            ),
        }

    def compose(self, classification_result) -> Workflow:
        """Compose a workflow based on task classification."""
        task_type = classification_result.task_type
        complexity = classification_result.complexity.value
        domain = classification_result.domain.value

        workflow_map = {
            "requirements_gathering": "requirements_gathering",
            "architecture_design": "architecture_design",
            "implementation": "implementation",
            "testing_qa": "testing_qa",
            "deployment_devops": "deployment_devops",
            "maintenance_monitoring": "maintenance_monitoring",
        }

        base_key = workflow_map.get(task_type, "implementation")
        base_workflow = self.workflow_templates[base_key]

        if len(classification_result.sdlc_stages) > 2:
            base_workflow = self.workflow_templates["full_lifecycle"]

        adapted = self._adapt_for_complexity(base_workflow, complexity)
        adapted = self._adapt_for_domain(adapted, domain)
        adapted = self._adapt_for_availability(adapted)

        return adapted

    def compose_dynamic(
        self, classification_result, task_description: str = ""
    ) -> GeneratedWorkflow:
        """Dynamically generate a workflow with DAG-based execution."""
        task_type = classification_result.task_type
        complexity = classification_result.complexity.value
        domain = classification_result.domain.value

        phase_configs = self._generate_phase_configs(
            task_type, complexity, domain, task_description
        )
        dag = self._build_dag_from_configs(phase_configs)
        phases = self._configs_to_phases(phase_configs)

        if dag.has_cycle():
            dag = self._resolve_cycles(dag)

        workflow_name = (
            "Dynamic: %s" % classification_result.task_type.replace("_", " ").title()
        )
        generated = GeneratedWorkflow(
            name=workflow_name,
            description="Dynamically generated workflow for %s task" % task_type,
            phases=phases,
            dag=dag,
        )

        validation = self.validator.validate(generated)
        generated.validation_result = validation

        if validation.is_valid:
            generated.critical_path = self._compute_critical_path(generated)
            generated.estimated_duration_seconds = self._estimate_duration(generated)

        workflow_id = hashlib.md5(workflow_name.encode()).hexdigest()[:8]
        self.generated_workflows[workflow_id] = generated

        self.metrics.record_workflow_created(generated)

        return generated

    def _generate_phase_configs(
        self, task_type: str, complexity: str, domain: str, task_description: str
    ) -> List[DynamicPhaseConfig]:
        """Generate phase configurations dynamically based on task analysis."""
        configs = []

        base_phases = {
            "requirements_gathering": [
                DynamicPhaseConfig(
                    "Discovery",
                    "Discover context and existing state",
                    ["FileRead", "Grep", "Glob", "Explore-agent"],
                    [],
                    parallel=True,
                    timeout_seconds=300,
                ),
                DynamicPhaseConfig(
                    "Elicitation",
                    "Gather and document requirements",
                    ["AskUserQuestion", "FileWrite", "TodoWrite"],
                    ["Discovery"],
                    parallel=False,
                    timeout_seconds=600,
                    on_failure="abort",
                ),
                DynamicPhaseConfig(
                    "Analysis",
                    "Analyze feasibility and constraints",
                    ["WebSearch", "WebFetch", "Plan-agent"],
                    ["Discovery"],
                    parallel=True,
                    timeout_seconds=300,
                ),
            ],
            "architecture_design": [
                DynamicPhaseConfig(
                    "Context Analysis",
                    "Analyze existing architecture",
                    ["FileRead", "Grep", "Glob", "Explore-agent"],
                    [],
                    parallel=True,
                    timeout_seconds=300,
                ),
                DynamicPhaseConfig(
                    "Pattern Research",
                    "Research architectural patterns",
                    ["WebSearch", "WebFetch", "Skill"],
                    [],
                    parallel=True,
                    timeout_seconds=300,
                ),
                DynamicPhaseConfig(
                    "Design",
                    "Create architecture design",
                    ["Plan-agent", "FileWrite"],
                    ["Context Analysis", "Pattern Research"],
                    parallel=False,
                    timeout_seconds=600,
                    on_failure="abort",
                ),
                DynamicPhaseConfig(
                    "Documentation",
                    "Document architecture decisions",
                    ["FileWrite", "Bash"],
                    ["Design"],
                    parallel=False,
                    timeout_seconds=300,
                ),
            ],
            "implementation": [
                DynamicPhaseConfig(
                    "Setup",
                    "Create project structure",
                    ["Bash", "FileWrite", "FileRead", "TodoWrite"],
                    [],
                    parallel=False,
                    timeout_seconds=300,
                    on_failure="abort",
                ),
                DynamicPhaseConfig(
                    "Core Development",
                    "Implement core functionality",
                    ["Agent", "FileEdit", "FileWrite", "FileRead", "Bash"],
                    ["Setup"],
                    parallel=True,
                    timeout_seconds=1800,
                ),
                DynamicPhaseConfig(
                    "Integration",
                    "Integrate components",
                    ["Agent", "FileEdit", "Bash"],
                    ["Core Development"],
                    parallel=False,
                    timeout_seconds=600,
                ),
                DynamicPhaseConfig(
                    "Quality Gate",
                    "Run linters and type checks",
                    ["Bash", "LSP"],
                    ["Core Development"],
                    parallel=True,
                    timeout_seconds=600,
                ),
            ],
            "testing_qa": [
                DynamicPhaseConfig(
                    "Test Analysis",
                    "Analyze test coverage gaps",
                    ["Bash", "Explore-agent", "FileRead"],
                    [],
                    parallel=True,
                    timeout_seconds=300,
                ),
                DynamicPhaseConfig(
                    "Test Generation",
                    "Generate test cases",
                    ["Agent", "FileWrite", "FileRead"],
                    ["Test Analysis"],
                    parallel=True,
                    timeout_seconds=600,
                ),
                DynamicPhaseConfig(
                    "Test Execution",
                    "Run tests and analyze results",
                    ["Bash", "Agent", "TodoWrite"],
                    ["Test Generation"],
                    parallel=False,
                    timeout_seconds=900,
                ),
                DynamicPhaseConfig(
                    "Fix Failures",
                    "Fix failing tests",
                    ["Agent", "FileEdit", "Bash"],
                    ["Test Execution"],
                    parallel=False,
                    timeout_seconds=600,
                    condition="has_failures",
                ),
            ],
            "deployment_devops": [
                DynamicPhaseConfig(
                    "Infrastructure Check",
                    "Verify infrastructure readiness",
                    ["Bash", "FileRead", "WebSearch"],
                    [],
                    parallel=True,
                    timeout_seconds=300,
                ),
                DynamicPhaseConfig(
                    "Build",
                    "Build artifacts",
                    ["Bash", "FileRead"],
                    ["Infrastructure Check"],
                    parallel=False,
                    timeout_seconds=600,
                    on_failure="abort",
                ),
                DynamicPhaseConfig(
                    "Deploy",
                    "Deploy to target environment",
                    ["Bash", "Agent", "TodoWrite"],
                    ["Build"],
                    parallel=False,
                    timeout_seconds=900,
                    on_failure="abort",
                ),
                DynamicPhaseConfig(
                    "Verification",
                    "Verify deployment health",
                    ["Bash", "WebFetch"],
                    ["Deploy"],
                    parallel=True,
                    timeout_seconds=300,
                ),
            ],
            "maintenance_monitoring": [
                DynamicPhaseConfig(
                    "Diagnosis",
                    "Identify root cause",
                    ["Bash", "Grep", "FileRead", "Explore-agent"],
                    [],
                    parallel=True,
                    timeout_seconds=300,
                ),
                DynamicPhaseConfig(
                    "Fix Development",
                    "Develop and test fix",
                    ["Agent", "FileEdit", "Bash"],
                    ["Diagnosis"],
                    parallel=False,
                    timeout_seconds=600,
                ),
                DynamicPhaseConfig(
                    "Regression Prevention",
                    "Add tests and monitoring",
                    ["Agent", "FileWrite", "Bash"],
                    ["Fix Development"],
                    parallel=True,
                    timeout_seconds=300,
                ),
            ],
        }

        configs = list(base_phases.get(task_type, base_phases["implementation"]))

        if complexity == "complex":
            planning = DynamicPhaseConfig(
                "Planning",
                "Create detailed implementation plan",
                ["Plan-agent", "TodoWrite"],
                [],
                parallel=False,
                timeout_seconds=300,
                on_failure="abort",
            )
            configs.insert(0, planning)
            for cfg in configs:
                if cfg.name != "Planning":
                    cfg.dependencies.append("Planning")
            for cfg in configs:
                cfg.timeout_seconds = int(cfg.timeout_seconds * 1.5)
                cfg.retry_count = min(cfg.retry_count + 1, 5)

        elif complexity == "simple":
            if len(configs) > 2:
                configs = [configs[0], configs[-1]]
                configs[0].dependencies = []
                configs[1].dependencies = [configs[0].name]

        domain_enhancements = {
            "data_ml": ["NotebookEdit"],
            "devops": ["ScheduleCron", "RemoteTrigger"],
            "security": ["Grep", "Bash"],
        }
        extra_caps = domain_enhancements.get(domain, [])
        if extra_caps and configs:
            configs[-1].capabilities.extend(extra_caps)

        return configs

    def _build_dag_from_configs(self, configs: List[DynamicPhaseConfig]) -> WorkflowDAG:
        """Build a DAG from phase configurations."""
        dag = WorkflowDAG()
        for cfg in configs:
            dag.add_node(cfg.name)
        for cfg in configs:
            for dep in cfg.dependencies:
                dag.add_edge(dep, cfg.name, cfg.condition)
        return dag

    def _configs_to_phases(
        self, configs: List[DynamicPhaseConfig]
    ) -> List[WorkflowPhase]:
        """Convert DynamicPhaseConfig list to WorkflowPhase list."""
        phases = []
        for cfg in configs:
            phases.append(
                WorkflowPhase(
                    name=cfg.name,
                    description=cfg.description,
                    capabilities=cfg.capabilities,
                    parallel=cfg.parallel,
                    timeout_seconds=cfg.timeout_seconds,
                    retry_count=cfg.retry_count,
                    on_failure=cfg.on_failure,
                )
            )
        return phases

    def _resolve_cycles(self, dag: WorkflowDAG) -> WorkflowDAG:
        """Resolve cycles in DAG by removing back edges."""
        visited = set()
        rec_stack = set()
        edges_to_remove = []

        def dfs(node):
            visited.add(node)
            rec_stack.add(node)
            for neighbor in dag.adjacency.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in rec_stack:
                    edges_to_remove.append((node, neighbor))
            rec_stack.discard(node)

        for node in dag.nodes:
            if node not in visited:
                dfs(node)

        new_dag = WorkflowDAG()
        for node in dag.nodes:
            new_dag.add_node(node)
        for edge in dag.edges:
            if (edge.from_phase, edge.to_phase) not in edges_to_remove:
                new_dag.add_edge(edge.from_phase, edge.to_phase, edge.condition)

        return new_dag

    def _compute_critical_path(self, workflow: GeneratedWorkflow) -> List[str]:
        """Compute the critical path through the workflow DAG."""
        try:
            order = workflow.dag.topological_sort()
        except ValueError:
            return []

        phase_map = {p.name: p for p in workflow.phases}
        earliest_finish = {}
        predecessor = {}

        for phase_name in order:
            phase = phase_map.get(phase_name)
            if not phase:
                continue
            deps = workflow.dag.get_dependencies(phase_name)
            if not deps:
                earliest_finish[phase_name] = phase.timeout_seconds
                predecessor[phase_name] = None
            else:
                max_dep = max(deps, key=lambda d: earliest_finish.get(d, 0))
                earliest_finish[phase_name] = (
                    earliest_finish.get(max_dep, 0) + phase.timeout_seconds
                )
                predecessor[phase_name] = max_dep

        if not earliest_finish:
            return []

        end = max(earliest_finish, key=lambda k: earliest_finish.get(k, 0))
        path = []
        current = end
        while current is not None:
            path.append(current)
            current = predecessor.get(current)
        path.reverse()
        return path

    def _estimate_duration(self, workflow: GeneratedWorkflow) -> float:
        """Estimate total workflow duration considering parallelism."""
        try:
            groups = workflow.dag.get_parallel_groups()
        except ValueError:
            return sum(p.timeout_seconds for p in workflow.phases)

        phase_map = {p.name: p for p in workflow.phases}
        total = 0.0
        for group in groups:
            group_max = max(
                (
                    phase_map.get(
                        n, WorkflowPhase("", "", [], False, 0, 0, "")
                    ).timeout_seconds
                    for n in group
                ),
                default=0,
            )
            total += group_max
        return total

    def validate_workflow(self, workflow) -> ValidationResult:
        """Validate a workflow before execution."""
        if isinstance(workflow, GeneratedWorkflow):
            return workflow.validation_result or self.validator.validate(workflow)
        return self.validator.validate_from_template(workflow)

    def prepare_rollback(self, workflow, context: Dict) -> str:
        """Prepare rollback state for a workflow execution."""
        return self.rollback_manager.save_state(workflow, context)

    def rollback_execution(self, checkpoint_id: str):
        """Rollback to a previous checkpoint."""
        return self.rollback_manager.rollback(checkpoint_id)

    def _adapt_for_complexity(self, workflow: Workflow, complexity: str) -> Workflow:
        """Adapt workflow based on task complexity."""
        phases = list(workflow.phases)

        if complexity == "simple":
            if len(phases) > 2:
                merged = WorkflowPhase(
                    name="%s + %s" % (phases[0].name, phases[1].name),
                    description="%s. %s"
                    % (phases[0].description, phases[1].description),
                    capabilities=list(
                        set(phases[0].capabilities + phases[1].capabilities)
                    ),
                    parallel=False,
                    timeout_seconds=phases[0].timeout_seconds
                    + phases[1].timeout_seconds,
                    retry_count=max(phases[0].retry_count, phases[1].retry_count),
                    on_failure="abort",
                )
                phases = [merged] + phases[2:]

        elif complexity == "complex":
            if "Plan-agent" not in phases[0].capabilities:
                phases[0].capabilities.append("Plan-agent")
            for phase in phases:
                phase.timeout_seconds = int(phase.timeout_seconds * 1.5)
                phase.retry_count = min(phase.retry_count + 1, 5)

        return Workflow(
            name=workflow.name,
            description=workflow.description,
            stages=workflow.stages,
            phases=phases,
            estimated_duration=workflow.estimated_duration,
            estimated_cost=workflow.estimated_cost,
            required_capabilities=workflow.required_capabilities,
            optional_capabilities=workflow.optional_capabilities,
            adaptation_rules=workflow.adaptation_rules,
        )

    def _adapt_for_domain(self, workflow: Workflow, domain: str) -> Workflow:
        """Adapt workflow based on task domain."""
        domain_capabilities = {
            "data_ml": ["NotebookEdit"],
            "devops": ["ScheduleCron", "RemoteTrigger"],
            "security": ["Grep", "Bash"],
            "web": ["WebSearch", "WebFetch"],
            "mobile": ["Bash"],
            "api": ["WebSearch", "WebFetch"],
        }

        extra_caps = domain_capabilities.get(domain, [])
        optional = list(workflow.optional_capabilities)
        for cap in extra_caps:
            if cap not in optional and cap not in workflow.required_capabilities:
                optional.append(cap)

        return Workflow(
            name=workflow.name,
            description=workflow.description,
            stages=workflow.stages,
            phases=workflow.phases,
            estimated_duration=workflow.estimated_duration,
            estimated_cost=workflow.estimated_cost,
            required_capabilities=workflow.required_capabilities,
            optional_capabilities=optional,
            adaptation_rules=workflow.adaptation_rules,
        )

    def _adapt_for_availability(self, workflow: Workflow) -> Workflow:
        """Adapt workflow based on what capabilities are actually available."""
        available_names = set(c.name for c in self.registry.get_available())

        required = [c for c in workflow.required_capabilities if c in available_names]
        optional = [c for c in workflow.optional_capabilities if c in available_names]

        phases = []
        for phase in workflow.phases:
            available_caps = [c for c in phase.capabilities if c in available_names]
            if available_caps:
                phases.append(
                    WorkflowPhase(
                        name=phase.name,
                        description=phase.description,
                        capabilities=available_caps,
                        parallel=phase.parallel,
                        timeout_seconds=phase.timeout_seconds,
                        retry_count=phase.retry_count,
                        on_failure=phase.on_failure,
                    )
                )

        return Workflow(
            name=workflow.name,
            description=workflow.description,
            stages=workflow.stages,
            phases=phases,
            estimated_duration=workflow.estimated_duration,
            estimated_cost=workflow.estimated_cost,
            required_capabilities=required,
            optional_capabilities=optional,
            adaptation_rules=workflow.adaptation_rules,
        )

    def get_workflow_plan(self, workflow) -> str:
        """Generate a human-readable workflow plan."""
        if isinstance(workflow, GeneratedWorkflow):
            return self._get_generated_plan(workflow)

        lines = [
            "Workflow: %s" % workflow.name,
            "=" * 50,
            "Description: %s" % workflow.description,
            "Stages: %s" % ", ".join(workflow.stages),
            "Estimated duration: %s" % workflow.estimated_duration,
            "Estimated cost: %s" % workflow.estimated_cost,
            "",
            "Phases:",
        ]

        for i, phase in enumerate(workflow.phases, 1):
            lines.append("")
            lines.append("  Phase %d: %s" % (i, phase.name))
            lines.append("  Description: %s" % phase.description)
            lines.append("  Capabilities: %s" % ", ".join(phase.capabilities))
            lines.append("  Parallel: %s" % phase.parallel)
            lines.append("  Timeout: %ds" % phase.timeout_seconds)
            lines.append("  Retries: %d" % phase.retry_count)
            lines.append("  On failure: %s" % phase.on_failure)

        lines.append("")
        lines.append(
            "Required capabilities: %s" % ", ".join(workflow.required_capabilities)
        )
        lines.append(
            "Optional capabilities: %s" % ", ".join(workflow.optional_capabilities)
        )

        return "\n".join(lines)

    def _get_generated_plan(self, workflow: GeneratedWorkflow) -> str:
        """Generate plan for a dynamically generated workflow."""
        lines = [
            "Workflow: %s [DYNAMIC]" % workflow.name,
            "=" * 50,
            "Description: %s" % workflow.description,
            "DAG nodes: %d" % len(workflow.dag.nodes),
            "DAG edges: %d" % len(workflow.dag.edges),
            "Critical path: %s" % " -> ".join(workflow.critical_path),
            "Estimated duration: %.0fs" % workflow.estimated_duration_seconds,
            "",
            "Validation: %s"
            % (
                "PASS"
                if workflow.validation_result and workflow.validation_result.is_valid
                else "FAIL"
            ),
        ]

        if workflow.validation_result and not workflow.validation_result.is_valid:
            for issue in workflow.validation_result.issues:
                lines.append("  - %s" % issue)

        parallel_groups = workflow.dag.get_parallel_groups()
        lines.append("")
        lines.append("Execution groups (parallel within groups):")
        for i, group in enumerate(parallel_groups, 1):
            lines.append("  Group %d: %s" % (i, ", ".join(group)))

        lines.append("")
        lines.append("Phases:")
        for i, phase in enumerate(workflow.phases, 1):
            deps = workflow.dag.get_dependencies(phase.name)
            lines.append("")
            lines.append("  Phase %d: %s" % (i, phase.name))
            lines.append("  Description: %s" % phase.description)
            lines.append("  Dependencies: %s" % (", ".join(deps) if deps else "None"))
            lines.append("  Capabilities: %s" % ", ".join(phase.capabilities))
            lines.append("  Parallel: %s" % phase.parallel)
            lines.append("  Timeout: %ds" % phase.timeout_seconds)

        return "\n".join(lines)

    def get_metrics_report(self) -> str:
        """Get workflow metrics report."""
        return self.metrics.generate_report()

    def get_execution_analytics(self) -> Dict:
        """Get execution analytics from metrics."""
        return self.metrics.get_analytics()
