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
    def list_alerts(priority: str = None, status: str = None, limit: int = 200):
        alerts = dl.load_fraud_alerts()
        if priority:
            alerts = [a for a in alerts if a["priority"].lower() == priority.lower()]
        if status:
            alerts = [a for a in alerts if a["status"].lower() == status.lower()]
        alerts = sorted(alerts, key=lambda a: a["risk_score"], reverse=True)
        return alerts[:limit]

    @staticmethod
    def get_alert(alert_id: str):
        alerts = dl.load_fraud_alerts()
        return next((a for a in alerts if a["alert_id"] == alert_id), None)

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
