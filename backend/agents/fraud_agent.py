from agents.base_agent import BaseAgent
from services.fraud_service import FraudService


class FraudDetectionAgent(BaseAgent):
    name = "Fraud Detection Agent"

    FRAUD_KEYWORDS = [
        "suspicious", "fraud", "unauthorized", "didn't make this",
        "stolen", "hacked", "another country", "unrecognized",
        "not me", "scam", "phishing",
    ]

    def is_fraud_related(self, message: str) -> bool:
        text = message.lower()
        return any(k in text for k in self.FRAUD_KEYWORDS)

    def _execute(self, message: str, customer: dict):
        assessment = FraudService.score_transaction_description(message, customer)
        alert = None
        if assessment["priority"] in ("Critical", "High"):
            alert = FraudService.create_alert_from_chat(customer, message)
        return {
            "triggered": True,
            "assessment": assessment,
            "alert": alert,
        }
