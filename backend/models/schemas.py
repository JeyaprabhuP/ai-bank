from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str
    customer_id: Optional[str] = None


class ChatRequest(BaseModel):
    message: str
    customer_id: Optional[str] = None
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    intent: str
    fraud_assessment: Optional[Dict[str, Any]] = None
    fraud_alert: Optional[Dict[str, Any]] = None
    compliance: Optional[Dict[str, Any]] = None
    ticket: Optional[Dict[str, Any]] = None
    agent_trace: List[Dict[str, Any]] = []
    execution_time_ms: float
    source: Optional[str] = None
    session_id: Optional[str] = None


class TicketCreateRequest(BaseModel):
    customer_id: str
    subject: str
    priority: str = "Medium"
