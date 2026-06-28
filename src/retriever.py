import os
import logging
from typing import Any
from dotenv import load_dotenv
from src.vectorstore import VectorStoreManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

def get_retriever(k: int = 4) -> Any:
    """Initialize and return FAISS retriever with top k chunks"""
    vector_dir = os.getenv("VECTOR_DIR", "vectorstore")
    embedding_model = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    
    logger.info(f"Loading vector store from {vector_dir}")
    
    vs_manager = VectorStoreManager(
        embedding_model=embedding_model,
        vector_dir=vector_dir
    )
    
    retriever = vs_manager.get_retriever(k=k, score_threshold=0.3)
    
    logger.info(f"Retriever initialized successfully with k={k}")
    return retriever
