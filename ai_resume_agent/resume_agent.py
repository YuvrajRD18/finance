"""High-level AI Resume Agent that orchestrates parsing, scoring, and feedback."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from .resume_parser import ParsedResume, ResumeParser
from .resume_scorer import ResumeScorer, ScoreResult


@dataclass
class AgentReport:
    """Full analysis report produced by :class:`ResumeAgent`."""

    parsed: ParsedResume
    score_result: ScoreResult
    overall_feedback: str = ""

    def __str__(self) -> str:
        lines = [
            "=" * 60,
            "  AI RESUME AGENT – ANALYSIS REPORT",
            "=" * 60,
            "",
            str(self.score_result),
            "",
            "Overall Feedback:",
            self.overall_feedback,
            "",
            "=" * 60,
        ]
        return "\n".join(lines)


def _build_feedback(parsed: ParsedResume, result: ScoreResult) -> str:
    """Generate a human-readable overall feedback paragraph."""
    parts: List[str] = []

    score = result.total_score
    if score >= 80:
        parts.append(
            "Your resume is strong and well-structured. "
            "A few minor tweaks could make it even better."
        )
    elif score >= 50:
        parts.append(
            "Your resume has a solid foundation but could benefit "
            "from additional detail and stronger language."
        )
    else:
        parts.append(
            "Your resume needs significant improvement. "
            "Focus on adding missing sections and expanding existing content."
        )

    detected = parsed.section_names
    if detected:
        parts.append(f"Detected sections: {', '.join(detected)}.")

    if result.suggestions:
        parts.append(
            f"There are {len(result.suggestions)} suggestion(s) – "
            "review them above to prioritise your next edits."
        )

    return " ".join(parts)


class ResumeAgent:
    """Facade that ties parsing, scoring, and feedback together.

    Usage::

        agent = ResumeAgent()
        report = agent.analyze(resume_text)
        print(report)
    """

    def __init__(self) -> None:
        self._parser = ResumeParser()
        self._scorer = ResumeScorer()

    def analyze(self, text: str) -> AgentReport:
        """Analyze raw resume text and return a full :class:`AgentReport`."""
        parsed = self._parser.parse(text)
        score_result = self._scorer.score(parsed)
        feedback = _build_feedback(parsed, score_result)
        return AgentReport(
            parsed=parsed,
            score_result=score_result,
            overall_feedback=feedback,
        )

    def analyze_sections(self, text: str) -> Dict[str, str]:
        """Return a mapping of canonical section names to their content."""
        return dict(self._parser.parse(text).sections)

    def get_score(self, text: str) -> int:
        """Return the numeric score (0-100) for the resume."""
        parsed = self._parser.parse(text)
        return self._scorer.score(parsed).total_score

    def get_suggestions(self, text: str) -> List[str]:
        """Return the list of improvement suggestions."""
        parsed = self._parser.parse(text)
        return self._scorer.score(parsed).suggestions
