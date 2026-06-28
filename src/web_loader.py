"""
Web content loader using requests and BeautifulSoup.
"""

import logging
import requests
from typing import Dict, Optional
from bs4 import BeautifulSoup
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


class WebLoader:
    """Load and clean web content."""

    def __init__(self):
        """Initialize web loader."""
        pass

    def clean_html(self, html: str) -> str:
        """
        Clean HTML by removing unwanted elements.

        Args:
            html: Raw HTML content

        Returns:
            Cleaned text
        """
        soup = BeautifulSoup(html, "html.parser")

        # Remove unwanted tags
        for tag in soup(["script", "style", "noscript", "svg", "iframe"]):
            tag.decompose()

        # Remove hidden elements
        for element in soup.find_all(style=lambda x: x and "display:none" in x):
            element.decompose()

        # Get text with proper spacing
        text = soup.get_text(separator=" ", strip=True)

        return text

    def load_url(
        self,
        url: str,
        metadata: Optional[Dict] = None
    ) -> Document:
        """
        Load content from a URL using requests.

        Args:
            url: URL to load
            metadata: Optional metadata to attach

        Returns:
            Document object with cleaned content
        """
        logger.info(f"Loading web content from {url}")

        try:
            response = requests.get(
                url,
                timeout=30,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            response.raise_for_status()

            html = response.text
            cleaned_text = self.clean_html(html)

            if not cleaned_text:
                logger.warning(f"No content extracted from {url}")

            doc_metadata = metadata or {}
            doc_metadata["source"] = url

            return Document(page_content=cleaned_text, metadata=doc_metadata)

        except Exception as e:
            logger.error(f"Failed to load {url}: {e}")
            raise
