"""Tests for the AI Resume Agent package."""

import pytest

from ai_resume_agent import ResumeAgent, ResumeParser, ResumeScorer
from ai_resume_agent.resume_parser import ParsedResume

# ---------------------------------------------------------------------------
# Sample resume fixtures
# ---------------------------------------------------------------------------

FULL_RESUME = """\
John Doe

Contact
john.doe@email.com | (555) 123-4567 | New York, NY

Summary
Experienced software engineer with 10 years of expertise in full-stack
development, cloud infrastructure, and data engineering. Proven track record
of delivering scalable solutions that drive business value.

Experience
Senior Software Engineer, Acme Corp — 2019-Present
Led a team of 8 engineers to redesign the payments platform, increasing
throughput by 40% and reducing latency by 25%. Developed microservices
architecture using Python, Go, and Kubernetes. Managed $2M annual cloud budget.

Software Engineer, Beta Inc — 2015-2019
Built data pipelines processing 500 GB/day. Implemented CI/CD workflows that
reduced deployment time from 2 hours to 15 minutes.

Education
B.S. Computer Science, MIT — 2015
Graduated summa cum laude. Relevant coursework in algorithms, databases,
distributed systems, and machine learning.

Skills
Python, Go, JavaScript, SQL, Kubernetes, Docker, AWS, GCP, Terraform,
PostgreSQL, Redis, Kafka, CI/CD, Agile, Scrum

Certifications
AWS Solutions Architect – Professional
Certified Kubernetes Administrator (CKA)

Projects
Open-source contributor to Apache Airflow. Built a personal finance tracker
used by 1 000+ users.
"""

MINIMAL_RESUME = """\
Jane Smith
jane@example.com

Experience
Worked at a company.

Education
University degree.
"""

EMPTY_RESUME = ""


# ===========================================================================
# ResumeParser tests
# ===========================================================================


class TestResumeParser:
    def setup_method(self):
        self.parser = ResumeParser()

    def test_parse_full_resume_sections(self):
        result = self.parser.parse(FULL_RESUME)
        assert isinstance(result, ParsedResume)
        for section in ("summary", "experience", "education", "skills"):
            assert result.has_section(section), f"Missing section: {section}"

    def test_parse_detects_certifications(self):
        result = self.parser.parse(FULL_RESUME)
        assert result.has_section("certifications")

    def test_parse_detects_projects(self):
        result = self.parser.parse(FULL_RESUME)
        assert result.has_section("projects")

    def test_parse_header_block(self):
        result = self.parser.parse(FULL_RESUME)
        assert result.has_section("header") or "John Doe" in result.raw_text

    def test_parse_empty_string(self):
        result = self.parser.parse(EMPTY_RESUME)
        assert result.sections == {}
        assert result.raw_text == ""

    def test_parse_none_text(self):
        result = self.parser.parse(None)
        assert result.sections == {}

    def test_section_names_sorted(self):
        result = self.parser.parse(FULL_RESUME)
        assert result.section_names == sorted(result.section_names)

    def test_has_section_case_insensitive(self):
        result = self.parser.parse(FULL_RESUME)
        # has_section lowercases the input, so both forms match
        assert result.has_section("EXPERIENCE") is True
        assert result.has_section("experience") is True

    def test_minimal_resume_has_experience(self):
        result = self.parser.parse(MINIMAL_RESUME)
        assert result.has_section("experience")

    def test_minimal_resume_has_education(self):
        result = self.parser.parse(MINIMAL_RESUME)
        assert result.has_section("education")

    def test_alias_work_experience(self):
        text = "Work Experience\nDid some work for 5 years at a big company."
        result = self.parser.parse(text)
        assert result.has_section("experience")

    def test_alias_professional_summary(self):
        text = "Professional Summary\nA seasoned professional with many years of deep expertise."
        result = self.parser.parse(text)
        assert result.has_section("summary")

    def test_alias_technical_skills(self):
        text = "Technical Skills\nPython, Java, SQL, and many other technologies."
        result = self.parser.parse(text)
        assert result.has_section("skills")


# ===========================================================================
# ResumeScorer tests
# ===========================================================================


class TestResumeScorer:
    def setup_method(self):
        self.parser = ResumeParser()
        self.scorer = ResumeScorer()

    def _score(self, text: str):
        return self.scorer.score(self.parser.parse(text))

    def test_full_resume_high_score(self):
        result = self._score(FULL_RESUME)
        assert result.total_score >= 80

    def test_minimal_resume_lower_score(self):
        result = self._score(MINIMAL_RESUME)
        assert result.total_score < 80

    def test_empty_resume_zero(self):
        result = self._score(EMPTY_RESUME)
        assert result.total_score == 0

    def test_suggestions_for_missing_sections(self):
        result = self._score(MINIMAL_RESUME)
        assert any("Contact" in s or "contact" in s.lower() for s in result.suggestions)

    def test_suggestions_for_summary(self):
        result = self._score(MINIMAL_RESUME)
        assert any("summary" in s.lower() for s in result.suggestions)

    def test_no_action_verbs_suggestion(self):
        text = "Experience\nDid things at a place for some time, nothing special."
        result = self._score(text)
        assert any("action verb" in s.lower() for s in result.suggestions)

    def test_no_metrics_suggestion(self):
        text = "Experience\nManaged a team and delivered projects on time every quarter."
        result = self._score(text)
        assert any("metric" in s.lower() or "quantif" in s.lower() for s in result.suggestions)

    def test_score_between_0_and_100(self):
        for text in (FULL_RESUME, MINIMAL_RESUME, EMPTY_RESUME):
            result = self._score(text)
            assert 0 <= result.total_score <= 100

    def test_bonus_for_certifications(self):
        result = self._score(FULL_RESUME)
        assert result.section_scores.get("bonus", 0) > 0

    def test_section_scores_present(self):
        result = self._score(FULL_RESUME)
        for key in ("contact", "summary", "experience", "education", "skills"):
            assert key in result.section_scores


# ===========================================================================
# ResumeAgent (facade) tests
# ===========================================================================


class TestResumeAgent:
    def setup_method(self):
        self.agent = ResumeAgent()

    def test_analyze_returns_report(self):
        report = self.agent.analyze(FULL_RESUME)
        assert report.parsed is not None
        assert report.score_result is not None
        assert isinstance(report.overall_feedback, str)

    def test_analyze_report_str(self):
        report = self.agent.analyze(FULL_RESUME)
        text = str(report)
        assert "AI RESUME AGENT" in text
        assert "Resume Score:" in text

    def test_analyze_sections(self):
        sections = self.agent.analyze_sections(FULL_RESUME)
        assert "experience" in sections
        assert "education" in sections

    def test_get_score(self):
        score = self.agent.get_score(FULL_RESUME)
        assert isinstance(score, int)
        assert 0 <= score <= 100

    def test_get_suggestions(self):
        suggestions = self.agent.get_suggestions(MINIMAL_RESUME)
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0

    def test_empty_resume_feedback(self):
        report = self.agent.analyze(EMPTY_RESUME)
        assert "significant improvement" in report.overall_feedback.lower()

    def test_strong_resume_feedback(self):
        report = self.agent.analyze(FULL_RESUME)
        assert "strong" in report.overall_feedback.lower()

    def test_get_score_empty(self):
        assert self.agent.get_score(EMPTY_RESUME) == 0
