"""
knowledge_search.py

- Lightweight keyword + fuzzy matching over KnowledgeRepository.
- Returns top-N candidate records with scores and matched snippets.
"""
from typing import List, Dict, Any, Optional, Tuple
from difflib import SequenceMatcher
import re
import math
import logging

from knowledge_loader import KnowledgeRepository

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def _tokenize(text: str) -> List[str]:
    # simple tokenization: lowercase words
    return re.findall(r"\w+", text.lower())


def _token_overlap_score(query_tokens: List[str], text_tokens: List[str]) -> float:
    if not query_tokens or not text_tokens:
        return 0.0
    set_q = set(query_tokens)
    set_t = set(text_tokens)
    overlap = set_q & set_t
    # normalized by min(len(q), len(t)) to avoid bias from long texts
    denom = max(1, min(len(set_q), len(set_t)))
    return len(overlap) / denom


def _fuzzy_ratio(a: str, b: str) -> float:
    # difflib ratio in 0..1
    return SequenceMatcher(None, a, b).ratio()


class KnowledgeSearch:
    """
    Search engine over in-memory knowledge.

    Scoring combines:
      - token overlap (importance for exact keyword matches)
      - fuzzy ratio (for approximate matches)
    """

    def __init__(self, repo: KnowledgeRepository):
        self.repo = repo

    def search(self, query: str, top_n: int = 5, source_filter: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        if not query:
            return []
        q = query.strip().lower()
        q_tokens = _tokenize(q)
        results: List[Tuple[float, Dict[str, Any]]] = []
        for source, idx, record in self.repo.filter_by_source(source_filter):
            text = self.repo.get_index_text(source, idx)
            if not text:
                continue
            t_tokens = _tokenize(text)
            overlap = _token_overlap_score(q_tokens, t_tokens)
            fuzzy = _fuzzy_ratio(q, text)
            # Score combination: give more weight to overlap for precision
            score = 0.6 * overlap + 0.4 * fuzzy
            # small boost if query words appear in key fields (id, name)
            boost = 0.0
            for k in ("id", "name", "customer_id", "account_number"):
                if isinstance(record.get(k), str) and record[k].lower() in q:
                    boost += 0.15
            score = max(0.0, min(1.0, score + boost))
            if score > 0:
                results.append((score, {
                    "source": source,
                    "index": idx,
                    "record": record,
                    "score": round(score, 4),
                    "snippet": self._make_snippet(q_tokens, text)
                }))
        # sort descending by score, then by source/name
        results.sort(key=lambda x: (-x[0], x[1].get("source", "")))
        top = [r for _, r in results[:top_n]]
        logger.debug("Search(%s) -> %d results (top %d)", query, len(results), top_n)
        return top

    def _make_snippet(self, q_tokens: List[str], text: str, max_len: int = 200) -> str:
        # Try to find a window containing query tokens
        if not q_tokens:
            return text[:max_len] + ("..." if len(text) > max_len else "")
        lower = text.lower()
        best_pos = None
        for token in q_tokens:
            pos = lower.find(token)
            if pos >= 0:
                best_pos = pos
                break
        if best_pos is None:
            return text[:max_len] + ("..." if len(text) > max_len else "")
        start = max(0, best_pos - 50)
        snippet = text[start:start + max_len]
        if start > 0:
            snippet = "..." + snippet
        if len(text) > start + max_len:
            snippet = snippet + "..."
        return snippet
