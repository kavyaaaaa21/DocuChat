"""
test_chunker.py — Tests for services/chunker.py
"""

import pytest
from unittest.mock import patch
from services.chunker import chunk_text


class TestChunkText:

    def test_returns_list(self, sample_pages):
        chunks = chunk_text(sample_pages)
        assert isinstance(chunks, list)

    def test_chunks_are_not_empty(self, sample_pages):
        chunks = chunk_text(sample_pages)
        assert len(chunks) > 0

    def test_chunk_has_required_keys(self, sample_pages):
        """Each chunk must contain text, page, and chunk_index."""
        chunks = chunk_text(sample_pages)
        for chunk in chunks:
            assert "text"        in chunk
            assert "page"        in chunk
            assert "chunk_index" in chunk

    def test_chunk_index_is_sequential(self, sample_pages):
        """chunk_index should start at 0 and increment by 1."""
        chunks = chunk_text(sample_pages)
        for i, chunk in enumerate(chunks):
            assert chunk["chunk_index"] == i

    def test_page_number_is_preserved(self, sample_pages):
        """Each chunk should carry the page number of its source page."""
        chunks = chunk_text(sample_pages)
        page_numbers = {c["page"] for c in chunks}
        source_pages = {p["page"] for p in sample_pages}
        assert page_numbers.issubset(source_pages)

    def test_no_chunk_exceeds_max_size(self, sample_pages):
        """No chunk text should exceed the configured CHUNK_SIZE significantly."""
        with patch("services.chunker.settings") as mock_settings:
            mock_settings.CHUNK_SIZE    = 100
            mock_settings.CHUNK_OVERLAP = 10
            chunks = chunk_text(sample_pages)
            for chunk in chunks:
                # Allow small tolerance for splitter behavior
                assert len(chunk["text"]) <= 200

    def test_chunks_cover_all_text(self, sample_pages):
        """All page text should appear in at least one chunk."""
        chunks = chunk_text(sample_pages)
        all_chunk_text = " ".join(c["text"] for c in chunks)
        for page in sample_pages:
            # At least a meaningful portion of each page is covered
            words = page["text"].split()[:5]
            assert any(w in all_chunk_text for w in words)

    def test_empty_pages_list(self):
        """Should handle an empty pages list without error."""
        chunks = chunk_text([])
        assert chunks == []

    def test_single_page(self):
        """Should correctly chunk a single page."""
        pages = [{"page": 1, "text": "Short text that fits in one chunk."}]
        chunks = chunk_text(pages)
        assert len(chunks) >= 1
        assert chunks[0]["page"] == 1

    def test_whitespace_only_pages_are_skipped(self):
        """Pages with only whitespace should not produce chunks."""
        pages = [
            {"page": 1, "text": "   \n\n\t  "},
            {"page": 2, "text": "Valid content here."},
        ]
        chunks = chunk_text(pages)
        pages_present = {c["page"] for c in chunks}
        assert 1 not in pages_present
        assert 2 in pages_present

    def test_large_document_chunking(self):
        """Should handle a large document with many pages."""
        pages = [
            {"page": i, "text": f"This is content for page {i}. " * 50}
            for i in range(1, 21)
        ]
        chunks = chunk_text(pages)
        assert len(chunks) > 20          # Expect more chunks than pages
        assert all("text" in c for c in chunks)

    def test_chunk_text_is_stripped(self, sample_pages):
        """Chunk texts should have no leading/trailing whitespace."""
        chunks = chunk_text(sample_pages)
        for chunk in chunks:
            assert chunk["text"] == chunk["text"].strip()
