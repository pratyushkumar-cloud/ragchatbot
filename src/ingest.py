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
    documents = []
    sources = load_sources()
    last_updated = datetime.now().strftime("%Y-%m-%d")

    from langchain_community.document_loaders import PyPDFLoader, UnstructuredPDFLoader
    from pypdf import PdfReader

    web_loader = WebLoader()

    # ---------- PDF Validation ----------
    def is_valid_pdf(path):
        try:
            PdfReader(path)
            return True
        except Exception as e:
            logger.warning(f"Invalid PDF skipped: {path} -> {e}")
            return False

    # ---------- Load Local PDFs ----------
    for file in os.listdir(DATA_DIR):
        if file.endswith(".pdf"):
            filepath = os.path.join(DATA_DIR, file)
            logger.info(f"Loading local PDF: {file}")

            if not is_valid_pdf(filepath):
                continue

            try:
                loader = PyPDFLoader(filepath)
                pdf_docs = loader.load()

            except Exception as e:
                logger.warning(f"PyPDF failed for {file}, trying fallback: {e}")

                try:
                    loader = UnstructuredPDFLoader(filepath)
                    pdf_docs = loader.load()
                except Exception as e2:
                    logger.error(f"Skipping broken PDF: {file} -> {e2}")
                    continue

            source_info = None
            for source in sources:
                if source["type"] == "PDF" and file.lower() in source["url"].lower():
                    source_info = source
                    break

            for doc in pdf_docs:
                if source_info:
                    doc.metadata.update({
                        "scheme": source_info["scheme"],
                        "title": source_info["title"],
                        "document_type": source_info["document_type"],
                        "publisher": source_info["publisher"],
                        "source": source_info["url"],
                        "url": source_info["url"],
                    })
                else:
                    doc.metadata.update({
                        "scheme": "general",
                        "title": file.replace(".pdf", ""),
                        "document_type": "PDF",
                        "publisher": "Unknown",
                        "source": "",
                        "url": "",
                    })

                doc.metadata.update({
                    "last_updated": last_updated,
                    "page": doc.metadata.get("page", "")
                })

            documents.extend(pdf_docs)

    # ---------- Web Sources ----------
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