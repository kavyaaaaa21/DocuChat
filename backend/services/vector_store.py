import os
import json
import faiss
import numpy as np
from typing import List, Dict
from core.config import settings
from core.logger import get_logger

logger = get_logger(__name__)


def save_vector_store(document_id: str, chunks: List[Dict], embeddings: List[List[float]]):
    """
    Creates a FAISS index from embeddings and saves it to disk
    along with chunk metadata (text, page, chunk_index).

    Args:
        document_id: Unique ID for the document
        chunks:      List of chunk dicts {text, page, chunk_index}
        embeddings:  Corresponding list of embedding vectors
    """
    save_dir = os.path.join(settings.FAISS_INDEX_DIR, document_id)
    os.makedirs(save_dir, exist_ok=True)

    # Build FAISS index
    vectors = np.array(embeddings, dtype="float32")
    dimension = vectors.shape[1]

    index = faiss.IndexFlatL2(dimension)
    index.add(vectors)

    # Save FAISS binary index
    faiss.write_index(index, os.path.join(save_dir, "index.faiss"))

    # Save chunk metadata as JSON
    with open(os.path.join(save_dir, "chunks.json"), "w") as f:
        json.dump(chunks, f, indent=2)

    logger.info(f"FAISS index saved | doc={document_id} | vectors={index.ntotal}")


def load_vector_store(document_id: str):
    """
    Loads a FAISS index and chunk metadata from disk.

    Returns:
        (faiss.Index, List[Dict]) — index and chunk list
    """
    save_dir = os.path.join(settings.FAISS_INDEX_DIR, document_id)
    index_path = os.path.join(save_dir, "index.faiss")
    chunks_path = os.path.join(save_dir, "chunks.json")

    if not os.path.exists(index_path):
        raise FileNotFoundError(f"No vector store found for document_id: {document_id}")

    index = faiss.read_index(index_path)

    with open(chunks_path, "r") as f:
        chunks = json.load(f)

    logger.info(f"FAISS index loaded | doc={document_id} | vectors={index.ntotal}")
    return index, chunks