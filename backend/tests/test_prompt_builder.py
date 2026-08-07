import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from knowledge.knowledge_loader import Record
from knowledge.knowledge_search import SearchResult
from knowledge import prompt_builder as pb


class TestPromptBuilder(unittest.TestCase):
    def _fake_result(self):
        record = Record(
            source="policies.json", collection="policies", id="P1",
            text="Overdraft fees are 25 USD per occurrence.", data={},
        )
        return SearchResult(record=record, score=0.87, matched_terms=["overdraft", "fee"])

    def test_build_prompt_includes_all_sections(self):
        prompt = pb.build_prompt(
            "What is the overdraft fee?",
            [self._fake_result()],
            history=[{"role": "user", "content": "Hi"}, {"role": "assistant", "content": "Hello!"}],
        )
        self.assertIn("system_prompt", prompt)
        self.assertIn("user_prompt", prompt)
        self.assertIn("Overdraft fees are 25 USD", prompt["user_prompt"])
        self.assertIn("What is the overdraft fee?", prompt["user_prompt"])
        self.assertIn("Hello!", prompt["user_prompt"])

    def test_system_prompt_instructs_grounding(self):
        prompt = pb.build_prompt("test", [])
        self.assertIn("primary source of truth", prompt["system_prompt"])
        self.assertIn("Never fabricate", prompt["system_prompt"])

    def test_no_results_states_none_found(self):
        prompt = pb.build_prompt("unrelated question", [])
        self.assertIn("no relevant historical records found", prompt["user_prompt"])

    def test_no_history_states_none(self):
        prompt = pb.build_prompt("q", [self._fake_result()], history=None)
        self.assertIn("no prior conversation", prompt["user_prompt"])

    def test_history_trims_to_max_turns(self):
        history = [{"role": "user", "content": f"msg{i}"} for i in range(10)]
        formatted = pb.format_history(history, max_turns=3)
        self.assertNotIn("msg0", formatted)
        self.assertIn("msg9", formatted)


if __name__ == "__main__":
    unittest.main()
