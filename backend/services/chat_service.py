from typing import List, Dict, Optional
from openai import AsyncOpenAI
from services.retriever import retrieve_chunks
from models.chat import ChatResponse, Citation, ChatHistoryItem
from core.config import settings
from core.logger import get_logger

logger = get_logger(__name__)
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

SYSTEM_PROMPT = """You are DocuChat AI, an intelligent document assistant.
Answer questions strictly based on the provided document context.
Always cite the specific page numbers where you found the information.
If the answer is not found in the context, say: "I couldn't find that in the document."
Be concise, accurate, and helpful."""


async def get_chat_response(
    document_id: str,
    query: str,
    chat_history: Optional[List[ChatHistoryItem]] = None
) -> ChatResponse:
    """
    Full RAG pipeline:
      1. Retrieve top-K relevant chunks from FAISS
      2. Build a context-aware prompt with citations
      3. Call OpenAI GPT to generate a grounded answer
      4. Return answer + structured source citations

    Args:
        document_id:  The document to query
        query:        The user's question
        chat_history: Previous messages for multi-turn support

    Returns:
        ChatResponse with answer and citations
    """
    # Step 1 — Retrieve relevant chunks
    chunks = retrieve_chunks(document_id, query)

    # Step 2 — Build context string with page references
    context_parts = []
    for i, chunk in enumerate(chunks):
        context_parts.append(f"[Source {i+1} | Page {chunk['page']}]\n{chunk['text']}")
    context = "\n\n".join(context_parts)

    # Step 3 — Build messages with history
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if chat_history:
        for h in chat_history:
            messages.append({"role": h.role, "content": h.content})

    messages.append({
        "role": "user",
        "content": f"Context:\n{context}\n\nQuestion: {query}"
    })

    # Step 4 — Generate answer via LLM
    logger.info(f"Calling LLM for query: '{query[:60]}'")
    response = await client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=messages,
        temperature=0.2,
        max_tokens=800
    )

    answer = response.choices[0].message.content

    # Step 5 — Build citations from retrieved chunks
    citations = [
        Citation(
            chunk_index=c["chunk_index"],
            page=c["page"],
            snippet=c["text"][:200] + "..." if len(c["text"]) > 200 else c["text"]
        )
        for c in chunks
    ]

    logger.info(f"Chat response generated | citations={len(citations)}")
    return ChatResponse(answer=answer, citations=citations)
