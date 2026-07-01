import os
import logging
from datetime import datetime
from typing import Dict, Any, List
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from src.retriever import get_retriever
from src.prompt import PromptTemplates
from src.guardrails import Guardrails

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

retriever = get_retriever(k=6)


def answer_query(question: str) -> Dict[str, Any]:
    """Answer a factual question using RAG with source citation"""
    logger.info(f"Processing question: {question}")
    
    # Debug environment variable loading
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")
    logger.info(f"API Key from env: {api_key[:10] if api_key else 'None'}...{api_key[-10:] if api_key else 'None'}")
    
    # Initialize LLM with current environment variables
    llm = ChatGroq(
        model=os.getenv("LLM_MODEL", "llama-3.3-70b-versatile"),
        temperature=float(os.getenv("LLM_TEMPERATURE", "0")),
        groq_api_key=api_key
    )
    
    if Guardrails.is_advice_question(question):
        logger.info("Question detected as advice request - refusing")
        return {
            "answer": "I can only provide factual information about mutual funds. I do not provide investment advice, recommendations, or return predictions.",
            "source": "",
            "document": "",
            "page": "",
            "publisher": "",
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
    # Filter out "unknown" document names
    unique_documents = [doc for doc in unique_documents if doc != "Unknown" and doc != ""]
    document_names = ", ".join(unique_documents) if unique_documents else "official documents"

    prompt = PromptTemplates.get_rag_prompt(context, question, document_names)

    response = llm.invoke(prompt)
    
    answer = response.content.strip()
    
    # Post-processing: filter generic advice
    answer = Guardrails.filter_generic_advice(answer)
    
    # Check if answer indicates information not found
    not_found_indicators = [
        "couldn't find this information",
        "information not found",
        "not available in the provided",
        "does not contain information"
    ]
    
    is_not_found = any(indicator in answer.lower() for indicator in not_found_indicators)
    
    if is_not_found:
        source = ""
        document = ""
        page = ""
        publisher = ""
        last_updated = ""
        # Clean up the answer to remove the document names suffix
        answer = "I couldn't find this information in the selected official documents."
    else:
        source = docs[0].metadata.get("source", "")
        document = docs[0].metadata.get("title", "")
        page = str(docs[0].metadata.get("page", "")) if docs[0].metadata.get("page") is not None else ""
        publisher = docs[0].metadata.get("publisher", "")
        last_updated = docs[0].metadata.get("last_updated", "")
        
        # Add "Last updated from sources" only if answer was found
        current_date = datetime.now().strftime("%B %d, %Y")
        answer = f"{answer} Last updated from sources: {current_date}"

    logger.info(f"Answer generated with source: {source}")
    
    return {
        "answer": answer,
        "source": source,
        "document": document,
        "page": page,
        "publisher": publisher,
        "last_updated": last_updated
    }
