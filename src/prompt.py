"""
Prompt templates for the RAG system.
"""

from typing import List


class PromptTemplates:
    """Centralized prompt templates."""

    SYSTEM_PROMPT = """You are a Mutual Fund FAQ Assistant.

STRICT RULES:
1. Use ONLY the provided context.
2. Never use external knowledge.
3. Never hallucinate.
4. Maximum three sentences.
5. Always cite Document Name, Page Number (if PDF), and Official Source URL.
6. If the answer is unavailable, respond EXACTLY: "I couldn't find this information in the selected official documents."
7. Never provide investment advice, recommendations, or return predictions."""

    @staticmethod
    def get_rag_prompt(
        context: str,
        question: str,
        document_names: List[str]
    ) -> str:
        """
        Generate RAG prompt with context and question.

        Args:
            context: Retrieved context chunks
            question: User question
            document_names: List of document names for citation

        Returns:
            Formatted prompt string
        """
        doc_citation = ", ".join(document_names)

        return f"""{PromptTemplates.SYSTEM_PROMPT}

Context:
{context}

Question: {question}

Answer: (End your answer with: Last updated from sources: {doc_citation})"""

    @staticmethod
    def get_advice_refusal() -> str:
        """
        Get the investment advice refusal message.

        Returns:
            Refusal message
        """
        return "I can only provide factual information about mutual funds. I do not provide investment advice, recommendations, or return predictions. Last updated from sources: AMFI"
