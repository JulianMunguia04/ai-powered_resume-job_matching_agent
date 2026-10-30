
import re

from services.skill_extraction import extract_skills


# --------------------------------------------------
# SECTION HEADINGS
# --------------------------------------------------

SECTION_HEADINGS = {
    "required": [
        "required",
        "requirements",
        "required qualifications",
        "minimum qualifications",
        "minimum requirements",
        "what you need",
        "what we're looking for",
        "qualifications",
        "must have",
        "essential skills",
    ],
    "preferred": [
        "preferred",
        "preferred qualifications",
        "preferred skills",
        "nice to have",
        "nice-to-have",
        "bonus qualifications",
        "desired qualifications",
    ],
    "responsibilities": [
        "responsibilities",
        "responsibilities and duties",
        "what you'll do",
        "what you will do",
        "duties",
        "your role",
        "key responsibilities",
    ],
    "experience": [
        "experience",
        "work experience",
        "professional experience",
        "years of experience",
        "experience requirements",
    ],
    "education": [
        "education",
        "educational requirements",
        "academic qualifications",
        "academic requirements",
    ],
}


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


# --------------------------------------------------
# TEXT NORMALIZATION
# --------------------------------------------------

def normalize_text(text):
    """
    Normalize text for comparing headings and evidence.
    Preserve characters such as + and # for technical terms.
    """
    text = text.lower()
    text = re.sub(r"[^a-z0-9+# ]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def normalize_heading(line):
    return normalize_text(line)


# --------------------------------------------------
# JOB SECTION EXTRACTION
# --------------------------------------------------

def extract_job_sections(description):
    """
    Divide a job description into recognizable sections.

    Unrecognized content is placed in the general section.
    """
    sections = {
        "general": [],
        "required": [],
        "preferred": [],
        "responsibilities": [],
        "experience": [],
        "education": [],
    }

    heading_lookup = {
        normalize_heading(heading): section
        for section, headings in SECTION_HEADINGS.items()
        for heading in headings
    }

    current_section = "general"

    for line in description.splitlines():
        cleaned_line = line.strip()

        if not cleaned_line:
            continue

        # Remove a trailing colon before checking the heading.
        normalized = normalize_heading(cleaned_line.rstrip(":"))

        if normalized in heading_lookup:
            current_section = heading_lookup[normalized]
            continue

        sections[current_section].append(cleaned_line)

    return {
        section: "\n".join(lines).strip()
        for section, lines in sections.items()
    }


# --------------------------------------------------
# REQUIREMENT CLASSIFICATION
# --------------------------------------------------


def classify_requirement(text, section_type="general"):
    """
    Determine whether a requirement is required, preferred,
    or simply mentioned.

    Explicit section context takes priority over sentence cues.
    """
    normalized = normalize_text(text)

    # Explicit preferred wording takes priority.
    if any(cue in normalized for cue in PREFERRED_CUES):
        return "preferred"

    # Required sections are mandatory.
    if section_type == "required":
        return "required"

    # Experience and education sections contain formal
    # qualifications, treated as required by default.
    if section_type in ["experience", "education"]:
        return "required"

    # Explicit required wording.
    if any(cue in normalized for cue in REQUIRED_CUES):
        return "required"

    if section_type == "preferred":
        return "preferred"

    return "mentioned"



def find_evidence_section(evidence, sections):
    """
    Determine which section contains a piece of evidence.

    Uses normalized text so punctuation and bullet formatting
    do not prevent matching.
    """
    normalized_evidence = normalize_text(evidence)

    if not normalized_evidence:
        return "general"

    for section_name, section_text in sections.items():
        if not section_text:
            continue

        for line in section_text.splitlines():
            normalized_line = normalize_text(line)

            if (
                normalized_evidence in normalized_line
                or normalized_line in normalized_evidence
            ):
                return section_name

    return "general"


# --------------------------------------------------
# EXPERIENCE REQUIREMENTS
# --------------------------------------------------

def extract_experience_requirements(sections):
    """
    Extract years-of-experience requirements.

    Supports examples such as:
    - 1-2 years of experience
    - 3 to 5 years of experience
    - 3+ years of experience
    - At least 2 years of experience
    - Minimum of 5 years of experience
    """
    experience_requirements = []

    patterns = [
        # Range: 1-2 years or 1 to 2 years
        (
            r"(\d+(?:\.\d+)?)\s*(?:-|–|to)\s*"
            r"(\d+(?:\.\d+)?)\s+years?",
            "range",
        ),

        # At least / minimum of: at least 2 years
        (
            r"(?:at least|minimum of|min\.?)\s*"
            r"(\d+(?:\.\d+)?)\s+years?",
            "minimum",
        ),

        # Plus notation: 3+ years
        (
            r"(\d+(?:\.\d+)?)\s*\+\s*years?",
            "plus",
        ),

        # General: 2 years of experience
        (
            r"(\d+(?:\.\d+)?)\s+years?",
            "exact",
        ),
    ]

    for section_name in ["experience", "required", "preferred", "general"]:
        section_text = sections.get(section_name, "")

        if not section_text:
            continue

        for line in section_text.splitlines():
            cleaned_line = line.strip()

            if not re.search(r"\bexperience\b", cleaned_line, re.IGNORECASE):
                continue

            for pattern, pattern_type in patterns:
                match = re.search(pattern, cleaned_line, re.IGNORECASE)

                if not match:
                    continue

                if pattern_type == "range":
                    min_years = float(match.group(1))
                    max_years = float(match.group(2))

                elif pattern_type == "minimum":
                    min_years = float(match.group(1))
                    max_years = None

                elif pattern_type == "plus":
                    min_years = float(match.group(1))
                    max_years = None

                else:
                    min_years = float(match.group(1))
                    max_years = min_years

                requirement_type = classify_requirement(
                    cleaned_line,
                    section_name,
                )

                experience_requirements.append({
                    "min_years": min_years,
                    "max_years": max_years,
                    "requirement_type": requirement_type,
                    "evidence": cleaned_line,
                })

                # One match per line is sufficient.
                break

    # Remove duplicate requirements.
    unique_requirements = []
    seen = set()

    for requirement in experience_requirements:
        key = (
            requirement["min_years"],
            requirement["max_years"],
            requirement["evidence"].lower(),
        )

        if key not in seen:
            seen.add(key)
            unique_requirements.append(requirement)

    return unique_requirements


# --------------------------------------------------
# EDUCATION REQUIREMENTS
# --------------------------------------------------

def extract_education_requirements(sections):
    """
    Extract education requirements and identify degree level
    and field of study when possible.
    """
    education_requirements = []

    degree_patterns = [
        (r"\bph\.?d\.?\b|\bdoctorate\b", "phd"),
        (r"\bmaster'?s?\b|\bmasters\b", "masters"),
        (r"\bbachelor'?s?\b|\bbachelors\b", "bachelors"),
        (r"\bdiploma\b", "diploma"),
        (r"\bassociate'?s?\b|\bassociates\b", "associates"),
        (r"\bcertificate\b|\bcertification\b", "certificate"),
    ]

    for section_name in [
        "education",
        "required",
        "preferred",
        "general",
    ]:
        section_text = sections.get(section_name, "")

        if not section_text:
            continue

        for line in section_text.splitlines():
            cleaned_line = line.strip()
            normalized = normalize_text(cleaned_line)

            if not any(
                cue in normalized for cue in EDUCATION_CUES
            ):
                continue

            degree_level = None

            for pattern, level in degree_patterns:
                if re.search(pattern, cleaned_line, re.IGNORECASE):
                    degree_level = level
                    break

            # Extract the field of study following "in" or "of".
            field = None

            field_match = re.search(
                r"\b(?:in|of)\s+(.+?)(?:[.;]|$)",
                cleaned_line,
                re.IGNORECASE,
            )

            if field_match:
                field = field_match.group(1).strip()
                field = re.sub(r"^a\s+", "", field, flags=re.IGNORECASE)

            education_requirements.append({
                "degree_level": degree_level,
                "field": field,
                "description": cleaned_line,
                "requirement_type": classify_requirement(
                    cleaned_line,
                    section_name,
                ),
            })

    # Remove duplicate entries.
    unique_requirements = []
    seen = set()

    for requirement in education_requirements:
        key = requirement["description"].lower()

        if key not in seen:
            seen.add(key)
            unique_requirements.append(requirement)

    return unique_requirements


# --------------------------------------------------
# RESPONSIBILITIES
# --------------------------------------------------

def extract_responsibilities(sections):
    """
    Extract responsibilities only from the responsibilities section.

    Experience and education requirements are no longer mixed
    into the responsibilities list.
    """
    responsibilities = []

    for line in sections.get("responsibilities", "").splitlines():
        cleaned_line = line.strip()

        if not cleaned_line:
            continue

        responsibilities.append(cleaned_line)

    return responsibilities


# --------------------------------------------------
# SENIORITY
# --------------------------------------------------

def extract_seniority(description):
    """
    Identify a likely seniority level from the job description.
    """
    text = description.lower()

    seniority_levels = [
        ("principal", ["principal"]),
        ("staff", ["staff engineer", "staff developer"]),
        ("lead", ["lead engineer", "lead developer", "team lead"]),
        ("senior", ["senior", "sr."]),
        ("mid", ["mid-level", "mid level", "intermediate"]),
        ("junior", ["junior", "jr."]),
        ("intern", ["intern", "internship"]),
    ]

    for level, keywords in seniority_levels:
        if any(keyword in text for keyword in keywords):
            return level

    return "unspecified"


# --------------------------------------------------
# MAIN JOB ANALYSIS
# --------------------------------------------------

def analyze_job(description):
    """
    Analyze a job description and return structured information
    about skills, experience, education, responsibilities,
    seniority, and sections.
    """
    sections = extract_job_sections(description)

    # Extract technical skills and their supporting evidence.
    extracted_skills = extract_skills(description)

    skills = []

    for skill in extracted_skills:
        evidence = skill.get("evidence", [])

        requirement_types = []

        for sentence in evidence:
            section_type = find_evidence_section(sentence, sections)

            requirement_types.append(
                classify_requirement(sentence, section_type)
            )

        # Use the strongest classification found for the skill.
        if "required" in requirement_types:
            requirement_type = "required"
        elif "preferred" in requirement_types:
            requirement_type = "preferred"
        else:
            requirement_type = "mentioned"

        skills.append({
            "name": skill["name"],
            "requirement_type": requirement_type,
            "evidence": evidence,
        })

    experience_requirements = extract_experience_requirements(sections)

    education_requirements = extract_education_requirements(sections)

    responsibilities = extract_responsibilities(sections)

    seniority = extract_seniority(description)

    return {
        "skills": skills,
        "experience_requirements": experience_requirements,
        "education_requirements": education_requirements,
        "responsibilities": responsibilities,
        "seniority": seniority,
        "sections": sections,
        "analysis_version": "3.0",
    }
