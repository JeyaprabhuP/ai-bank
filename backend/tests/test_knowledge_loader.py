import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from knowledge import knowledge_loader as kl


class TestKnowledgeLoader(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self._write_json("policies.json", [
            {"policy_id": "P1", "title": "Fee Policy", "text": "Overdraft fees are 25 USD."}
        ])
        self._write_json("faq.json", {"faq": [
            {"faq_id": "F1", "question": "How do I reset password?", "answer": "Use Settings > Security."}
        ]})
        self._write_json("empty.json", [])
        kl.load_knowledge_base(self.tmpdir.name, force_reload=True)

    def tearDown(self):
        self.tmpdir.cleanup()

    def _write_json(self, name, content):
        with open(os.path.join(self.tmpdir.name, name), "w", encoding="utf-8") as f:
            json.dump(content, f)

    def test_loads_all_files(self):
        kb = kl.load_knowledge_base(self.tmpdir.name, force_reload=True)
        self.assertEqual(kb.file_count, 3)
        self.assertEqual(kb.record_count, 2)  # empty.json contributes 0

    def test_normalizes_list_and_wrapped_dict_files(self):
        kb = kl.load_knowledge_base(self.tmpdir.name, force_reload=True)
        collections = {r.collection for r in kb.records}
        self.assertIn("policies", collections)
        self.assertIn("faq", collections)

    def test_record_id_extraction(self):
        kb = kl.load_knowledge_base(self.tmpdir.name, force_reload=True)
        ids = {r.id for r in kb.records}
        self.assertIn("P1", ids)
        self.assertIn("F1", ids)

    def test_caches_after_first_load(self):
        kb1 = kl.load_knowledge_base(self.tmpdir.name)
        kb2 = kl.load_knowledge_base(self.tmpdir.name)
        self.assertIs(kb1, kb2)

    def test_missing_dir_returns_empty_kb(self):
        kb = kl.load_knowledge_base("/nonexistent/path/xyz", force_reload=True)
        self.assertEqual(kb.record_count, 0)

    def test_malformed_json_is_skipped_not_fatal(self):
        with open(os.path.join(self.tmpdir.name, "broken.json"), "w") as f:
            f.write("{not valid json")
        kb = kl.load_knowledge_base(self.tmpdir.name, force_reload=True)
        self.assertGreaterEqual(kb.record_count, 2)


if __name__ == "__main__":
    unittest.main()
