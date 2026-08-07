"""
chat_service.py

Coordinates the end-to-end workflow:

    User Question
        -> Search Historical Data   (knowledge_search.py)
        -> Build Prompt             (prompt_builder.py)
        -> Call LLM                 (agents.llm_provider)
        -> Return Response (+ metadata: records used, confidence)

This is the single entry point other code — agents/customer_agent.py,
an API route, a CLI, etc. — should call to get a knowledge-grounded
reply. It intentionally does not import anything from the agents/
package except `get_llm_provider`, so it has no circular-import risk
and can be reused outside the agent flow (e.g. a standalone /chat
endpoint) too.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from agents.llm_provider import get_llm_provider

from .knowledge_loader import load_knowledge_base
from .knowledge_search import SearchResult, search
from .prompt_builder import build_prompt

logger = logging.getLogger("banking_ai_platform")

# Load once at import time so the first real request isn't slowed down
# by a cold-start file scan.
load_knowledge_base()


@dataclass
class ChatResponse:
    reply: str
    grounded: bool                       # True if any historical record was used
    used_records: List[Dict] = field(default_factory=list)
    top_confidence: float = 0.0
    collections_searched: Optional[List[str]] = None


def _serialize(results: List[SearchResult]) -> List[Dict]:
    return [
        {
            "source": r.record.source,
            "collection": r.record.collection,
            "id": r.record.id,
            "score": r.score,
            "matched_terms": r.matched_terms,
        }
        for r in results
    ]


def answer(
    user_question: str,
    history: Optional[List[Dict[str, str]]] = None,
    collections: Optional[List[str]] = None,
    top_k: int = 5,
) -> ChatResponse:
    """
    Full pipeline for one turn: search -> build prompt -> call LLM.

    collections: optional list to scope retrieval to specific mock_data
    files, e.g. ["policies", "faq"] for a policy-inquiry intent. Pass
    None to search everything.
    """
    results = search(user_question, top_k=top_k, collections=collections)

    if results:
        logger.info(
            "chat_service: used records "
            + ", ".join(f"{r.record.source}:{r.record.id}({r.score:.2f})" for r in results)
        )

    prompt = build_prompt(user_question, results, history=history)

    try:
        provider = get_llm_provider()
        reply = provider.generate(prompt["system_prompt"], prompt["user_prompt"])
    except Exception:
        logger.exception("chat_service: LLM generation failed")
        if results:
            best = results[0].record
            reply = (
                "I'm unable to reach the AI service right now, but based on our "
                f"records ({best.source}): {best.text[:300]}"
            )
        else:
            reply = "I'm unable to reach the AI service right now. Please try again shortly."

    return ChatResponse(
        reply=reply,
        grounded=bool(results),
        used_records=_serialize(results),
        top_confidence=results[0].score if results else 0.0,
        collections_searched=collections,
    )
