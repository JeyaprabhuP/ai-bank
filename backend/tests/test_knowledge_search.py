import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from knowledge import knowledge_loader as kl
from knowledge import knowledge_search as ks


class TestKnowledgeSearch(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        with open(os.path.join(self.tmpdir.name, "policies.json"), "w") as f:
            json.dump([
                {"policy_id": "P1", "title": "Overdraft Fee Policy",
                 "text": "Overdraft transactions incur a flat fee of 25 USD."},
                {"policy_id": "P2", "title": "Interest Rate Policy",
                 "text": "Savings accounts earn 2.1% APY compounded monthly."},
            ], f)
        with open(os.path.join(self.tmpdir.name, "faq.json"), "w") as f:
            json.dump([
                {"faq_id": "F1", "question": "How do I dispute a charge?",
                 "answer": "Open the Transactions tab and select Dispute within 60 days."},
            ], f)
        kl.load_knowledge_base(self.tmpdir.name, force_reload=True)

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_finds_relevant_record(self):
        results = ks.search("what is the overdraft fee")
        self.assertTrue(any(r.record.id == "P1" for r in results))
        self.assertGreater(results[0].score, 0)

    def test_ranks_best_match_first(self):
        results = ks.search("overdraft fee amount")
        self.assertEqual(results[0].record.id, "P1")

    def test_collection_filter(self):
        results = ks.search("dispute charge", collections=["policies"])
        self.assertFalse(any(r.record.collection == "faq" for r in results))

    def test_no_match_returns_empty(self):
        results = ks.search("quantum entanglement spaceship")
        self.assertEqual(results, [])

    def test_fuzzy_match_handles_typo(self):
        results = ks.search("overdaft fee")  # typo: overdaft
        self.assertTrue(any(r.record.id == "P1" for r in results))

    def test_top_k_limits_results(self):
        results = ks.search("policy", top_k=1)
        self.assertLessEqual(len(results), 1)

    def test_empty_query_returns_empty(self):
        self.assertEqual(ks.search(""), [])


if __name__ == "__main__":
    unittest.main()
