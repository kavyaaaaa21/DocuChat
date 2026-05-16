from typing import List, Dict
from langchain.text_splitter import RecursiveCharacterTextSplitter
from core.config import settings
from core.logger import get_logger

logger = get_logger(__name__)


def chunk_text(pages: List[Dict]) -> List[Dict]:
    """
    Splits page text into overlapping chunks for retrieval.

    Args:
        pages: Output from pdf_processor — list of {page, text}

    Returns:
        List of chunks: [{text, page, chunk_index}, ...]
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " ", ""]
    )

    all_chunks = []
    chunk_index = 0

    for page_data in pages:
        page_num = page_data["page"]
        page_text = page_data["text"]

        splits = splitter.split_text(page_text)

        for split in splits:
            if split.strip():
                all_chunks.append({
                    "text": split.strip(),
                    "page": page_num,
                    "chunk_index": chunk_index
                })
                chunk_index += 1

    logger.info(
        f"Chunking complete | chunks={len(all_chunks)} | "
        f"size={settings.CHUNK_SIZE} | overlap={settings.CHUNK_OVERLAP}"
    )
    return all_chunks
