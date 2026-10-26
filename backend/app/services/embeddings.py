from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

_model = None

def get_model():
    """Load the model once and reuse it."""
    global _model

    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)

    return _model


def embed_text(text: str) -> list[float]:
    """Convert text into a semantic embedding."""
    model = get_model()

    embedding = model.encode(
        text,
        normalize_embeddings=True
    )

    return embedding.tolist()
