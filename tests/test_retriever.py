"""
test_retriever.py
Tests for services/retriever.py

Covers:
  - Top-K results returned correctly
  - Result schema (text, page, chunk_index, score)
  - Score ordering (ascending L2 distance)
  - Custom top_k override
  - Missing document raises FileNotFoundError
  - Empty query still returns results
  - Exact-match vector produces near-zero score
"""

import os
import pytest
import numpy as np
from unittest.mock import patch

from services.retriever import retrieve_chunks
from conftest import FAKE_DOC_ID, FAKE_EMBEDDING, EMBEDDING_DIM


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _build_faiss_pair(chunks, embeddings):
    """Creates an in-memory FAISS index + chunk list (mirrors vector_store)."""
    import faiss
    vectors = np.array(embeddings, dtype="float32")
    index   = faiss.IndexFlatL2(EMBEDDING_DIM)
    index.add(vectors)
    return index, chunks


def _patched_retrieve(chunks, embeddings, query="test", top_k=3):
    with patch("services.retriever.load_vector_store",
               return_value=_build_faiss_pair(chunks, embeddings)), \
         patch("services.retriever.generate_embeddings",
               return_value=[FAKE_EMBEDDING]):
        return retrieve_chunks(FAKE_DOC_ID, query, top_k=top_k)


# ─── Core retrieval ───────────────────────────────────────────────────────────

class TestRetrieveChunks:

    def test_returns_list(self, sample_chunks, sample_embeddings):
        result = _patched_retrieve(sample_chunks, sample_embeddings)
        assert isinstance(result, list)

    def test_returns_correct_top_k(self, sample_chunks, sample_embeddings):
        result = _patched_retrieve(sample_chunks, sample_embeddings, top_k=3)
        assert len(result) == 3

    def test_top_k_one_returns_single_result(self, sample_chunks, sample_embeddings):
        result = _patched_retrieve(sample_chunks, sample_embeddings, top_k=1)
        assert len(result) == 1

    def test_top_k_does_not_exceed_chunk_count(self, sample_chunks, sample_embeddings):
        result = _patched_retrieve(sample_chunks, sample_embeddings, top_k=999)
        assert len(result) <= len(sample_chunks)

    def test_default_top_k_uses_settings(self, sample_chunks, sample_embeddings):
        with patch("services.retriever.load_vector_store",
                   return_value=_build_faiss_pair(sample_chunks, sample_embeddings)), \
             patch("services.retriever.generate_embeddings",
                   return_value=[FAKE_EMBEDDING]), \
             patch("services.retriever.settings") as mock_s:
            mock_s.TOP_K = 2
            result = retrieve_chunks(FAKE_DOC_ID, "query")
        assert len(result) <= 2


# ─── Result schema ────────────────────────────────────────────────────────────

class TestResultSchema:

    def setup_method(self):
        pass

    def _get_results(self, sample_chunks, sample_embeddings):
        return _patched_retrieve(sample_chunks, sample_embeddings, top_k=3)

    def test_has_text_key(self, sample_chunks, sample_embeddings):
        for item in self._get_results(sample_chunks, sample_embeddings):
            assert "text" in item

    def test_has_page_key(self, sample_chunks, sample_embeddings):
        for item in self._get_results(sample_chunks, sample_embeddings):
            assert "page" in item

    def test_has_chunk_index_key(self, sample_chunks, sample_embeddings):
        for item in self._get_results(sample_chunks, sample_embeddings):
            assert "chunk_index" in item

    def test_has_score_key(self, sample_chunks, sample_embeddings):
        for item in self._get_results(sample_chunks, sample_embeddings):
            assert "score" in item

    def test_score_is_float(self, sample_chunks, sample_embeddings):
        for item in self._get_results(sample_chunks, sample_embeddings):
            assert isinstance(item["score"], float)

    def test_score_is_non_negative(self, sample_chunks, sample_embeddings):
        for item in self._get_results(sample_chunks, sample_embeddings):
            assert item["score"] >= 0.0

    def test_text_is_str(self, sample_chunks, sample_embeddings):
        for item in self._get_results(sample_chunks, sample_embeddings):
            assert isinstance(item["text"], str)

    def test_page_is_int(self, sample_chunks, sample_embeddings):
        for item in self._get_results(sample_chunks, sample_embeddings):
            assert isinstance(item["page"], int)

    def test_chunk_index_is_int(self, sample_chunks, sample_embeddings):
        for item in self._get_results(sample_chunks, sample_embeddings):
            assert isinstance(item["chunk_index"], int)

    def test_text_is_not_empty(self, sample_chunks, sample_embeddings):
        for item in self._get_results(sample_chunks, sample_embeddings):
            assert item["text"] != ""


# ─── Score ordering ───────────────────────────────────────────────────────────

class TestScoreOrdering:

    def test_scores_are_ascending(self, sample_chunks, sample_embeddings):
        """FAISS returns nearest neighbours: lower L2 = better match."""
        result = _patched_retrieve(sample_chunks, sample_embeddings, top_k=5)
        scores = [r["score"] for r in result]
        assert scores == sorted(scores)

    def test_exact_match_vector_score_near_zero(self):
        """Query vector identical to stored vector → L2 distance ≈ 0."""
        exact_vec = [0.5] * EMBEDDING_DIM
        chunks    = [{"text": "exact match", "page": 1, "chunk_index": 0}]

        with patch("services.retriever.load_vector_store",
                   return_value=_build_faiss_pair(chunks, [exact_vec])), \
             patch("services.retriever.generate_embeddings",
                   return_value=[exact_vec]):
            result = retrieve_chunks(FAKE_DOC_ID, "any query", top_k=1)

        assert pytest.approx(result[0]["score"], abs=1e-4) == 0.0

    def test_different_vectors_produce_nonzero_scores(self, sample_chunks):
        """Dissimilar vectors should have positive scores."""
        distinct_embeddings = [
            [float(i) * 0.01] * EMBEDDING_DIM for i in range(1, len(sample_chunks) + 1)
        ]
        query_vec = [99.0] * EMBEDDING_DIM   # far from all stored vectors

        with patch("services.retriever.load_vector_store",
                   return_value=_build_faiss_pair(sample_chunks, distinct_embeddings)), \
             patch("services.retriever.generate_embeddings",
                   return_value=[query_vec]):
            result = retrieve_chunks(FAKE_DOC_ID, "far query", top_k=3)

        assert all(r["score"] > 0 for r in result)


# ─── Error handling ───────────────────────────────────────────────────────────

class TestRetrieveErrors:

    def test_missing_document_raises_file_not_found(self):
        with patch("services.retriever.load_vector_store",
                   side_effect=FileNotFoundError("No index")):
            with pytest.raises(FileNotFoundError):
                retrieve_chunks("bad-doc-id", "query")

    def test_embedding_failure_propagates(self, sample_chunks, sample_embeddings):
        with patch("services.retriever.load_vector_store",
                   return_value=_build_faiss_pair(sample_chunks, sample_embeddings)), \
             patch("services.retriever.generate_embeddings",
                   side_effect=RuntimeError("OpenAI API error")):
            with pytest.raises(RuntimeError):
                retrieve_chunks(FAKE_DOC_ID, "query")

    def test_empty_query_returns_results(self, sample_chunks, sample_embeddings):
        result = _patched_retrieve(sample_chunks, sample_embeddings, query="", top_k=3)
        assert isinstance(result, list)
        assert len(result) > 0
