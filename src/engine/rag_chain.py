import os
from typing import List, Dict, Any

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document

from openai import OpenAI  # Grok uses OpenAI-compatible API


# ==============================
# CONFIG
# ==============================
CHROMA_DIR = "chroma_db"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Grok Config
GROK_API_KEY = os.getenv("GROK_API_KEY")
GROK_BASE_URL = "https://api.x.ai/v1"
GROK_MODEL = "grok-1"   # or grok-1.5 if enabled


# ==============================
# RAG CHAIN CLASS
# ==============================

class RAGChain:
    def __init__(self):
        # Embeddings
        self.embedding = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL
        )

        # Vector DB
        self.vectordb = Chroma(
            persist_directory=CHROMA_DIR,
            embedding_function=self.embedding
        )

        # Retriever
        self.retriever = self._build_retriever()

        # Grok Client
        self.client = OpenAI(
            api_key=GROK_API_KEY,
            base_url=GROK_BASE_URL
        )

    # ==============================
    # RETRIEVER (MMR)
    # ==============================
    def _build_retriever(self):
        return self.vectordb.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": 5,
                "fetch_k": 20,
                "lambda_mult": 0.7
            }
        )

    # ==============================
    # RETRIEVE DOCS
    # ==============================
    def retrieve(self, query: str, filters=None) -> List[Document]:
        if filters:
            return self.vectordb.similarity_search(
                query,
                k=5,
                filter=filters
            )
        return self.retriever.get_relevant_documents(query)

    # ==============================
    # BUILD CONTEXT
    # ==============================
    def _build_context(self, docs: List[Document]) -> str:
        blocks = []

        for i, doc in enumerate(docs):
            meta = doc.metadata

            blocks.append(f"""
[Document {i+1}]
Source: {meta.get('source')}
Scheme: {meta.get('scheme')}
Type: {meta.get('document_type')}

Content:
{doc.page_content}
""")

        return "\n\n".join(blocks)

    # ==============================
    # PROMPT
    # ==============================
    def _build_prompt(self, query: str, context: str) -> str:
        return f"""
You are a mutual fund assistant.

STRICT RULES:
- Answer ONLY from context
- If not found → say "Information not available"
- Do not guess
- Prefer exact numbers

CONTEXT:
{context}

QUESTION:
{query}

ANSWER:
"""

    # ==============================
    # CALL GROK API
    # ==============================
    def _call_grok(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=GROK_MODEL,
            messages=[
                {"role": "system", "content": "You are a financial assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        return response.choices[0].message.content

    # ==============================
    # MAIN FUNCTION
    # ==============================
    def ask(self, query: str, filters=None) -> Dict[str, Any]:
        docs = self.retrieve(query, filters)

        if not docs:
            return {
                "answer": "No relevant documents found",
                "sources": []
            }

        context = self._build_context(docs)
        prompt = self._build_prompt(query, context)

        answer = self._call_grok(prompt)

        return {
            "answer": answer,
            "sources": [
                {
                    "source": d.metadata.get("source"),
                    "scheme": d.metadata.get("scheme"),
                    "type": d.metadata.get("document_type")
                }
                for d in docs
            ]
        }


# ==============================
# TEST
# ==============================
if __name__ == "__main__":
    rag = RAGChain()

    result = rag.ask("What is the expense ratio of SBI Bluechip Fund?")

    print("\n🧠 Answer:\n", result["answer"])
    print("\n📚 Sources:\n", result["sources"])