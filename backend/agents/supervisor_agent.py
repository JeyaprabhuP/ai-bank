"""
Supervisor Agent — orchestrates the multi-agent flow.

Flow (mirrors the LangGraph-style graph described in the spec):

    Customer message
        -> Supervisor Agent (intent detection)
        -> Fraud Detection Agent   (if fraud-related)
        -> Customer Support Agent  (drafts the reply)
        -> Compliance Agent        (checks regulatory rules)
        -> Unified AI Response
        -> Support Ticket created
        -> Dashboard updated (alerts/tickets are persisted to mock_data)

This is implemented as plain Python for zero-dependency portability.
To run it as an actual LangGraph StateGraph, wrap each `_execute` call
below as a graph node and connect them with the same edges — the
business logic doesn't need to change.
"""
import time
import logging
from agents.base_agent import BaseAgent
from agents.fraud_agent import FraudDetectionAgent
from agents.customer_agent import CustomerSupportAgent
from agents.compliance_agent import ComplianceAgent
from services.ticket_service import TicketService
from services.customer_service import CustomerService

logger = logging.getLogger("banking_ai_platform")


class SupervisorAgent(BaseAgent):
    name = "Supervisor Agent"

    def __init__(self):
        self.fraud_agent = FraudDetectionAgent()
        self.customer_agent = CustomerSupportAgent()
        self.compliance_agent = ComplianceAgent()

    def _execute(self, message: str, customer_id: str = None, session_id: str = None):
        trace = []
        t0 = time.time()

        customer = CustomerService.get_customer(customer_id) if customer_id else None
        trace.append({"step": "intent_detection", "agent": self.name})

        fraud_result = None
        if self.fraud_agent.is_fraud_related(message):
            fraud_result = self.fraud_agent.run(message, customer)
            trace.append({"step": "fraud_analysis", "agent": self.fraud_agent.name, "result": fraud_result["assessment"]})

        support_result = self.customer_agent.run(message, customer, fraud_result, session_id=session_id)
        trace.append({"step": "draft_response", "agent": self.customer_agent.name, "intent": support_result["intent"]})

        compliance_result = self.compliance_agent.run(fraud_result=fraud_result)
        trace.append({"step": "compliance_check", "agent": self.compliance_agent.name, "rules_triggered": len(compliance_result["triggered_rules"])})

        ticket = None
        if support_result["intent"] == "fraud_report":
            priority = fraud_result["assessment"]["priority"] if fraud_result else "Medium"
            ticket = TicketService.create_ticket(
                customer_id=customer_id or "UNKNOWN",
                subject=f"Fraud report: {message[:60]}",
                priority=priority,
                assigned_agent=self.fraud_agent.name,
            )
            trace.append({"step": "ticket_created", "ticket_id": ticket["ticket_id"]})

        elapsed_ms = round((time.time() - t0) * 1000, 2)
        logger.info(
            f"agent=SupervisorAgent status=success execution_time_ms={elapsed_ms} "
            f"selected_agents={[t['agent'] for t in trace if 'agent' in t]} "
            f"risk_score={fraud_result['assessment']['risk_score'] if fraud_result else 'n/a'}"
        )

        return {
            "reply": support_result["reply"],
            "intent": support_result["intent"],
            "fraud_assessment": fraud_result["assessment"] if fraud_result else None,
            "fraud_alert": fraud_result["alert"] if fraud_result else None,
            "compliance": compliance_result,
            "ticket": ticket,
            "agent_trace": trace,
            "execution_time_ms": elapsed_ms,
        }
