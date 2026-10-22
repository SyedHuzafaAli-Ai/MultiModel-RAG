# from pypdf import PdfReader

# def load_pdf(file_path):

#     reader = PdfReader(file_path)

#     pages = []

#     for i, page in enumerate(reader.pages):

#         text = page.extract_text()

#         pages.append({
#             "page": i + 1,
#             "text": text
#         })

#     return pages

"""
PDF loading. Extracts text per page.
"""

from pypdf import PdfReader
from pypdf.errors import PdfReadError
from app.logger import get_logger

logger = get_logger(__name__)


def load_pdf(file_path: str) -> list[dict]:
    """
    Returns a list of {"page": int, "text": str} dicts, one per page.
    Pages with no extractable text (e.g. scanned images) are skipped with a warning.
    """
    try:
        reader = PdfReader(file_path)
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except PdfReadError as e:
        logger.error(f"Corrupted or unreadable PDF: {file_path} | {e}")
        raise ValueError(f"Could not read PDF '{file_path}': {e}") from e

    if len(reader.pages) == 0:
        logger.warning(f"PDF has no pages: {file_path}")
        return []

    pages = []
    for i, page in enumerate(reader.pages):
        try:
            text = page.extract_text()
        except Exception as e:
            logger.warning(f"Failed to extract text from page {i + 1} of {file_path}: {e}")
            continue

        if not text or not text.strip():
            logger.warning(f"Page {i + 1} of {file_path} has no extractable text. Skipping.")
            continue

        pages.append({"page": i + 1, "text": text})

    logger.info(f"Loaded {len(pages)}/{len(reader.pages)} pages with text from {file_path}")
    return pages