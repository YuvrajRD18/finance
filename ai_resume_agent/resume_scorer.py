"""Score a parsed resume and surface actionable improvement suggestions."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List

from .resume_parser import ParsedResume


@dataclass
class ScoreResult:
    """Result produced by :class:`ResumeScorer`."""

    total_score: int = 0  # 0-100
    section_scores: Dict[str, int] = field(default_factory=dict)
    suggestions: List[str] = field(default_factory=list)

    def __str__(self) -> str:  # pragma: no cover – cosmetic
        lines = [f"Resume Score: {self.total_score}/100", ""]
        if self.section_scores:
            lines.append("Section Scores:")
            for name, score in sorted(self.section_scores.items()):
                lines.append(f"  {name}: {score}")
            lines.append("")
        if self.suggestions:
            lines.append("Suggestions:")
            for idx, s in enumerate(self.suggestions, 1):
                lines.append(f"  {idx}. {s}")
        return "\n".join(lines)


# Sections that a strong resume should include, with max points each.
_EXPECTED_SECTIONS: Dict[str, int] = {
    "contact": 10,
    "summary": 15,
    "experience": 25,
    "education": 15,
    "skills": 15,
}

# Bonus sections worth extra credit (up to 20 points total).
_BONUS_SECTIONS: Dict[str, int] = {
    "certifications": 5,
    "projects": 5,
    "awards": 5,
    "publications": 5,
}

# ---- helpers used by individual section scorers ----------------------

_ACTION_VERBS = re.compile(
    r"\b(?:led|managed|developed|designed|implemented|increased|decreased|"
    r"created|built|delivered|achieved|improved|analyzed|optimized|launched|"
    r"coordinated|negotiated|mentored|supervised|established|generated|"
    r"reduced|streamlined|spearheaded|executed|orchestrated)\b",
    re.IGNORECASE,
)

_METRIC_PATTERN = re.compile(r"\d+\s*%|\$\s*[\d,.]+|\d{2,}")


class ResumeScorer:
    """Evaluate a :class:`ParsedResume` and produce a :class:`ScoreResult`."""

    def score(self, resume: ParsedResume) -> ScoreResult:
        section_scores: Dict[str, int] = {}
        suggestions: List[str] = []

        # --- required sections ---
        for section, max_pts in _EXPECTED_SECTIONS.items():
            pts, tips = self._score_section(resume, section, max_pts)
            section_scores[section] = pts
            suggestions.extend(tips)

        # --- bonus sections ---
        bonus = 0
        for section, max_pts in _BONUS_SECTIONS.items():
            if resume.has_section(section):
                bonus += max_pts
        bonus = min(bonus, 20)
        section_scores["bonus"] = bonus

        total = sum(section_scores.values())
        total = max(0, min(total, 100))

        return ScoreResult(
            total_score=total,
            section_scores=section_scores,
            suggestions=suggestions,
        )

    # ------------------------------------------------------------------
    # Per-section scoring
    # ------------------------------------------------------------------

    def _score_section(
        self, resume: ParsedResume, section: str, max_pts: int
    ) -> tuple[int, List[str]]:
        tips: List[str] = []

        if not resume.has_section(section):
            tips.append(f"Add a '{section.title()}' section to strengthen your resume.")
            return 0, tips

        content = resume.sections[section]
        length = len(content.split())

        # Base score: section exists → half credit.
        pts = max_pts // 2

        # Depth bonus: enough content?
        if length >= 20:
            pts += max_pts - pts  # full credit
        elif length >= 10:
            pts += (max_pts - pts) // 2
        else:
            tips.append(
                f"Expand your '{section.title()}' section – "
                f"it currently has only {length} words."
            )

        # Experience-specific quality checks.
        if section == "experience":
            pts, tips = self._quality_experience(content, pts, max_pts, tips)

        return pts, tips

    @staticmethod
    def _quality_experience(
        content: str, pts: int, max_pts: int, tips: List[str]
    ) -> tuple[int, List[str]]:
        if not _ACTION_VERBS.search(content):
            deduction = max_pts // 5
            pts = max(0, pts - deduction)
            tips.append(
                "Use strong action verbs (e.g. 'Led', 'Developed', 'Implemented') "
                "to describe your accomplishments."
            )

        if not _METRIC_PATTERN.search(content):
            deduction = max_pts // 5
            pts = max(0, pts - deduction)
            tips.append(
                "Quantify achievements with metrics (e.g. 'Increased revenue by 20%')."
            )

        return pts, tips
