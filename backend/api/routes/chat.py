from fastapi import APIRouter, HTTPException
from models.chat import ChatRequest, ChatResponse
from services.chat_service import get_chat_response
from core.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Accepts a user query and document_id.
    Retrieves relevant chunks via FAISS and generates
    a grounded answer with source citations.
    """
    try:
        logger.info(f"Chat request for doc: {request.document_id} | Query: {request.query}")
        response = await get_chat_response(
            document_id=request.document_id,
            query=request.query,
            chat_history=request.chat_history
        )
        return response

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Document not found. Please upload a PDF first.")
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
