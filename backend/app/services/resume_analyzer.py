import re

from services.skill_extraction import extract_skills

SECTION_NAMES = {
    "summary": ["summary", "professional summary", "profile", "objective"],
    "experience": [
        "experience",
        "work experience",
        "employment history",
        "professional experience",
    ],
    "education": ["education", "academic background"],
    "projects": ["projects", "personal projects", "academic projects"],
    "certifications": ["certifications", "certificates", "licenses"],
    "skills": ["skills", "technical skills", "technologies"],
}

def normalize_heading(line: str) -> str:
    """Normalize a possible resume heading for comparison."""
    return re.sub(r"[^a-z ]", "", line.lower()).strip()


def extract_sections(text: str) -> dict:
    """
    Split resume text into common sections based on heading lines.

    This is a first-pass parser. It will not recognize every possible
    resume layout or heading.
    """
    sections = {}
    current_section = "other"
    sections[current_section] = []

    heading_lookup = {
        heading: section
        for section, headings in SECTION_NAMES.items()
        for heading in headings
    }

    for line in text.splitlines():
        cleaned_line = line.strip()

        if not cleaned_line:
            continue

        normalized = normalize_heading(cleaned_line)

        if normalized in heading_lookup:
            current_section = heading_lookup[normalized]
            sections.setdefault(current_section, [])
        else:
            sections.setdefault(current_section, []).append(cleaned_line)

    return {
        section: "\n".join(lines).strip()
        for section, lines in sections.items()
        if lines
    }


def analyze_resume(text: str) -> dict:
    """Create a structured first-pass analysis of resume text."""
    sections = extract_sections(text)
    skills = extract_skills(text)

    return {
        "skills": skills,
        "sections": sections,
        "analysis_version": "1.0",
    }