import fitz  # PyMuPDF
from typing import List, Dict
from core.logger import get_logger

logger = get_logger(__name__)


def extract_text_from_pdf(file_path: str) -> List[Dict]:
    """
    Extracts text from each page of a PDF.

    Returns:
        List of dicts: [{"page": int, "text": str}, ...]
    """
    pages = []

    try:
        doc = fitz.open(file_path)
        logger.info(f"Opened PDF: {file_path} | Pages: {len(doc)}")

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text").strip()

            if text:  # Skip empty pages
                pages.append({
                    "page": page_num + 1,
                    "text": text
                })

        doc.close()
        logger.info(f"Extracted text from {len(pages)} pages.")

    except Exception as e:
        logger.error(f"PDF extraction failed: {e}")
        raise

    return pages
