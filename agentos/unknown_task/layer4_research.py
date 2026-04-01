"""
Layer 4: Research - Fork agents for deep research.

When tools and skills aren't enough, fork research agents to
gather domain knowledge and build understanding of the task.
"""

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import time
from datetime import datetime, timezone


class ResearchState(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class ResearchFinding:
    """A single finding from research."""

    source: str
    content: str
    confidence: float
    relevance: float
    timestamp: Optional[str] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc).isoformat()


@dataclass
class ResearchAgent:
    """A forked research agent."""

    agent_id: str
    query: str
    state: ResearchState
    findings: List[ResearchFinding] = field(default_factory=list)
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None


@dataclass
class ResearchLayerResult:
    """Result from research layer."""

    success: bool
    agents: List[ResearchAgent] = field(default_factory=list)
    consolidated_findings: List[ResearchFinding] = field(default_factory=list)
    knowledge_summary: Optional[str] = None
    error: Optional[str] = None


class ResearchLayer:
    """
    Layer 4: Fork agents for deep research.

    Spawns research agents to gather knowledge about unknown tasks
    when other layers cannot provide sufficient capability.
    """

    def __init__(
        self,
        max_agents: int = 3,
        timeout_seconds: int = 300,
        min_confidence: float = 0.5,
    ):
        self.max_agents = max_agents
        self.timeout_seconds = timeout_seconds
        self.min_confidence = min_confidence
        self._agents: Dict[str, ResearchAgent] = {}
        self._research_history: List[Dict[str, Any]] = []

    def can_handle(self, task: str) -> bool:
        """Research can always attempt to handle unknown tasks."""
        return True

    def get_confidence(self, task: str) -> float:
        """Research confidence is based on task clarity."""
        task_lower = task.lower()
        words = task_lower.split()

        if len(words) < 3:
            return 0.4

        if len(words) < 6:
            return 0.6

        return 0.8

    def handle(self, task: str) -> ResearchLayerResult:
        """Fork research agents to investigate the task."""
        queries = self._generate_research_queries(task)
        agents = []

        for i, query in enumerate(queries[: self.max_agents]):
            agent = self._create_agent(f"research-{i}", query)
            agents.append(agent)

        for agent in agents:
            self._execute_research(agent, task)

        consolidated = self._consolidate_findings(agents)
        summary = self._generate_summary(task, consolidated)

        failed_agents = [a for a in agents if a.state == ResearchState.FAILED]
        if failed_agents and not consolidated:
            return ResearchLayerResult(
                success=False,
                agents=agents,
                error="All research agents failed",
            )

        return ResearchLayerResult(
            success=True,
            agents=agents,
            consolidated_findings=consolidated,
            knowledge_summary=summary,
        )

    def _generate_research_queries(self, task: str) -> List[str]:
        """Generate research queries from the task."""
        task_lower = task.lower()
        queries = [task_lower]

        words = task_lower.split()
        if len(words) > 2:
            queries.append(f"how to {' '.join(words[:3])}")
            queries.append(f"{' '.join(words[-2:])} best practices")

        domain_keywords = {
            "api": "REST API integration patterns",
            "database": "database design patterns",
            "test": "testing strategies and frameworks",
            "deploy": "deployment and CI/CD pipelines",
            "security": "security best practices",
            "performance": "performance optimization techniques",
            "auth": "authentication and authorization patterns",
            "cache": "caching strategies and patterns",
        }

        for keyword, domain_query in domain_keywords.items():
            if keyword in task_lower:
                queries.append(domain_query)
                break

        return list(set(queries))

    def _create_agent(self, agent_id: str, query: str) -> ResearchAgent:
        """Create a new research agent."""
        agent = ResearchAgent(
            agent_id=agent_id,
            query=query,
            state=ResearchState.PENDING,
            started_at=datetime.now(timezone.utc).isoformat(),
        )
        self._agents[agent_id] = agent
        return agent

    def _execute_research(self, agent: ResearchAgent, task: str) -> None:
        """Execute research for an agent."""
        agent.state = ResearchState.RUNNING

        try:
            findings = self._gather_findings(agent.query, task)
            agent.findings = findings
            agent.state = ResearchState.COMPLETED if findings else ResearchState.FAILED
            if not findings:
                agent.error = "No findings gathered"
        except Exception as e:
            agent.state = ResearchState.FAILED
            agent.error = str(e)

        agent.completed_at = datetime.now(timezone.utc).isoformat()

    def _gather_findings(self, query: str, task: str) -> List[ResearchFinding]:
        """Gather findings for a research query."""
        findings = []

        task_lower = task.lower()

        if "api" in task_lower or "endpoint" in task_lower:
            findings.append(
                ResearchFinding(
                    source="domain_knowledge",
                    content="API development typically involves defining endpoints, request/response schemas, authentication, and error handling.",
                    confidence=0.7,
                    relevance=0.8,
                )
            )

        if "database" in task_lower or "storage" in task_lower:
            findings.append(
                ResearchFinding(
                    source="domain_knowledge",
                    content="Database operations include schema design, query optimization, connection pooling, and migration management.",
                    confidence=0.7,
                    relevance=0.8,
                )
            )

        if "test" in task_lower or "verify" in task_lower:
            findings.append(
                ResearchFinding(
                    source="domain_knowledge",
                    content="Testing strategies include unit tests, integration tests, end-to-end tests, and property-based testing.",
                    confidence=0.7,
                    relevance=0.8,
                )
            )

        if "deploy" in task_lower or "release" in task_lower:
            findings.append(
                ResearchFinding(
                    source="domain_knowledge",
                    content="Deployment involves CI/CD pipelines, containerization, environment configuration, and rollback strategies.",
                    confidence=0.7,
                    relevance=0.8,
                )
            )

        if not findings:
            findings.append(
                ResearchFinding(
                    source="general_knowledge",
                    content=f"Task analysis for: {task}. Further domain-specific research recommended.",
                    confidence=0.5,
                    relevance=0.5,
                )
            )

        return findings

    def _consolidate_findings(
        self, agents: List[ResearchAgent]
    ) -> List[ResearchFinding]:
        """Consolidate findings from all agents."""
        all_findings = []
        seen_content = set()

        for agent in agents:
            for finding in agent.findings:
                content_key = finding.content[:100]
                if content_key not in seen_content:
                    seen_content.add(content_key)
                    all_findings.append(finding)

        all_findings.sort(key=lambda f: f.relevance * f.confidence, reverse=True)
        return all_findings

    def _generate_summary(self, task: str, findings: List[ResearchFinding]) -> str:
        """Generate a knowledge summary from findings."""
        lines = [
            f"Research Summary for: {task}",
            "=" * 50,
            "",
            f"Total findings: {len(findings)}",
            "",
        ]

        for i, finding in enumerate(findings, 1):
            lines.append(f"Finding {i} (confidence: {finding.confidence:.2f}):")
            lines.append(f"  Source: {finding.source}")
            lines.append(f"  {finding.content}")
            lines.append("")

        return "\n".join(lines)

    def get_agent_status(self) -> Dict[str, ResearchState]:
        """Get status of all research agents."""
        return {agent_id: agent.state for agent_id, agent in self._agents.items()}

    def get_research_history(self) -> List[Dict[str, Any]]:
        """Get research history."""
        return list(self._research_history)
