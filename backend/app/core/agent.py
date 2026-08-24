import os
import re
from typing import Any, Dict, Optional

from app.retrieval import RetrievalService
from app.logging import setup_logging
from app.core.constants import (
    MAX_TURNS,
    MAX_VERIFICATION_ATTEMPTS,
    ORDER_ID_RE,
    EMAIL_RE,
    UNSAFE_PHRASES,
    PROMPT_INJECTION_RE,
    ORDER_KEYWORDS,
    POLICY_KEYWORDS,
    GREETING_KEYWORDS,
    RETRIEVAL_TOP_K,
    RETRIEVAL_SCORE_THRESHOLD,
    GENERAL_SCORE_THRESHOLD,
    RETRIEVAL_SNIPPET_MAX_LENGTH,
    SYSTEM_PROMPT,
    MAX_TURNS_REACHED_MESSAGE,
    UNSAFE_REQUEST_MESSAGE,
    PROMPT_INJECTION_MESSAGE,
    VERIFICATION_PROMPT_MESSAGE,
    VERIFICATION_SUCCESS_MESSAGE,
    ORDER_LOOKUP_MESSAGE,
    ORDER_NEEDS_VERIFICATION_MESSAGE,
    GREETING_MESSAGE,
    GENERAL_FALLBACK_MESSAGE,
    GENERAL_HELP_MESSAGE,
    ESCALATION_AFTER_VERIFICATION_FAILURE_MESSAGE,
    SUGGESTED_QUESTIONS,
    PREDEFINED_ANSWERS,
)
from app.core.session import Session
from app.core.llm import generate as llm_generate
import logging

# Configures the logging system for the agent module
setup_logging()
logger = logging.getLogger("agent")

# Determines whether the LLM is available based on API key presence
USE_LLM = bool(os.getenv("ANTHROPIC_API_KEY"))


# Core agent that handles customer conversations, intent detection, and safety checks
class AgentCore:
    def __init__(self):
        self.retrieval = RetrievalService()
        self.sessions: Dict[str, Session] = {}

    # Retrieves an existing session or creates a new one if it doesn't exist
    def _get_session(self, session_id: str) -> Session:
        if session_id not in self.sessions:
            self.sessions[session_id] = Session(session_id)
        return self.sessions[session_id]

    # Checks user message for unsafe requests or prompt injection attempts
    def _safety_check(self, user_message: str) -> Optional[str]:
        lower = user_message.lower()
        for phrase in UNSAFE_PHRASES:
            if phrase in lower:
                return "unsafe"
        if PROMPT_INJECTION_RE.search(lower):
            return "injection"
        return None

    # Validates that order ID and email match expected formats
    def _validate_order_input(self, order_id: str, email: str) -> Optional[str]:
        if not ORDER_ID_RE.match(order_id):
            return "invalid_order_id"
        if not EMAIL_RE.match(email):
            return "invalid_email"
        return None

    # Determines what the user wants to do based on their message and session state
    def _detect_intent(self, user_message: str, session: Session) -> str:
        lower = user_message.lower()
        has_order_id = bool(re.search(r"[A-Z]{2,}-\d{4,}", user_message))
        has_email = bool(re.search(r"[\w\.-]+@[\w\.-]+", user_message))
        if has_order_id and has_email:
            return "verification_response"
        if session.state == "needs_verification" and (has_order_id or has_email):
            return "verification_response"
        if has_order_id or any(k in lower for k in ORDER_KEYWORDS):
            return "order_inquiry"
        if any(k in lower for k in POLICY_KEYWORDS):
            return "knowledge_query"
        if any(k == lower.strip() or lower.strip().startswith(k + " ") for k in GREETING_KEYWORDS):
            return "greeting"
        return "general"

    # Strips common markdown formatting from text for clean display
    def _strip_markdown(self, text: str) -> str:
        text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
        text = re.sub(r"\*{1,2}([^*]+)\*{1,2}", r"\1", text)
        text = re.sub(r"^[\*\-\+]\s+", "", text, flags=re.MULTILINE)
        text = re.sub(r"^\d+\.\s+", "", text, flags=re.MULTILINE)
        return text.strip()

    # Returns a canned answer for predefined questions, or None if no match
    def _get_predefined_answer(self, user_message: str) -> Optional[str]:
        normalized = user_message.strip()
        if normalized in PREDEFINED_ANSWERS:
            return PREDEFINED_ANSWERS[normalized]
        lower = normalized.lower()
        for question, answer in PREDEFINED_ANSWERS.items():
            if lower == question.lower():
                return answer
        return None

    # Main chat handler that processes a user message and returns an agent response
    async def chat(self, session_id: str, user_message: str) -> Dict[str, Any]:
        session = self._get_session(session_id)
        session.turn_count += 1
        if session.turn_count > MAX_TURNS:
            return {
                "session_id": session_id,
                "message": {"role": "assistant", "content": MAX_TURNS_REACHED_MESSAGE},
                "state": "escalated",
                "evidence": None,
                "tool_calls": None,
                "suggested_questions": SUGGESTED_QUESTIONS,
            }

        safety = self._safety_check(user_message)
        if safety == "unsafe":
            session.state = "escalated"
            return {
                "session_id": session_id,
                "message": {"role": "assistant", "content": UNSAFE_REQUEST_MESSAGE},
                "state": "escalated",
                "evidence": None,
                "tool_calls": None,
                "suggested_questions": SUGGESTED_QUESTIONS,
            }
        if safety == "injection":
            session.state = "failed_safe"
            return {
                "session_id": session_id,
                "message": {"role": "assistant", "content": PROMPT_INJECTION_MESSAGE},
                "state": "failed_safe",
                "evidence": None,
                "tool_calls": None,
                "suggested_questions": SUGGESTED_QUESTIONS,
            }

        intent = self._detect_intent(user_message, session)

        if intent == "verification_response":
            match = re.search(r"([A-Z]{2,}-\d{4,})", user_message)
            email_match = re.search(r"[\w\.-]+@[\w\.-]+", user_message)
            order_id = match.group(1) if match else ""
            email = email_match.group(0) if email_match else ""
            validation_error = self._validate_order_input(order_id, email)
            if validation_error:
                session.verification_attempts += 1
                if session.verification_attempts >= MAX_VERIFICATION_ATTEMPTS:
                    session.state = "escalated"
                    return {
                        "session_id": session_id,
                        "message": {"role": "assistant", "content": ESCALATION_AFTER_VERIFICATION_FAILURE_MESSAGE},
                        "state": "escalated",
                        "evidence": None,
                        "tool_calls": None,
                        "suggested_questions": SUGGESTED_QUESTIONS,
                    }
                return {
                    "session_id": session_id,
                    "message": {"role": "assistant", "content": VERIFICATION_PROMPT_MESSAGE},
                    "state": "needs_verification",
                    "evidence": None,
                    "tool_calls": None,
                    "suggested_questions": SUGGESTED_QUESTIONS,
                }
            session.pending_order_id = order_id
            session.pending_email = email
            session.state = "verified"
            return {
                "session_id": session_id,
                "message": {"role": "assistant", "content": VERIFICATION_SUCCESS_MESSAGE},
                "state": "verified",
                "evidence": None,
                "tool_calls": [{"tool": "lookup_order", "order_id": order_id, "email": email}],
                "suggested_questions": SUGGESTED_QUESTIONS,
            }

        if intent == "order_inquiry":
            if session.pending_order_id and session.pending_email:
                session.state = "ready_to_answer"
                return {
                    "session_id": session_id,
                    "message": {"role": "assistant", "content": ORDER_LOOKUP_MESSAGE},
                    "state": "ready_to_answer",
                    "evidence": None,
                    "tool_calls": [{"tool": "lookup_order", "order_id": session.pending_order_id, "email": session.pending_email}],
                    "suggested_questions": SUGGESTED_QUESTIONS,
                }
            session.state = "needs_verification"
            return {
                "session_id": session_id,
                "message": {"role": "assistant", "content": ORDER_NEEDS_VERIFICATION_MESSAGE},
                "state": "needs_verification",
                "evidence": None,
                "tool_calls": None,
                "suggested_questions": SUGGESTED_QUESTIONS,
            }

        if intent == "greeting":
            session.state = "ready_to_answer"
            return {
                "session_id": session_id,
                "message": {"role": "assistant", "content": GREETING_MESSAGE},
                "state": "ready_to_answer",
                "evidence": None,
                "tool_calls": None,
                "suggested_questions": SUGGESTED_QUESTIONS,
            }

        predefined_answer = self._get_predefined_answer(user_message)
        if predefined_answer is not None:
            session.state = "ready_to_answer"
            return {
                "session_id": session_id,
                "message": {"role": "assistant", "content": predefined_answer},
                "state": "ready_to_answer",
                "evidence": None,
                "tool_calls": None,
                "suggested_questions": SUGGESTED_QUESTIONS,
            }

        if intent == "knowledge_query" or intent == "general":
            results = self.retrieval.query(user_message, top_k=RETRIEVAL_TOP_K, score_threshold=RETRIEVAL_SCORE_THRESHOLD)
            if not results:
                session.state = "ready_to_answer"
                return {
                    "session_id": session_id,
                    "message": {"role": "assistant", "content": GENERAL_FALLBACK_MESSAGE},
                    "state": "ready_to_answer",
                    "evidence": None,
                    "tool_calls": None,
                    "suggested_questions": SUGGESTED_QUESTIONS,
                }
            min_confidence = GENERAL_SCORE_THRESHOLD if intent == "general" else 0.0
            if results[0]["score"] < min_confidence:
                session.state = "ready_to_answer"
                return {
                    "session_id": session_id,
                    "message": {"role": "assistant", "content": GENERAL_FALLBACK_MESSAGE},
                    "state": "ready_to_answer",
                    "evidence": None,
                    "tool_calls": None,
                    "suggested_questions": SUGGESTED_QUESTIONS,
                }
            evidence = {"source_id": results[0]["source_id"], "snippet": results[0]["snippet"], "score": results[0]["score"]}
            session.state = "ready_to_answer"
            content = self._strip_markdown(results[0]["snippet"][:RETRIEVAL_SNIPPET_MAX_LENGTH])
            if USE_LLM:
                try:
                    llm_messages = [
                        {"role": "user", "content": (
                            f"Answer the customer's question using ONLY the evidence below. "
                            f"If the evidence does not contain the answer, say you cannot verify.\n\n"
                            f"Question: {user_message}\n\n"
                            f"Evidence from {results[0]['source_id'].replace('_', ' ').title()}:\n"
                            f"{results[0]['snippet']}\n\n"
                            f"Respond in plain text only. Do not use markdown headings, bold, or bullet points."
                        )}
                    ]
                    content = self._strip_markdown(llm_generate(llm_messages, system=SYSTEM_PROMPT))
                except Exception as exc:
                    logger.error("LLM generation failed: %s", exc)
            return {
                "session_id": session_id,
                "message": {"role": "assistant", "content": content},
                "state": "ready_to_answer",
                "evidence": evidence,
                "tool_calls": None,
                "suggested_questions": SUGGESTED_QUESTIONS,
            }

        session.state = "ready_to_answer"
        return {
            "session_id": session_id,
            "message": {"role": "assistant", "content": GENERAL_HELP_MESSAGE},
            "state": "ready_to_answer",
            "evidence": None,
            "tool_calls": None,
            "suggested_questions": SUGGESTED_QUESTIONS,
        }


# Singleton instance of the agent core used across the application
agent_core = AgentCore()
