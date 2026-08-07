from fastapi import APIRouter, Depends
from models.schemas import TicketCreateRequest
from utils.security import get_current_user
from services.ticket_service import TicketService

router = APIRouter(tags=["Tickets"])


@router.post("/ticket")
def create_ticket(payload: TicketCreateRequest, user=Depends(get_current_user)):
    return TicketService.create_ticket(
        customer_id=payload.customer_id,
        subject=payload.subject,
        priority=payload.priority,
    )


@router.get("/tickets")
def list_tickets(status: str = None, user=Depends(get_current_user)):
    return TicketService.list_tickets(status=status)
