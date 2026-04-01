"""
Layer 1: Skills - Check existing skills for matching capabilities.

First line of defense: scan registered skills for capability matches
before escalating to more expensive layers.
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class SkillMatchType(Enum):
    EXACT = "exact"
    PARTIAL = "partial"
    SEMANTIC = "semantic"


@dataclass
class SkillMatch:
    """Represents a match between task and skill."""

    skill_name: str
    match_type: SkillMatchType
    confidence: float
    matched_keywords: List[str] = field(default_factory=list)
    description: str = ""


@dataclass
class SkillsLayerResult:
    """Result from skills layer processing."""

    success: bool
    matched_skills: List[SkillMatch] = field(default_factory=list)
    capability_found: bool = False
    execution_plan: Optional[str] = None
    error: Optional[str] = None


class SkillsLayer:
    """
    Layer 1: Check if existing skills can handle the unknown task.

    Uses keyword matching, semantic similarity, and capability registry
    to find the best skill match for an unknown task.
    """

    def __init__(self, skill_registry: Optional[Dict[str, Any]] = None):
        self.skill_registry = skill_registry or {}
        self._keyword_index: Dict[str, List[str]] = {}
        self._build_keyword_index()

    def _build_keyword_index(self) -> None:
        """Build inverted index of keywords to skills."""
        for skill_name, skill_data in self.skill_registry.items():
            keywords = self._extract_keywords(skill_data)
            for keyword in keywords:
                if keyword not in self._keyword_index:
                    self._keyword_index[keyword] = []
                self._keyword_index[keyword].append(skill_name)

    def _extract_keywords(self, skill_data: Dict[str, Any]) -> List[str]:
        """Extract searchable keywords from skill metadata."""
        keywords = []
        for key in ["name", "description", "keywords", "capabilities", "triggers"]:
            value = skill_data.get(key, "")
            if isinstance(value, str):
                keywords.extend(re.findall(r"\b\w+\b", value.lower()))
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        keywords.extend(re.findall(r"\b\w+\b", item.lower()))
        return list(set(keywords))

    def can_handle(self, task: str) -> bool:
        """Check if any skill can handle this task."""
        return self.get_confidence(task) > 0.0

    def get_confidence(self, task: str) -> float:
        """Get confidence score for skill-based handling."""
        matches = self._find_matches(task)
        if not matches:
            return 0.0
        return max(m.confidence for m in matches)

    def _find_matches(self, task: str) -> List[SkillMatch]:
        """Find all skill matches for the task."""
        task_lower = task.lower()
        task_words = set(re.findall(r"\b\w+\b", task_lower))
        matches = []

        for skill_name, skill_data in self.skill_registry.items():
            match = self._score_skill_match(skill_name, skill_data, task_words)
            if match and match.confidence > 0.0:
                matches.append(match)

        matches.sort(key=lambda m: m.confidence, reverse=True)
        return matches

    def _score_skill_match(
        self,
        skill_name: str,
        skill_data: Dict[str, Any],
        task_words: set,
    ) -> Optional[SkillMatch]:
        """Score how well a skill matches the task."""
        matched_keywords = []
        max_confidence = 0.0
        match_type = SkillMatchType.SEMANTIC

        for keyword in self._keyword_index:
            if keyword in task_words:
                matched_skills = self._keyword_index[keyword]
                if skill_name in matched_skills:
                    matched_keywords.append(keyword)

        if matched_keywords:
            overlap = len(matched_keywords) / max(len(task_words), 1)
            max_confidence = min(overlap * 2.0, 0.8)
            match_type = SkillMatchType.PARTIAL

        skill_name_lower = skill_name.lower()
        if any(word in skill_name_lower for word in task_words):
            max_confidence = max(max_confidence, 0.9)
            match_type = SkillMatchType.EXACT

        description = skill_data.get("description", "")
        if description and any(word in description.lower() for word in task_words):
            max_confidence = max(max_confidence, 0.7)

        if not matched_keywords and max_confidence == 0.0:
            return None

        return SkillMatch(
            skill_name=skill_name,
            match_type=match_type,
            confidence=max_confidence,
            matched_keywords=matched_keywords,
            description=description,
        )

    def handle(self, task: str) -> SkillsLayerResult:
        """Attempt to handle task using existing skills."""
        matches = self._find_matches(task)

        if not matches:
            return SkillsLayerResult(
                success=False,
                error="No matching skills found for task",
            )

        best_match = matches[0]
        skill_data = self.skill_registry.get(best_match.skill_name, {})

        execution_plan = self._generate_execution_plan(best_match, skill_data, task)

        return SkillsLayerResult(
            success=True,
            matched_skills=matches,
            capability_found=True,
            execution_plan=execution_plan,
        )

    def _generate_execution_plan(
        self,
        match: SkillMatch,
        skill_data: Dict[str, Any],
        task: str,
    ) -> str:
        """Generate an execution plan based on the matched skill."""
        steps = skill_data.get("steps", [])
        if steps:
            plan_lines = [f"Using skill: {match.skill_name}", "", "Steps:"]
            for i, step in enumerate(steps, 1):
                plan_lines.append(f"  {i}. {step}")
            return "\n".join(plan_lines)

        return (
            f"Execute skill '{match.skill_name}' for task.\n"
            f"Description: {match.description}\n"
            f"Match confidence: {match.confidence:.2f}"
        )

    def register_skill(self, name: str, metadata: Dict[str, Any]) -> None:
        """Register a new skill in the registry."""
        self.skill_registry[name] = metadata
        self._build_keyword_index()

    def get_skill_names(self) -> List[str]:
        """Get all registered skill names."""
        return list(self.skill_registry.keys())
