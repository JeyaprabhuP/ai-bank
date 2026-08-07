"""
chat_service.py

- Coordinates the flow:
    - Load knowledge
    - Search historical data
    - Build prompt
    - Call OpenAI
    - Return response + metadata (which historical records were used)
"""
from typing import List, Dict, Any, Optional
import logging

from knowledge_loader import KnowledgeRepository
from knowledge_search import KnowledgeSearch
from prompt_builder import build_prompt_messages
from openai_client import OpenAIClient

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class ChatService:
    def __init__(self, mock_data_dir: str, openai_client: Optional[OpenAIClient] = None):
        self.repo = KnowledgeRepository(mock_data_dir)
        self.repo.load()
        self.search = KnowledgeSearch(self.repo)
        self.openai = openai_client or OpenAIClient()
        # In-memory conversation memory keyed by session_id
        self._conversations: Dict[str, List[Dict[str, str]]] = {}

    def get_conversation(self, session_id: str) -> List[Dict[str, str]]:
        return self._conversations.setdefault(session_id, [])

    def handle_user_query(
        self,
        session_id: str,
        user_question: str,
        top_n: int = 5,
        source_filter: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Process one user query:
          - Search knowledge
          - Build prompt (system + kb + conversation)
          - Call OpenAI
          - Store assistant reply in conversation memory
          - Return assistant content + metadata
        """
        conv = self.get_conversation(session_id)
        # search
        top = self.search.search(user_question, top_n=top_n, source_filter=source_filter or None)
        # build prompt
        messages = build_prompt_messages(user_question, top, chat_history=conv)
        # call
        try:
            resp = self.openai.chat(messages)
            # extract assistant text (supporting the usual response structure)
            choices = resp.get("choices", [])
            if choices:
                assistant_text = choices[0].get("message", {}).get("content", "")
            else:
                assistant_text = resp.get("message", {}).get("content", "")
        except Exception as e:
            logger.exception("Error during OpenAI call: %s", e)
            assistant_text = "Error: failed to get response from language model."

        # Save messages to conversation memory
        conv.append({"role": "user", "content": user_question})
        conv.append({"role": "assistant", "content": assistant_text})

        result = {
            "assistant": assistant_text,
            "used_records": [{"source": r["source"], "index": r["index"], "score": r["score"]} for r in top],
            "conversation": conv,
        }
        return result
