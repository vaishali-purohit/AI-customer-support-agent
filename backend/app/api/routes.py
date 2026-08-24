from fastapi import APIRouter, HTTPException
from app.models.schemas import ChatRequest, ChatResponse, VerificationRequest, HealthResponse
from app.core import agent_core
from app.services import OrderService
from app.core.llm import generate as llm_generate
from app.core.constants import (
    ORDER_FORMAT_PROMPT,
    ORDER_LOOKUP_FAILED_MESSAGE,
)
import logging
import uuid
import os

logger = logging.getLogger("api")
router = APIRouter()
order_service = OrderService()
USE_LLM = bool(os.getenv("ANTHROPIC_API_KEY"))


# Formats order details into a plain text response without using the LLM
def _format_order_hardcoded(order_result) -> str:
    content = (
        f"Here are the details for order {order_result.order_id}:\n\n"
        f"Status: {order_result.status}\n"
        f"Order date: {order_result.order_date}\n"
        f"Estimated delivery: {order_result.estimated_delivery or 'N/A'}\n"
        f"Shipping method: {order_result.shipping_method or 'N/A'}\n"
        f"Tracking: {order_result.tracking_number or 'N/A'}\n\n"
        f"Items:\n"
    )
    for item in order_result.items:
        content += (
            f"- {item['product_name']} ({item['size']}, {item['color']}) x{item['quantity']}\n"
        )
    content += (
        f"\nSubtotal: ${order_result.subtotal_cents / 100:.2f}\n"
        f"Shipping: ${order_result.shipping_cents / 100:.2f}\n"
        f"Discount: -${order_result.discount_cents / 100:.2f}\n"
        f"Total: ${order_result.total_cents / 100:.2f}\n\n"
        f"Is there anything else I can help with?"
    )
    return content


# Formats order details using the LLM for a more natural response
def _format_order_llm(order_result, user_message: str) -> str:
    items = "\n".join(
        f"- {item['product_name']} ({item['size']}, {item['color']}) x{item['quantity']}"
        for item in order_result.items
    )
    order_details = (
        f"Status: {order_result.status}\n"
        f"Order date: {order_result.order_date}\n"
        f"Estimated delivery: {order_result.estimated_delivery or 'N/A'}\n"
        f"Shipping method: {order_result.shipping_method or 'N/A'}\n"
        f"Tracking: {order_result.tracking_number or 'N/A'}\n\n"
        f"Items:\n{items}\n\n"
        f"Subtotal: ${order_result.subtotal_cents / 100:.2f}\n"
        f"Shipping: ${order_result.shipping_cents / 100:.2f}\n"
        f"Discount: -${order_result.discount_cents / 100:.2f}\n"
        f"Total: ${order_result.total_cents / 100:.2f}"
    )
    messages = [
        {
            "role": "user",
            "content": (
                f"The customer asked: \"{user_message}\"\n\n"
                f"Here are their verified order details:\n{order_details}\n\n"
                f"Format a concise, professional response with these details. Do not invent any information."
            ),
        }
    ]
    return llm_generate(messages, system=ORDER_FORMAT_PROMPT)


# Health check endpoint that returns the API status
@router.get("/health", response_model=HealthResponse)
def health():
    return {"status": "ok"}


# Returns the list of suggested questions from the backend
@router.get("/suggested-questions")
def get_suggested_questions():
    from app.core.constants import SUGGESTED_QUESTIONS
    return {"suggested_questions": SUGGESTED_QUESTIONS}


# Chat endpoint that processes user messages and returns agent responses
@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not request.messages:
        raise HTTPException(status_code=400, detail="No messages provided")
    user_message = request.messages[-1].content
    session_id = request.session_id or str(uuid.uuid4())
    response = await agent_core.chat(session_id, user_message)
    if response.get("tool_calls"):
        for tool_call in response["tool_calls"]:
            if tool_call.get("tool") == "lookup_order":
                try:
                    order_result = order_service.lookup(tool_call["order_id"], tool_call["email"])
                    if USE_LLM:
                        try:
                            response["message"]["content"] = _format_order_llm(order_result, user_message)
                        except Exception as exc:
                            logger.error("LLM order formatting failed: %s", exc)
                            response["message"]["content"] = _format_order_hardcoded(order_result)
                    else:
                        response["message"]["content"] = _format_order_hardcoded(order_result)
                    response["tool_calls"] = None
                    response["state"] = "ready_to_answer"
                    response["suggested_questions"] = response.get("suggested_questions")
                except ValueError as e:
                    error_msg = str(e)
                    response["message"]["content"] = ORDER_LOOKUP_FAILED_MESSAGE
                    response["state"] = "failed_safe"
                    response["tool_calls"] = None
                    response["suggested_questions"] = response.get("suggested_questions")
                    logger.error("Order lookup failed: %s", error_msg)
    return ChatResponse(**response)


# Direct order verification endpoint that looks up an order by ID and email
@router.post("/verify-order")
def verify_order(request: VerificationRequest):
    try:
        result = order_service.lookup(request.order_id, request.email)
        return result.model_dump()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
