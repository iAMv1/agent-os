import json
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class SDLCStage(Enum):
    REQUIREMENTS = "requirements"
    DESIGN = "design"
    IMPLEMENTATION = "implementation"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    MAINTENANCE = "maintenance"
    COLLABORATION = "collaboration"
    INFRASTRUCTURE = "infrastructure"


class TaskComplexity(Enum):
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"


class Domain(Enum):
    WEB = "web"
    MOBILE = "mobile"
    DATA_ML = "data_ml"
    DEVOPS = "devops"
    SECURITY = "security"
    GENERAL = "general"
    CLI = "cli"
    API = "api"
    FRONTEND = "frontend"
    BACKEND = "backend"
    FULLSTACK = "fullstack"


@dataclass
class ClassificationResult:
    task_type: str
    sdlc_stages: List[SDLCStage]
    complexity: TaskComplexity
    domain: Domain
    estimated_files: int
    requires_user_input: bool
    keywords: List[str]
    confidence: float


class TaskClassifier:
    """Classifies software development tasks into SDLC stages, complexity, and domain."""

    # Keyword patterns for task type classification
    TASK_PATTERNS = {
        "requirements_gathering": [
            r"\b(need|want|should|must)\b.*\b(build|create|make|develop)\b",
            r"\b(help me understand|figure out|clarify|define)\b",
            r"\b(gather|collect|identify)\b.*\b(requirements|needs|features)\b",
            r"\b(what|how|why)\b.*\b(should|would|could)\b",
            r"\b(user stories|user journeys|epics|features)\b",
            r"\b(problem|pain point|goal|objective)\b",
        ],
        "architecture_design": [
            r"\b(design|architect|structure|organize)\b.*\b(system|app|project|codebase)\b",
            r"\b(how should i|what is the best way)\b.*\b(structure|organize|build)\b",
            r"\b(architecture|design pattern|microservice|monolith)\b",
            r"\b(plan|roadmap|blueprint|spec)\b",
            r"\b(component|module|service|layer)\b.*\b(boundary|interface|contract)\b",
        ],
        "implementation": [
            r"\b(build|create|implement|write|develop|code|make)\b",
            r"\b(add|new|feature|functionality)\b",
            r"\b(api|endpoint|route|handler|controller)\b",
            r"\b(component|page|screen|view|widget)\b",
            r"\b(model|schema|database|table|collection)\b",
            r"\b(auth|login|register|signup|oauth|jwt)\b",
            r"\b(form|validation|input|submit)\b",
        ],
        "testing_qa": [
            r"\b(test|spec|assert|expect|verify|validate)\b",
            r"\b(unit test|integration test|e2e|end.to.end)\b",
            r"\b(bug|issue|error|crash|broken|failing)\b",
            r"\b(coverage|mock|stub|fixture)\b",
            r"\b(qa|quality|assurance|review)\b",
        ],
        "deployment_devops": [
            r"\b(deploy|release|ship|publish|launch)\b",
            r"\b(ci|cd|pipeline|workflow|action)\b",
            r"\b(docker|container|kubernetes|k8s)\b",
            r"\b(infrastructure|server|cloud|aws|gcp|azure)\b",
            r"\b(environment|staging|production|dev)\b",
        ],
        "maintenance_monitoring": [
            r"\b(fix|debug|troubleshoot|diagnose|investigate)\b",
            r"\b(optimize|improve|refactor|clean up|restructure)\b",
            r"\b(performance|speed|memory|cpu|bottleneck)\b",
            r"\b(monitor|alert|log|metric|trace)\b",
            r"\b(migrate|upgrade|update|patch)\b",
        ],
    }

    # Domain detection patterns
    DOMAIN_PATTERNS = {
        Domain.WEB: [
            r"\b(react|vue|angular|svelte|next\.?js|nuxt|remix)\b",
            r"\b(html|css|tailwind|bootstrap|styled)\b",
            r"\b(browser|frontend|frontend|web app|website)\b",
        ],
        Domain.MOBILE: [
            r"\b(react native|flutter|swift|kotlin|android|ios)\b",
            r"\b(mobile|app store|play store|simulator)\b",
        ],
        Domain.DATA_ML: [
            r"\b(pandas|numpy|scikit|tensorflow|pytorch|jupyter)\b",
            r"\b(data|ml|machine learning|model|training|prediction)\b",
            r"\b(etl|pipeline|dataframe|dataset)\b",
        ],
        Domain.DEVOPS: [
            r"\b(docker|kubernetes|terraform|ansible|helm)\b",
            r"\b(ci/cd|pipeline|deploy|infrastructure|iac)\b",
            r"\b(aws|gcp|azure|cloud|serverless)\b",
        ],
        Domain.SECURITY: [
            r"\b(security|vulnerability|pentest|audit|auth)\b",
            r"\b(encrypt|hash|token|jwt|oauth|cors|csrf)\b",
        ],
        Domain.CLI: [
            r"\b(cli|command.line|terminal|shell|script)\b",
            r"\b(argparse|click|cobra|argparse)\b",
        ],
        Domain.API: [
            r"\b(api|rest|graphql|grpc|endpoint|route)\b",
            r"\b(express|fastapi|flask|django|spring)\b",
        ],
        Domain.FRONTEND: [
            r"\b(react|vue|angular|svelte|frontend|ui|ux)\b",
            r"\b(component|page|screen|widget|layout)\b",
        ],
        Domain.BACKEND: [
            r"\b(backend|server|database|api|service)\b",
            r"\b(node|python|java|go|rust|ruby)\b",
        ],
    }

    # Complexity indicators
    COMPLEXITY_PATTERNS = {
        TaskComplexity.SIMPLE: [
            r"\b(simple|basic|quick|easy|small|tiny)\b",
            r"\b(one|single|just|only)\b.*\b(file|function|change)\b",
            r"\b(tiny|minor|trivial)\b",
        ],
        TaskComplexity.COMPLEX: [
            r"\b(complex|large|big|enterprise|full)\b",
            r"\b(system|platform|framework|ecosystem)\b",
            r"\b(multi|many|several|numerous)\b.*\b(component|service|feature)\b",
            r"\b(end.to.end|complete|full.stack|production)\b",
        ],
    }

    def classify(self, task_description: str) -> ClassificationResult:
        """Classify a task description into SDLC stages, complexity, and domain."""
        task_lower = task_description.lower()

        # Determine task type and SDLC stages
        task_type, stages = self._determine_task_type(task_lower)

        # Determine domain
        domain = self._determine_domain(task_lower)

        # Determine complexity
        complexity = self._determine_complexity(task_lower)

        # Estimate file count
        estimated_files = self._estimate_file_count(task_lower, complexity)

        # Check if user input is needed
        requires_user_input = self._requires_user_input(task_lower)

        # Extract keywords
        keywords = self._extract_keywords(task_lower)

        # Calculate confidence
        confidence = self._calculate_confidence(task_lower, task_type, domain)

        return ClassificationResult(
            task_type=task_type,
            sdlc_stages=stages,
            complexity=complexity,
            domain=domain,
            estimated_files=estimated_files,
            requires_user_input=requires_user_input,
            keywords=keywords,
            confidence=confidence,
        )

    def _determine_task_type(self, task_lower: str) -> Tuple[str, List[SDLCStage]]:
        """Determine the primary task type and associated SDLC stages."""
        scores = {}
        for task_type, patterns in self.TASK_PATTERNS.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, task_lower):
                    score += 1
            scores[task_type] = score

        if not scores or max(scores.values()) == 0:
            # Default to implementation if no clear pattern
            return "implementation", [SDLCStage.IMPLEMENTATION]

        best_type = max(scores, key=scores.get)

        stage_map = {
            "requirements_gathering": [SDLCStage.REQUIREMENTS],
            "architecture_design": [SDLCStage.DESIGN, SDLCStage.REQUIREMENTS],
            "implementation": [SDLCStage.IMPLEMENTATION],
            "testing_qa": [SDLCStage.TESTING, SDLCStage.MAINTENANCE],
            "deployment_devops": [SDLCStage.DEPLOYMENT, SDLCStage.INFRASTRUCTURE],
            "maintenance_monitoring": [SDLCStage.MAINTENANCE],
        }

        return best_type, stage_map.get(best_type, [SDLCStage.IMPLEMENTATION])

    def _determine_domain(self, task_lower: str) -> Domain:
        """Determine the primary domain of the task."""
        scores = {}
        for domain, patterns in self.DOMAIN_PATTERNS.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, task_lower):
                    score += 1
            scores[domain] = score

        if max(scores.values()) == 0:
            return Domain.GENERAL

        best_domain = max(scores, key=scores.get)

        # Check for fullstack (both frontend and backend detected)
        frontend_score = scores.get(Domain.FRONTEND, 0)
        backend_score = scores.get(Domain.BACKEND, 0)
        if frontend_score > 0 and backend_score > 0:
            return Domain.FULLSTACK

        return best_domain

    def _determine_complexity(self, task_lower: str) -> TaskComplexity:
        """Determine task complexity."""
        simple_score = sum(
            1
            for p in self.COMPLEXITY_PATTERNS[TaskComplexity.SIMPLE]
            if re.search(p, task_lower)
        )
        complex_score = sum(
            1
            for p in self.COMPLEXITY_PATTERNS[TaskComplexity.COMPLEX]
            if re.search(p, task_lower)
        )

        if complex_score > simple_score:
            return TaskComplexity.COMPLEX
        elif simple_score > 0:
            return TaskComplexity.SIMPLE
        else:
            return TaskComplexity.MEDIUM

    def _estimate_file_count(self, task_lower: str, complexity: TaskComplexity) -> int:
        """Estimate number of files involved."""
        base = {
            TaskComplexity.SIMPLE: 3,
            TaskComplexity.MEDIUM: 10,
            TaskComplexity.COMPLEX: 50,
        }

        # Adjust based on keywords
        if any(w in task_lower for w in ["app", "system", "platform", "full"]):
            base[complexity] *= 2
        if any(w in task_lower for w in ["file", "script", "function"]):
            base[complexity] = max(1, base[complexity] // 3)

        return base[complexity]

    def _requires_user_input(self, task_lower: str) -> bool:
        """Check if task likely requires user input."""
        input_indicators = [
            r"\b(should i|which|what kind|how many|do you think)\b",
            r"\b(prefer|want|need|like|choose|decide)\b",
            r"\b(my|our|the)\b.*\b(requirement|preference|style|approach)\b",
        ]
        return any(re.search(p, task_lower) for p in input_indicators)

    def _extract_keywords(self, task_lower: str) -> List[str]:
        """Extract relevant keywords from task description."""
        tech_keywords = [
            "react",
            "vue",
            "angular",
            "svelte",
            "next",
            "nuxt",
            "remix",
            "node",
            "python",
            "java",
            "go",
            "rust",
            "ruby",
            "typescript",
            "javascript",
            "express",
            "fastapi",
            "flask",
            "django",
            "spring",
            "rails",
            "postgres",
            "mysql",
            "mongodb",
            "redis",
            "sqlite",
            "docker",
            "kubernetes",
            "terraform",
            "aws",
            "gcp",
            "azure",
            "api",
            "rest",
            "graphql",
            "grpc",
            "grpc",
            "auth",
            "oauth",
            "jwt",
            "login",
            "register",
            "test",
            "jest",
            "pytest",
            "vitest",
            "cypress",
            "ci",
            "cd",
            "pipeline",
            "deploy",
            "git",
            "github",
            "gitlab",
        ]

        found = []
        for kw in tech_keywords:
            if kw in task_lower:
                found.append(kw)
        return found

    def _calculate_confidence(
        self, task_lower: str, task_type: str, domain: Domain
    ) -> float:
        """Calculate classification confidence (0.0 to 1.0)."""
        confidence = 0.5  # Base confidence

        # More keywords = higher confidence
        word_count = len(task_lower.split())
        if word_count > 20:
            confidence += 0.2
        elif word_count > 10:
            confidence += 0.1

        # Clear domain = higher confidence
        if domain != Domain.GENERAL:
            confidence += 0.1

        # Clear task type = higher confidence
        if task_type != "implementation":
            confidence += 0.1

        return min(confidence, 1.0)

    def to_dict(self, result: ClassificationResult) -> dict:
        """Convert classification result to dictionary."""
        return {
            "task_type": result.task_type,
            "sdlc_stages": [s.value for s in result.sdlc_stages],
            "complexity": result.complexity.value,
            "domain": result.domain.value,
            "estimated_files": result.estimated_files,
            "requires_user_input": result.requires_user_input,
            "keywords": result.keywords,
            "confidence": result.confidence,
        }
