import os
import csv
import logging
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv

from langchain_text_splitters import RecursiveCharacterTextSplitter

from web_loader import WebLoader
from vectorstore import VectorStoreManager

# ---------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------

load_dotenv()

DATA_DIR = os.getenv("DATA_DIR", "data")
VECTOR_DIR = os.getenv("VECTOR_DIR", "vectorstore")
SOURCES_FILE = os.path.join(DATA_DIR, "sources.csv")

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2"
)

# ---------------------------------------------------------------------
# Load Sources Configuration
# ---------------------------------------------------------------------


def load_sources() -> List[Dict[str, str]]:
    """
    Load sources configuration from CSV file.

    Returns:
        List of source configurations
    """
    sources = []

    if not os.path.exists(SOURCES_FILE):
        logger.warning(f"sources.csv not found at {SOURCES_FILE}")
        return sources

    with open(SOURCES_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sources.append(row)

    logger.info(f"Loaded {len(sources)} sources from {SOURCES_FILE}")
    return sources


# ---------------------------------------------------------------------
# Load Documents
# ---------------------------------------------------------------------


def load_documents() -> List[Any]:
    """
    Load all documents from sources configuration.
    Supports local PDFs and web scraping.
    """
    documents = []
    sources = load_sources()
    last_updated = datetime.now().strftime("%Y-%m-%d")

    from langchain_community.document_loaders import PyPDFLoader
    web_loader = WebLoader()

    # Load local PDFs first
    for file in os.listdir(DATA_DIR):
        if file.endswith(".pdf"):
            logger.info(f"Loading local PDF: {file}")
            
            loader = PyPDFLoader(os.path.join(DATA_DIR, file))
            pdf_docs = loader.load()
            
            # Find matching source info
            source_info = None
            for source in sources:
                if source["type"] == "PDF" and file.lower() in source["url"].lower():
                    source_info = source
                    break
            
            if source_info:
                for doc in pdf_docs:
                    doc.metadata.update({
                        "scheme": source_info["scheme"],
                        "title": source_info["title"],
                        "document_type": source_info["document_type"],
                        "publisher": source_info["publisher"],
                        "source": source_info["url"],
                        "url": source_info["url"],
                        "last_updated": last_updated,
                        "page": doc.metadata.get("page", "")
                    })
            else:
                for doc in pdf_docs:
                    doc.metadata.update({
                        "scheme": "general",
                        "title": file.replace(".pdf", ""),
                        "document_type": "PDF",
                        "publisher": "Unknown",
                        "source": "",
                        "url": "",
                        "last_updated": last_updated,
                        "page": doc.metadata.get("page", "")
                    })
            
            documents.extend(pdf_docs)

    # Scrape web sources
    for source in sources:
        if source["type"] != "Web":
            continue
            
        url = source["url"]
        title = source["title"]
        publisher = source["publisher"]
        document_type = source["document_type"]
        scheme = source["scheme"]

        logger.info(f"Scraping web: {title}")

        try:
            doc = web_loader.load_url(
                url,
                metadata={
                    "scheme": scheme,
                    "title": title,
                    "document_type": document_type,
                    "publisher": publisher,
                    "source": url,
                    "url": url,
                    "last_updated": last_updated,
                    "page": ""
                }
            )
            documents.append(doc)

        except Exception as e:
            logger.error(f"Failed to scrape {title}: {e}")

    return documents


# ---------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------


def split_documents(documents: List[Any]) -> List[Any]:
    """
    Split documents into chunks.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    return splitter.split_documents(documents)


# ---------------------------------------------------------------------
# Create Vector Database
# ---------------------------------------------------------------------


def create_vectorstore():
    """Create vector store from sources configuration."""
    logger.info("=" * 60)
    logger.info("Loading Documents")
    logger.info("=" * 60)

    documents = load_documents()

    logger.info(f"Loaded {len(documents)} documents")

    logger.info("=" * 60)
    logger.info("Splitting Documents")
    logger.info("=" * 60)

    chunks = split_documents(documents)

    logger.info(f"Created {len(chunks)} chunks")

    logger.info("=" * 60)
    logger.info("Generating Embeddings")
    logger.info("=" * 60)

    vs_manager = VectorStoreManager(
        embedding_model=EMBEDDING_MODEL,
        vector_dir=VECTOR_DIR
    )

    vs_manager.create_vectorstore(chunks, save=True)

    logger.info("=" * 60)
    logger.info("Vector Store Created Successfully")
    logger.info("=" * 60)
    logger.info(f"Saved to: {VECTOR_DIR}")


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

if __name__ == "__main__":
    create_vectorstore()