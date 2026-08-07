"""
LLM abstraction layer.

By default this runs in MOCK mode (no API key needed) so the whole demo
works out of the box. Set OPENAI_API_KEY (and optionally OPENAI_MODEL) to
switch to real OpenAI calls. To point at Azure OpenAI or a local Ollama
instance instead, add a new provider class below implementing
`generate(system_prompt, user_prompt)` and select it in `get_llm_provider()`.
"""
import os
import random
from dotenv import load_dotenv

load_dotenv()


class LLMProvider:
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        raise NotImplementedError


class MockLLMProvider(LLMProvider):
    """Deterministic, template-based responses. No network calls."""

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        opener = random.choice([
            "Thanks for reaching out.",
            "I understand your concern.",
            "Got it — let me help with that.",
        ])
        context = (user_prompt or "").strip()
        return f"{opener} {context[:140]}".strip() or opener


class OpenAIProvider(LLMProvider):
    def __init__(self, model: str = None):
        from openai import OpenAI
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.model = model or os.environ.get("OPENAI_MODEL") or os.environ.get("LLM_MODEL", "gpt-4o-mini")

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=400,
        )
        return response.choices[0].message.content


class OllamaProvider(LLMProvider):
    """Example of swapping in a local model. Requires `requests` and a running Ollama server."""

    def __init__(self, model: str = None, base_url: str = None):
        self.model = model or os.environ.get("OPENAI_MODEL", "llama3")
        self.base_url = base_url or os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        import requests
        resp = requests.post(
            f"{self.base_url}/api/generate",
            json={"model": self.model, "prompt": f"{system_prompt}\n\n{user_prompt}", "stream": False},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json().get("response", "")


def get_llm_provider() -> LLMProvider:
    backend = os.environ.get("LLM_BACKEND", "auto").lower()
    if backend == "mock":
        return MockLLMProvider()
    if backend == "ollama":
        return OllamaProvider()
    if backend == "openai" or (backend == "auto" and os.environ.get("OPENAI_API_KEY")):
        try:
            return OpenAIProvider()
        except Exception:
            return MockLLMProvider()
    return MockLLMProvider()
