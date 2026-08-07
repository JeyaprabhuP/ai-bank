"""
openai_client.py

Small wrapper around the OpenAI Chat API so that it's easy to mock in tests.
"""
import os
from typing import List, Dict, Any, Optional
import logging
import openai

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class OpenAIClient:
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OpenAI API key is not set. Calls will fail unless a mock is used.")
        openai.api_key = api_key
        self.model = model

    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.0, max_tokens: int = 512) -> Dict[str, Any]:
        """
        Send messages to OpenAI ChatCompletion API and return the response dict.
        """
        try:
            resp = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return resp
        except Exception as e:
            logger.exception("OpenAI API call failed: %s", e)
            raise
