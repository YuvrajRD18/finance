# finance

## AI Resume Agent

A Python-based AI agent that parses, scores, and provides improvement suggestions for resumes.

### Features

- **Resume Parsing** – Extracts canonical sections (Experience, Education, Skills, etc.) from plain-text resumes.
- **Resume Scoring** – Evaluates completeness, depth, use of action verbs, and quantified metrics. Score range: 0–100.
- **Improvement Suggestions** – Actionable tips to strengthen each section.

### Quick Start

```python
from ai_resume_agent import ResumeAgent

agent = ResumeAgent()
report = agent.analyze(open("my_resume.txt").read())
print(report)
```

### Running Tests

```bash
pip install pytest
python -m pytest tests/ -v
```