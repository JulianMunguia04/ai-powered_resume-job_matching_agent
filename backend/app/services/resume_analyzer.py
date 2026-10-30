
import re
from datetime import date

from services.skill_extraction import extract_skills


# --------------------------------------------------
# SECTION HEADINGS
# --------------------------------------------------

SECTION_NAMES = {
    "summary": [
        "summary",
        "professional summary",
        "profile",
        "objective",
        "about me",
    ],
    "experience": [
        "experience",
        "work experience",
        "employment history",
        "professional experience",
        "work history",
        "professional background",
    ],
    "education": [
        "education",
        "academic background",
        "educational background",
    ],
    "projects": [
        "projects",
        "personal projects",
        "academic projects",
        "technical projects",
        "selected projects",
    ],
    "certifications": [
        "certifications",
        "certificates",
        "licenses",
        "licenses and certifications",
    ],
    "skills": [
        "skills",
        "technical skills",
        "technologies",
        "technical proficiencies",
        "core competencies",
    ],
}


# --------------------------------------------------
# DEGREE LEVELS
# --------------------------------------------------

DEGREE_PATTERNS = [
    (r"\bph\.?d\.?\b|\bdoctorate\b", "phd"),
    (r"\bmaster'?s?\b|\bmasters\b|\bm\.sc\.?\b|\bmba\b", "masters"),
    (r"\bbachelor'?s?\b|\bbachelors\b|\bb\.sc\.?\b|\bb\.a\.?\b|\bb\.s\.?\b", "bachelors"),
    (r"\bassociate'?s?\b|\bassociate degree\b", "associates"),
    (r"\bdiploma\b", "diploma"),
    (r"\bcertificate\b|\bcertification\b", "certificate"),
]


# --------------------------------------------------
# TEXT NORMALIZATION
# --------------------------------------------------

def normalize_heading(line: str) -> str:
    """Normalize a possible resume heading for comparison."""
    return re.sub(r"[^a-z ]", "", line.lower()).strip()


def normalize_text(text: str) -> str:
    """Normalize text for consistent comparisons."""
    return re.sub(r"\s+", " ", text.lower()).strip()


# --------------------------------------------------
# SECTION EXTRACTION
# --------------------------------------------------

def extract_sections(text: str) -> dict:
    """
    Split resume text into common sections based on heading lines.

    Unrecognized content is stored under 'other'.
    """
    sections = {"other": []}

    current_section = "other"

    heading_lookup = {
        normalize_heading(heading): section
        for section, headings in SECTION_NAMES.items()
        for heading in headings
    }

    for line in text.splitlines():
        cleaned_line = line.strip()

        if not cleaned_line:
            continue

        # Allow headings with trailing colons.
        normalized = normalize_heading(cleaned_line.rstrip(":"))

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


# --------------------------------------------------
# SKILL EXTRACTION
# --------------------------------------------------

def analyze_resume_skills(text: str, sections: dict) -> list:
    """
    Extract skills and identify the section containing their evidence.

    Being listed in a skills section does not automatically mean
    the candidate has demonstrated the skill.
    """
    extracted_skills = extract_skills(text)

    analyzed_skills = []

    for skill in extracted_skills:
        evidence_items = []

        for evidence in skill.get("evidence", []):
            normalized_evidence = normalize_text(evidence)
            evidence_section = "other"

            for section_name, section_text in sections.items():
                normalized_section = normalize_text(section_text)

                if normalized_evidence in normalized_section:
                    evidence_section = section_name
                    break

            evidence_items.append({
                "text": evidence,
                "section": evidence_section,
            })

        analyzed_skills.append({
            "name": skill["name"],
            "evidence": evidence_items,
        })

    return analyzed_skills


# --------------------------------------------------
# DATE EXTRACTION
# --------------------------------------------------

MONTHS = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12,
}


def parse_date_value(value: str):
    """
    Convert a month/year or year into a (year, month) tuple.

    Examples:
    May 2023 -> (2023, 5)
    2024 -> (2024, 1)

    Returns None when the date cannot be interpreted.
    """
    value = value.strip().lower()

    if value in ["present", "current", "now"]:
        today = date.today()
        return today.year, today.month

    month_year = re.fullmatch(
        r"([a-z]+)\.?\s+(\d{4})",
        value,
    )

    if month_year:
        month_name = month_year.group(1)
        year = int(month_year.group(2))

        month = MONTHS.get(month_name)

        if month:
            return year, month

    year_only = re.fullmatch(r"\d{4}", value)

    if year_only:
        return int(value), 1

    return None


def extract_date_ranges(text: str) -> list:
    """
    Identify date ranges such as:
    May 2023 - August 2024
    2022 - 2024
    January 2025 - Present

    This is a first-pass date parser.
    """
    month_pattern = (
        r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|"
        r"Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|"
        r"Aug(?:ust)?|Sep(?:t(?:ember)?)?|"
        r"Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
    )

    date_pattern = (
        rf"(?:{month_pattern}\.?\s+\d{{4}}|\d{{4}}|"
        r"Present|Current|Now)"
    )

    range_pattern = re.compile(
        rf"({date_pattern})\s*(?:-|–|—|to)\s*({date_pattern})",
        re.IGNORECASE,
    )

    ranges = []

    for match in range_pattern.finditer(text):
        start = parse_date_value(match.group(1))
        end = parse_date_value(match.group(2))

        if not start or not end:
            continue

        if start > end:
            continue

        ranges.append({
            "start": {
                "year": start[0],
                "month": start[1],
            },
            "end": {
                "year": end[0],
                "month": end[1],
            },
            "evidence": match.group(0),
        })

    return ranges


def calculate_total_experience(date_ranges: list):
    """
    Calculate the combined duration of date ranges in months.

    Overlapping date ranges are merged to avoid double-counting
    concurrent jobs.
    """
    intervals = []

    for date_range in date_ranges:
        start = date_range["start"]
        end = date_range["end"]

        start_month = start["year"] * 12 + start["month"] - 1
        end_month = end["year"] * 12 + end["month"] - 1

        intervals.append((start_month, end_month))

    if not intervals:
        return {
            "total_months": None,
            "total_years": None,
        }

    intervals.sort()

    merged = []

    for start, end in intervals:
        if not merged or start > merged[-1][1] + 1:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)

    total_months = sum(
        end - start + 1
        for start, end in merged
    )

    return {
        "total_months": total_months,
        "total_years": round(total_months / 12, 2),
    }


# --------------------------------------------------
# WORK EXPERIENCE EXTRACTION
# --------------------------------------------------

def extract_work_experience(sections: dict) -> dict:
    """
    Extract recognizable employment date ranges and supporting
    resume text.

    This does not yet reliably identify every job title or employer.
    """
    experience_text = sections.get("experience", "")

    date_ranges = extract_date_ranges(experience_text)

    entries = []

    lines = experience_text.splitlines()

    for index, line in enumerate(lines):
        ranges = extract_date_ranges(line)

        if not ranges:
            continue

        # Capture the date line and nearby context.
        context = []

        if index > 0:
            context.append(lines[index - 1].strip())

        context.append(line.strip())

        if index + 1 < len(lines):
            context.append(lines[index + 1].strip())

        entries.append({
            "date_ranges": ranges,
            "evidence": [item for item in context if item],
        })

    total_experience = calculate_total_experience(date_ranges)

    return {
        "entries": entries,
        "date_ranges": date_ranges,
        "total_experience": total_experience,
    }


# --------------------------------------------------
# EDUCATION EXTRACTION
# --------------------------------------------------

def extract_education(sections: dict) -> list:
    """
    Extract education records and identify degree levels,
    fields of study, institutions, and dates when recognizable.
    """
    education_text = sections.get("education", "")

    if not education_text:
        return []

    lines = [
        line.strip()
        for line in education_text.splitlines()
        if line.strip()
    ]

    education_records = []

    for index, line in enumerate(lines):
        degree_level = None

        for pattern, level in DEGREE_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                degree_level = level
                break

        if not degree_level:
            continue

        field = None

        field_match = re.search(
            r"\b(?:in|of)\s+(.+?)(?:[,;]|$)",
            line,
            re.IGNORECASE,
        )

        if field_match:
            field = field_match.group(1).strip()

        graduation_year = None

        year_match = re.search(
            r"\b(19\d{2}|20\d{2})\b",
            line,
        )

        if year_match:
            graduation_year = int(year_match.group(1))

        # Include adjacent lines as context for the education record.
        evidence = []

        if index > 0:
            evidence.append(lines[index - 1])

        evidence.append(line)

        if index + 1 < len(lines):
            evidence.append(lines[index + 1])

        institution = None

        for context_line in evidence:
            if context_line != line and not re.search(
                r"\b(19\d{2}|20\d{2})\b",
                context_line,
            ):
                institution = context_line
                break

        education_records.append({
            "degree_level": degree_level,
            "field": field,
            "institution": institution,
            "graduation_year": graduation_year,
            "evidence": evidence,
        })

    return education_records


# --------------------------------------------------
# PROJECT EXTRACTION
# --------------------------------------------------

def extract_projects(sections: dict) -> list:
    """
    Preserve project descriptions as individual entries.

    Project boundaries are initially inferred from non-empty lines.
    """
    project_text = sections.get("projects", "")

    projects = []

    for line in project_text.splitlines():
        cleaned_line = line.strip()

        if cleaned_line:
            projects.append({
                "description": cleaned_line,
            })

    return projects


# --------------------------------------------------
# CERTIFICATION EXTRACTION
# --------------------------------------------------

def extract_certifications(sections: dict) -> list:
    """
    Extract certification entries from the certifications section.
    """
    certification_text = sections.get("certifications", "")

    return [
        line.strip()
        for line in certification_text.splitlines()
        if line.strip()
    ]


# --------------------------------------------------
# MAIN RESUME ANALYSIS
# --------------------------------------------------

def analyze_resume(text: str) -> dict:
    """
    Analyze a resume and return structured candidate information.
    """
    sections = extract_sections(text)

    skills = analyze_resume_skills(text, sections)

    work_experience = extract_work_experience(sections)

    education = extract_education(sections)

    projects = extract_projects(sections)

    certifications = extract_certifications(sections)

    return {
        "skills": skills,
        "work_experience": work_experience,
        "education": education,
        "projects": projects,
        "certifications": certifications,
        "sections": sections,
        "analysis_version": "2.0",
    }
