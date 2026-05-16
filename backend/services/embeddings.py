from typing import List
from openai import OpenAI
from core.config import settings
from core.logger import get_logger

logger = get_logger(__name__)
client = OpenAI(api_key=settings.OPENAI_API_KEY)


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
    all_embeddings = []
    batch_size = 100

    for i in range(0, len(cleaned), batch_size):
        batch = cleaned[i: i + batch_size]
        response = client.embeddings.create(
            model=settings.EMBEDDING_MODEL,
            input=batch
        )
        batch_embeddings = [item.embedding for item in response.data]
        all_embeddings.extend(batch_embeddings)
        logger.info(f"Embedded batch {i // batch_size + 1} | {len(batch)} chunks")

    logger.info(f"Embedding complete. Total vectors: {len(all_embeddings)}")
    return all_embeddings