from fastapi import APIRouter, Depends
from models.schemas import ChatRequest, ChatResponse
from utils.security import get_current_user
from agents.supervisor_agent import SupervisorAgent

router = APIRouter(tags=["Chat"])
supervisor = SupervisorAgent()


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, user=Depends(get_current_user)):
    customer_id = payload.customer_id or user.get("customer_id")
    result = supervisor.run(payload.message, customer_id, session_id=payload.session_id)
    result["session_id"] = payload.session_id
    return result
