from pydantic import BaseModel, Field
from typing import Optional, List

# Represents a single message in a conversation with a role and content
class Message(BaseModel):
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str

# Request schema for sending a chat message to the agent
class ChatRequest(BaseModel):
    messages: List[Message]
    session_id: Optional[str] = None

# Response schema returned by the chat endpoint
class ChatResponse(BaseModel):
    session_id: str
    message: Message
    state: str
    evidence: Optional[dict] = None
    tool_calls: Optional[List[dict]] = None
    suggested_questions: Optional[List[str]] = None

# Request schema for direct order verification
class VerificationRequest(BaseModel):
    order_id: str
    email: str

# Response schema for a successful order lookup
class OrderLookupResponse(BaseModel):
    order_id: str
    status: str
    order_date: str
    estimated_delivery: Optional[str]
    shipping_method: Optional[str]
    tracking_number: Optional[str]
    items: List[dict]
    subtotal_cents: int
    shipping_cents: int
    discount_cents: int
    total_cents: int
    customer: dict

# Response schema for health check endpoint
class HealthResponse(BaseModel):
    status: str

# Request schema for calling a tool by name with arguments
class ToolCallRequest(BaseModel):
    tool_name: str
    arguments: dict

# Response schema for tool execution results
class ToolCallResponse(BaseModel):
    success: bool
    result: Optional[dict] = None
    error: Optional[str] = None
