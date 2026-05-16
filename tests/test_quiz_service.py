"""
test_quiz_service.py
Tests for services/quiz_service.py

Covers:
  - generate_quiz: returns QuizGenerateResponse with quiz_id + questions
  - generate_quiz: correct question count, types, hidden answers
  - generate_quiz: True/False and Short Answer variants
  - evaluate_quiz: correct MCQ scoring
  - evaluate_quiz: True/False scoring
  - evaluate_quiz: short answer uses LLM judge
  - evaluate_quiz: score / percentage calculation
  - evaluate_quiz: per-question feedback structure
  - evaluate_quiz: unknown quiz_id raises ValueError
  - evaluate_quiz: unanswered questions scored as incorrect
"""

import json
import uuid
import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from services.quiz_service import generate_quiz, evaluate_quiz, quiz_store
from models.quiz import (
    QuizGenerateResponse, QuizSubmitResponse,
    Question, QuestionType, AnswerFeedback
)
from conftest import FAKE_DOC_ID


# ─── Helpers ─────────────────────────────────────────────────────────────────

RETRIEVED_CHUNKS = [
    {"text": "RAG stands for Retrieval-Augmented Generation.", "page": 1, "chunk_index": 0, "score": 0.05},
    {"text": "FAISS is used for fast semantic similarity search.", "page": 2, "chunk_index": 2, "score": 0.10},
]


def _llm_mcq_response(num=2):
    questions = []
    for i in range(num):
        questions.append({
            "question":      f"Sample MCQ question {i+1}?",
            "options":       ["A. Option one", "B. Option two", "C. Option three", "D. Option four"],
            "correct_answer": "B",
            "explanation":   "Option two is correct because of X.",
        })
    return MagicMock(**{"choices[0].message.content": json.dumps(questions)})


def _llm_tf_response():
    questions = [{
        "question":      "DocuChat AI supports quiz generation.",
        "options":       ["True", "False"],
        "correct_answer": "True",
        "explanation":   "It explicitly supports quiz generation.",
    }]
    return MagicMock(**{"choices[0].message.content": json.dumps(questions)})


def _llm_sa_response():
    questions = [{
        "question":      "What does RAG stand for?",
        "options":       None,
        "correct_answer": "Retrieval-Augmented Generation",
        "explanation":   "RAG combines retrieval with generation.",
    }]
    return MagicMock(**{"choices[0].message.content": json.dumps(questions)})


def _mock_create(llm_response):
    mock = AsyncMock(return_value=llm_response)
    return mock


# ─── Quiz generation: MCQ ─────────────────────────────────────────────────────

class TestGenerateQuizMCQ:

    @pytest.mark.asyncio
    async def test_returns_quiz_generate_response(self):
        with patch("services.quiz_service.retrieve_chunks", return_value=RETRIEVED_CHUNKS), \
             patch("services.quiz_service.client") as mock_c:
            mock_c.chat.completions.create = _mock_create(_llm_mcq_response(2))
            result = await generate_quiz(FAKE_DOC_ID, QuestionType.MCQ, 2)
        assert isinstance(result, QuizGenerateResponse)

    @pytest.mark.asyncio
    async def test_quiz_id_is_string(self):
        with patch("services.quiz_service.retrieve_chunks", return_value=RETRIEVED_CHUNKS), \
             patch("services.quiz_service.client") as mock_c:
            mock_c.chat.completions.create = _mock_create(_llm_mcq_response(2))
            result = await generate_quiz(FAKE_DOC_ID, QuestionType.MCQ, 2)
        assert isinstance(result.quiz_id, str)
        assert len(result.quiz_id) > 0

    @pytest.mark.asyncio
    async def test_correct_number_of_questions(self):
        with patch("services.quiz_service.retrieve_chunks", return_value=RETRIEVED_CHUNKS), \
             patch("services.quiz_service.client") as mock_c:
            mock_c.chat.completions.create = _mock_create(_llm_mcq_response(3))
            result = await generate_quiz(FAKE_DOC_ID, QuestionType.MCQ, 3)
        assert len(result.questions) == 3

    @pytest.mark.asyncio
    async def test_correct_answers_hidden_from_response(self):
        """Client must NOT receive correct_answer or explanation."""
        with patch("services.quiz_service.retrieve_chunks", return_value=RETRIEVED_CHUNKS), \
             patch("services.quiz_service.client") as mock_c:
            mock_c.chat.completions.create = _mock_create(_llm_mcq_response(2))
            result = await generate_quiz(FAKE_DOC_ID, QuestionType.MCQ, 2)
        for q in result.questions:
            assert q.correct_answer is None
            assert q.explanation    is None

    @pytest.mark.asyncio
    async def test_questions_stored_in_quiz_store(self):
        with patch("services.quiz_service.retrieve_chunks", return_value=RETRIEVED_CHUNKS), \
             patch("services.quiz_service.client") as mock_c:
            mock_c.chat.completions.create = _mock_create(_llm_mcq_response(2))
            result = await generate_quiz(FAKE_DOC_ID, QuestionType.MCQ, 2)
        assert result.quiz_id in quiz_store
        assert len(quiz_store[result.quiz_id]) == 2

    @pytest.mark.asyncio
    async def test_stored_questions_have_correct_answers(self):
        with patch("services.quiz_service.retrieve_chunks", return_value=RETRIEVED_CHUNKS), \
             patch("services.quiz_service.client") as mock_c:
            mock_c.chat.completions.create = _mock_create(_llm_mcq_response(2))
            result = await generate_quiz(FAKE_DOC_ID, QuestionType.MCQ, 2)
        for q in quiz_store[result.quiz_id]:
            assert q.correct_answer is not None

    @pytest.mark.asyncio
    async def test_each_question_has_question_id(self):
        with patch("services.quiz_service.retrieve_chunks", return_value=RETRIEVED_CHUNKS), \
             patch("services.quiz_service.client") as mock_c:
            mock_c.chat.completions.create = _mock_create(_llm_mcq_response(2))
            result = await generate_quiz(FAKE_DOC_ID, QuestionType.MCQ, 2)
        for q in result.questions:
            assert q.question_id is not None and q.question_id != ""

    @pytest.mark.asyncio
    async def test_each_question_has_options(self):
        with patch("services.quiz_service.retrieve_chunks", return_value=RETRIEVED_CHUNKS), \
             patch("services.quiz_service.client") as mock_c:
            mock_c.chat.completions.create = _mock_create(_llm_mcq_response(2))
            result = await generate_quiz(FAKE_DOC_ID, QuestionType.MCQ, 2)
        for q in result.questions:
            assert isinstance(q.options, list)
            assert len(q.options) == 4


# ─── Quiz generation: True / False ────────────────────────────────────────────

class TestGenerateQuizTrueFalse:

    @pytest.mark.asyncio
    async def test_tf_questions_have_two_options(self):
        with patch("services.quiz_service.retrieve_chunks", return_value=RETRIEVED_CHUNKS), \
             patch("services.quiz_service.client") as mock_c:
            mock_c.chat.completions.create = _mock_create(_llm_tf_response())
            result = await generate_quiz(FAKE_DOC_ID, QuestionType.TRUE_FALSE, 1)
        for q in result.questions:
            assert len(q.options) == 2

    @pytest.mark.asyncio
    async def test_tf_options_are_true_and_false(self):
        with patch("services.quiz_service.retrieve_chunks", return_value=RETRIEVED_CHUNKS), \
             patch("services.quiz_service.client") as mock_c:
            mock_c.chat.completions.create = _mock_create(_llm_tf_response())
            result = await generate_quiz(FAKE_DOC_ID, QuestionType.TRUE_FALSE, 1)
        for q in result.questions:
            assert set(q.options) == {"True", "False"}


# ─── Quiz generation: Short Answer ────────────────────────────────────────────

class TestGenerateQuizShortAnswer:

    @pytest.mark.asyncio
    async def test_sa_questions_have_no_options(self):
        with patch("services.quiz_service.retrieve_chunks", return_value=RETRIEVED_CHUNKS), \
             patch("services.quiz_service.client") as mock_c:
            mock_c.chat.completions.create = _mock_create(_llm_sa_response())
            result = await generate_quiz(FAKE_DOC_ID, QuestionType.SHORT_ANSWER, 1)
        for q in result.questions:
            assert q.options is None or q.options == []


# ─── Quiz evaluation: MCQ ─────────────────────────────────────────────────────

class TestEvaluateQuizMCQ:

    @pytest.fixture(autouse=True)
    async def _setup(self):
        """Injects two MCQ questions directly into quiz_store."""
        self.q1_id = str(uuid.uuid4())
        self.q2_id = str(uuid.uuid4())
        self.quiz_id = str(uuid.uuid4())

        quiz_store[self.quiz_id] = [
            Question(
                question_id=self.q1_id,
                question_type=QuestionType.MCQ,
                question="What is FAISS?",
                options=["A. Fuzzy AI", "B. Facebook AI Similarity Search",
                         "C. Fast API", "D. None"],
                correct_answer="B",
                explanation="FAISS is Facebook AI Similarity Search."
            ),
            Question(
                question_id=self.q2_id,
                question_type=QuestionType.MCQ,
                question="What does RAG stand for?",
                options=["A. Random", "B. Rapid", "C. Retrieval-Augmented Generation", "D. None"],
                correct_answer="C",
                explanation="Retrieval-Augmented Generation."
            ),
        ]

    @pytest.mark.asyncio
    async def test_perfect_score_both_correct(self):
        result = await evaluate_quiz(
            self.quiz_id,
            {self.q1_id: "B", self.q2_id: "C"}
        )
        assert result.score == 2
        assert result.total == 2
        assert result.percentage == 100.0

    @pytest.mark.asyncio
    async def test_zero_score_both_wrong(self):
        result = await evaluate_quiz(
            self.quiz_id,
            {self.q1_id: "A", self.q2_id: "A"}
        )
        assert result.score == 0
        assert result.percentage == 0.0

    @pytest.mark.asyncio
    async def test_partial_score(self):
        result = await evaluate_quiz(
            self.quiz_id,
            {self.q1_id: "B", self.q2_id: "A"}   # 1 correct, 1 wrong
        )
        assert result.score == 1
        assert result.percentage == 50.0

    @pytest.mark.asyncio
    async def test_returns_quiz_submit_response(self):
        result = await evaluate_quiz(self.quiz_id, {self.q1_id: "B", self.q2_id: "C"})
        assert isinstance(result, QuizSubmitResponse)

    @pytest.mark.asyncio
    async def test_feedback_count_matches_question_count(self):
        result = await evaluate_quiz(self.quiz_id, {self.q1_id: "B", self.q2_id: "C"})
        assert len(result.feedback) == 2

    @pytest.mark.asyncio
    async def test_feedback_items_are_answer_feedback(self):
        result = await evaluate_quiz(self.quiz_id, {self.q1_id: "B", self.q2_id: "C"})
        for fb in result.feedback:
            assert isinstance(fb, AnswerFeedback)

    @pytest.mark.asyncio
    async def test_correct_is_correct_field_true(self):
        result = await evaluate_quiz(self.quiz_id, {self.q1_id: "B", self.q2_id: "C"})
        for fb in result.feedback:
            assert fb.is_correct is True

    @pytest.mark.asyncio
    async def test_wrong_answer_is_correct_field_false(self):
        result = await evaluate_quiz(self.quiz_id, {self.q1_id: "X", self.q2_id: "X"})
        for fb in result.feedback:
            assert fb.is_correct is False

    @pytest.mark.asyncio
    async def test_feedback_includes_correct_answer_when_wrong(self):
        result = await evaluate_quiz(self.quiz_id, {self.q1_id: "A", self.q2_id: "A"})
        for fb in result.feedback:
            assert fb.correct_answer in ("B", "C")

    @pytest.mark.asyncio
    async def test_unanswered_question_counted_as_wrong(self):
        result = await evaluate_quiz(self.quiz_id, {})   # no answers provided
        assert result.score == 0

    @pytest.mark.asyncio
    async def test_case_insensitive_matching(self):
        result = await evaluate_quiz(self.quiz_id, {self.q1_id: "b", self.q2_id: "c"})
        assert result.score == 2

    @pytest.mark.asyncio
    async def test_percentage_is_float(self):
        result = await evaluate_quiz(self.quiz_id, {self.q1_id: "B", self.q2_id: "C"})
        assert isinstance(result.percentage, float)

    @pytest.mark.asyncio
    async def test_quiz_id_echoed_in_response(self):
        result = await evaluate_quiz(self.quiz_id, {self.q1_id: "B", self.q2_id: "C"})
        assert result.quiz_id == self.quiz_id


# ─── Quiz evaluation: True / False ───────────────────────────────────────────

class TestEvaluateQuizTrueFalse:

    @pytest.fixture(autouse=True)
    async def _setup(self):
        self.q_id    = str(uuid.uuid4())
        self.quiz_id = str(uuid.uuid4())
        quiz_store[self.quiz_id] = [
            Question(
                question_id=self.q_id,
                question_type=QuestionType.TRUE_FALSE,
                question="DocuChat AI supports quiz generation.",
                options=["True", "False"],
                correct_answer="True",
                explanation="Yes, it supports quiz generation."
            )
        ]

    @pytest.mark.asyncio
    async def test_true_answer_correct(self):
        result = await evaluate_quiz(self.quiz_id, {self.q_id: "True"})
        assert result.score == 1

    @pytest.mark.asyncio
    async def test_false_answer_wrong(self):
        result = await evaluate_quiz(self.quiz_id, {self.q_id: "False"})
        assert result.score == 0


# ─── Quiz evaluation: Short Answer (LLM judge) ───────────────────────────────

class TestEvaluateQuizShortAnswer:

    @pytest.fixture(autouse=True)
    async def _setup(self):
        self.q_id    = str(uuid.uuid4())
        self.quiz_id = str(uuid.uuid4())
        quiz_store[self.quiz_id] = [
            Question(
                question_id=self.q_id,
                question_type=QuestionType.SHORT_ANSWER,
                question="What does RAG stand for?",
                options=None,
                correct_answer="Retrieval-Augmented Generation",
                explanation="RAG = Retrieval-Augmented Generation."
            )
        ]

    @pytest.mark.asyncio
    async def test_correct_sa_answer_scored_by_llm(self):
        eval_resp = MagicMock()
        eval_resp.choices[0].message.content = json.dumps(
            {"is_correct": True, "feedback": "Great answer!"}
        )
        with patch("services.quiz_service.client") as mock_c:
            mock_c.chat.completions.create = AsyncMock(return_value=eval_resp)
            result = await evaluate_quiz(self.quiz_id, {self.q_id: "Retrieval-Augmented Generation"})
        assert result.score == 1

    @pytest.mark.asyncio
    async def test_wrong_sa_answer_scored_by_llm(self):
        eval_resp = MagicMock()
        eval_resp.choices[0].message.content = json.dumps(
            {"is_correct": False, "feedback": "Incorrect. The answer is Retrieval-Augmented Generation."}
        )
        with patch("services.quiz_service.client") as mock_c:
            mock_c.chat.completions.create = AsyncMock(return_value=eval_resp)
            result = await evaluate_quiz(self.quiz_id, {self.q_id: "Random guess"})
        assert result.score == 0


# ─── Error handling ───────────────────────────────────────────────────────────

class TestQuizServiceErrors:

    @pytest.mark.asyncio
    async def test_unknown_quiz_id_raises_value_error(self):
        with pytest.raises(ValueError, match="Quiz not found"):
            await evaluate_quiz("nonexistent-quiz-id", {})

    @pytest.mark.asyncio
    async def test_retriever_failure_propagates_on_generate(self):
        with patch("services.quiz_service.retrieve_chunks",
                   side_effect=FileNotFoundError("No index")):
            with pytest.raises(FileNotFoundError):
                await generate_quiz(FAKE_DOC_ID, QuestionType.MCQ, 3)

    @pytest.mark.asyncio
    async def test_llm_json_parse_failure_propagates(self):
        bad_resp = MagicMock()
        bad_resp.choices[0].message.content = "NOT VALID JSON {{{"

        with patch("services.quiz_service.retrieve_chunks", return_value=RETRIEVED_CHUNKS), \
             patch("services.quiz_service.client") as mock_c:
            mock_c.chat.completions.create = AsyncMock(return_value=bad_resp)
            with pytest.raises(Exception):
                await generate_quiz(FAKE_DOC_ID, QuestionType.MCQ, 2)
