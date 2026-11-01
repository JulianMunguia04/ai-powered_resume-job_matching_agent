
import re


MATCHING_VERSION = "2.0"


# These relationships identify potentially transferable experience.
# They are NOT treated as exact skill matches.
RELATED_SKILLS = {
    "TypeScript": ["JavaScript"],
    "Next.js": ["React"],
    "React": ["Next.js", "Vue.js"],
    "Vue.js": ["React"],
    "PostgreSQL": ["MySQL", "SQL"],
    "MySQL": ["PostgreSQL", "SQL"],
    "MongoDB": ["PostgreSQL", "MySQL"],
    "Flask": ["Django"],
    "Django": ["Flask"],
    "Kubernetes": ["Docker"],
    "Docker": ["Kubernetes"],
    "PyTorch": ["TensorFlow"],
    "TensorFlow": ["PyTorch"],
    "Express": ["Node.js"],
}


DEGREE_LEVELS = {
    "diploma": 1,
    "associate": 2,
    "bachelors": 3,
    "masters": 4,
    "doctorate": 5,
}


def normalize_name(value: str) -> str:
    """Normalize names for comparisons without changing their meaning."""
    return re.sub(r"[^a-z0-9]", "", str(value).lower())


def find_resume_skill(
    resume_skills: list[dict],
    required_skill: str,
):
    """Find an exact normalized skill match in the resume analysis."""
    required_normalized = normalize_name(required_skill)

    for skill in resume_skills:
        if normalize_name(skill.get("name", "")) == required_normalized:
            return skill

    return None


def get_evidence_details(skill: dict) -> list[dict]:
    """
    Return structured evidence when available.

    Falls back to the original string-based evidence format so older
    resume analysis data remains compatible.
    """
    details = skill.get("evidence_details", [])

    if details:
        return [
            item if isinstance(item, dict)
            else {"text": str(item), "section": "other"}
            for item in details
        ]

    return [
        {"text": str(item), "section": "other"}
        for item in skill.get("evidence", [])
    ]


def classify_resume_evidence(
    skill: dict,
    sections: dict,
) -> tuple[str, list[str]]:
    """
    Classify skill evidence as demonstrated, listed, or not found.

    Work experience and projects count as demonstrated evidence.
    Skills-section entries count as listed evidence.
    """
    demonstrated_evidence = []
    listed_evidence = []

    for item in get_evidence_details(skill):
        evidence = item.get("text", "").strip()
        section = item.get("section", "other").lower()

        if not evidence:
            continue

        # Prefer the section metadata from the updated resume analyzer.
        if section in {"experience", "projects"}:
            demonstrated_evidence.append(evidence)
            continue

        # Fallback for older analysis data without reliable section metadata.
        evidence_lower = evidence.lower()
        experience_text = sections.get("experience", "").lower()
        project_text = sections.get("projects", "").lower()

        if (
            evidence_lower in experience_text
            or evidence_lower in project_text
        ):
            demonstrated_evidence.append(evidence)

        elif section == "skills":
            listed_evidence.append(evidence)

        else:
            listed_evidence.append(evidence)

    if demonstrated_evidence:
        return "demonstrated", demonstrated_evidence

    if listed_evidence:
        return "listed", listed_evidence

    return "not_found", []


def find_transferable_evidence(
    required_skill: str,
    resume_skills: list[dict],
) -> list[dict]:
    """
    Find explicitly defined related skills.

    Related skills are suggestions for transferable experience, not
    proof that the candidate possesses the exact required skill.
    """
    related_names = RELATED_SKILLS.get(required_skill, [])
    results = []

    for related_name in related_names:
        resume_skill = find_resume_skill(resume_skills, related_name)

        if resume_skill is None:
            continue

        evidence = resume_skill.get("evidence", [])

        results.append({
            "related_skill": related_name,
            "relationship": "related but not equivalent",
            "evidence": evidence,
            "explanation": (
                f"The resume contains {related_name}, which is related "
                f"to {required_skill}, but does not establish direct "
                f"experience with {required_skill}."
            ),
        })

    return results


def match_skill_requirement(
    requirement: dict,
    resume_skills: list[dict],
    resume_sections: dict,
) -> dict:
    """Evaluate one job skill requirement against resume evidence."""
    required_skill = requirement["name"]

    resume_skill = find_resume_skill(
        resume_skills,
        required_skill,
    )

    if resume_skill is None:
        transferable_evidence = find_transferable_evidence(
            required_skill,
            resume_skills,
        )

        return {
            "requirement": required_skill,
            "importance": requirement.get(
                "requirement_type",
                "mentioned",
            ),
            "status": "not_found",
            "evidence": [],
            "transferable_evidence": transferable_evidence,
            "explanation": (
                f"No direct evidence for {required_skill} was identified "
                "in the resume."
            ),
        }

    status, evidence = classify_resume_evidence(
        resume_skill,
        resume_sections,
    )

    if status == "demonstrated":
        explanation = (
            f"The resume provides project or work experience evidence "
            f"for {required_skill}."
        )

    elif status == "listed":
        explanation = (
            f"{required_skill} appears in the resume, but no supporting "
            "project or work experience evidence was identified."
        )

    else:
        explanation = (
            f"No supporting evidence for {required_skill} was identified."
        )

    return {
        "requirement": required_skill,
        "importance": requirement.get(
            "requirement_type",
            "mentioned",
        ),
        "status": status,
        "evidence": evidence,
        "transferable_evidence": [],
        "explanation": explanation,
    }


def normalize_requirement_list(value):
    """Accept either one requirement dictionary or a list of dictionaries."""
    if isinstance(value, dict):
        return [value]

    if isinstance(value, list):
        return value

    return []


def match_education_requirements(
    education_requirements,
    resume_education,
):
    """Compare job education requirements against resume education records."""
    results = []

    for requirement in normalize_requirement_list(education_requirements):
        required_level = requirement.get("degree_level")
        required_field = requirement.get("field")

        best_match = None
        best_level_match = False
        best_field_match = False

        for education in resume_education:
            candidate_level = education.get("degree_level")
            candidate_field = education.get("field")

            level_match = (
                required_level is None
                or (
                    candidate_level in DEGREE_LEVELS
                    and required_level in DEGREE_LEVELS
                    and DEGREE_LEVELS[candidate_level]
                    >= DEGREE_LEVELS[required_level]
                )
            )

            field_match = False

            if required_field and candidate_field:
                required_words = set(
                    re.findall(r"[a-z0-9]+", required_field.lower())
                )
                candidate_words = set(
                    re.findall(r"[a-z0-9]+", candidate_field.lower())
                )

                # Avoid treating generic words as meaningful field matches.
                generic_words = {
                    "and", "or", "in", "of", "a", "the",
                    "related", "field",
                }

                required_words -= generic_words
                candidate_words -= generic_words

                field_match = bool(
                    required_words
                    and candidate_words
                    and required_words.intersection(candidate_words)
                )

            if level_match and field_match:
                best_match = education
                best_level_match = True
                best_field_match = True
                break

            if level_match and not best_level_match:
                best_match = education
                best_level_match = True
                best_field_match = field_match

            elif field_match and not best_field_match:
                best_match = education
                best_field_match = True

        if best_level_match and best_field_match:
            status = "matched"
            explanation = (
                "The resume contains an education record that matches "
                "the required degree level and field."
            )

        elif best_level_match:
            status = "partial"
            explanation = (
                "The resume contains a degree at the required level, "
                "but the field could not be confirmed as a match."
            )

        elif best_field_match:
            status = "partial"
            explanation = (
                "The resume contains education in a related field, "
                "but the required degree level could not be confirmed."
            )

        else:
            status = "not_found"
            explanation = (
                "No education record matching the stated requirement "
                "was identified."
            )

        results.append({
            "requirement": requirement,
            "status": status,
            "matched_education": best_match,
            "explanation": explanation,
        })

    return results


def match_experience_requirements(
    experience_requirements,
    resume_work_experience,
):
    """
    Compare required years of experience with documented employment duration.

    This currently measures total documented employment duration.
    It does not yet determine whether every role is relevant to the
    specific job being evaluated.
    """
    results = []

    total_experience = resume_work_experience.get(
        "total_experience",
        {},
    )

    candidate_years = total_experience.get("total_years", 0)

    for requirement in normalize_requirement_list(experience_requirements):
        minimum_years = requirement.get("min_years")
        maximum_years = requirement.get("max_years")

        if minimum_years is None:
            status = "insufficient_data"
            explanation = (
                "The job's minimum experience requirement could not "
                "be determined."
            )

        elif candidate_years >= minimum_years:
            status = "meets_minimum"
            explanation = (
                f"The resume documents approximately {candidate_years} "
                f"years of total employment, compared with a minimum "
                f"requirement of {minimum_years} years."
            )

        else:
            status = "below_minimum"
            explanation = (
                f"The resume documents approximately {candidate_years} "
                f"years of total employment, compared with a minimum "
                f"requirement of {minimum_years} years."
            )

        results.append({
            "requirement": requirement,
            "candidate_documented_years": candidate_years,
            "status": status,
            "explanation": explanation,
            "experience_basis": "total_documented_employment",
            "note": (
                "This is total documented employment duration, not "
                "a verified measure of job-relevant experience."
            ),
        })

    return results


def match_job_requirements(
    resume_analysis: dict,
    job_analysis: dict,
) -> dict:
    """
    Compare extracted job skill, education, and experience requirements
    against the analyzed resume.
    """
    results = []

    resume_skills = resume_analysis.get("skills", [])
    resume_sections = resume_analysis.get("sections", {})

    for requirement in job_analysis.get("skills", []):
        results.append(
            match_skill_requirement(
                requirement,
                resume_skills,
                resume_sections,
            )
        )

    skill_summary = {
        "total": len(results),
        "demonstrated": sum(
            result["status"] == "demonstrated"
            for result in results
        ),
        "listed": sum(
            result["status"] == "listed"
            for result in results
        ),
        "not_found": sum(
            result["status"] == "not_found"
            for result in results
        ),
        "with_transferable_evidence": sum(
            bool(result.get("transferable_evidence"))
            for result in results
        ),
    }

    education_results = match_education_requirements(
        job_analysis.get("education_requirements", []),
        resume_analysis.get("education", []),
    )

    experience_results = match_experience_requirements(
        job_analysis.get("experience_requirements", []),
        resume_analysis.get("work_experience", {}),
    )

    return {
        "summary": skill_summary,
        "requirements": results,
        "education_requirements": education_results,
        "experience_requirements": experience_results,
        "matching_version": MATCHING_VERSION,
    }
