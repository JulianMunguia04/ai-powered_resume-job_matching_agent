
import re

from rank_bm25 import BM25Okapi

from services.requirement_matching import match_job_requirements


# Initial experimental weights.
SEMANTIC_WEIGHT = 0.35
BM25_WEIGHT = 0.25
STRUCTURED_WEIGHT = 0.40


def tokenize(text: str) -> list[str]:
    """Convert text into lowercase word tokens for BM25."""
    return re.findall(r"\b[a-zA-Z0-9+#.]+\b", text.lower())


def normalize_bm25_scores(scores: list[float]) -> list[float]:
    """
    Normalize BM25 scores across the current job collection.

    This produces relative scores, not probabilities.
    """
    if not scores:
        return []

    maximum = max(scores)

    if maximum <= 0:
        return [0.0 for _ in scores]

    return [
        max(0.0, min(1.0, score / maximum))
        for score in scores
    ]


def calculate_semantic_score(resume: dict, job: dict) -> float:
    """Calculate cosine similarity using previously stored embeddings."""
    if resume["embedding_model"] != job["embedding_model"]:
        return 0.0

    resume_vector = resume["embedding"]
    job_vector = job["embedding"]

    if len(resume_vector) != len(job_vector):
        return 0.0

    # Both vectors were normalized during embedding generation.
    cosine_similarity = sum(
        resume_value * job_value
        for resume_value, job_value in zip(resume_vector, job_vector)
    )

    # Keep the score within the 0-1 range.
    return max(0.0, min(1.0, float(cosine_similarity)))


def calculate_structured_score(matching_result: dict) -> float:
    """
    Calculate a weighted requirement-evidence score.

    Required requirements count more than preferred or mentioned
    requirements. A demonstrated match receives more credit than
    a skill appearing only in the skills list.
    """
    importance_weights = {
        "required": 3.0,
        "preferred": 2.0,
        "mentioned": 1.0,
    }

    status_scores = {
        "demonstrated": 1.0,
        "listed": 0.5,
        "partial": 0.5,
        "not_found": 0.0,
    }

    requirements = matching_result.get("requirements", [])

    if not requirements:
        return 0.0

    total_weight = 0.0
    achieved_weight = 0.0

    for requirement in requirements:
        importance = requirement.get("importance", "mentioned")
        status = requirement.get("status", "not_found")

        weight = importance_weights.get(importance, 1.0)
        evidence_score = status_scores.get(status, 0.0)

        total_weight += weight
        achieved_weight += weight * evidence_score

    if total_weight == 0:
        return 0.0

    return achieved_weight / total_weight


def calculate_hybrid_matches(resume: dict, jobs: dict) -> list[dict]:
    """Rank all available jobs against one previously analyzed resume."""

    available_jobs = [
        job for job in jobs.values()
        if job.get("analysis")
        and job.get("embedding_model") == resume.get("embedding_model")
        and len(job.get("embedding", [])) == len(resume.get("embedding", []))
    ]

    if not available_jobs:
        return []

    # BM25 compares the resume against the entire job collection.
    job_documents = [
        tokenize(f"{job['title']} {job['description']}")
        for job in available_jobs
    ]

    resume_query = tokenize(resume["text"])
    bm25 = BM25Okapi(job_documents)
    raw_bm25_scores = bm25.get_scores(resume_query).tolist()

    normalized_bm25_scores = normalize_bm25_scores(raw_bm25_scores)

    results = []

    for index, job in enumerate(available_jobs):
        semantic_score = calculate_semantic_score(resume, job)

        structured_result = match_job_requirements(
            resume["analysis"],
            job["analysis"],
        )

        structured_score = calculate_structured_score(
            structured_result
        )

        bm25_score = normalized_bm25_scores[index]

        hybrid_score = (
            SEMANTIC_WEIGHT * semantic_score
            + BM25_WEIGHT * bm25_score
            + STRUCTURED_WEIGHT * structured_score
        )

        results.append({
            "job_id": job["id"],
            "title": job["title"],
            "scores": {
                "semantic": round(semantic_score, 4),
                "bm25": round(bm25_score, 4),
                "structured": round(structured_score, 4),
                "hybrid": round(hybrid_score, 4),
            },
            "matching": structured_result,
        })

    results.sort(
        key=lambda result: result["scores"]["hybrid"],
        reverse=True,
    )

    return results
