import os
import re

# Agent behavior limits
MAX_TURNS = 20
MAX_TOOL_CALLS = 10
MAX_VERIFICATION_ATTEMPTS = 3

# Input validation patterns
ORDER_ID_RE = re.compile(r"^[A-Z]{2,}-\d{4,}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# Safety and prompt injection detection
UNSAFE_PHRASES = [
    "cancel my order",
    "cancel order",
    "refund my order",
    "i want a refund",
    "process a refund",
    "get a refund",
    "change my address",
    "update my address",
    "delete my account",
]
PROMPT_INJECTION_RE = re.compile(r"(ignore|forget|disregard).*(instruction|system|prompt)")

# Intent detection keywords
ORDER_KEYWORDS = ["order", "status", "tracking", "delivery", "shipped", "delivered"]
POLICY_KEYWORDS = ["return", "refund", "shipping", "policy", "exchange", "warranty", "size", "fit"]
GREETING_KEYWORDS = ["hi", "hello", "hey", "how are you", "good morning", "good afternoon", "good evening"]

# LLM settings
LLM_MODEL = "claude-sonnet-5"
LLM_MAX_TOKENS = 1024

# Retrieval settings
RETRIEVAL_TOP_K = 2
RETRIEVAL_SCORE_THRESHOLD = 0.15
GENERAL_SCORE_THRESHOLD = 0.2
RETRIEVAL_SNIPPET_MAX_LENGTH = 800

# Order service field controls
MASKED_FIELDS = {"email", "phone", "payment_method", "internal_cost", "cost_price_cents"}
RETURNABLE_FIELDS = {
    "status",
    "order_date",
    "estimated_delivery",
    "shipping_method",
    "tracking_number",
    "items",
    "subtotal_cents",
    "shipping_cents",
    "discount_cents",
    "total_cents",
}

# System prompts
SYSTEM_PROMPT = """You are the Sunnystep customer-support AI agent. Your ONLY job is to help customers with Sunnystep products, orders, returns, shipping, and policies.

STRICT RULES:
1. SCOPE: Only discuss Sunnystep products, orders, returns, shipping, and policies. 
   - If a customer asks about anything else (politics, weather, jokes, general knowledge, personal topics, other companies, etc.), politely decline: "I'm here to help with Sunnystep products, orders, and policies. How can I assist you today?"
2. EVIDENCE: Answer ONLY using the provided evidence below. If the evidence does not contain the answer, say "I cannot verify that information. Is there something else I can help you with?"
3. ACCURACY: Never invent policies, products, prices, dates, or order details.
4. PRIVACY: Never expose another customer's data.
5. SAFETY: For unsafe or unsupported requests (cancellations, refunds, address changes), refuse and escalate.
6. TONE: Keep responses concise, professional, and friendly.
7. ESCALATION: If you cannot help, connect the customer with a human agent.
"""

ORDER_FORMAT_PROMPT = """You are formatting verified order details for a Sunnystep customer support response. Present the information concisely and professionally. Use only the order details provided. Do not add any information not present in the data."""

# Response messages
MAX_TURNS_REACHED_MESSAGE = "I've reached the maximum number of turns for this conversation. I'll connect you with a human agent who can continue helping."
UNSAFE_REQUEST_MESSAGE = "I'm not able to perform cancellations, refunds, or address changes. I can help you look up your order status, explain our policies, or connect you with a human agent."
PROMPT_INJECTION_MESSAGE = "I'm here to help with Sunnystep orders and policies. How can I assist you?"
VERIFICATION_PROMPT_MESSAGE = "Please provide both your order number (like ORD-3001) and the email address on the order."
VERIFICATION_SUCCESS_MESSAGE = "Thank you. I'll look up your order now."
ORDER_LOOKUP_MESSAGE = "Let me pull up your order details."
ORDER_NEEDS_VERIFICATION_MESSAGE = "To look up your order, I'll need your order number and the email address associated with the order. Could you please provide both?"
GREETING_MESSAGE = "Hello! I'm here to help with Sunnystep products, orders, and policies. How can I assist you today?"
GENERAL_FALLBACK_MESSAGE = "I'm here to help with Sunnystep products, orders, and policies. How can I assist you today?"
GENERAL_HELP_MESSAGE = "I can help with questions about Sunnystep policies, products, orders, and returns. What would you like to know?"
ESCALATION_AFTER_VERIFICATION_FAILURE_MESSAGE = "I wasn't able to verify your identity after several attempts. I'll connect you with a human agent who can help."
ORDER_LOOKUP_FAILED_MESSAGE = "I couldn't verify that order. Please check the order number and email and try again."
GENERIC_ERROR_MESSAGE = "Something went wrong on our end. I've logged the issue, and a support agent will follow up if needed."

SUGGESTED_QUESTIONS = [
    "Do you ship internationally",
    "How long does shipping take?",
    "How much does shipping cost?",
    "Does my order include duties and taxes?",
]

PREDEFINED_ANSWERS = {
    "Do you ship internationally": "Yes, we ship worldwide! Wherever you are, you can enjoy Sunnystep's comfort and support.",
    "How long does shipping take?": "Singapore: 2-4 business days.\nInternational: 7-14 business days, depending on location.\nShipping times may vary during peak seasons.",
    "How much does shipping cost?": "For Singapore:\n- Enjoy free standard shipping on orders over SGD 120.\n- A SGD 6 shipping fee applies to orders below SGD 120.\nFor international orders:\n- Shipping fees vary by country and will be displayed at checkout.",
    "Does my order include duties and taxes?": "Yes, the total amount during checkout includes all costs associated with your order, including taxes and delivery fees. Taxes are calculated based on the laws applicable to the delivery address.",
}

# API and CORS settings
API_TITLE = "AI Backend API"
API_VERSION = "0.1.0"
CORS_ALLOW_ORIGINS = ["http://localhost:3000"]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["*"]
CORS_ALLOW_HEADERS = ["*"]

# Knowledge base settings
KNOWLEDGE_PATH = os.getenv("KNOWLEDGE_PATH", "./data/knowledge")
