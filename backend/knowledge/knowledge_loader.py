"""
knowledge_loader.py

Loads every JSON file from the mock_data/ directory into a single,
in-memory knowledge repository at application startup, and caches it
so later calls are free.

Zero external dependencies, deliberately simple: each JSON file becomes
one "collection" (named after the file, minus extension). Every record
in a collection is normalized into a `Record`:

    Record(
        source="policies.json",
        collection="policies",
        id="<record id if present, else index>",
        text="<flattened searchable text of the record>",
        data={...original record...},
    )

This flat, source-tagged shape is what makes knowledge_search.py
possible without a vector index: we can keyword/fuzzy match over
`text` and always know exactly which file + record produced a hit.

--- Future migration to a vector DB / RAG ---
Keep `load_knowledge_base()` and the `Record` shape exactly as they
are. In knowledge_search.py, replace the keyword scoring with an
embedding call over each `record.text` at load time (store vectors in
FAISS/Pinecone/Chroma keyed by `record.source` + `record.id`), then
replace `search()`'s body with a similarity query. Nothing in
prompt_builder.py or chat_service.py needs to change, since they only
depend on the `Record`/`SearchResult` shapes, not on how scoring works.
"""
from __future__ import annotations

import glob
import json
import logging
import os
import threading
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger("banking_ai_platform")

DEFAULT_MOCK_DATA_DIR = os.environ.get(
    "MOCK_DATA_DIR",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mock_data"),
)


@dataclass
class Record:
    """A single normalized, searchable unit of historical knowledge."""
    source: str            # e.g. "policies.json"
    collection: str        # e.g. "policies"
    id: str                # record id, or "<collection>_<index>" if none present
    text: str              # flattened text used for keyword/fuzzy search
    data: Dict[str, Any]   # original record, untouched


@dataclass
class KnowledgeBase:
    """In-memory cache of every record loaded from mock_data/."""
    records: List[Record] = field(default_factory=list)
    by_collection: Dict[str, List[Record]] = field(default_factory=dict)
    loaded_from: str = ""
    file_count: int = 0
    record_count: int = 0


_lock = threading.Lock()
_cache: Optional[KnowledgeBase] = None


def _flatten(value: Any, parts: List[str]) -> None:
    """Recursively flatten any JSON value into a list of text fragments."""
    if value is None:
        return
    if isinstance(value, dict):
        for k, v in value.items():
            parts.append(str(k))
            _flatten(v, parts)
    elif isinstance(value, list):
        for item in value:
            _flatten(item, parts)
    else:
        parts.append(str(value))


_ID_KEY_CANDIDATES = (
    "id", "customer_id", "account_id", "transaction_id",
    "policy_id", "faq_id", "rule_id", "ticket_id", "session_id",
)


def _record_id(collection: str, index: int, raw: Any) -> str:
    if isinstance(raw, dict):
        for key in _ID_KEY_CANDIDATES:
            if key in raw and raw[key] not in (None, ""):
                return str(raw[key])
    return f"{collection}_{index}"


def _normalize_file(path: str) -> List[Record]:
    """Load a single JSON file and normalize its contents into Records."""
    collection = os.path.splitext(os.path.basename(path))[0]
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        logger.error(f"knowledge_loader: failed to load {path}: {exc}")
        return []

    # Files may be: a top-level list of records, a dict wrapping a list
    # under a key (e.g. {"policies": [...]}), or a single record dict.
    items: List[Any]
    if isinstance(raw, list):
        items = raw
    elif isinstance(raw, dict):
        list_values = [v for v in raw.values() if isinstance(v, list)]
        items = list_values[0] if len(list_values) == 1 else [raw]
    else:
        items = [raw]

    records: List[Record] = []
    for i, item in enumerate(items):
        parts: List[str] = []
        _flatten(item, parts)
        text = " ".join(parts).strip()
        if not text:
            continue
        records.append(Record(
            source=os.path.basename(path),
            collection=collection,
            id=_record_id(collection, i, item),
            text=text,
            data=item if isinstance(item, dict) else {"value": item},
        ))
    return records


def load_knowledge_base(mock_data_dir: str = None, force_reload: bool = False) -> KnowledgeBase:
    """
    Load (or return the cached) knowledge base built from every *.json
    file under `mock_data_dir`. Thread-safe; loads from disk only once
    unless `force_reload=True`.
    """
    global _cache
    mock_data_dir = mock_data_dir or DEFAULT_MOCK_DATA_DIR

    with _lock:
        if _cache is not None and not force_reload:
            return _cache

        kb = KnowledgeBase(loaded_from=mock_data_dir)
        if not os.path.isdir(mock_data_dir):
            logger.warning(f"knowledge_loader: mock_data dir not found: {mock_data_dir}")
            _cache = kb
            return kb

        json_paths = sorted(glob.glob(os.path.join(mock_data_dir, "*.json")))
        for path in json_paths:
            file_records = _normalize_file(path)
            collection = os.path.splitext(os.path.basename(path))[0]
            kb.by_collection.setdefault(collection, []).extend(file_records)
            kb.records.extend(file_records)

        kb.file_count = len(json_paths)
        kb.record_count = len(kb.records)
        logger.info(
            f"knowledge_loader: loaded {kb.record_count} records from "
            f"{kb.file_count} files in {mock_data_dir}"
        )
        _cache = kb
        return kb


def get_knowledge_base() -> KnowledgeBase:
    """Convenience accessor: loads on first call, cached afterwards."""
    return load_knowledge_base()


def reload_knowledge_base() -> KnowledgeBase:
    """Force a fresh reload from disk (e.g. after mock data changes)."""
    return load_knowledge_base(force_reload=True)
