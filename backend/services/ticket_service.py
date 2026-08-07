import uuid
from datetime import datetime
from services import data_loader as dl


class TicketService:
    @staticmethod
    def list_tickets(status: str = None, limit: int = 100):
        tickets = dl.load_tickets()
        if status:
            tickets = [t for t in tickets if t["status"].lower() == status.lower()]
        tickets = sorted(tickets, key=lambda t: t["created_at"], reverse=True)
        return tickets[:limit]

    @staticmethod
    def create_ticket(customer_id: str, subject: str, priority: str = "Medium", assigned_agent: str = "Customer Support Agent"):
        tickets = dl.load_tickets()
        new_ticket = {
            "ticket_id": f"TICKET{len(tickets) + 1:04d}-{uuid.uuid4().hex[:4]}",
            "customer_id": customer_id,
            "subject": subject,
            "status": "open",
            "priority": priority,
            "created_at": datetime.utcnow().isoformat(),
            "assigned_agent": assigned_agent,
        }
        tickets.insert(0, new_ticket)
        dl.save_tickets(tickets)
        return new_ticket
