import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from services.pdf_processor import extract_text_from_pdf
from services.chunker import chunk_text
from services.embeddings import generate_embeddings
from services.vector_store import save_vector_store
from core.config import settings
from core.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/")
async def upload_pdf(file: UploadFile = File(...)):
    """
    Accepts a PDF file, extracts text, chunks it,
    generates embeddings, and stores them in FAISS.
    Returns a unique document_id for subsequent chat/quiz calls.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    document_id = str(uuid.uuid4())

    # Save uploaded file temporarily
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(settings.UPLOAD_DIR, f"{document_id}.pdf")

    try:
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        logger.info(f"PDF saved: {file_path}")

        # Pipeline: Extract → Chunk → Embed → Store
        pages = extract_text_from_pdf(file_path)
        chunks = chunk_text(pages)
        logger.info(f"Document split into {len(chunks)} chunks.")

        embeddings = generate_embeddings([c["text"] for c in chunks])
        save_vector_store(document_id, chunks, embeddings)
        logger.info(f"Vector store saved for document_id: {document_id}")

        return JSONResponse(content={
            "document_id": document_id,
            "filename": file.filename,
            "total_chunks": len(chunks),
            "message": "PDF processed successfully."
        })

    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")