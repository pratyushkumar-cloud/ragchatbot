"""
Guardrails for investment advice detection.
"""

import logging
from typing import List

logger = logging.getLogger(__name__)


class Guardrails:
    """Investment advice detection and filtering."""

    ADVICE_KEYWORDS = [
        "best",
        "recommend",
        "which fund is better",
        "portfolio review",
        "financial planning",
        "future predictions",
        "highest returns",
        "good investment",
        "better to invest",
        "suggest",
        "advice",
        "recommendation",
        "should i invest in",
        "top performing",
        "best performing",
        "highest return",
        "buy or sell",
        "investment strategy"
    ]

    GENERIC_PHRASES = [
        "you can visit the website",
        "check the investor service centres",
        "contact the customer support",
        "refer to the website",
        "for more information",
        "please visit",
        "we recommend"
    ]

    @staticmethod
    def is_advice_question(question: str) -> bool:
        """
        Check if a question is asking for investment advice.

        Args:
            question: User question

        Returns:
            True if question asks for advice
        """
        question_lower = question.lower()
        return any(keyword in question_lower for keyword in Guardrails.ADVICE_KEYWORDS)

    @staticmethod
    def contains_generic_advice(answer: str) -> bool:
        """
        Check if answer contains generic advice phrases not from context.

        Args:
            answer: Generated answer

        Returns:
            True if generic advice detected
        """
        answer_lower = answer.lower()
        return any(phrase in answer_lower for phrase in Guardrails.GENERIC_PHRASES)

    @staticmethod
    def filter_generic_advice(answer: str) -> str:
        """
        Replace generic advice with unavailable message.

        Args:
            answer: Generated answer

        Returns:
            Filtered answer
        """
        if Guardrails.contains_generic_advice(answer):
            logger.info("Detected generic advice in answer, replacing with unavailable message")
            return "I couldn't find this information in the selected official documents."
        return answer
