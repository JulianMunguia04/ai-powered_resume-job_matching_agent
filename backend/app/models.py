
import uuid

from sqlalchemy import text, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from pgvector.sqlalchemy import Vector

from services.database import db


class Embedding(db.Model):
    __tablename__ = "embeddings"

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    model_name = db.Column(db.String(255), nullable=False)
    dimensions = db.Column(db.Integer, nullable=False)
    embedding = db.Column(Vector(384), nullable=False)

    created_at = db.Column(
        db.DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )


class Resume(db.Model):
    __tablename__ = "resumes"

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    embedding_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("embeddings.id", ondelete="RESTRICT"),
        nullable=False,
        unique=True
    )

    candidate_name = db.Column(db.String(255), nullable=True)
    raw_text = db.Column(db.Text, nullable=False)
    analysis = db.Column(JSONB, nullable=False)

    created_at = db.Column(
        db.DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    embedding_record = db.relationship("Embedding")


class Job(db.Model):
    __tablename__ = "jobs"

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    embedding_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("embeddings.id", ondelete="RESTRICT"),
        nullable=False,
        unique=True
    )

    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    analysis = db.Column(JSONB, nullable=False)

    created_at = db.Column(
        db.DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    embedding_record = db.relationship("Embedding")


class Matching(db.Model):
    __tablename__ = "matchings"

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    resume_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False
    )

    job_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False
    )

    # Human-readable LLM explanation.
    text = db.Column(db.Text, nullable=False)

    # Structured LLM output: skills, strengths, gaps, etc.
    analysis = db.Column(JSONB, nullable=False)

    # Scores from the matching pipeline.
    scores = db.Column(JSONB, nullable=False)

    # Document versions used to generate this match.
    resume_updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False
    )

    job_updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    resume = db.relationship("Resume")
    job = db.relationship("Job")

    __table_args__ = (
        db.UniqueConstraint(
            "resume_id",
            "job_id",
            name="uq_matching_resume_job"
        ),
    )