from typing import List
from openai import OpenAI
from core.config import settings
from core.logger import get_logger
from sentence_transformers import SentenceTransformer

logger = get_logger(__name__)
client = OpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)


def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generates vector embeddings for a list of text strings
    using OpenAI's embedding model.

    Args:
        texts: List of chunk text strings

    Returns:
        List of embedding vectors (list of floats)
    """
    if not texts:
        raise ValueError("No texts provided for embedding.")

    # OpenAI recommends replacing newlines with spaces for embeddings
    cleaned = [t.replace("\n", " ") for t in texts]

    logger.info(f"Generating embeddings for {len(cleaned)} chunks...")

    # Batch in groups of 100 to stay within API limits
    model = SentenceTransformer("all-MiniLM-L6-v2")
    vectors = model.encode(cleaned, show_progress_bar=True)
    embeddings = [v.tolist() for v in vectors]

    logger.info(f"Embedding complete. Total vectors: {len(embeddings)}")
    return embeddings