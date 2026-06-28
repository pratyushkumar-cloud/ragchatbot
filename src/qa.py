import os
import logging
from typing import Dict, Any, List
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from src.retriever import get_retriever
from src.prompt import PromptTemplates
from src.guardrails import Guardrails

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

retriever = get_retriever(k=4)
llm = ChatGroq(
    model=os.getenv("LLM_MODEL", "llama-3.3-70b-versatile"),
    temperature=float(os.getenv("LLM_TEMPERATURE", "0")),
    groq_api_key=os.getenv("GROQ_API_KEY")
)


def answer_query(question: str) -> Dict[str, Any]:
    """Answer a factual question using RAG with source citation"""
    logger.info(f"Processing question: {question}")
    
    if Guardrails.is_advice_question(question):
        logger.info("Question detected as advice request - refusing")
        return {
            "answer": PromptTemplates.get_advice_refusal(),
            "source": "AMFI",
            "document": "AMFI",
            "page": "",
            "publisher": "AMFI",
            "last_updated": ""
        }

    docs = retriever.invoke(question)
    
    if not docs:
        logger.info("No relevant documents found")
        return {
            "answer": "I couldn't find this information in the selected official documents.",
            "source": "",
            "document": "",
            "page": "",
            "publisher": "",
            "last_updated": ""
        }

    context = "\n\n".join([f"[Source: {d.metadata.get('source', 'Unknown')}]\n{d.page_content}" for d in docs])
    
    # Deduplicate document names
    unique_documents = list(set([d.metadata.get("title", "Unknown") for d in docs]))
    document_names = ", ".join(unique_documents)

    prompt = PromptTemplates.get_rag_prompt(context, question, document_names)

    response = llm.invoke(prompt)
    
    answer = response.content.strip()
    
    # Post-processing: filter generic advice
    answer = Guardrails.filter_generic_advice(answer)
    
    if answer == "I couldn't find this information in the selected official documents.":
        source = ""
        document = ""
        page = ""
        publisher = ""
        last_updated = ""
    else:
        source = docs[0].metadata.get("source", "")
        document = docs[0].metadata.get("title", "")
        page = docs[0].metadata.get("page", "")
        publisher = docs[0].metadata.get("publisher", "")
        last_updated = docs[0].metadata.get("last_updated", "")

    logger.info(f"Answer generated with source: {source}")
    
    return {
        "answer": answer,
        "source": source,
        "document": document,
        "page": page,
        "publisher": publisher,
        "last_updated": last_updated
    }
