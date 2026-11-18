import json
import os

from openai import OpenAI


_client = None


def get_openai_client():
    """Create the OpenAI client once and reuse it."""
    global _client

    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is missing from the environment."
            )

        _client = OpenAI(api_key=api_key)

    return _client


def generate_match_explanation(
    resume_text: str,
    job_title: str,
    job_description: str,
    requirement_matching: dict,
    scores: dict,
    resume_skills: list,
    job_skills: list,
) -> dict:
    """
    Generate a structured explanation of one resume-job match.

    The requirement matching data is supplied as evidence. The LLM
    must not invent skills, experience, or qualifications.
    """

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    evidence = {
        "requirement_matching": requirement_matching,
        "scores": scores,
        "resume_skills": resume_skills,
        "job_skills": job_skills,
    }

    prompt = f"""
You are an objective resume-to-job matching analyst.

Evaluate how well the candidate's resume matches the job description.

Your task is to explain the match using ONLY the information provided.

IMPORTANT RULES:

1. Do not invent skills, experience, qualifications, or achievements.
2. Do not claim that a candidate has a skill unless the resume evidence
   supports that claim.
3. Distinguish between demonstrated skills and skills merely listed.
4. Treat transferable skills as related experience, not exact matches.
5. Explain important gaps honestly and constructively.
6. Do not assume that total employment duration is relevant experience
   for this particular job.
7. Do not interpret matching scores as percentages.
8. Do not make hiring decisions based on protected characteristics.
9. Be specific and reference actual resume evidence where possible.
10. Consider required skills more important than preferred or mentioned
    skills.

JOB TITLE:
{job_title}

JOB DESCRIPTION:
{job_description}

RESUME:
{resume_text}

MATCHING ENGINE EVIDENCE:
{json.dumps(evidence, ensure_ascii=False, default=str)}

Return:
- A concise match summary.
- An overall assessment explaining the strongest reasons for the match.
- Specific strengths supported by resume evidence.
- Important gaps or areas where evidence is missing.
- A practical recommendation for the recruiter.

Be balanced. A high similarity score does not automatically mean
the candidate meets every job requirement.
"""

    schema = {
        "type": "object",
        "properties": {
            "match_summary": {
                "type": "string"
            },
            "overall_assessment": {
                "type": "string"
            },
            "strengths": {
                "type": "array",
                "items": {
                    "type": "string"
                }
            },
            "gaps": {
                "type": "array",
                "items": {
                    "type": "string"
                }
            },
            "recommendation": {
                "type": "string"
            }
        },
        "required": [
            "match_summary",
            "overall_assessment",
            "strengths",
            "gaps",
            "recommendation"
        ],
        "additionalProperties": False
    }

    client = get_openai_client()

    response = client.responses.create(
        model=model,
        input=prompt,
        text={
            "format": {
                "type": "json_schema",
                "name": "resume_job_match",
                "strict": True,
                "schema": schema
            }
        }
    )

    if not response.output_text:
        raise RuntimeError(
            "OpenAI returned an empty match explanation."
        )

    try:
        result = json.loads(response.output_text)
    except json.JSONDecodeError as error:
        raise RuntimeError(
            "OpenAI returned invalid JSON for the match explanation."
        ) from error

    return result
