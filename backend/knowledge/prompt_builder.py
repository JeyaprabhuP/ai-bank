"""
prompt_builder.py

Assembles the final prompt sent to the LLM provider from:
  - a fixed system prompt (trained-data-first instructions)
  - relevant historical knowledge (from knowledge_search.py)
  - recent conversation history
  - the current user question

Kept separate from chat_service.py so the prompt format can be tuned
or unit-tested independently of the retrieval/orchestration logic.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from .knowledge_search import SearchResult

SYSTEM_PROMPT = (
    "You are an intelligent AI assistant specialized in this application.\n\n"
    "Always use the provided historical knowledge first.\n"
    "Treat the historical knowledge as the primary source of truth.\n"
    "Use conversation history to maintain context.\n"
    "If the answer cannot be found in the historical knowledge, use your "
    "general knowledge and clearly state that the information is not "
    "available in the trained dataset.\n"
    "Never fabricate customer data or policy information."
)


def format_history(history: Optional[List[Dict[str, str]]], max_turns: int = 6) -> str:
    if not history:
        return "(no prior conversation)"
    trimmed = history[-max_turns:]
    return "\n".join(f"{turn.get('role', 'user')}: {turn.get('content', '')}" for turn in trimmed)


def format_knowledge(results: List[SearchResult]) -> str:
    if not results:
        return "(no relevant historical records found)"
    lines = []
    for i, r in enumerate(results, start=1):
        lines.append(
            f"[{i}] source={r.record.source} id={r.record.id} "
            f"relevance={r.score:.2f}\n    {r.record.text[:400]}"
        )
    return "\n".join(lines)


def build_prompt(
    user_question: str,
    search_results: List[SearchResult],
    history: Optional[List[Dict[str, str]]] = None,
) -> Dict[str, str]:
    """
    Returns {"system_prompt": ..., "user_prompt": ...}, ready to hand
    straight to any LLMProvider.generate(system_prompt, user_prompt).
    """
    knowledge_block = format_knowledge(search_results)
    history_block = format_history(history)

    user_prompt = (
        f"Historical knowledge (primary source of truth):\n{knowledge_block}\n\n"
        f"Conversation history:\n{history_block}\n\n"
        f"Current user question:\n{user_question}\n\n"
        "Instructions: Prioritize the historical knowledge above. If it "
        "does not contain the answer, answer from general knowledge and "
        "say so explicitly."
    )
    return {"system_prompt": SYSTEM_PROMPT, "user_prompt": user_prompt}
