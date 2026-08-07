import json
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from knowledge import knowledge_loader as kl


class TestChatService(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        with open(os.path.join(self.tmpdir.name, "policies.json"), "w") as f:
            json.dump([
                {"policy_id": "P1", "title": "Overdraft Fee Policy",
                 "text": "Overdraft transactions incur a flat fee of 25 USD."},
            ], f)
        kl.load_knowledge_base(self.tmpdir.name, force_reload=True)
        # Import after the knowledge base is seeded so chat_service's
        # module-level load_knowledge_base() call reuses the cache.
        global chat_service
        from knowledge import chat_service

    def tearDown(self):
        self.tmpdir.cleanup()

    @patch("knowledge.chat_service.get_llm_provider")
    def test_answer_grounds_reply_in_matching_record(self, mock_get_provider):
        mock_provider = mock_get_provider.return_value
        mock_provider.generate.return_value = "The overdraft fee is 25 USD."

        response = chat_service.answer("What is the overdraft fee?")

        self.assertTrue(response.grounded)
        self.assertGreater(response.top_confidence, 0)
        self.assertEqual(response.used_records[0]["id"], "P1")
        self.assertEqual(response.reply, "The overdraft fee is 25 USD.")

    @patch("knowledge.chat_service.get_llm_provider")
    def test_answer_ungrounded_when_no_match(self, mock_get_provider):
        mock_provider = mock_get_provider.return_value
        mock_provider.generate.return_value = "General answer."

        response = chat_service.answer("tell me about quantum computing")

        self.assertFalse(response.grounded)
        self.assertEqual(response.used_records, [])

    @patch("knowledge.chat_service.get_llm_provider")
    def test_answer_falls_back_gracefully_on_llm_error(self, mock_get_provider):
        mock_get_provider.side_effect = RuntimeError("provider unavailable")

        response = chat_service.answer("What is the overdraft fee?")

        self.assertIn("unable to reach the AI service", response.reply)
        self.assertTrue(response.grounded)  # records were still found

    @patch("knowledge.chat_service.get_llm_provider")
    def test_collections_filter_is_passed_through(self, mock_get_provider):
        mock_provider = mock_get_provider.return_value
        mock_provider.generate.return_value = "ok"

        response = chat_service.answer("overdraft fee", collections=["policies"])

        self.assertEqual(response.collections_searched, ["policies"])


if __name__ == "__main__":
    unittest.main()
