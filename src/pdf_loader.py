"""
PDF download and extraction module.
"""

import os
import logging
import requests
from typing import List, Optional
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


class PDFLoader:
    """Handle PDF download and extraction."""

    def __init__(self, download_dir: str = "data"):
        """
        Initialize PDF loader.

        Args:
            download_dir: Directory to save downloaded PDFs
        """
        self.download_dir = download_dir
        os.makedirs(download_dir, exist_ok=True)

    def download_pdf(
        self,
        url: str,
        filename: Optional[str] = None,
        timeout: int = 60
    ) -> str:
        """
        Download a PDF from URL.

        Args:
            url: URL of the PDF
            filename: Optional custom filename
            timeout: Download timeout in seconds

        Returns:
            Path to downloaded file
        """
        if not filename:
            filename = url.split("/")[-1]
            if not filename.endswith(".pdf"):
                filename += ".pdf"

        filepath = os.path.join(self.download_dir, filename)

        if os.path.exists(filepath):
            logger.info(f"PDF already exists: {filepath}")
            return filepath

        logger.info(f"Downloading PDF from {url}")

        try:
            response = requests.get(url, timeout=timeout, stream=True)
            response.raise_for_status()

            with open(filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            logger.info(f"Downloaded PDF to {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Failed to download PDF from {url}: {e}")
            raise

    def load_pdf(
        self,
        filepath: str,
        metadata: Optional[dict] = None
    ) -> List[Document]:
        """
        Load a PDF file and extract text.

        Args:
            filepath: Path to PDF file
            metadata: Optional metadata to attach to documents

        Returns:
            List of Document objects
        """
        logger.info(f"Loading PDF: {filepath}")

        loader = PyPDFLoader(filepath)
        documents = loader.load()

        if metadata:
            for doc in documents:
                doc.metadata.update(metadata)

        logger.info(f"Extracted {len(documents)} pages from PDF")
        return documents

    def load_from_url(
        self,
        url: str,
        filename: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> List[Document]:
        """
        Download and load a PDF from URL.

        Args:
            url: URL of the PDF
            filename: Optional custom filename
            metadata: Optional metadata to attach

        Returns:
            List of Document objects
        """
        filepath = self.download_pdf(url, filename)
        return self.load_pdf(filepath, metadata)
