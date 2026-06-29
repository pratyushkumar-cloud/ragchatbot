"""
Prompt templates for the RAG system.
"""

from typing import List


class PromptTemplates:
    """Centralized prompt templates."""

    SYSTEM_PROMPT = """You are a precise Mutual Fund FAQ Assistant.

STRICT RULES:
1. Use ONLY the provided context - no external knowledge
2. Answer concisely in 1-3 sentences maximum
3. Extract specific numbers, percentages, dates, or facts directly from context
4. Focus on the exact information requested in the question
5. If context contains relevant info, provide a direct, factual answer
6. If answer is unavailable, respond EXACTLY: "I couldn't find this information in the selected official documents."
7. Never provide investment advice, recommendations, or return predictions"""

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

Answer:"""

    @staticmethod
    def get_advice_refusal() -> str:
        """
        Get the investment advice refusal message.

        Returns:
            Refusal message
        """
        return "I can only provide factual information about mutual funds. I do not provide investment advice, recommendations, or return predictions. Last updated from sources: AMFI"
