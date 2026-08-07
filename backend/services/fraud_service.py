import random
import uuid
from datetime import datetime
from services import data_loader as dl


def compute_risk_score(amount, is_foreign, new_device, failed_login_attempts, merchant_category=""):
    score = 0
    if amount > 5000:
        score += 30
    elif amount > 1500:
        score += 15
    if is_foreign:
        score += 25
    if new_device:
        score += 20
    score += min(failed_login_attempts * 5, 20)
    if merchant_category in ("wire_transfer", "atm_withdrawal"):
        score += 10
    return min(score, 100)


def priority_for(score):
    if score >= 90:
        return "Critical"
    if score >= 70:
        return "High"
    if score >= 40:
        return "Medium"
    return "Low"


def action_for(priority):
    return {
        "Critical": "Freeze Card",
        "High": "Verify with Customer",
        "Medium": "Monitor Account",
        "Low": "No Action Required",
    }[priority]


class FraudService:
    @staticmethod
    def list_alerts(
        priority: str = None,
        status: str = None,
        alert_id: str = None,
        customer_id: str = None,
        customer_name: str = None,
        resolved_by: str = None,
        recommended_action: str = None,
        source: str = None,
        chat_initiated: bool = None,
        min_risk_score: int = None,
        max_risk_score: int = None,
        limit: int = 200,
    ):
        alerts = dl.load_fraud_alerts()
        if priority:
            alerts = [a for a in alerts if a["priority"].lower() == priority.lower()]
        if status:
            alerts = [a for a in alerts if a["status"].lower() == status.lower()]
        if alert_id:
            alerts = [a for a in alerts if alert_id.lower() in a.get("alert_id", "").lower()]
        if customer_id:
            alerts = [a for a in alerts if customer_id.lower() in a.get("customer_id", "").lower()]
        if customer_name:
            alerts = [a for a in alerts if customer_name.lower() in a.get("customer_name", "").lower()]
        if resolved_by:
            alerts = [a for a in alerts if resolved_by.lower() == (a.get("resolved_by") or "").lower()]
        if recommended_action:
            alerts = [a for a in alerts if recommended_action.lower() in a.get("recommended_action", "").lower()]
        if source:
            alerts = [a for a in alerts if source.lower() in a.get("source", "").lower()]
        if chat_initiated is not None:
            alerts = [a for a in alerts if bool(a.get("chat_initiated")) is chat_initiated]
        if min_risk_score is not None:
            alerts = [a for a in alerts if a.get("risk_score", 0) >= min_risk_score]
        if max_risk_score is not None:
            alerts = [a for a in alerts if a.get("risk_score", 0) <= max_risk_score]
        alerts = sorted(alerts, key=lambda a: a["risk_score"], reverse=True)
        return alerts[:limit]

    @staticmethod
    def get_alert(alert_id: str):
        alerts = dl.load_fraud_alerts()
        return next((a for a in alerts if a["alert_id"] == alert_id), None)

    @staticmethod
    def get_alert_details(alert_id: str):
        alert = FraudService.get_alert(alert_id)
        if not alert:
            return None

        decision_trail = [
            {
                "actor": "Fraud Detection Agent",
                "decision": alert.get("recommended_action"),
                "summary": f'Risk score {alert.get("risk_score")}/100 classified as {alert.get("priority")}',
                "timestamp": alert.get("created_at"),
            }
        ]

        if alert.get("chat_initiated"):
            decision_trail.append(
                {
                    "actor": "Supervisor Agent",
                    "decision": "Initiated proactive customer chat",
                    "summary": f'Chat initiated by {alert.get("chat_initiated_by", "system")}',
                    "timestamp": alert.get("chat_initiated_at"),
                }
            )

        if alert.get("supervisor_action"):
            decision_trail.append(
                {
                    "actor": "Supervisor Agent",
                    "decision": alert.get("supervisor_action"),
                    "summary": alert.get("supervisor_note") or "Supervisor action recorded",
                    "timestamp": alert.get("action_at") or alert.get("resolved_at"),
                }
            )

        related_tickets = []
        customer_id = alert.get("customer_id")
        if customer_id:
            for ticket in dl.load_tickets():
                if ticket.get("customer_id") == customer_id:
                    related_tickets.append(ticket)

        related_tickets = sorted(related_tickets, key=lambda t: t.get("created_at", ""), reverse=True)[:5]
        decision_trail = [item for item in decision_trail if item.get("timestamp")]
        decision_trail = sorted(decision_trail, key=lambda item: item["timestamp"])

        return {
            "alert": alert,
            "decision_trail": decision_trail,
            "related_tickets": related_tickets,
        }

    @staticmethod
    def score_transaction_description(description: str, customer: dict):
        """
        Heuristic scorer used by the Fraud Agent when a customer describes
        an incident in free text (no structured transaction to look up).
        """
        text = description.lower()
        amount = 500
        is_foreign = any(k in text for k in ["abroad", "another country", "overseas", "foreign", "international"])
        new_device = any(k in text for k in ["new phone", "new device", "different device", "unrecognized device"])
        if any(k in text for k in ["large", "big amount", "thousand", "$5", "$1"]):
            amount = 6000
        failed_logins = customer.get("failed_login_attempts", 0) if customer else 0
        score = compute_risk_score(amount, is_foreign, new_device, failed_logins)
        priority = priority_for(score)
        return {
            "risk_score": score,
            "priority": priority,
            "recommended_action": action_for(priority),
            "factors": {
                "amount_assumed": amount,
                "foreign_activity_mentioned": is_foreign,
                "new_device_mentioned": new_device,
                "failed_login_attempts": failed_logins,
            },
        }

    @staticmethod
    def create_alert_from_chat(customer: dict, description: str):
        result = FraudService.score_transaction_description(description, customer)
        alerts = dl.load_fraud_alerts()
        new_alert = {
            "alert_id": f"ALERT{len(alerts) + 1:04d}-{uuid.uuid4().hex[:4]}",
            "transaction_id": "N/A (reported via chat)",
            "customer_id": customer["customer_id"] if customer else "UNKNOWN",
            "customer_name": customer["name"] if customer else "Unknown",
            "risk_score": result["risk_score"],
            "priority": result["priority"],
            "recommended_action": result["recommended_action"],
            "status": "open",
            "created_at": datetime.utcnow().isoformat(),
            "factors": result["factors"],
            "source": "chat_report",
            "description": description,
        }
        alerts.insert(0, new_alert)
        dl.save_fraud_alerts(alerts)
        return new_alert

    @staticmethod
    def apply_supervisor_action(alert_id: str, action: str, mark_resolved: bool = True, note: str = None):
        alerts = dl.load_fraud_alerts()
        alert = next((a for a in alerts if a["alert_id"] == alert_id), None)
        if not alert:
            return None

        alert["supervisor_action"] = action
        if note:
            alert["supervisor_note"] = note
        alert["action_at"] = datetime.utcnow().isoformat()

        if mark_resolved:
            alert["status"] = "resolved"
            alert["resolved_at"] = datetime.utcnow().isoformat()
            from services.ticket_service import TicketService

            TicketService.resolve_customer_open_tickets(
                alert.get("customer_id"),
                resolution_action=f"Auto-resolved after supervisor action: {action}",
            )
        else:
            alert["status"] = "investigating"

        dl.save_fraud_alerts(alerts)
        return alert

    @staticmethod
    def initiate_chat(alert_id: str, initiated_by: str = None, note: str = None):
        alerts = dl.load_fraud_alerts()
        alert = next((a for a in alerts if a["alert_id"] == alert_id), None)
        if not alert:
            return None

        if (alert.get("status") or "").lower() == "resolved":
            raise ValueError("Cannot initiate chat for a resolved alert")

        alert["chat_initiated"] = True
        alert["chat_initiated_at"] = datetime.utcnow().isoformat()
        if initiated_by:
            alert["chat_initiated_by"] = initiated_by
        if note:
            alert["chat_initiated_note"] = note

        if (alert.get("status") or "").lower() == "open":
            alert["status"] = "investigating"

        dl.save_fraud_alerts(alerts)
        return alert
