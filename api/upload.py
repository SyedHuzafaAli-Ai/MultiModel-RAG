# from fastapi import UploadFile, File, APIRouter
# import shutil
# import os

# #from ingestion.loaders.pdf_loader import load_pdf
# #from ingestion.chunking.text_chunker import chunk_text

# router = APIRouter()

# UPLOAD_DIR = "data/raw"


# @router.post("/upload")
# async def upload_file(file: UploadFile = File(...)):

#     os.makedirs(UPLOAD_DIR, exist_ok=True)

#     file_path = os.path.join(UPLOAD_DIR, file.filename)

#     # Save uploaded file
#     with open(file_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)

#     # Load PDF pages
#     #pages = load_pdf(file_path)

#     #total_chunks = 0

#     #for page in pages:

#         #page_text = page["text"]
#         #page_number = page["page"]

#         #chunks = chunk_text(
#             #text=page_text,
#             #filename=file.filename,
#             #page_number=page_number
#         #)

#         #total_chunks += len(chunks)

#     return {
#         "filename": file.filename,
#         #"chunks_stored": total_chunks,
#         "message": "File uploaded successfully"
#     }

"""
Upload endpoint: save file -> load PDF -> chunk -> embed -> store in Pinecone.
"""

import os
import shutil
import uuid

from fastapi import UploadFile, File, APIRouter, HTTPException

from app.config import settings
from app.logger import get_logger
from ingestion.loaders.pdf_loader import load_pdf
from ingestion.chunking.text_chunker import chunk_text
from retrieval.vector_store import store_chunks

logger = get_logger(__name__)
router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf"}


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        logger.warning(f"Rejected upload with unsupported extension: {file.filename}")
        raise HTTPException(status_code=400, detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(settings.UPLOAD_DIR, file.filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"Saved uploaded file to {file_path}")
    except Exception as e:
        logger.error(f"Failed to save uploaded file {file.filename}: {e}")
        raise HTTPException(status_code=500, detail="Failed to save uploaded file") from e

    try:
        pages = load_pdf(file_path)
    except Exception as e:
        logger.error(f"Failed to load PDF {file.filename}: {e}")
        raise HTTPException(status_code=422, detail=f"Could not read PDF: {e}") from e

    if not pages:
        logger.warning(f"No extractable text found in {file.filename}")
        return {
            "filename": file.filename,
            "chunks_stored": 0,
            "message": "File uploaded but no extractable text was found (it may be a scanned/image-only PDF)."
        }

    document_id = str(uuid.uuid4())
    total_chunks = 0
    failed_pages = []

    for page in pages:
        try:
            chunks = chunk_text(page["text"])
            stored = store_chunks(chunks=chunks, filename=file.filename, page_number=page["page"], document_id=document_id)
            total_chunks += stored
        except Exception as e:
            logger.error(f"Failed to process page {page['page']} of {file.filename}: {e}")
            failed_pages.append(page["page"])

    if total_chunks == 0:
        logger.error(f"No chunks were stored for {file.filename}")
        raise HTTPException(status_code=500, detail="File was read but no chunks could be stored. Check server logs.")

    response = {
        "filename": file.filename,
        "document_id": document_id,
        "pages_processed": len(pages),
        "chunks_stored": total_chunks,
        "message": "File uploaded and indexed successfully"
    }

    if failed_pages:
        response["warning"] = f"Pages {failed_pages} failed to process — see logs"

    logger.info(f"Upload complete: {file.filename} | {total_chunks} chunks | doc_id={document_id}")
    return response