from fastapi import APIRouter, HTTPException
from models.quiz import (
    QuizGenerateRequest, QuizGenerateResponse,
    QuizSubmitRequest, QuizSubmitResponse
)
from services.quiz_service import generate_quiz, evaluate_quiz
from core.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/generate", response_model=QuizGenerateResponse)
async def generate(request: QuizGenerateRequest):
    """
    Generates a quiz (MCQ / True-False / Short Answer)
    from the uploaded document's content.
    """
    try:
        logger.info(
            f"Quiz generation: doc={request.document_id} | "
            f"type={request.question_type} | count={request.num_questions}"
        )
        result = await generate_quiz(
            document_id=request.document_id,
            question_type=request.question_type,
            num_questions=request.num_questions,
            topic_focus=request.topic_focus
        )
        return result

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Document not found. Please upload a PDF first.")
    except Exception as e:
        logger.error(f"Quiz generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/submit", response_model=QuizSubmitResponse)
async def submit(request: QuizSubmitRequest):
    """
    Accepts user answers, evaluates them, and returns
    a score with detailed per-question feedback.
    """
    try:
        logger.info(f"Quiz submission for quiz_id: {request.quiz_id}")
        result = await evaluate_quiz(
            quiz_id=request.quiz_id,
            user_answers=request.user_answers
        )
        return result

    except Exception as e:
        logger.error(f"Quiz evaluation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))