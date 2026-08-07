"""
knowledge_search.py

Lightweight, dependency-free keyword + fuzzy search over the
in-memory KnowledgeBase produced by knowledge_loader.py.

No embeddings, no vector DB. The algorithm:
  1. Tokenize the query and each record's text (lowercased, stopwords
     removed).
  2. Score each record by keyword overlap, weighted by an inverse
     document-frequency-style term so rare/specific terms (e.g.
     "overdraft", "ACC-1042") count for more than common ones.
  3. Add a small fuzzy-match bonus (stdlib difflib) for near-misses —
     typos, plurals, minor variants — so "transactoin" still matches
     "transaction".
  4. Return the top-N records sorted by score, optionally filtered to
     specific collections/sources (e.g. only "policies" + "faq").

--- Future migration to a vector DB ---
Replace this module's internals with an embedding similarity query
against your vector index, but keep returning `SearchResult` objects
with the same fields. prompt_builder.py and chat_service.py only
depend on that shape, so they need no changes.
"""
from __future__ import annotations

import logging
import math
import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Dict, List, Optional

from .knowledge_loader import Record, get_knowledge_base

logger = logging.getLogger("banking_ai_platform")

_TOKEN_RE = re.compile(r"[a-z0-9]+")
_STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "do", "does", "did",
    "what", "when", "where", "why", "how", "can", "i", "my", "me", "to",
    "for", "of", "on", "in", "and", "or", "please", "you", "your", "it",
    "this", "that", "with", "be", "have", "has", "about",
}


def _tokenize(text: str) -> List[str]:
    return [t for t in _TOKEN_RE.findall((text or "").lower()) if t not in _STOPWORDS]


@dataclass
class SearchResult:
    record: Record
    score: float          # normalized 0.0 - 1.0 relevance score
    matched_terms: List[str]


def _idf_weights(query_tokens: List[str], records: List[Record]) -> Dict[str, float]:
    n = max(len(records), 1)
    weights: Dict[str, float] = {}
    for term in set(query_tokens):
        doc_freq = sum(1 for r in records if term in r.text.lower())
        weights[term] = math.log((n + 1) / (doc_freq + 1)) + 1.0
    return weights


def _fuzzy_bonus(term: str, text_tokens: set) -> float:
    """Bonus if `term` closely matches a token in the record even without
    an exact substring hit (handles typos / minor variants)."""
    best = 0.0
    for tok in text_tokens:
        if abs(len(tok) - len(term)) > 3:
            continue
        ratio = SequenceMatcher(None, term, tok).ratio()
        if ratio > best:
            best = ratio
    return best if best >= 0.8 else 0.0


def search(
    query: str,
    top_k: int = 5,
    collections: Optional[List[str]] = None,
    min_score: float = 0.05,
) -> List[SearchResult]:
    """
    Return the top_k most relevant Records for `query`.

    collections: optional allow-list of collection names (filenames
    without .json), e.g. ["policies", "faq"], to scope the search to
    specific data sources.
    """
    kb = get_knowledge_base()
    pool = kb.records
    if collections:
        allowed = set(collections)
        pool = [r for r in pool if r.collection in allowed]

    query_tokens = _tokenize(query)
    if not query_tokens or not pool:
        return []

    weights = _idf_weights(query_tokens, pool)
    max_possible = sum(weights.values()) or 1.0

    results: List[SearchResult] = []
    for record in pool:
        text_lower = record.text.lower()
        text_tokens = set(_tokenize(record.text))
        score = 0.0
        matched: List[str] = []
        for term in query_tokens:
            if term in text_lower:
                score += weights[term]
                matched.append(term)
            else:
                bonus = _fuzzy_bonus(term, text_tokens)
                if bonus:
                    score += weights[term] * bonus * 0.6
                    matched.append(f"{term}~")
        normalized = min(score / max_possible, 1.0)
        if normalized >= min_score:
            results.append(SearchResult(record=record, score=round(normalized, 4), matched_terms=matched))

    results.sort(key=lambda r: r.score, reverse=True)
    top = results[:top_k]

    logger.info(
        f"knowledge_search: query={query!r} candidates={len(pool)} "
        f"matches={len(results)} returned={len(top)}"
    )
    return top
