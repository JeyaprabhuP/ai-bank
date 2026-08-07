import logging
from agents.base_agent import BaseAgent
from agents.llm_provider import get_llm_provider
from services import data_loader as dl
from services.faq_service import FAQService
from services.transaction_service import TransactionService

logger = logging.getLogger("banking_ai_platform")


class CustomerSupportAgent(BaseAgent):
    name = "Customer Support Agent"

    def __init__(self):
        super().__init__()
        self.session_memory = {}

    def _execute(self, message: str, customer: dict, fraud_result: dict = None, session_id: str = None, conversation_history: list = None):
        if fraud_result and fraud_result.get("triggered"):
            priority = fraud_result["assessment"]["priority"]
            action = fraud_result["assessment"]["recommended_action"]
            if priority in ("Critical", "High"):
                reply = (
                    f"I've reviewed the activity you described and flagged it as {priority} risk "
                    f"(score {fraud_result['assessment']['risk_score']}/100). "
                    f"Our recommended action is: {action}. "
                    "I've alerted our Fraud team and opened a support ticket so this is handled right away. "
                    "You will not be held liable for confirmed unauthorized charges."
                )
            else:
                reply = (
                    f"I looked into what you described — it currently scores as {priority} risk "
                    f"({fraud_result['assessment']['risk_score']}/100), so no immediate account action is needed, "
                    "but I've logged it and our team will keep monitoring your account."
                )
            return {"reply": reply, "intent": "fraud_report", "source": None}

        text = (message or "").strip()
        if not text:
            return {"reply": "Please tell me what banking help you need.", "intent": "unknown request", "source": None}

        intent = self._detect_intent(text)
        if not self._is_banking_related(text, intent):
            return {
                "reply": "I am a banking customer support assistant and can only help with banking-related queries.",
                "intent": "unknown request",
                "source": None,
            }

        customer_id = customer.get("customer_id") if customer else None
        if intent in {"balance inquiry", "account inquiry", "transaction inquiry", "fraud reporting", "card blocking", "loan inquiry", "policy inquiry", "complaint registration"} and not customer_id:
            return {
                "reply": "I can help with that, but I need your customer ID before I can access account-specific information.",
                "intent": intent,
                "source": None,
            }

        context = self._build_context(customer_id, text, intent)
        history = self._get_history(session_id, conversation_history)
        system_prompt = (
            "Answer only banking-related questions."
            "Use only the provided banking context."
            "Never fabricate balances, transactions, or customer information."
            "If required information is missing, state that it is unavailable."
            "Recommend escalation to a human agent when appropriate."
            "Detect signs of fraud and advise the customer to secure their account."
            "Maintain a professional, empathetic, and concise tone."
            "Preserve customer privacy and never disclose another customer's information."
            )
        prompt = self._build_prompt(text, intent, context, history)

        try:
            provider = get_llm_provider()
            reply = provider.generate(system_prompt, prompt)
        except Exception as exc:
            logger.exception("LLM generation failed")
            reply = self._fallback_reply(intent, context)

        if session_id:
            self.session_memory[session_id] = history + [{"role": "assistant", "content": reply}]

        return {"reply": reply, "intent": intent, "source": context.get("source")}

    def _detect_intent(self, text: str) -> str:
        lowered = text.lower()
        if any(k in lowered for k in ["hi", "hello", "hey", "good morning", "good afternoon"]):
            return "greeting"
        if any(k in lowered for k in ["balance", "available balance", "account balance"]):
            return "balance inquiry"
        if any(k in lowered for k in ["transaction", "transactions", "statement", "recent purchases"]):
            return "transaction inquiry"
        if any(k in lowered for k in ["account", "profile", "details"]):
            return "account inquiry"
        if any(k in lowered for k in ["fraud", "suspicious", "unauthorized", "stolen", "not me"]):
            return "fraud reporting"
        if any(k in lowered for k in ["block card", "freeze card", "lost card", "disable card"]):
            return "card blocking"
        if any(k in lowered for k in ["loan", "mortgage", "credit"]):
            return "loan inquiry"
        if any(k in lowered for k in ["policy", "fee", "interest", "terms"]):
            return "policy inquiry"
        if any(k in lowered for k in ["complaint", "issue", "problem", "angry"]):
            return "complaint registration"
        return "unknown request"

    def _is_banking_related(self, text: str, intent: str) -> bool:
        banking_terms = ["account", "balance", "transaction", "fraud", "card", "loan", "policy", "payment", "bank", "complaint", "deposit", "withdraw"]
        return intent != "unknown request" or any(term in text.lower() for term in banking_terms)

    def _build_context(self, customer_id: str, text: str, intent: str):
        if intent == "transaction inquiry" and customer_id:
            txns = TransactionService.list_transactions(customer_id, limit=5)
            return {
                "source": "transactions.csv",
                "summary": f"Recent transactions for {customer_id}: " + "; ".join(
                    f"{t['amount']} {t['currency']} at {t['merchant_category']}" for t in txns[:3]
                ),
            }

        if intent == "balance inquiry" and customer_id:
            accounts = [a for a in dl.load_accounts() if a["customer_id"] == customer_id]
            if accounts:
                total = sum(a["balance"] for a in accounts)
                return {"source": "accounts.json", "summary": f"Total available balance is {total:.2f} USD across {len(accounts)} account(s)."}
            return {"source": "accounts.json", "summary": "No matching account data was found for that customer ID."}

        if intent == "policy inquiry":
            faq_matches = FAQService.search(text)
            top = faq_matches[0] if faq_matches else None
            return {"source": "faq.json", "summary": top["answer"] if top else "No policy answer found."}

        return {"source": None, "summary": "No extra account context was needed."}

    def _build_prompt(self, text: str, intent: str, context: dict, history: list):
        history_text = "\n".join(f"{item['role']}: {item['content']}" for item in history[-4:])
        return (
            f"User question: {text}\n"
            f"Detected intent: {intent}\n"
            f"Conversation history:\n{history_text}\n"
            f"Customer context summary:\n{context.get('summary', '')}\n"
            "Answer as a helpful banking support assistant and keep the response concise."
        )

    def _get_history(self, session_id: str, conversation_history: list):
        if conversation_history:
            return conversation_history
        if session_id and session_id in self.session_memory:
            return self.session_memory[session_id]
        return []

    def _fallback_reply(self, intent: str, context: dict) -> str:
        summary = context.get("summary", "")
        if intent == "balance inquiry" and summary:
            return f"I’m unable to reach the live AI service right now, but I can still confirm from your account records that {summary.lower()}."
        if intent == "transaction inquiry" and summary:
            return f"I’m unable to reach the live AI service right now, but I can still summarize the latest activity from your account records: {summary}."
        if summary:
            return f"I’m unable to reach the live AI service right now, but I can still help from the available banking context: {summary}."
        return "I’m here to help with your banking questions. Please tell me what you need."
