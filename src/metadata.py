"""
Metadata management for documents.
"""

import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)


class MetadataManager:
    """Manage document metadata."""

    @staticmethod
    def create_metadata(
        scheme: str,
        title: str,
        document_type: str,
        publisher: str,
        source: str,
        page: Optional[int] = None,
        url: Optional[str] = None,
        last_updated: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create standardized metadata for a document.

        Args:
            scheme: Fund scheme name
            title: Document title
            document_type: Type of document (Factsheet, SID, KIM, etc.)
            publisher: Publisher name (SBI Mutual Fund, AMFI, SEBI)
            source: Source URL or identifier
            page: Page number (for PDFs)
            url: Full URL
            last_updated: Last updated date

        Returns:
            Metadata dictionary
        """
        metadata = {
            "scheme": scheme,
            "title": title,
            "document_type": document_type,
            "publisher": publisher,
            "source": source,
            "last_updated": last_updated or datetime.now().strftime("%Y-%m-%d")
        }

        if page is not None:
            metadata["page"] = page

        if url:
            metadata["url"] = url

        return metadata

    @staticmethod
    def update_document_metadata(
        document: Any,
        metadata: Dict[str, Any]
    ) -> Any:
        """
        Update a document's metadata while preserving existing fields.

        Args:
            document: LangChain Document object
            metadata: New metadata to add/update

        Returns:
            Updated document
        """
        document.metadata.update(metadata)
        return document
