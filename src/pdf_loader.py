"""
Production-grade PDF download and extraction module.
"""

import os
import logging
import requests
from typing import List, Optional
from langchain_community.document_loaders import PyPDFLoader, UnstructuredPDFLoader
from langchain_core.documents import Document
from pypdf import PdfReader

logger = logging.getLogger(**name**)

class PDFLoader:
"""Handle PDF download and extraction."""

```
def __init__(self, download_dir: str = "data"):
    self.download_dir = download_dir
    os.makedirs(download_dir, exist_ok=True)

# ---------- PDF VALIDATION ----------
def _is_valid_pdf(self, path: str) -> bool:
    try:
        PdfReader(path)
        return True
    except Exception as e:
        logger.warning(f"Invalid PDF detected: {path} -> {e}")
        return False

# ---------- DOWNLOAD ----------
def download_pdf(
    self,
    url: str,
    filename: Optional[str] = None,
    timeout: int = 60
) -> str:

    if not filename:
        filename = url.split("/")[-1]
        if not filename.endswith(".pdf"):
            filename += ".pdf"

    filepath = os.path.join(self.download_dir, filename)
    temp_path = filepath + ".tmp"

    if os.path.exists(filepath):
        logger.info(f"PDF already exists: {filepath}")
        return filepath

    logger.info(f"Downloading PDF from {url}")

    try:
        response = requests.get(url, timeout=timeout, stream=True)
        response.raise_for_status()

        # Write to temp file first (IMPORTANT)
        with open(temp_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        # Validate before saving
        if not self._is_valid_pdf(temp_path):
            os.remove(temp_path)
            raise ValueError("Downloaded file is not a valid PDF")

        os.rename(temp_path, filepath)

        logger.info(f"Downloaded PDF to {filepath}")
        return filepath

    except Exception as e:
        logger.error(f"Failed to download PDF from {url}: {e}")
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise

# ---------- LOAD ----------
def load_pdf(
    self,
    filepath: str,
    metadata: Optional[dict] = None
) -> List[Document]:

    logger.info(f"Loading PDF: {filepath}")

    # Try PyPDF first (fast)
    try:
        loader = PyPDFLoader(filepath)
        documents = loader.load()
    except Exception as e:
        logger.warning(f"PyPDF failed, switching to Unstructured: {e}")

        try:
            loader = UnstructuredPDFLoader(filepath)
            documents = loader.load()
        except Exception as e2:
            logger.error(f"Both loaders failed for {filepath}: {e2}")
            return []  # skip corrupted file safely

    if metadata:
        for doc in documents:
            doc.metadata.update(metadata)

    logger.info(f"Extracted {len(documents)} pages from PDF")
    return documents

# ---------- MAIN ----------
def load_from_url(
    self,
    url: str,
    filename: Optional[str] = None,
    metadata: Optional[dict] = None
) -> List[Document]:

    filepath = self.download_pdf(url, filename)
    return self.load_pdf(filepath, metadata)
```
