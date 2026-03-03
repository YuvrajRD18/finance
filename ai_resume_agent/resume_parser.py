"""Parse raw resume text into structured sections."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List


# Canonical section names mapped from common header variants.
_SECTION_ALIASES: Dict[str, str] = {
    "experience": "experience",
    "work experience": "experience",
    "professional experience": "experience",
    "employment history": "experience",
    "education": "education",
    "academic background": "education",
    "skills": "skills",
    "technical skills": "skills",
    "core competencies": "skills",
    "projects": "projects",
    "certifications": "certifications",
    "certificates": "certifications",
    "summary": "summary",
    "professional summary": "summary",
    "objective": "summary",
    "contact": "contact",
    "contact information": "contact",
    "awards": "awards",
    "honors": "awards",
    "publications": "publications",
    "languages": "languages",
    "references": "references",
}

# Pattern that matches a line that looks like a section header.
_HEADER_RE = re.compile(
    r"^\s*(?P<header>[A-Za-z][A-Za-z &/]+[A-Za-z])\s*:?\s*$",
    re.MULTILINE,
)


@dataclass
class ParsedResume:
    """Structured representation of a parsed resume."""

    sections: Dict[str, str] = field(default_factory=dict)
    raw_text: str = ""

    @property
    def section_names(self) -> List[str]:
        """Return sorted list of detected section names."""
        return sorted(self.sections.keys())

    def has_section(self, name: str) -> bool:
        """Check whether a canonical section exists."""
        return name.lower() in self.sections


class ResumeParser:
    """Extract canonical sections from plain-text resume content."""

    def parse(self, text: str) -> ParsedResume:
        """Parse *text* and return a :class:`ParsedResume`.

        The parser identifies section headers (lines that consist of a
        short capitalised phrase, optionally followed by a colon) and
        maps them to canonical names such as ``experience``,
        ``education``, ``skills``, etc.

        Content before the first recognised header is stored under the
        ``"header"`` key (typically the candidate's name / contact
        block).
        """
        if not text or not text.strip():
            return ParsedResume(sections={}, raw_text=text or "")

        sections: Dict[str, str] = {}
        current_section: str | None = None
        current_lines: List[str] = []

        for line in text.splitlines():
            stripped = line.strip()
            canonical = self._match_header(stripped)
            if canonical is not None:
                # Flush the previous section.
                self._flush(sections, current_section, current_lines)
                current_section = canonical
                current_lines = []
            else:
                current_lines.append(line)

        # Flush the last section.
        self._flush(sections, current_section, current_lines)

        return ParsedResume(sections=sections, raw_text=text)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _match_header(line: str) -> str | None:
        """Return canonical section name if *line* is a header, else ``None``."""
        cleaned = line.rstrip(":").strip().lower()
        return _SECTION_ALIASES.get(cleaned)

    @staticmethod
    def _flush(
        sections: Dict[str, str],
        section: str | None,
        lines: List[str],
    ) -> None:
        body = "\n".join(lines).strip()
        if not body:
            return
        key = section if section else "header"
        if key in sections:
            sections[key] += "\n" + body
        else:
            sections[key] = body
