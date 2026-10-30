
import re

from services.skill_extraction import extract_skills


REQUIRED_CUES = [
    "required",
    "requirements",
    "must have",
    "must be proficient",
    "essential",
    "minimum qualifications",
    "minimum requirements",
]

PREFERRED_CUES = [
    "preferred",
    "nice to have",
    "nice-to-have",
    "an asset",
    "bonus",
    "ideally",
    "would be an advantage",
]

EDUCATION_CUES = [
    "bachelor",
    "master",
    "degree",
    "diploma",
    "phd",
    "certification",
    "certified",
]

RESPONSIBILITY_CUES = [
    "responsible for",
    "you will",
    "you'll",
    "develop",
    "design",
    "build",
    "maintain",
    "implement",
    "collaborate",
    "manage",
    "support",
]


def classify_requirement(text: str) -> str:
    """Classify how strongly a job description presents a requirement."""
    lowered = text.lower()

    if any(cue in lowered for cue in REQUIRED_CUES):
        return "required"

    if any(cue in lowered for cue in PREFERRED_CUES):
        return "preferred"

    return "mentioned"


def extract_experience_requirements(text: str) -> list[dict]:
    """Extract explicit years-of-experience statements."""
    patterns = [
        r"(\d+)\+?\s*(?:-|to)\s*(\d+)\s+years?\s+of\s+experience",
        r"(\d+)\+?\s*years?\s+of\s+experience",
    ]

    results = []

    for pattern in patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            if len(match.groups()) == 2:
                minimum_years = int(match.group(1))
                maximum_years = int(match.group(2))
            else:
                minimum_years = int(match.group(1))
                maximum_years = None

            results.append({
                "minimum_years": minimum_years,
                "maximum_years": maximum_years,
                "evidence": match.group(0),
            })

    return results


def extract_education_requirements(text: str) -> list[dict]:
    """Find lines that appear to describe education or certification criteria."""
    results = []

    for line in text.splitlines():
        cleaned = line.strip()

        if not cleaned:
            continue

        lowered = cleaned.lower()

        if any(cue in lowered for cue in EDUCATION_CUES):
            results.append({
                "description": cleaned,
                "requirement_type": classify_requirement(cleaned),
            })

    return results


def extract_responsibilities(text: str) -> list[str]:
    """Identify likely responsibility statements."""
    results = []

    for line in text.splitlines():
        cleaned = line.strip().lstrip("-•* ").strip()

        if not cleaned:
            continue

        lowered = cleaned.lower()

        if any(cue in lowered for cue in RESPONSIBILITY_CUES):
            results.append(cleaned)

    return results


def analyze_job(description: str) -> dict:
    """Convert a job description into structured matching information."""
    detected_skills = extract_skills(description)

    skill_requirements = []

    for skill in detected_skills:
        for evidence in skill["evidence"]:
            skill_requirements.append({
                "name": skill["name"],
                "requirement_type": classify_requirement(evidence),
                "evidence": evidence,
            })

    return {
        "skills": skill_requirements,
        "experience_requirements": extract_experience_requirements(description),
        "education_requirements": extract_education_requirements(description),
        "responsibilities": extract_responsibilities(description),
        "analysis_version": "1.0",
    }
