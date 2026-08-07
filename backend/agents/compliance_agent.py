from agents.base_agent import BaseAgent
from services.data_loader import load_compliance_rules


class ComplianceAgent(BaseAgent):
    name = "Compliance Agent"

    def _execute(self, fraud_result: dict = None, amount: float = None):
        rules = load_compliance_rules()
        triggered = []
        if amount and amount > 10000:
            triggered.append(next(r for r in rules if r["rule_id"] == "REG-CTR-1"))
        if fraud_result and fraud_result.get("triggered"):
            priority = fraud_result["assessment"]["priority"]
            if priority in ("Critical", "High"):
                triggered.append(next(r for r in rules if r["rule_id"] == "REG-KYC-2"))
            if fraud_result["assessment"]["factors"].get("foreign_activity_mentioned"):
                triggered.append(next(r for r in rules if r["rule_id"] == "REG-AML-3"))
        return {"triggered_rules": triggered, "compliant": True}
