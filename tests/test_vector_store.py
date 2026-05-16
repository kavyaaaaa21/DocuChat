"""
test_vector_store.py — Tests for services/vector_store.py
"""

import os
import json
import pytest
import numpy as np
import faiss
from unittest.mock import patch
from services.vector_store import save_vector_store, load_vector_store
from conftest import FAKE_DOCUMENT_ID, FAKE_EMBEDDING, EMBEDDING_DIM


class TestSaveVectorStore:

    def test_creates_index_file(self, tmp_path, sample_chunks, sample_embeddings):
        with patch("services.vector_store.settings") as s:
            s.FAISS_INDEX_DIR = str(tmp_path)
            save_vector_store(FAKE_DOCUMENT_ID, sample_chunks, sample_embeddings)

        index_path = tmp_path / FAKE_DOCUMENT_ID / "index.faiss"
        assert index_path.exists()

    def test_creates_chunks_json(self, tmp_path, sample_chunks, sample_embeddings):
        with patch("services.vector_store.settings") as s:
            s.FAISS_INDEX_DIR = str(tmp_path)
            save_vector_store(FAKE_DOCUMENT_ID, sample_chunks, sample_embeddings)

        chunks_path = tmp_path / FAKE_DOCUMENT_ID / "chunks.json"
        assert chunks_path.exists()

    def test_chunks_json_matches_input(self, tmp_path, sample_chunks, sample_embeddings):
        with patch("services.vector_store.settings") as s:
            s.FAISS_INDEX_DIR = str(tmp_path)
            save_vector_store(FAKE_DOCUMENT_ID, sample_chunks, sample_embeddings)

        with open(tmp_path / FAKE_DOCUMENT_ID / "chunks.json") as f:
            stored = json.load(f)

        assert stored == sample_chunks

    def test_faiss_index_contains_correct_vector_count(self, tmp_path, sample_chunks, sample_embeddings):
        with patch("services.vector_store.settings") as s:
            s.FAISS_INDEX_DIR = str(tmp_path)
            save_vector_store(FAKE_DOCUMENT_ID, sample_chunks, sample_embeddings)

        index = faiss.read_index(str(tmp_path / FAKE_DOCUMENT_ID / "index.faiss"))
        assert index.ntotal == len(sample_embeddings)

    def test_creates_directory_if_not_exists(self, tmp_path, sample_chunks, sample_embeddings):
        new_dir = tmp_path / "new_subdir"
        assert not new_dir.exists()

        with patch("services.vector_store.settings") as s:
            s.FAISS_INDEX_DIR = str(new_dir)
            save_vector_store(FAKE_DOCUMENT_ID, sample_chunks, sample_embeddings)

        assert new_dir.exists()

    def test_different_docs_saved_separately(self, tmp_path, sample_chunks, sample_embeddings):
        doc_a = "doc-aaa"
        doc_b = "doc-bbb"

        with patch("services.vector_store.settings") as s:
            s.FAISS_INDEX_DIR = str(tmp_path)
            save_vector_store(doc_a, sample_chunks, sample_embeddings)
            save_vector_store(doc_b, sample_chunks, sample_embeddings)

        assert (tmp_path / doc_a / "index.faiss").exists()
        assert (tmp_path / doc_b / "index.faiss").exists()


class TestLoadVectorStore:

    def test_load_returns_index_and_chunks(self, tmp_path, sample_chunks, sample_embeddings):
        with patch("services.vector_store.settings") as s:
            s.FAISS_INDEX_DIR = str(tmp_path)
            save_vector_store(FAKE_DOCUMENT_ID, sample_chunks, sample_embeddings)
            index, chunks = load_vector_store(FAKE_DOCUMENT_ID)

        assert isinstance(index, faiss.IndexFlatL2)
        assert isinstance(chunks, list)

    def test_loaded_chunks_match_saved(self, tmp_path, sample_chunks, sample_embeddings):
        with patch("services.vector_store.settings") as s:
            s.FAISS_INDEX_DIR = str(tmp_path)
            save_vector_store(FAKE_DOCUMENT_ID, sample_chunks, sample_embeddings)
            _, chunks = load_vector_store(FAKE_DOCUMENT_ID)

        assert chunks == sample_chunks

    def test_loaded_index_has_correct_vector_count(self, tmp_path, sample_chunks, sample_embeddings):
        with patch("services.vector_store.settings") as s:
            s.FAISS_INDEX_DIR = str(tmp_path)
            save_vector_store(FAKE_DOCUMENT_ID, sample_chunks, sample_embeddings)
            index, _ = load_vector_store(FAKE_DOCUMENT_ID)

        assert index.ntotal == len(sample_embeddings)

    def test_raises_file_not_found_for_missing_doc(self, tmp_path):
        with patch("services.vector_store.settings") as s:
            s.FAISS_INDEX_DIR = str(tmp_path)
            with pytest.raises(FileNotFoundError):
                load_vector_store("non-existent-doc-id")

    def test_save_then_search_returns_results(self, tmp_path, sample_chunks, sample_embeddings):
        """Saved index should be searchable after loading."""
        with patch("services.vector_store.settings") as s:
            s.FAISS_INDEX_DIR = str(tmp_path)
            save_vector_store(FAKE_DOCUMENT_ID, sample_chunks, sample_embeddings)
            index, _ = load_vector_store(FAKE_DOCUMENT_ID)

        query = np.array([FAKE_EMBEDDING], dtype="float32")
        distances, indices = index.search(query, 3)
        assert len(indices[0]) == 3
        assert all(i >= 0 for i in indices[0])
