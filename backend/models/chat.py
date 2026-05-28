
from pydantic import BaseModel
from typing import List, Optional, Literal


class ChatHistoryItem(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    document_id: str
    query: str
    chat_history: Optional[List[ChatHistoryItem]] = []

    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "550e8400-e29b-41d4-a716-446655440000",
                "query": "What is the quiz mode?",
                "chat_history": []
            }
        }


class Citation(BaseModel):
    chunk_index: int
    page: int
    snippet: str


class ChatResponse(BaseModel):
    answer: str
    citations: List[Citation]

    class Config:
        json_schema_extra = {
            "example": {
                "answer": "The quiz mode generates context-aware questions from your document...",
                "citations": [
                    {
                        "chunk_index": 3,
                        "page": 2,
                        "snippet": "Quiz Mode allows automatic quiz generation..."
                    }
                ]
            }
        }
