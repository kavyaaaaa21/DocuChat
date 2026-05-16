import uuid
import json
from typing import List, Dict, Optional
from openai import AsyncOpenAI
from services.retriever import retrieve_chunks
from models.quiz import (
    QuizGenerateResponse, QuizSubmitResponse,
    Question, QuestionType, AnswerFeedback
)
from core.config import settings
from core.logger import get_logger

logger = get_logger(__name__)
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

# In-memory quiz store (swap for Redis/DB in production)
quiz_store: Dict[str, List[Question]] = {}


# ─────────────────────────────────────────────
#  QUIZ GENERATION
# ─────────────────────────────────────────────

def _build_generation_prompt(
    context: str,
    question_type: QuestionType,
    num_questions: int
) -> str:
    type_instructions = {
        QuestionType.MCQ: (
            "Generate multiple choice questions. Each question must have "
            "4 options (A, B, C, D) and one correct answer."
        ),
        QuestionType.TRUE_FALSE: (
            "Generate True/False questions. Each question has two options: "
            "True or False, with one correct answer."
        ),
        QuestionType.SHORT_ANSWER: (
            "Generate short answer questions where the user types a brief response. "
            "Provide a model answer for evaluation."
        ),
    }

    return f"""You are a quiz generator. Based on the document context below, generate {num_questions} 
{question_type.value} questions.

{type_instructions[question_type]}

Return ONLY a valid JSON array (no markdown, no explanation) in this format:
[
  {{
    "question": "...",
    "options": ["A. ...", "B. ...", "C. ...", "D. ..."],   // omit for short_answer
    "correct_answer": "A",
    "explanation": "Brief explanation of the correct answer"
  }}
]

Document Context:
{context}"""


async def generate_quiz(
    document_id: str,
    question_type: QuestionType,
    num_questions: int,
    topic_focus: Optional[str] = None
) -> QuizGenerateResponse:
    """
    Retrieves relevant document chunks and uses LLM to generate
    a structured quiz of the specified type.
    """
    query = topic_focus if topic_focus else "key concepts main ideas important facts"
    chunks = retrieve_chunks(document_id, query, top_k=min(num_questions + 2, 10))

    context = "\n\n".join(
        f"[Page {c['page']}] {c['text']}" for c in chunks
    )

    prompt = _build_generation_prompt(context, question_type, num_questions)

    logger.info(f"Generating {num_questions} {question_type.value} questions for doc={document_id}")

    response = await client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=2000
    )

    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()

    questions_data: List[Dict] = json.loads(raw)

    questions = [
        Question(
            question_id=str(uuid.uuid4()),
            question_type=question_type,
            question=q["question"],
            options=q.get("options"),
            correct_answer=q["correct_answer"],
            explanation=q.get("explanation", "")
        )
        for q in questions_data
    ]

    quiz_id = str(uuid.uuid4())
    # Store questions for evaluation later (hide correct answers from user)
    quiz_store[quiz_id] = questions

    # Return questions without revealing correct answers
    safe_questions = [
        Question(
            question_id=q.question_id,
            question_type=q.question_type,
            question=q.question,
            options=q.options,
            correct_answer=None,   # Hidden from client
            explanation=None
        )
        for q in questions
    ]

    logger.info(f"Quiz generated | quiz_id={quiz_id} | questions={len(questions)}")
    return QuizGenerateResponse(quiz_id=quiz_id, questions=safe_questions)


# ─────────────────────────────────────────────
#  QUIZ EVALUATION
# ─────────────────────────────────────────────

async def evaluate_quiz(
    quiz_id: str,
    user_answers: Dict[str, str]
) -> QuizSubmitResponse:
    """
    Compares user answers against stored correct answers.
    Uses LLM for short answer evaluation.
    Returns a score and per-question feedback.
    """
    if quiz_id not in quiz_store:
        raise ValueError(f"Quiz not found: {quiz_id}")

    questions = quiz_store[quiz_id]
    feedback_list: List[AnswerFeedback] = []
    correct_count = 0

    for question in questions:
        user_answer = user_answers.get(question.question_id, "").strip()
        is_correct = False
        feedback_text = ""

        if question.question_type in (QuestionType.MCQ, QuestionType.TRUE_FALSE):
            # Exact match evaluation
            is_correct = user_answer.upper() == question.correct_answer.upper()
            feedback_text = (
                f"Correct! {question.explanation}"
                if is_correct
                else f"Incorrect. The correct answer is '{question.correct_answer}'. {question.explanation}"
            )

        elif question.question_type == QuestionType.SHORT_ANSWER:
            # LLM-based evaluation for open-ended answers
            eval_prompt = f"""Question: {question.question}
Model Answer: {question.correct_answer}
User Answer: {user_answer}

Evaluate if the user's answer is substantially correct.
Respond in JSON: {{"is_correct": true/false, "feedback": "brief feedback"}}"""

            eval_response = await client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[{"role": "user", "content": eval_prompt}],
                temperature=0.1,
                max_tokens=200
            )
            eval_raw = eval_response.choices[0].message.content.strip()
            eval_raw = eval_raw.replace("```json", "").replace("```", "").strip()
            eval_data = json.loads(eval_raw)
            is_correct = eval_data.get("is_correct", False)
            feedback_text = eval_data.get("feedback", "")

        if is_correct:
            correct_count += 1

        feedback_list.append(AnswerFeedback(
            question_id=question.question_id,
            question=question.question,
            user_answer=user_answer,
            correct_answer=question.correct_answer,
            is_correct=is_correct,
            feedback=feedback_text
        ))

    total = len(questions)
    score_pct = round((correct_count / total) * 100, 1) if total > 0 else 0.0

    logger.info(f"Quiz evaluated | quiz_id={quiz_id} | score={correct_count}/{total} ({score_pct}%)")

    return QuizSubmitResponse(
        quiz_id=quiz_id,
        score=correct_count,
        total=total,
        percentage=score_pct,
        feedback=feedback_list
    )