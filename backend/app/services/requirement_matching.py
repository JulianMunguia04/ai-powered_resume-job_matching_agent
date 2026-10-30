
def find_resume_skill(resume_skills: list[dict], required_skill: str):
    """Find an exact normalized skill match in the resume analysis."""
    for skill in resume_skills:
        if skill["name"].lower() == required_skill.lower():
            return skill

    return None


def classify_resume_evidence(skill: dict, sections: dict) -> tuple[str, list[str]]:
    """
    Determine whether a skill is demonstrated in experience/projects
    or only listed in the resume.
    """
    experience_text = sections.get("experience", "").lower()
    project_text = sections.get("projects", "").lower()

    demonstrated_evidence = []
    listed_evidence = []

    for evidence in skill.get("evidence", []):
        normalized_evidence = evidence.lower()

        if (
            normalized_evidence in experience_text
            or normalized_evidence in project_text
        ):
            demonstrated_evidence.append(evidence)
        else:
            listed_evidence.append(evidence)

    if demonstrated_evidence:
        return "demonstrated", demonstrated_evidence

    if listed_evidence:
        return "listed", listed_evidence

    return "not_found", []


def match_skill_requirement(
    requirement: dict,
    resume_skills: list[dict],
    resume_sections: dict,
) -> dict:
    """Evaluate one job skill requirement against resume evidence."""
    required_skill = requirement["name"]

    resume_skill = find_resume_skill(resume_skills, required_skill)

    if resume_skill is None:
        return {
            "requirement": required_skill,
            "importance": requirement["requirement_type"],
            "status": "not_found",
            "evidence": [],
            "explanation": (
                f"No evidence for {required_skill} was identified "
                "in the analyzed resume."
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
    else:
        explanation = (
            f"{required_skill} appears in the resume, but no supporting "
            "project or work experience evidence was identified."
        )

    return {
        "requirement": required_skill,
        "importance": requirement["requirement_type"],
        "status": status,
        "evidence": evidence,
        "explanation": explanation,
    }


def match_job_requirements(resume_analysis: dict, job_analysis: dict) -> dict:
    """Compare all extracted job skill requirements against a resume."""
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

    summary = {
        "total": len(results),
        "demonstrated": sum(
            result["status"] == "demonstrated" for result in results
        ),
        "listed": sum(
            result["status"] == "listed" for result in results
        ),
        "not_found": sum(
            result["status"] == "not_found" for result in results
        ),
    }

    return {
        "summary": summary,
        "requirements": results,
        "matching_version": "1.0",
    }
