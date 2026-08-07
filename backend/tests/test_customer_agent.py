import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.customer_agent import CustomerSupportAgent


class CustomerSupportAgentTests(unittest.TestCase):
    def test_balance_inquiry_uses_customer_account_data(self):
        agent = CustomerSupportAgent()
        result = agent._execute("What is my account balance?", {"customer_id": "CUST0001", "name": "Allison Hill"})

        self.assertEqual(result["intent"], "balance inquiry")
        self.assertIn("balance", result["reply"].lower())
        self.assertIn("68701.09", result["reply"])
        self.assertIn("account records", result["reply"].lower())

    def test_non_banking_query_is_rejected(self):
        agent = CustomerSupportAgent()
        result = agent._execute("Tell me a joke", {"customer_id": "CUST0001", "name": "Allison Hill"})

        self.assertEqual(result["intent"], "unknown request")
        self.assertIn("banking", result["reply"].lower())


if __name__ == "__main__":
    unittest.main()
