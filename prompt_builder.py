"""
prompt_builder.py

- Construct the Chat prompt sent to OpenAI.
- Compose:
    - system instructions
    - relevant historical knowledge (top matches)
    - previous chat history (list of messages)
    - current user question
- Returns a messages list for chat-based models.
"""
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

SYSTEM_PROMPT = """You are an intelligent AI assistant specialized in this application.

Always use the provided historical knowledge first.
Treat the historical knowledge as the primary source of truth.
Use conversation history to maintain context.
If the answer cannot be found in the historical knowledge, use your general knowledge and clearly state that the information is not available in the trained dataset.
Never fabricate customer data or policy information."""


def build_prompt_messages(
    user_question: str,
    top_records: List[Dict[str, Any]],
    chat_history: Optional[List[Dict[str, str]]] = None,
    show_scores: bool = True,
) -> List[Dict[str, str]]:
    """
    Returns messages list suitable for OpenAI chat API.

    - chat_history: list of {"role": "user|assistant", "content": "..."} representing prior conversation.
    - top_records: list of dicts from KnowledgeSearch with keys source, index, record, score, snippet.
    """
    messages: List[Dict[str, str]] = []
    messages.append({"role": "system", "content": SYSTEM_PROMPT})

    # Add relevant historical knowledge
    if top_records:
        kb_lines = ["Relevant historical knowledge (sorted by relevance):"]
        for i, r in enumerate(top_records, start=1):
            src = r.get("source")
            score = r.get("score")
            rec = r.get("record")
            snippet = r.get("snippet", "")
            kb_lines.append(f"{i}. Source: {src} | Relevance: {score}")
            # pretty-print record (limited)
            try:
                # show a small JSON-like rendering
                import json
                rec_preview = json.dumps(rec, ensure_ascii=False, indent=2)
                kb_lines.append(rec_preview)
            except Exception:
                kb_lines.append(str(rec))
            if snippet:
                kb_lines.append(f"Snippet: {snippet}")
        kb_text = "\n\n".join(kb_lines)
    else:
        kb_text = "No relevant historical knowledge found."

    messages.append({"role": "system", "content": kb_text})

    # Append chat history so model has context
    if chat_history:
        for m in chat_history:
            role = m.get("role", "user")
            content = m.get("content", "")
            messages.append({"role": role, "content": content})

    # Final user message contains the explicit question and an instruction to prefer historical facts
    user_block = (
        f"User question: {user_question}\n\n"
        "Please answer using the historical knowledge above when available. "
        "If you must use general knowledge, clearly say that the trained dataset had no matching facts, and avoid fabricating any customer or policy data."
    )
    messages.append({"role": "user", "content": user_block})
    logger.debug("Built prompt with %d messages (kb items=%d)", len(messages), len(top_records))
    return messages
