"""
test_pdf_processor.py
Tests for services/pdf_processor.py

Covers:
  - Successful multi-page text extraction
  - Empty page skipping
  - Correct page numbering (1-based, sequential)
  - Output schema validation
  - Error handling (missing file, corrupt PDF, non-PDF)
"""

import os
import pytest
import fitz
import tempfile


from services.pdf_processor import extract_text_from_pdf


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _make_pdf(page_texts: list) -> str:
    """Creates a real temporary PDF; empty strings produce blank pages."""
    tmp  = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    path = tmp.name
    tmp.close()

    doc = fitz.open()
    for text in page_texts:
        page = doc.new_page()
        if text:
            page.insert_text((50, 72), text)
    doc.save(path)
    doc.close()
    return path


# ─── Happy path ───────────────────────────────────────────────────────────────

class TestExtractTextFromPDF:

    def test_returns_list(self, temp_pdf_path):
        result = extract_text_from_pdf(temp_pdf_path)
        assert isinstance(result, list)

    def test_correct_page_count(self):
        path = _make_pdf(["Page one.", "Page two.", "Page three."])
        try:
            assert len(extract_text_from_pdf(path)) == 3
        finally:
            os.unlink(path)

    def test_dict_has_page_and_text_keys(self, temp_pdf_path):
        for item in extract_text_from_pdf(temp_pdf_path):
            assert "page" in item and "text" in item

    def test_page_numbers_are_one_based(self):
        path = _make_pdf(["First.", "Second."])
        try:
            pages = [r["page"] for r in extract_text_from_pdf(path)]
            assert pages[0] == 1
            assert pages[1] == 2
        finally:
            os.unlink(path)

    def test_page_numbers_are_sequential(self):
        path = _make_pdf([f"Content {i}." for i in range(5)])
        try:
            pages = [r["page"] for r in extract_text_from_pdf(path)]
            assert pages == sorted(pages)
        finally:
            os.unlink(path)

    def test_text_content_preserved(self):
        path = _make_pdf(["DocuChat AI is a RAG-based assistant."])
        try:
            result = extract_text_from_pdf(path)
            assert "DocuChat" in result[0]["text"]
        finally:
            os.unlink(path)

    def test_text_is_stripped(self):
        path = _make_pdf(["  whitespace  "])
        try:
            for item in extract_text_from_pdf(path):
                assert item["text"] == item["text"].strip()
        finally:
            os.unlink(path)

    def test_multipage_content_all_preserved(self):
        path = _make_pdf([
            "Introduction to RAG systems.",
            "FAISS enables fast vector search.",
            "LangChain orchestrates the pipeline.",
        ])
        try:
            combined = " ".join(r["text"] for r in extract_text_from_pdf(path))
            assert "FAISS"     in combined
            assert "LangChain" in combined
        finally:
            os.unlink(path)

    def test_single_page_pdf(self):
        path = _make_pdf(["Only page."])
        try:
            result = extract_text_from_pdf(path)
            assert len(result) == 1
            assert result[0]["page"] == 1
        finally:
            os.unlink(path)


# ─── Empty / blank page handling ─────────────────────────────────────────────

class TestEmptyPageSkipping:

    def test_blank_pages_skipped(self):
        # Page 1 = text, page 2 = blank, page 3 = text
        path = _make_pdf(["Real content.", "", "More content."])
        try:
            result = extract_text_from_pdf(path)
            assert all(r["text"].strip() != "" for r in result)
        finally:
            os.unlink(path)

    def test_all_blank_returns_empty_list(self):
        path = _make_pdf(["", "", ""])
        try:
            assert extract_text_from_pdf(path) == []
        finally:
            os.unlink(path)

    def test_only_nonempty_pages_counted(self):
        # 3 pages: real, blank, real — expect 2 items
        path = _make_pdf(["Content A.", "", "Content B."])
        try:
            assert len(extract_text_from_pdf(path)) == 2
        finally:
            os.unlink(path)


# ─── Output schema ────────────────────────────────────────────────────────────

class TestOutputSchema:

    def test_page_is_int(self, temp_pdf_path):
        for item in extract_text_from_pdf(temp_pdf_path):
            assert isinstance(item["page"], int)

    def test_text_is_str(self, temp_pdf_path):
        for item in extract_text_from_pdf(temp_pdf_path):
            assert isinstance(item["text"], str)

    def test_no_extra_keys(self, temp_pdf_path):
        for item in extract_text_from_pdf(temp_pdf_path):
            assert set(item.keys()) == {"page", "text"}

    def test_text_never_empty_string(self, temp_pdf_path):
        for item in extract_text_from_pdf(temp_pdf_path):
            assert item["text"] != ""


# ─── Error handling ───────────────────────────────────────────────────────────

class TestErrorHandling:

    def test_missing_file_raises(self):
        with pytest.raises(Exception):
            extract_text_from_pdf("/tmp/__nonexistent__.pdf")

    def test_empty_path_raises(self):
        with pytest.raises(Exception):
            extract_text_from_pdf("")

    def test_non_pdf_extension_raises(self):
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False, mode="w") as f:
            f.write("plain text")
            path = f.name
        try:
            with pytest.raises(Exception):
                extract_text_from_pdf(path)
        finally:
            os.unlink(path)

    def test_corrupted_pdf_raises(self):
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False, mode="wb") as f:
            f.write(b"%PDF-1.4\nGARBAGE!!!")
            path = f.name
        try:
            with pytest.raises(Exception):
                extract_text_from_pdf(path)
        finally:
            os.unlink(path)
