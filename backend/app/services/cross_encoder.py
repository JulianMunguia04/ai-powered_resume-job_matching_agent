
from sentence_transformers import CrossEncoder

MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

_model = None


def get_cross_encoder():
    """
    Load the Cross-Encoder once and reuse it.
    """
    global _model

    if _model is None:
        _model = CrossEncoder(MODEL_NAME)

    return _model


def calculate_cross_encoder_score(resume_text: str, job_text: str) -> float:
    """
    Evaluate how relevant a resume is to a job description.

    The model receives both texts together rather than
    comparing two independently generated embeddings.
    """

    model = get_cross_encoder()

    score = model.predict(
        [(job_text, resume_text)],
        show_progress_bar=False
    )

    return float(score[0])
