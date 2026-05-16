"""
test_routes.py — Integration tests for all three API routes.
Uses FastAPI's TestClient to test HTTP behaviour end-to-end.
"""

import io
import json
import uuid
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient

# Add backend to path so imports resolve correctly
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from main import app
from conftest import FAKE_DOCUMENT_ID, FAKE_QUIZ_ID

client = TestClient(app)


# ─────────────────────────────────────────────
#  HELPER
# ─────────────────────────────────────────────

def fake_pdf_bytes():
    """Returns minimal PDF bytes for upload testing."""
    import fitz
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 100), "Test content for DocuChat AI.")
    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf.read()


# ─────────────────────────────────────────────
#  UPLOAD ROUTE TESTS
# ─────────────────────────────────────────────

class TestUploadRoute:

    @patch("api.routes.upload.save_vector_store")
    @patch("api.routes.upload.generate_embeddings")
    @patch("api.routes.upload.chunk_text")
    @patch("api.routes.upload.extract_text_from_pdf")
    def test_upload_success(self, mock_extract, mock_chunk, mock_embed, mock_save):
        mock_extract.return_value = [{"page": 1, "text": "Content."}]
        mock_chunk.return_value   = [{"text": "Content.", "page": 1, "chunk_index": 0}]
        mock_embed.return_value   = [[0.1] * 1536]
        mock_save.return_value    = None

        response = client.post(
            "/api/upload/",
            files={"file": ("test.pdf", fake_pdf_bytes(), "application/pdf")}
        )
        assert response.status_code == 200
        data = response.json()
        assert "document_id" in data
        assert data["total_chunks"] == 1
        assert data["filename"] == "test.pdf"

    def test_upload_rejects_non_pdf(self):
        response = client.post(
            "/api/upload/",
            files={"file": ("doc.txt", b"hello world", "text/plain")}
        )
        assert response.status_code == 400
        assert "PDF" in response.json()["detail"]

    @patch("api.routes.upload.extract_text_from_pdf", side_effect=Exception("Read error"))
    def test_upload_returns_500_on_processing_error(self, _):
        response = client.post(
            "/api/upload/",
            files={"file": ("test.pdf", fake_pdf_bytes(), "application/pdf")}
        )
        assert response.status_code == 500

    @patch("api.routes.upload.save_vector_store")
    @patch("api.routes.upload.generate_embeddings")
    @patch("api.routes.upload.chunk_text")
    @patch("api.routes.upload.extract_text_from_pdf")
    def test_upload_returns_unique_document_ids(self, mock_extract, mock_chunk, mock_embed, mock_save):
        mock_extract.return_value = [{"page": 1, "text": "Content."}]
        mock_chunk.return_value   = [{"text": "Content.", "page": 1, "chunk_index": 0}]
        mock_embed.return_value   = [[0.1] * 1536]
        mock_save.return_value    = None

        r1 = client.post("/api/upload/", files={"file": ("a.pdf", fake_pdf_bytes(), "application/pdf")})
        r2 = client.post("/api/upload/", files={"file": ("b.pdf", fake_pdf_bytes(), "application/pdf")})

        assert r1.json()["document_id"] != r2.json()["document_id"]


# ─────────────────────────────────────────────
#  CHAT ROUTE TESTS
# ─────────────────────────────────────────────

class TestChatRoute:

    @patch("api.routes.chat.get_chat_response", new_callable=AsyncMock)
    def test_chat_success(self, mock_chat):
        from models.chat import ChatResponse, Citation
        mock_chat.return_value = ChatResponse(
            answer="Quiz mode generates questions.",
            citations=[Citation(chunk_index=0, page=1, snippet="Quiz mode...")]
        )

        response = client.post("/api/chat/", json={
            "document_id": FAKE_DOCUMENT_ID,
            "query": "What is quiz mode?"
        })
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "citations" in data
        assert len(data["citations"]) == 1

    @patch("api.routes.chat.get_chat_response", new_callable=AsyncMock)
    def test_chat_returns_404_on_missing_doc(self, mock_chat):
        mock_chat.side_effect = FileNotFoundError("No index found.")

        response = client.post("/api/chat/", json={
            "document_id": "non-existent",
            "query": "Anything?"
        })
        assert response.status_code == 404

    @patch("api.routes.chat.get_chat_response", new_callable=AsyncMock)
    def test_chat_returns_500_on_error(self, mock_chat):
        mock_chat.side_effect = RuntimeError("LLM timeout.")

        response = client.post("/api/chat/", json={
            "document_id": FAKE_DOCUMENT_ID,
            "query": "Anything?"
        })
        assert response.status_code == 500

    def test_chat_missing_query_returns_422(self):
        response = client.post("/api/chat/", json={"document_id": FAKE_DOCUMENT_ID})
        assert response.status_code == 422

    def test_chat_missing_document_id_returns_422(self):
        response = client.post("/api/chat/", json={"query": "hello?"})
        assert response.status_code == 422

    @patch("api.routes.chat.get_chat_response", new_callable=AsyncMock)
    def test_chat_with_history(self, mock_chat):
        from models.chat import ChatResponse, Citation
        mock_chat.return_value = ChatResponse(answer="Follow-up answer.", citations=[])

        response = client.post("/api/chat/", json={
            "document_id": FAKE_DOCUMENT_ID,
            "query": "Follow up?",
            "chat_history": [
                {"role": "user",      "content": "What is DocuChat?"},
                {"role": "assistant", "content": "It is a PDF assistant."}
            ]
        })
        assert response.status_code == 200


# ─────────────────────────────────────────────
#  QUIZ ROUTE TESTS
# ─────────────────────────────────────────────

class TestQuizRoute:

    @patch("api.routes.quiz.generate_quiz", new_callable=AsyncMock)
    def test_generate_quiz_success(self, mock_gen):
        from models.quiz import QuizGenerateResponse, Question, QuestionType
        mock_gen.return_value = QuizGenerateResponse(
            quiz_id=FAKE_QUIZ_ID,
            questions=[
                Question(
                    question_id=str(uuid.uuid4()),
                    question_type=QuestionType.MCQ,
                    question="What is FAISS?",
                    options=["A. Framework", "B. Vector DB library", "C. API", "D. LLM"],
                    correct_answer=None,
                    explanation=None
                )
            ]
        )

        response = client.post("/api/quiz/generate", json={
            "document_id": FAKE_DOCUMENT_ID,
            "question_type": "mcq",
            "num_questions": 1
        })
        assert response.status_code == 200
        data = response.json()
        assert "quiz_id" in data
        assert len(data["questions"]) == 1
        assert data["questions"][0]["correct_answer"] is None

    @patch("api.routes.quiz.generate_quiz", new_callable=AsyncMock)
    def test_generate_returns_404_on_missing_doc(self, mock_gen):
        mock_gen.side_effect = FileNotFoundError("No index.")

        response = client.post("/api/quiz/generate", json={
            "document_id": "bad-id",
            "question_type": "mcq",
            "num_questions": 3
        })
        assert response.status_code == 404

    @patch("api.routes.quiz.evaluate_quiz", new_callable=AsyncMock)
    def test_submit_quiz_success(self, mock_eval):
        from models.quiz import QuizSubmitResponse, AnswerFeedback
        qid = str(uuid.uuid4())
        mock_eval.return_value = QuizSubmitResponse(
            quiz_id=FAKE_QUIZ_ID,
            score=1,
            total=1,
            percentage=100.0,
            feedback=[
                AnswerFeedback(
                    question_id=qid,
                    question="What is FAISS?",
                    user_answer="B",
                    correct_answer="B",
                    is_correct=True,
                    feedback="Correct! FAISS is a vector DB library."
                )
            ]
        )

        response = client.post("/api/quiz/submit", json={
            "quiz_id": FAKE_QUIZ_ID,
            "user_answers": {qid: "B"}
        })
        assert response.status_code == 200
        data = response.json()
        assert data["score"]      == 1
        assert data["total"]      == 1
        assert data["percentage"] == 100.0
        assert data["feedback"][0]["is_correct"] is True

    @patch("api.routes.quiz.evaluate_quiz", new_callable=AsyncMock)
    def test_submit_returns_500_on_invalid_quiz(self, mock_eval):
        mock_eval.side_effect = ValueError("Quiz not found: bad-quiz")

        response = client.post("/api/quiz/submit", json={
            "quiz_id": "bad-quiz",
            "user_answers": {}
        })
        assert response.status_code == 500

    def test_generate_missing_document_id_returns_422(self):
        response = client.post("/api/quiz/generate", json={
            "question_type": "mcq",
            "num_questions": 3
        })
        assert response.status_code == 422

    @patch("api.routes.quiz.generate_quiz", new_callable=AsyncMock)
    def test_generate_with_topic_focus(self, mock_gen):
        from models.quiz import QuizGenerateResponse
        mock_gen.return_value = QuizGenerateResponse(quiz_id=FAKE_QUIZ_ID, questions=[])

        response = client.post("/api/quiz/generate", json={
            "document_id": FAKE_DOCUMENT_ID,
            "question_type": "true_false",
            "num_questions": 2,
            "topic_focus": "RAG pipeline"
        })
        assert response.status_code == 200
        _, kwargs = mock_gen.call_args
        assert kwargs.get("topic_focus") == "RAG pipeline"


# ─────────────────────────────────────────────
#  ROOT ENDPOINT
# ─────────────────────────────────────────────

def test_root_returns_ok():
    response = client.get("/")
    assert response.status_code == 200
    assert "DocuChat" in response.json()["message"]
