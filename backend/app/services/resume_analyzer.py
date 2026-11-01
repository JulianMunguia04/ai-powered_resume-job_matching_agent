
import re
from datetime import date

from services.skill_extraction import extract_skills


ANALYSIS_VERSION = "3.0"


SECTION_NAMES = {
    "summary": [
        "summary",
        "professional summary",
        "profile",
        "objective",
        "career objective",
    ],
    "experience": [
        "experience",
        "work experience",
        "employment history",
        "professional experience",
        "professional experience and employment",
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
        "technical competencies",
    ],
}


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


DATE_PATTERN = (
    r"\b("
    r"Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|"
    r"Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|"
    r"Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?"
    r")\.?\s+\d{4}\b"
    r"|\b\d{4}\b"
)


def clean_line(line):
    """Normalize whitespace while preserving the line's content."""
    return re.sub(r"\s+", " ", line).strip()


def normalize_heading(line):
    return re.sub(r"[^a-z ]", "", line.lower()).strip()


def normalize_text(text):
    return re.sub(r"\s+", " ", text.lower()).strip()


def split_nonempty_lines(text):
    return [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]


def extract_sections(text):
    """Split resume text into recognized sections."""
    sections = {"other": []}
    current_section = "other"

    heading_lookup = {
        normalize_heading(heading): section
        for section, headings in SECTION_NAMES.items()
        for heading in headings
    }

    for raw_line in text.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        normalized = normalize_heading(line)

        if normalized in heading_lookup:
            current_section = heading_lookup[normalized]
            sections.setdefault(current_section, [])
        else:
            sections.setdefault(current_section, []).append(line)

    return {
        section: "\n".join(lines).strip()
        for section, lines in sections.items()
        if lines
    }


def parse_date_value(value):
    """Convert a month/year or year value into a sortable month index."""
    value = value.strip().lower().replace(".", "")

    if value in {"present", "current", "now"}:
        today = date.today()
        return today.year, today.month

    month_match = re.search(
        r"\b([a-z]+)\s+(\d{4})\b",
        value,
        flags=re.IGNORECASE,
    )

    if month_match:
        month_name = month_match.group(1).lower()
        year = int(month_match.group(2))
        month = MONTHS.get(month_name)

        if month:
            return year, month

    year_match = re.search(r"\b(19|20)\d{2}\b", value)

    if year_match:
        return int(year_match.group()), 1

    return None


def extract_date_ranges(text):
    """Find date ranges such as 'May 2025 – Sept 2025'."""
    pattern = re.compile(
        rf"({DATE_PATTERN})\s*(?:-|–|—|to)\s*"
        rf"({DATE_PATTERN}|Present|Current|Now)",
        flags=re.IGNORECASE,
    )

    ranges = []

    for match in pattern.finditer(text):
        start_raw = match.group(1).strip()
        end_raw = match.group(2).strip()

        start = parse_date_value(start_raw)
        end = parse_date_value(end_raw)

        if not start or not end:
            continue

        if end < start:
            continue

        ranges.append({
            "start_raw": start_raw,
            "end_raw": end_raw,
            "start_year": start[0],
            "start_month": start[1],
            "end_year": end[0],
            "end_month": end[1],
            "months": (
                (end[0] - start[0]) * 12
                + end[1] - start[1]
                + 1
            ),
        })

    return ranges


def calculate_total_experience(date_ranges):
    """Calculate total calendar months, merging overlapping date ranges."""
    intervals = []

    for item in date_ranges:
        start = item["start_year"] * 12 + item["start_month"]
        end = item["end_year"] * 12 + item["end_month"]
        intervals.append((start, end))

    if not intervals:
        return {
            "total_months": 0,
            "total_years": 0.0,
        }

    intervals.sort()

    merged = []
    current_start, current_end = intervals[0]

    for start, end in intervals[1:]:
        if start <= current_end + 1:
            current_end = max(current_end, end)
        else:
            merged.append((current_start, current_end))
            current_start, current_end = start, end

    merged.append((current_start, current_end))

    total_months = sum(
        end - start + 1
        for start, end in merged
    )

    return {
        "total_months": total_months,
        "total_years": round(total_months / 12, 2),
    }


def split_columns(line):
    """Split lines that use tabs or multiple spaces as visual columns."""
    parts = re.split(r"\t+|\s{2,}", line)

    return [
        clean_line(part)
        for part in parts
        if clean_line(part)
    ]


def strip_date_range(line):
    """Remove the first date range from a line and return both parts."""
    ranges = extract_date_ranges(line)

    if not ranges:
        return clean_line(line), None

    match = re.search(
        rf"{DATE_PATTERN}\s*(?:-|–|—|to)\s*"
        rf"(?:{DATE_PATTERN}|Present|Current|Now)",
        line,
        flags=re.IGNORECASE,
    )

    if not match:
        return clean_line(line), ranges[0]

    remaining = line[:match.start()] + line[match.end():]

    return clean_line(remaining.strip(" |,\t-–—")), ranges[0]


def format_month_year(year, month):
    month_name = [
        "January", "February", "March", "April",
        "May", "June", "July", "August",
        "September", "October", "November", "December",
    ][month - 1]

    return f"{month_name} {year}"


def analyze_resume_skills(text, sections):
    """
    Extract skills while preserving compatibility with the existing
    requirement matcher.

    evidence remains a list of strings.
    evidence_details adds the section where each item appeared.
    """
    extracted = extract_skills(text)
    results = []

    for skill in extracted:
        evidence_details = []

        for evidence in skill.get("evidence", []):
            evidence_text = (
                evidence.get("text")
                if isinstance(evidence, dict)
                else evidence
            )

            if not evidence_text:
                continue

            evidence_section = "other"

            for section_name, section_text in sections.items():
                if evidence_text.lower() in section_text.lower():
                    evidence_section = section_name
                    break

            evidence_details.append({
                "text": evidence_text,
                "section": evidence_section,
            })

        results.append({
            "name": skill["name"],
            "evidence": [
                item["text"]
                for item in evidence_details
            ],
            "evidence_details": evidence_details,
        })

    return results


def extract_education(sections):
    """Extract multiple education records from the education section."""
    education_text = sections.get("education", "")
    lines = split_nonempty_lines(education_text)

    degree_patterns = [
        ("masters", r"\b(?:M\.?\s*S\.?|M\.?\s*Sc\.?|M\.?\s*Eng\.?|Master'?s)\b"),
        ("bachelors", r"\b(?:B\.?\s*S\.?|B\.?\s*Sc\.?|B\.?\s*A\.?|B\.?\s*Eng\.?|Bachelor'?s)\b"),
        ("doctorate", r"\b(?:Ph\.?\s*D\.?|Doctorate|Doctor of)\b"),
        ("associate", r"\b(?:A\.?\s*A\.?|A\.?\s*S\.?|Associate'?s)\b"),
        ("diploma", r"\bDiploma\b"),
    ]

    education_records = []
    current_institution = None

    for index, line in enumerate(lines):
        normalized = line.lower()

        degree_level = None
        for level, pattern in degree_patterns:
            if re.search(pattern, line, flags=re.IGNORECASE):
                degree_level = level
                break

        if degree_level is None:
            # Institution names generally precede their degree line.
            if not re.search(
                r"\b(dean'?s list|honou?rs?|expected|graduated|gpa)\b",
                normalized,
            ) and not re.search(r"\b(19|20)\d{2}\b", line):
                current_institution = line
            continue

        is_incoming = bool(re.search(r"\bincoming\b", line, re.IGNORECASE))
        has_expected_date = bool(
            re.search(r"\bexpected\b", line, re.IGNORECASE)
        )

        date_match = re.search(
            r"\bExpected\s+([A-Za-z.]+\s+\d{4})",
            line,
            flags=re.IGNORECASE,
        )

        expected_graduation = (
            clean_line(date_match.group(1))
            if date_match
            else None
        )

        year_match = re.search(r"\b(19|20)\d{2}\b", line)
        graduation_year = (
            int(year_match.group())
            if year_match
            else None
        )

        # Remove degree wording and expected graduation details to isolate field.
        field = re.sub(
            r"\bIncoming\b",
            "",
            line,
            flags=re.IGNORECASE,
        )
        field = re.sub(
            r"\bExpected\s+[A-Za-z.]+\s+\d{4}\b",
            "",
            field,
            flags=re.IGNORECASE,
        )
        field = re.sub(
            r"\b(19|20)\d{2}\b",
            "",
            field,
        )
        field = re.sub(
            r"\b(?:M\.?\s*S\.?|M\.?\s*Sc\.?|M\.?\s*Eng\.?|"
            r"B\.?\s*S\.?|B\.?\s*Sc\.?|B\.?\s*A\.?|B\.?\s*Eng\.?|"
            r"Ph\.?\s*D\.?|A\.?\s*A\.?|A\.?\s*S\.?|"
            r"Master'?s|Bachelor'?s|Associate'?s|Diploma)\b",
            "",
            field,
            flags=re.IGNORECASE,
        )
        field = re.sub(r"^\s*in\s+", "", field, flags=re.IGNORECASE)
        field = clean_line(field.strip(" |,-"))

        if is_incoming:
            status = "incoming"
        elif has_expected_date:
            status = "in_progress"
        else:
            status = "unspecified"

        evidence = [line]
        if current_institution:
            evidence.insert(0, current_institution)

        education_records.append({
            "degree_level": degree_level,
            "field": field or None,
            "institution": current_institution,
            "graduation_year": graduation_year,
            "expected_graduation": expected_graduation,
            "status": status,
            "evidence": evidence,
        })

    return education_records


def extract_work_experience(sections):
    """Convert experience section lines into structured employment records."""
    experience_text = sections.get("experience", "")
    lines = split_nonempty_lines(experience_text)

    entries = []
    all_date_ranges = []

    date_line_indexes = []

    for index, line in enumerate(lines):
        ranges = extract_date_ranges(line)

        if ranges:
            date_line_indexes.append(index)
            all_date_ranges.extend(ranges)

    for position, line_index in enumerate(date_line_indexes):
        line = lines[line_index]
        title_text, date_range = strip_date_range(line)

        previous_line = (
            lines[line_index - 1]
            if line_index > 0
            else ""
        )

        employer_columns = split_columns(previous_line)

        employer = (
            employer_columns[0]
            if employer_columns
            else previous_line
        )

        location = (
            employer_columns[1]
            if len(employer_columns) > 1
            else None
        )

        title_columns = split_columns(title_text)
        job_title = (
            title_columns[0]
            if title_columns
            else title_text
        )

        next_date_index = (
            date_line_indexes[position + 1]
            if position + 1 < len(date_line_indexes)
            else len(lines)
        )

        responsibility_lines = lines[line_index + 1:next_date_index]

        # Exclude an employer heading immediately before the next dated role.
        if responsibility_lines:
            responsibility_lines = [
                item for item in responsibility_lines
                if item.strip()
            ]

        start_date = None
        end_date = None

        if date_range:
            start_date = format_month_year(
                date_range["start_year"],
                date_range["start_month"],
            )

            if date_range["end_raw"].lower() in {
                "present", "current", "now"
            }:
                end_date = "Present"
            else:
                end_date = format_month_year(
                    date_range["end_year"],
                    date_range["end_month"],
                )

        entries.append({
            "employer": employer or None,
            "location": location,
            "job_title": job_title or None,
            "start_date": start_date,
            "end_date": end_date,
            "date_range": date_range,
            "responsibilities": responsibility_lines,
            "evidence": [
                previous_line,
                line,
                *responsibility_lines,
            ] if previous_line else [
                line,
                *responsibility_lines,
            ],
        })

    return {
        "entries": entries,
        "date_ranges": all_date_ranges,
        "total_experience": calculate_total_experience(all_date_ranges),
    }


def is_project_header(line):
    """Identify project title lines, usually containing a stack and dates."""
    has_date = bool(extract_date_ranges(line))
    has_separator = "|" in line

    return (
        has_date
        and has_separator
        and len(line) < 300
    )


def extract_projects(sections):
    """Group each project title, technology stack, date, and description."""
    project_text = sections.get("projects", "")
    lines = split_nonempty_lines(project_text)

    projects = []
    current_project = None

    def save_current():
        if current_project is not None:
            projects.append(current_project.copy())

    for line in lines:
        if is_project_header(line):
            save_current()

            parts = [clean_line(part) for part in line.split("|")]
            parts = [part for part in parts if part]

            name = parts[0] if parts else line
            remainder = " | ".join(parts[1:])

            _, date_range = strip_date_range(line)

            # Remove the date from the stack text.
            stack_text, _ = strip_date_range(remainder)

            technologies = [
                clean_line(item)
                for item in re.split(r",|;", stack_text)
                if clean_line(item)
            ]

            current_project = {
                "name": name,
                "technologies": technologies,
                "start_date": None,
                "end_date": None,
                "date_range": date_range,
                "descriptions": [],
                "evidence": [line],
            }

            if date_range:
                current_project["start_date"] = format_month_year(
                    date_range["start_year"],
                    date_range["start_month"],
                )

                if date_range["end_raw"].lower() in {
                    "present", "current", "now"
                }:
                    current_project["end_date"] = "Present"
                else:
                    current_project["end_date"] = format_month_year(
                        date_range["end_year"],
                        date_range["end_month"],
                    )

        elif current_project is not None:
            current_project["descriptions"].append(line)
            current_project["evidence"].append(line)

        else:
            # Keep unclassified project-section content rather than dropping it.
            current_project = {
                "name": None,
                "technologies": [],
                "start_date": None,
                "end_date": None,
                "date_range": None,
                "descriptions": [line],
                "evidence": [line],
            }

    save_current()

    return projects


def extract_certifications(sections):
    certification_text = sections.get("certifications", "")

    return [
        line
        for line in split_nonempty_lines(certification_text)
    ]


def analyze_resume(text):
    """Run the complete resume analysis pipeline."""
    sections = extract_sections(text)

    skills = analyze_resume_skills(text, sections)
    education = extract_education(sections)
    work_experience = extract_work_experience(sections)
    projects = extract_projects(sections)
    certifications = extract_certifications(sections)

    return {
        "skills": skills,
        "work_experience": work_experience,
        "education": education,
        "projects": projects,
        "certifications": certifications,
        "sections": sections,
        "analysis_version": ANALYSIS_VERSION,
    }
