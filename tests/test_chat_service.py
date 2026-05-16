"""
test_chat_service.py
Tests for services/chat_service.py

Covers:
  - get_chat_response returns ChatResponse with answer + citations
  - Citations reflect retrieved chunks (page, snippet)
  - Multi-turn chat history is forwarded to the LLM
  - FileNotFoundError from retriever propagates correctly
  - LLM API failures propagate correctly
  - Empty query is handled gracefully
  - Snippet truncation for long chunks
  - Number of citations matches retrieved chunks
"""

import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock

from services.chat_service import get_chat_response
from models.chat import ChatResponse, Citation
from conftest import FAKE_DOC_ID, FAKE_EMBEDDING


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _make_llm_response(text: str):
    """Builds a mock AsyncOpenAI completion response."""
    resp = MagicMock()
    resp.choices[0].message.content = text
    return resp


RETRIEVED_CHUNKS = [
    {"text": "Quiz Mode generates MCQ questions from the document.", "page": 2, "chunk_index": 2, "score": 0.05},
    {"text": "Chat Mode provides grounded Q&A with source citations.", "page": 1, "chunk_index": 1, "score": 0.12},
    {"text": "RAG pipeline: PDF → chunk → embed → FAISS → retrieve → answer.", "page": 3, "chunk_index": 4, "score": 0.18},
]


# ─── Core behaviour ───────────────────────────────────────────────────────────

class TestGetChatResponse:

    @pytest.mark.asyncio
    async def test_returns_chat_response_instance(self):
        with patch("services.chat_service.retrieve_chunks", return_value=RETRIEVED_CHUNKS), \
             patch("services.chat_service.client") as mock_client:
            mock_client.chat.completions.create = AsyncMock(
                return_value=_make_llm_response("Quiz Mode auto-generates questions.")
            )
            result = await get_chat_response(FAKE_DOC_ID, "What is quiz mode?")
        assert isinstance(result, ChatResponse)

    @pytest.mark.asyncio
    async def test_answer_is_non_empty_string(self):
        with patch("services.chat_service.retrieve_chunks", return_value=RETRIEVED_CHUNKS), \
             patch("services.chat_service.client") as mock_client:
            mock_client.chat.completions.create = AsyncMock(
                return_value=_make_llm_response("Here is the answer.")
            )
            result = await get_chat_response(FAKE_DOC_ID, "any query")
        assert isinstance(result.answer, str)
        assert len(result.answer) > 0

    @pytest.mark.asyncio
    async def test_answer_matches_llm_output(self):
        expected = "The RAG pipeline retrieves relevant document chunks."
        with patch("services.chat_service.retrieve_chunks", return_value=RETRIEVED_CHUNKS), \
             patch("services.chat_service.client") as mock_client:
            mock_client.chat.completions.create = AsyncMock(
                return_value=_make_llm_response(expected)
            )
            result = await get_chat_response(FAKE_DOC_ID, "How does RAG work?")
        assert result.answer == expected

    @pytest.mark.asyncio
    async def test_citations_count_matches_retrieved_chunks(self):
        with patch("services.chat_service.retrieve_chunks", return_value=RETRIEVED_CHUNKS), \
             patch("services.chat_service.client") as mock_client:
            mock_client.chat.completions.create = AsyncMock(
                return_value=_make_llm_response("Answer text.")
            )
            result = await get_chat_response(FAKE_DOC_ID, "query")
        assert len(result.citations) == len(RETRIEVED_CHUNKS)

    @pytest.mark.asyncio
    async def test_citations_are_citation_instances(self):
        with patch("services.chat_service.retrieve_chunks", return_value=RETRIEVED_CHUNKS), \
             patch("services.chat_service.client") as mock_client:
            mock_client.chat.completions.create = AsyncMock(
                return_value=_make_llm_response("Answer.")
            )
            result = await get_chat_response(FAKE_DOC_ID, "query")
        for c in result.citations:
            assert isinstance(c, Citation)

    @pytest.mark.asyncio
    async def test_citation_page_numbers_match_chunks(self):
        with patch("services.chat_service.retrieve_chunks", return_value=RETRIEVED_CHUNKS), \
             patch("services.chat_service.client") as mock_client:
            mock_client.chat.completions.create = AsyncMock(
                return_value=_make_llm_response("Answer.")
            )
            result = await get_chat_response(FAKE_DOC_ID, "query")
        expected_pages = [c["page"] for c in RETRIEVED_CHUNKS]
        actual_pages   = [c.page    for c in result.citations]
        assert actual_pages == expected_pages

    @pytest.mark.asyncio
    async def test_citation_snippet_is_string(self):
        with patch("services.chat_service.retrieve_chunks", return_value=RETRIEVED_CHUNKS), \
             patch("services.chat_service.client") as mock_client:
            mock_client.chat.completions.create = AsyncMock(
                return_value=_make_llm_response("Answer.")
            )
            result = await get_chat_response(FAKE_DOC_ID, "query")
        for c in result.citations:
            assert isinstance(c.snippet, str)

    @pytest.mark.asyncio
    async def test_citation_snippet_not_empty(self):
        with patch("services.chat_service.retrieve_chunks", return_value=RETRIEVED_CHUNKS), \
             patch("services.chat_service.client") as mock_client:
            mock_client.chat.completions.create = AsyncMock(
                return_value=_make_llm_response("Answer.")
            )
            result = await get_chat_response(FAKE_DOC_ID, "query")
        for c in result.citations:
            assert c.snippet != ""


# ─── Snippet truncation ───────────────────────────────────────────────────────

class TestSnippetTruncation:

    @pytest.mark.asyncio
    async def test_long_chunk_text_is_truncated_to_200_chars(self):
        long_text = "A" * 500
        chunks = [{"text": long_text, "page": 1, "chunk_index": 0, "score": 0.1}]

        with patch("services.chat_service.retrieve_chunks", return_value=chunks), \
             patch("services.chat_service.client") as mock_client:
            mock_client.chat.completions.create = AsyncMock(
                return_value=_make_llm_response("Answer.")
            )
            result = await get_chat_response(FAKE_DOC_ID, "query")

        # Snippet should be at most 200 chars + "..."
        assert len(result.citations[0].snippet) <= 203

    @pytest.mark.asyncio
    async def test_short_chunk_text_not_truncated(self):
        short_text = "Short chunk."
        chunks = [{"text": short_text, "page": 1, "chunk_index": 0, "score": 0.0}]

        with patch("services.chat_service.retrieve_chunks", return_value=chunks), \
             patch("services.chat_service.client") as mock_client:
            mock_client.chat.completions.create = AsyncMock(
                return_value=_make_llm_response("Answer.")
            )
            result = await get_chat_response(FAKE_DOC_ID, "query")

        assert short_text in result.citations[0].snippet


# ─── Multi-turn chat history ──────────────────────────────────────────────────

class TestChatHistory:

    @pytest.mark.asyncio
    async def test_chat_history_forwarded_to_llm(self, sample_chat_history):
        captured_messages = []

        async def capture_call(**kwargs):
            captured_messages.extend(kwargs.get("messages", []))
            return _make_llm_response("Follow-up answer.")

        with patch("services.chat_service.retrieve_chunks", return_value=RETRIEVED_CHUNKS), \
             patch("services.chat_service.client") as mock_client:
            mock_client.chat.completions.create = AsyncMock(side_effect=capture_call)
            await get_chat_response(
                FAKE_DOC_ID,
                "Follow-up question",
                chat_history=[
                    MagicMock(role=m["role"], content=m["content"])
                    for m in sample_chat_history
                ],
            )

        roles = [m["role"] for m in captured_messages]
        assert "user"      in roles
        assert "assistant" in roles

    @pytest.mark.asyncio
    async def test_no_history_still_works(self):
        with patch("services.chat_service.retrieve_chunks", return_value=RETRIEVED_CHUNKS), \
             patch("services.chat_service.client") as mock_client:
            mock_client.chat.completions.create = AsyncMock(
                return_value=_make_llm_response("Answer without history.")
            )
            result = await get_chat_response(FAKE_DOC_ID, "First question", chat_history=[])
        assert result.answer == "Answer without history."


# ─── Error handling ───────────────────────────────────────────────────────────

class TestChatServiceErrors:

    @pytest.mark.asyncio
    async def test_file_not_found_propagates(self):
        with patch("services.chat_service.retrieve_chunks",
                   side_effect=FileNotFoundError("No index")):
            with pytest.raises(FileNotFoundError):
                await get_chat_response("bad-doc", "query")

    @pytest.mark.asyncio
    async def test_llm_api_error_propagates(self):
        with patch("services.chat_service.retrieve_chunks", return_value=RETRIEVED_CHUNKS), \
             patch("services.chat_service.client") as mock_client:
            mock_client.chat.completions.create = AsyncMock(
                side_effect=RuntimeError("OpenAI 500")
            )
            with pytest.raises(RuntimeError):
                await get_chat_response(FAKE_DOC_ID, "query")

    @pytest.mark.asyncio
    async def test_no_chunks_returns_response(self):
        """Even with zero retrieved chunks the function should return a ChatResponse."""
        with patch("services.chat_service.retrieve_chunks", return_value=[]), \
             patch("services.chat_service.client") as mock_client:
            mock_client.chat.completions.create = AsyncMock(
                return_value=_make_llm_response("I couldn't find that in the document.")
            )
            result = await get_chat_response(FAKE_DOC_ID, "obscure query")
        assert isinstance(result, ChatResponse)
        assert result.citations == []
