"""
Vector store operations using FAISS.
"""

import os
import logging
from typing import List, Any
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

logger = logging.getLogger(__name__)


class VectorStoreManager:
    """Manage FAISS vector store operations."""

    def __init__(
        self,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        vector_dir: str = "vectorstore"
    ):
        """
        Initialize vector store manager.

        Args:
            embedding_model: Name of the embedding model
            vector_dir: Directory to save/load vector store
        """
        self.embedding_model = embedding_model
        self.vector_dir = vector_dir
        self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model)

    def create_vectorstore(
        self,
        documents: List[Any],
        save: bool = True
    ) -> FAISS:
        """
        Create FAISS vector store from documents.

        Args:
            documents: List of Document objects
            save: Whether to save the vector store

        Returns:
            FAISS vector store
        """
        logger.info("Creating FAISS vector store")

        vectorstore = FAISS.from_documents(documents, self.embeddings)

        if save:
            self.save_vectorstore(vectorstore)

        return vectorstore

    def save_vectorstore(self, vectorstore: FAISS) -> None:
        """
        Save vector store to disk.

        Args:
            vectorstore: FAISS vector store instance
        """
        os.makedirs(self.vector_dir, exist_ok=True)
        vectorstore.save_local(self.vector_dir)
        logger.info(f"Vector store saved to {self.vector_dir}")

    def load_vectorstore(self) -> FAISS:
        """
        Load vector store from disk.

        Returns:
            FAISS vector store
        """
        logger.info(f"Loading vector store from {self.vector_dir}")

        if not os.path.exists(self.vector_dir):
            raise FileNotFoundError(f"Vector store not found at {self.vector_dir}")

        vectorstore = FAISS.load_local(
            self.vector_dir,
            self.embeddings,
            allow_dangerous_deserialization=True
        )

        logger.info("Vector store loaded successfully")
        return vectorstore

    def get_retriever(
        self,
        k: int = 4,
        score_threshold: float = 0.3
    ) -> Any:
        """
        Get a retriever from the vector store.

        Args:
            k: Number of documents to retrieve
            score_threshold: Minimum similarity score

        Returns:
            Retriever instance
        """
        vectorstore = self.load_vectorstore()

        retriever = vectorstore.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={
                "k": k,
                "score_threshold": score_threshold
            }
        )

        logger.info(f"Retriever initialized with k={k}")
        return retriever
