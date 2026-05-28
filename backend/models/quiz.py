from pydantic import BaseModel
from typing import List, Optional, Dict
from enum import Enum


class QuestionType(str, Enum):
    MCQ          = "mcq"
    TRUE_FALSE   = "true_false"
    SHORT_ANSWER = "short_answer"


class Question(BaseModel):
    question_id: str
    question_type: QuestionType
    question: str
    options: Optional[List[str]] = None      # Only for MCQ & True/False
    correct_answer: Optional[str] = None     # Hidden from client on generate
    explanation: Optional[str] = None        # Hidden from client on generate


class QuizGenerateRequest(BaseModel):
    document_id: str
    question_type: QuestionType = QuestionType.MCQ
    num_questions: int = 5
    topic_focus: Optional[str] = None        # e.g. "technical architecture"

    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "550e8400-e29b-41d4-a716-446655440000",
                "question_type": "mcq",
                "num_questions": 5,
                "topic_focus": "RAG pipeline"
            }
        }


class QuizGenerateResponse(BaseModel):
    quiz_id: str
    questions: List[Question]


class QuizSubmitRequest(BaseModel):
    quiz_id: str
    user_answers: Dict[str, str]             # {question_id: answer}

    class Config:
        json_schema_extra = {
            "example": {
                "quiz_id": "abc123",
                "user_answers": {
                    "q1-uuid": "A",
                    "q2-uuid": "True"
                }
            }
        }


class AnswerFeedback(BaseModel):
    question_id: str
    question: str
    user_answer: str
    correct_answer: str
    is_correct: bool
    feedback: str


class QuizSubmitResponse(BaseModel):
    quiz_id: str
    score: int
    total: int
    percentage: float
    feedback: List[AnswerFeedback]
