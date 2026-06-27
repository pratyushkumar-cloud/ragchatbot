import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from src.retriever import get_retriever

load_dotenv()

retriever = get_retriever()
llm = ChatGroq(
    model=os.getenv("LLM_MODEL", "llama-3.3-70b-versatile"),
    temperature=float(os.getenv("LLM_TEMPERATURE", "0")),
    groq_api_key=os.getenv("GROQ_API_KEY")
)


def is_advice_question(q):
    keywords = ["should i", "best", "recommend", "invest"]
    return any(k in q.lower() for k in keywords)


def answer_query(question):
    if is_advice_question(question):
        return {
            "answer": "I can only provide factual information. No investment advice.",
            "source": "AMFI"
        }

    docs = retriever.invoke(question)
    
    if not docs:
        return {
            "answer": "I couldn't find relevant information in the documents to answer your question.",
            "source": "N/A"
        }

    context = "\n\n".join([f"[Source: {d.metadata.get('source', 'Unknown')}]\n{d.page_content}" for d in docs])

    prompt = f"""You are a precise mutual fund information assistant. Answer the question using ONLY the provided context.

STRICT RULES:
1. Answer concisely in 1-3 sentences
2. Use ONLY factual information from the context
3. If the context doesn't contain the answer, say "Information not found in the provided documents"
4. Include specific numbers, percentages, or dates from the context
5. Do not add information not present in the context
6. No investment advice or recommendations

Context:
{context}

Question: {question}

Answer:"""

    response = llm.invoke(prompt)

    source = docs[0].metadata.get("source", "")

    return {
        "answer": response.content.strip(),
        "source": source
    }