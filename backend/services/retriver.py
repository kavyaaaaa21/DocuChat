import numpy as np
from typing import List, Dict
from services.embeddings import generate_embeddings
from services.vector_store import load_vector_store
from core.config import settings
from core.logger import get_logger

logger = get_logger(__name__)


def retrieve_chunks(document_id: str, query: str, top_k: int = None) -> List[Dict]:
    """
    Embeds the query, runs semantic similarity search in FAISS,
    and returns the top-K most relevant chunks.

    Args:
        document_id: The document to search within
        query:       User's question or topic string
        top_k:       Number of chunks to return (defaults to settings.TOP_K)

    Returns:
        List of chunk dicts: [{text, page, chunk_index, score}, ...]
    """
    k = top_k or settings.TOP_K

    # Load the FAISS index + metadata for this document
    index, chunks = load_vector_store(document_id)

    # Embed the query
    query_embedding = generate_embeddings([query])[0]
    query_vector = np.array([query_embedding], dtype="float32")

    # Search FAISS — returns distances & indices of nearest neighbours
    distances, indices = index.search(query_vector, k)

    results = []
    for dist, idx in zip(distances[0], indices[0]):
        if idx == -1:
            continue  # FAISS returns -1 for empty slots
        chunk = chunks[idx].copy()
        chunk["score"] = float(dist)
        results.append(chunk)

    logger.info(f"Retrieved {len(results)} chunks for query: '{query[:60]}...'")
    return results
