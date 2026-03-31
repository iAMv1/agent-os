import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class WorkflowPhase:
    name: str
    description: str
    capabilities: List[str]  # capability names
    parallel: bool
    timeout_seconds: int
    retry_count: int
    on_failure: str  # "continue", "abort", "skip"


@dataclass
class Workflow:
    name: str
    description: str
    stages: List[str]  # SDLC stage names
    phases: List[WorkflowPhase]
    estimated_duration: str
    estimated_cost: str
    required_capabilities: List[str]
    optional_capabilities: List[str]
    adaptation_rules: Dict[str, str]


class WorkflowComposer:
    """Composes workflows from capabilities based on task classification."""

    def __init__(self, capability_registry):
        self.registry = capability_registry
        self.workflow_templates = self._build_templates()

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

        # Select base workflow template
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

        # If task spans multiple stages, use full lifecycle
        if len(classification_result.sdlc_stages) > 2:
            base_workflow = self.workflow_templates["full_lifecycle"]

        # Adapt workflow based on complexity
        adapted = self._adapt_for_complexity(base_workflow, complexity)

        # Adapt workflow based on domain
        adapted = self._adapt_for_domain(adapted, domain)

        # Adapt workflow based on available capabilities
        adapted = self._adapt_for_availability(adapted)

        return adapted

    def _adapt_for_complexity(self, workflow: Workflow, complexity: str) -> Workflow:
        """Adapt workflow based on task complexity."""
        phases = list(workflow.phases)

        if complexity == "simple":
            # Simplify: reduce phases, skip parallel execution
            if len(phases) > 2:
                # Merge first two phases
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
            # Enhance: add planning phase, increase parallelism
            if "Plan-agent" not in phases[0].capabilities:
                phases[0].capabilities.append("Plan-agent")
            # Increase timeout for complex tasks
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

        # Add domain-specific capabilities to optional
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

        # Filter out unavailable required capabilities
        required = [c for c in workflow.required_capabilities if c in available_names]
        optional = [c for c in workflow.optional_capabilities if c in available_names]

        # Filter phases
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

    def get_workflow_plan(self, workflow: Workflow) -> str:
        """Generate a human-readable workflow plan."""
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
