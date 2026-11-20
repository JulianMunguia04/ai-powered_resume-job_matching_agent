
import json

from rank_bm25 import BM25Okapi

from sqlalchemy.exc import IntegrityError

from services.database import db
from models import Resume, Job, Matching

from services.hybrid_matching import (
    calculate_hybrid_matches,
    rerank_with_cross_encoder,
    calculate_semantic_score,
    calculate_structured_score,
    normalize_bm25_scores,
    tokenize,
    SEMANTIC_WEIGHT,
    BM25_WEIGHT,
    STRUCTURED_WEIGHT,
)

from services.requirement_matching import match_job_requirements
from services.cross_encoder import calculate_cross_encoder_score
from services.llm_matching import generate_match_explanation


DEFAULT_TOP_K = 10
MATCHING_VERSION = "1.0"


# --------------------------------------------------
# DATABASE DATA ADAPTERS
# --------------------------------------------------

def resume_to_dict(resume):
    embedding = resume.embedding_record

    return {
        "id": str(resume.id),
        "candidate_name": resume.candidate_name,
        "text": resume.raw_text,
        "embedding": list(embedding.embedding),
        "embedding_model": embedding.model_name,
        "analysis": resume.analysis,
        "updated_at": resume.updated_at,
    }


def job_to_dict(job):
    embedding = job.embedding_record

    return {
        "id": str(job.id),
        "title": job.title,
        "description": job.description,
        "text": f"{job.title}\n{job.description}",
        "embedding": list(embedding.embedding),
        "embedding_model": embedding.model_name,
        "analysis": job.analysis,
        "updated_at": job.updated_at,
    }


# --------------------------------------------------
# GENERAL HELPERS
# --------------------------------------------------

def get_top_k(value):
    """Keep result limits within a reasonable range."""
    try:
        value = int(value)
    except (ValueError, TypeError):
        return DEFAULT_TOP_K

    return max(1, min(value, 50))


def get_skill_names(analysis):
    """Extract all distinct skill names from an analysis."""
    skills = analysis.get("skills", [])
    names = []
    seen = set()

    for skill in skills:
        name = skill.get("name", "").strip()

        if not name:
            continue

        normalized = name.lower()

        if normalized not in seen:
            seen.add(normalized)
            names.append(name)

    return names


def build_skill_comparison(requirement_matching):
    """
    Preserve the deterministic skill matching results.

    The LLM explains these results but does not decide or overwrite
    whether a skill is demonstrated, listed, or missing.
    """
    return requirement_matching.get("requirements", [])


def build_explanation_text(analysis):
    """Create a readable explanation from the structured LLM response."""
    sections = [
        f"Match Summary\n{analysis['match_summary']}",
        f"Overall Assessment\n{analysis['overall_assessment']}",
    ]

    if analysis.get("strengths"):
        strengths = "\n".join(
            f"- {item}" for item in analysis["strengths"]
        )
        sections.append(f"Strengths\n{strengths}")

    if analysis.get("gaps"):
        gaps = "\n".join(
            f"- {item}" for item in analysis["gaps"]
        )
        sections.append(f"Gaps\n{gaps}")

    sections.append(
        f"Recommendation\n{analysis['recommendation']}"
    )

    return "\n\n".join(sections)


# --------------------------------------------------
# CACHED LLM EXPLANATIONS
# --------------------------------------------------

def get_or_generate_matching(
    resume_record,
    job_record,
    resume_data,
    job_data,
    scores,
    requirement_matching,
):
    """
    Retrieve a cached explanation if both source documents are
    unchanged. Otherwise generate and save a new explanation.
    """

    existing = Matching.query.filter_by(
        resume_id=resume_record.id,
        job_id=job_record.id,
    ).first()

    cache_is_valid = (
      existing is not None
      and existing.resume_updated_at == resume_record.updated_at
      and existing.job_updated_at == job_record.updated_at
      and existing.analysis.get("matching_version") == MATCHING_VERSION
  )

    if cache_is_valid:
        return {
            "id": str(existing.id),
            "text": existing.text,
            "analysis": existing.analysis,
            "scores": existing.scores,
            "cached": True,
            "created_at": existing.created_at.isoformat(),
        }

    # Generate the LLM explanation using the existing evidence.
    llm_analysis = generate_match_explanation(
        resume_text=resume_data["text"],
        job_title=job_data["title"],
        job_description=job_data["description"],
        requirement_matching=requirement_matching,
        scores=scores,
        resume_skills=get_skill_names(resume_data["analysis"]),
        job_skills=get_skill_names(job_data["analysis"]),
    )

    # Keep deterministic matching evidence alongside the LLM response.
    analysis = {
        **llm_analysis,
        "skill_comparison": build_skill_comparison(
            requirement_matching
        ),
        "resume_skills": get_skill_names(resume_data["analysis"]),
        "job_skills": get_skill_names(job_data["analysis"]),
        "requirement_matching": requirement_matching,
        "matching_version": MATCHING_VERSION,
    }

    explanation_text = build_explanation_text(llm_analysis)

    if existing is None:
        existing = Matching(
            resume_id=resume_record.id,
            job_id=job_record.id,
            text=explanation_text,
            analysis=analysis,
            scores=scores,
            resume_updated_at=resume_record.updated_at,
            job_updated_at=job_record.updated_at,
        )

        db.session.add(existing)

        try:
            db.session.commit()
            db.session.refresh(existing)

        except IntegrityError:
            db.session.rollback()

            # Another request may have saved this same match
            # while this request was generating its explanation.
            existing = Matching.query.filter_by(
                resume_id=resume_record.id,
                job_id=job_record.id,
            ).first()

            if existing is None:
                # The error was caused by another constraint.
                raise

            return {
                "id": str(existing.id),
                "text": existing.text,
                "analysis": existing.analysis,
                "scores": existing.scores,
                "cached": True,
                "created_at": existing.created_at.isoformat(),
            }

    else:
        existing.text = explanation_text
        existing.analysis = analysis
        existing.scores = scores
        existing.resume_updated_at = resume_record.updated_at
        existing.job_updated_at = job_record.updated_at

        db.session.commit()
        db.session.refresh(existing)

    return {
        "id": str(existing.id),
        "text": existing.text,
        "analysis": existing.analysis,
        "scores": existing.scores,
        "cached": False,
        "created_at": existing.created_at.isoformat(),
    }


# --------------------------------------------------
# RESUME -> JOBS
# --------------------------------------------------

def find_jobs_for_resume(resume_id, top_k=DEFAULT_TOP_K):
    """
    Find the highest-ranking jobs for one resume.

    Ranking:
    1. Semantic similarity + BM25 + structured requirements.
    2. Cross-Encoder reranking.
    3. LLM explanation for the top results only.
    """

    resume_record = db.session.get(Resume, resume_id)

    if resume_record is None:
        raise LookupError("Resume not found.")

    resume_data = resume_to_dict(resume_record)

    if not resume_data["analysis"] or not resume_data["embedding"]:
        raise ValueError("Resume analysis or embedding is unavailable.")

    job_records = Job.query.all()

    jobs = {
        str(job.id): job_to_dict(job)
        for job in job_records
    }

    # First-stage hybrid ranking.
    matches = calculate_hybrid_matches(resume_data, jobs)

    # Second-stage Cross-Encoder reranking.
    matches = rerank_with_cross_encoder(
        resume_data,
        matches,
        jobs,
    )

    selected_matches = matches[:get_top_k(top_k)]

    results = []

    for match in selected_matches:
        job_record = next(
            (
                job for job in job_records
                if str(job.id) == match["job_id"]
            ),
            None,
        )

        if job_record is None:
            continue

        job_data = jobs[match["job_id"]]

        requirement_matching = match["matching"]

        scores = match["scores"]

        saved_matching = get_or_generate_matching(
            resume_record=resume_record,
            job_record=job_record,
            resume_data=resume_data,
            job_data=job_data,
            scores=scores,
            requirement_matching=requirement_matching,
        )

        results.append({
            "job": {
                "id": str(job_record.id),
                "title": job_record.title,
                "description": job_record.description,
            },
            "scores": scores,
            "matching": requirement_matching,
            "explanation": saved_matching,
        })

    return {
        "resume_id": str(resume_record.id),
        "total_matches": len(matches),
        "returned_matches": len(results),
        "ranking_method": {
            "name": "Hybrid NLP Matching with Cross-Encoder Reranking",
            "weights": {
                "semantic": SEMANTIC_WEIGHT,
                "bm25": BM25_WEIGHT,
                "structured": STRUCTURED_WEIGHT,
            },
            "final_ranking": "cross_encoder",
        },
        "matches": results,
    }


# --------------------------------------------------
# JOB -> APPLICANTS
# --------------------------------------------------

def find_applicants_for_job(job_id, top_k=DEFAULT_TOP_K):
    """
    Find the highest-ranking resumes for one job.

    BM25 searches the resume corpus using the job description.
    Structured matching evaluates each resume against the job.
    Cross-Encoder reranks the candidates.
    """

    job_record = db.session.get(Job, job_id)

    if job_record is None:
        raise LookupError("Job not found.")

    job_data = job_to_dict(job_record)

    if not job_data["analysis"] or not job_data["embedding"]:
        raise ValueError("Job analysis or embedding is unavailable.")

    resume_records = Resume.query.all()

    compatible_resumes = []

    for resume_record in resume_records:
        resume_data = resume_to_dict(resume_record)

        if not resume_data["analysis"] or not resume_data["embedding"]:
            continue

        if resume_data["embedding_model"] != job_data["embedding_model"]:
            continue

        if len(resume_data["embedding"]) != len(job_data["embedding"]):
            continue

        compatible_resumes.append(
            (resume_record, resume_data)
        )

    if not compatible_resumes:
        return {
            "job_id": str(job_record.id),
            "total_matches": 0,
            "returned_matches": 0,
            "ranking_method": {
                "name": "Hybrid NLP Matching with Cross-Encoder Reranking",
                "weights": {
                    "semantic": SEMANTIC_WEIGHT,
                    "bm25": BM25_WEIGHT,
                    "structured": STRUCTURED_WEIGHT,
                },
                "final_ranking": "cross_encoder",
            },
            "matches": [],
        }

    # Build the resume corpus for BM25.
    resume_documents = [
        tokenize(resume_data["text"])
        for _, resume_data in compatible_resumes
    ]

    job_query = tokenize(job_data["text"])

    bm25 = BM25Okapi(resume_documents)

    raw_scores = bm25.get_scores(job_query).tolist()
    normalized_scores = normalize_bm25_scores(raw_scores)

    ranked_candidates = []

    for index, (resume_record, resume_data) in enumerate(
        compatible_resumes
    ):
        semantic_score = calculate_semantic_score(
            resume_data,
            job_data,
        )

        requirement_matching = match_job_requirements(
            resume_data["analysis"],
            job_data["analysis"],
        )

        structured_score = calculate_structured_score(
            requirement_matching
        )

        bm25_score = normalized_scores[index]

        hybrid_score = (
            SEMANTIC_WEIGHT * semantic_score
            + BM25_WEIGHT * bm25_score
            + STRUCTURED_WEIGHT * structured_score
        )

        cross_encoder_score = calculate_cross_encoder_score(
            resume_data["text"],
            job_data["text"],
        )

        scores = {
            "semantic": round(semantic_score, 4),
            "bm25": round(bm25_score, 4),
            "structured": round(structured_score, 4),
            "hybrid": round(hybrid_score, 4),
            "cross_encoder": round(cross_encoder_score, 4),
        }

        ranked_candidates.append({
            "resume_record": resume_record,
            "resume_data": resume_data,
            "scores": scores,
            "matching": requirement_matching,
        })

    # Cross-Encoder is the final ranking stage.
    ranked_candidates.sort(
        key=lambda item: item["scores"]["cross_encoder"],
        reverse=True,
    )

    selected_candidates = ranked_candidates[:get_top_k(top_k)]

    results = []

    for candidate in selected_candidates:
        resume_record = candidate["resume_record"]
        resume_data = candidate["resume_data"]

        saved_matching = get_or_generate_matching(
            resume_record=resume_record,
            job_record=job_record,
            resume_data=resume_data,
            job_data=job_data,
            scores=candidate["scores"],
            requirement_matching=candidate["matching"],
        )

        results.append({
            "applicant": {
                "id": str(resume_record.id),
                "candidate_name": resume_record.candidate_name,
            },
            "scores": candidate["scores"],
            "matching": candidate["matching"],
            "explanation": saved_matching,
        })

    return {
        "job_id": str(job_record.id),
        "total_matches": len(ranked_candidates),
        "returned_matches": len(results),
        "ranking_method": {
            "name": "Hybrid NLP Matching with Cross-Encoder Reranking",
            "weights": {
                "semantic": SEMANTIC_WEIGHT,
                "bm25": BM25_WEIGHT,
                "structured": STRUCTURED_WEIGHT,
            },
            "final_ranking": "cross_encoder",
        },
        "matches": results,
    }
