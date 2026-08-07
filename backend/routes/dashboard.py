import random
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from utils.security import get_current_user
from services.fraud_service import FraudService
from services.ticket_service import TicketService
from services import data_loader as dl

router = APIRouter(tags=["Dashboard"])


@router.get("/dashboard")
def dashboard(user=Depends(get_current_user)):
    alerts = dl.load_fraud_alerts()
    tickets = dl.load_tickets()

    critical_alerts = [a for a in alerts if a["priority"] == "Critical"]
    open_tickets = [t for t in tickets if t["status"] in ("open", "in_progress")]
    resolved_tickets = [t for t in tickets if t["status"] in ("resolved", "closed")]

    priority_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    for a in alerts:
        priority_counts[a["priority"]] = priority_counts.get(a["priority"], 0) + 1

    # Fraud trend: alerts per day for the last 14 days (synthetic bucketing for demo)
    today = datetime.utcnow().date()
    trend = []
    for i in range(13, -1, -1):
        day = today - timedelta(days=i)
        count = sum(1 for a in alerts if a["created_at"][:10] == day.isoformat())
        trend.append({"date": day.isoformat(), "count": count})

    customers = dl.load_customers()
    top_risk_customers = sorted(
        [{"customer_id": c["customer_id"], "name": c["name"], "risk_profile": c["risk_profile"]} for c in customers],
        key=lambda c: {"high": 3, "medium": 2, "low": 1}.get(c["risk_profile"], 0),
        reverse=True,
    )[:5]

    return {
        "active_chats": random.randint(3, 18),
        "critical_alerts": len(critical_alerts),
        "open_tickets": len(open_tickets),
        "resolved_tickets": len(resolved_tickets),
        "avg_ai_response_time_ms": random.randint(180, 650),
        "fraud_trend": trend,
        "alert_priority_breakdown": priority_counts,
        "top_risk_customers": top_risk_customers,
        "system_health": {
            "api": "healthy",
            "agents": "healthy",
            "data_layer": "healthy",
        },
        "agent_status": [
            {"name": "Supervisor Agent", "status": "online"},
            {"name": "Customer Support Agent", "status": "online"},
            {"name": "Fraud Detection Agent", "status": "online"},
            {"name": "Compliance Agent", "status": "online"},
        ],
    }
