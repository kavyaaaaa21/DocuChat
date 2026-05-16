"""
conftest.py — Shared pytest fixtures available to all test files.
Run tests from the project root:  pytest tests/ -v
"""

import os
import sys
import uuid
import json
import pytest
import numpy as np
import tempfile

# Make backend importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

EMBEDDING_DIM  = 1536
FAKE_EMBEDDING = [0.01] * EMBEDDING_DIM

FAKE_DOC_ID  = "test-doc-" + str(uuid.uuid4())
FAKE_QUIZ_ID = "test-quiz-" + str(uuid.uuid4())


# ─── Sample data ────────────────────────────────────────────────────────────

@pytest.fixture
def sample_pages():
    return [
        {"page": 1, "text": "DocuChat AI enables users to interact with documents through chat and quiz modes."},
        {"page": 2, "text": "Quiz Mode generates MCQ, True/False, and Short Answer questions automatically."},
        {"page": 3, "text": "Technical stack: FastAPI, LangChain, FAISS, and OpenAI GPT series."},
    ]


@pytest.fixture
def sample_chunks():
    return [
        {"text": "DocuChat AI enables users to interact with documents.", "page": 1, "chunk_index": 0},
        {"text": "Chat Mode provides context-aware Q&A with source citations.", "page": 1, "chunk_index": 1},
        {"text": "Quiz Mode generates MCQ, True/False, and Short Answer questions.", "page": 2, "chunk_index": 2},
        {"text": "Technical stack includes FastAPI, LangChain, FAISS, and OpenAI.", "page": 3, "chunk_index": 3},
        {"text": "RAG pipeline retrieves relevant chunks for grounded answers.", "page": 3, "chunk_index": 4},
    ]


@pytest.fixture
def sample_embeddings():
    return [FAKE_EMBEDDING[:] for _ in range(5)]


@pytest.fixture
def sample_query():
    return "What is the quiz mode?"


@pytest.fixture
def sample_chat_history():
    return [
        {"role": "user",      "content": "What is DocuChat AI?"},
        {"role": "assistant", "content": "DocuChat AI is a RAG-based PDF assistant."},
    ]


@pytest.fixture
def sample_mcq_questions():
    return [
        {
            "question_id":   str(uuid.uuid4()),
            "question_type": "mcq",
            "question":      "What does RAG stand for?",
            "options":       ["A. Random Answer Generation", "B. Retrieval-Augmented Generation",
                              "C. Rapid Answer Grounding",  "D. None of the above"],
            "correct_answer": "B",
            "explanation":    "RAG stands for Retrieval-Augmented Generation.",
        },
        {
            "question_id":   str(uuid.uuid4()),
            "question_type": "mcq",
            "question":      "Which vector database is used?",
            "options":       ["A. Pinecone", "B. Weaviate", "C. FAISS", "D. Chroma"],
            "correct_answer": "C",
            "explanation":    "FAISS is used for semantic similarity search.",
        },
    ]


@pytest.fixture
def sample_tf_questions():
    return [
        {
            "question_id":   str(uuid.uuid4()),
            "question_type": "true_false",
            "question":      "DocuChat AI supports multiple question types.",
            "options":       ["True", "False"],
            "correct_answer": "True",
            "explanation":    "It supports MCQ, True/False, and Short Answer.",
        },
    ]


@pytest.fixture
def sample_sa_questions():
    return [
        {
            "question_id":   str(uuid.uuid4()),
            "question_type": "short_answer",
            "question":      "What is the purpose of text chunking?",
            "options":       None,
            "correct_answer": "To split large documents into smaller pieces for retrieval.",
            "explanation":    "Chunking improves retrieval precision.",
        },
    ]


# ─── File fixtures ───────────────────────────────────────────────────────────

@pytest.fixture
def temp_pdf_path():
    """Creates a real 2-page PDF via PyMuPDF."""
    import fitz
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        path = f.name

    doc = fitz.open()
    p1  = doc.new_page()
    p1.insert_text((50, 100), "DocuChat AI Test PDF\nPage one content about RAG systems.")
    p2  = doc.new_page()
    p2.insert_text((50, 100), "Page two content.\nQuiz Mode generates questions automatically.")
    doc.save(path)
    doc.close()

    yield path
    os.unlink(path)


@pytest.fixture
def temp_faiss_dir(tmp_path, sample_chunks, sample_embeddings):
    """Pre-populates a FAISS index on disk for retriever tests."""
    import faiss

    index_dir = tmp_path / FAKE_DOC_ID
    index_dir.mkdir()

    vectors = np.array(sample_embeddings, dtype="float32")
    index   = faiss.IndexFlatL2(EMBEDDING_DIM)
    index.add(vectors)
    faiss.write_index(index, str(index_dir / "index.faiss"))

    with open(index_dir / "chunks.json", "w") as f:
        json.dump(sample_chunks, f)

    return str(tmp_path)


# ─── Mock responses ──────────────────────────────────────────────────────────

@pytest.fixture
def mock_openai_chat_response():
    from unittest.mock import MagicMock
    resp = MagicMock()
    resp.choices[0].message.content = (
        "Quiz Mode automatically generates questions from your document."
    )
    return resp


@pytest.fixture
def mock_openai_embedding_response():
    from unittest.mock import MagicMock
    item           = MagicMock()
    item.embedding = FAKE_EMBEDDING
    resp           = MagicMock()
    resp.data      = [item]
    return resp
