"""
knowledge/ — local, no-vector-DB historical knowledge layer for the
chat assistant.

Modules:
    knowledge_loader  — loads & caches JSON files from mock_data/
    knowledge_search   — keyword + fuzzy relevance search over the cache
    prompt_builder      — assembles the enriched LLM prompt
    chat_service         — orchestrates the full turn: search -> prompt -> LLM
"""
from .chat_service import ChatResponse, answer  # noqa: F401
