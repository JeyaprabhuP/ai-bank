from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from utils.security import get_current_user
from services import data_loader as dl

router = APIRouter(tags=["Dashboard"])


def _is_ai_resolution(action: str, resolved_by: str = None):
    if (resolved_by or "").lower() == "ai":
        return True
    if not action:
        return False
    normalized = action.lower()
    return "auto-resolved" in normalized or "resolved by ai" in normalized or "ai agent" in normalized


@router.get("/dashboard")
def dashboard(user=Depends(get_current_user)):
    alerts = dl.load_fraud_alerts()
    tickets = dl.load_tickets()

    active_alerts = [a for a in alerts if (a.get("status") or "").lower() in ("open", "investigating")]
    proactive_alerts = [
        a
        for a in alerts
        if (a.get("status") or "").lower() in ("open", "investigating")
        and (a.get("priority") or "").lower() in ("critical", "high")
        and a.get("chat_initiated") is True
    ]

    critical_alerts = [a for a in active_alerts if (a.get("priority") or "").lower() == "critical"]
    open_tickets = [t for t in tickets if t["status"] in ("open", "in_progress")]
    # Mirrors chat queue behavior: active customer queries + proactive initiated alerts.
    active_chats = len(open_tickets) + len(proactive_alerts)

    # Deterministic workload-based response time estimate (no random drift between refreshes).
    avg_ai_response_time_ms = 180 + min(420, active_chats * 9)

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

    all_resolutions = []
    for ticket in tickets:
        if ticket.get("resolved_at"):
            all_resolutions.append(
                {
                    "kind": "ticket",
                    "id": ticket.get("ticket_id"),
                    "customer_id": ticket.get("customer_id"),
                    "title": ticket.get("subject"),
                    "status": ticket.get("status"),
                    "resolution_action": ticket.get("resolution_action"),
                    "resolution_reason": ticket.get("ai_resolution_reason"),
                    "resolved_by": ticket.get("resolved_by"),
                    "timestamp": ticket.get("resolved_at"),
                }
            )

    for alert in alerts:
        if alert.get("resolved_at") or alert.get("action_at"):
            all_resolutions.append(
                {
                    "kind": "alert",
                    "id": alert.get("alert_id"),
                    "customer_id": alert.get("customer_id"),
                    "title": alert.get("recommended_action"),
                    "status": alert.get("status"),
                    "resolution_action": alert.get("supervisor_action"),
                    "resolution_reason": alert.get("ai_resolution_reason") or alert.get("supervisor_note"),
                    "resolved_by": alert.get("resolved_by"),
                    "timestamp": alert.get("resolved_at") or alert.get("action_at"),
                }
            )

    ai_resolutions = [
        item
        for item in all_resolutions
        if _is_ai_resolution(item.get("resolution_action"), item.get("resolved_by"))
    ]
    ai_resolution_count = len(ai_resolutions)
    manual_resolution_count = len(all_resolutions) - ai_resolution_count

    recent_resolutions = sorted(ai_resolutions, key=lambda item: item["timestamp"], reverse=True)[:6]

    return {
        "active_chats": active_chats,
        "critical_alerts": len(critical_alerts),
        "open_tickets": len(open_tickets),
        "avg_ai_response_time_ms": avg_ai_response_time_ms,
        "fraud_trend": trend,
        "alert_priority_breakdown": priority_counts,
        "top_risk_customers": top_risk_customers,
        "recent_resolutions": recent_resolutions,
        "ai_resolution_count": ai_resolution_count,
        "manual_resolution_count": manual_resolution_count,
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
