"""
knowledge_loader.py

- Load all JSON files from a mock_data directory.
- Merge into a unified KnowledgeRepository with caching.
- Precompute a searchable "text" field per record.

Usage:
    repo = KnowledgeRepository("/path/to/mock_data")
    repo.load()  # loads and caches data
    repo.get_sources()  # list of sources
    repo.iter_records()  # yields (source, record_id, record_dict)
"""
from pathlib import Path
import json
import logging
from typing import Dict, Any, Iterator, Tuple, List
import threading

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class KnowledgeRepository:
    """
    A simple in-memory repository that loads JSON files once and caches them.
    Each file becomes a "source" whose records are a list or dictionary.
    """

    def __init__(self, data_dir: str | Path):
        self.data_dir = Path(data_dir)
        self._loaded = False
        self._lock = threading.RLock()
        self._data: Dict[str, List[Dict[str, Any]]] = {}
        self._index_texts: Dict[Tuple[str, int], str] = {}  # (source, idx) -> consolidated text

    def load(self) -> None:
        """Load all .json files in the directory. Idempotent."""
        with self._lock:
            if self._loaded:
                logger.debug("KnowledgeRepository: already loaded, skipping.")
                return
            if not self.data_dir.exists() or not self.data_dir.is_dir():
                raise FileNotFoundError(f"mock_data directory not found: {self.data_dir}")
            for p in sorted(self.data_dir.glob("*.json")):
                try:
                    with p.open("r", encoding="utf-8") as fh:
                        obj = json.load(fh)
                    src = p.stem  # file name without extension
                    records = self._normalize_records(obj)
                    self._data[src] = records
                    for i, rec in enumerate(records):
                        self._index_texts[(src, i)] = self._make_search_text(rec)
                    logger.info("Loaded %d records from %s", len(records), p.name)
                except Exception as e:
                    logger.exception("Failed to load %s: %s", p, e)
            self._loaded = True

    def _normalize_records(self, obj: Any) -> List[Dict[str, Any]]:
        """Normalize loaded JSON into a list of dict records."""
        if obj is None:
            return []
        if isinstance(obj, list):
            return [r if isinstance(r, dict) else {"value": r} for r in obj]
        if isinstance(obj, dict):
            # Convert dict-of-dict into list with id field when possible
            if all(isinstance(v, dict) for v in obj.values()):
                outgoing = []
                for key, val in obj.items():
                    rec = dict(val)
                    # attach id if not present
                    if "id" not in rec:
                        rec["id"] = key
                    outgoing.append(rec)
                return outgoing
            # otherwise single dict -> wrap
            return [obj]
        # fallback
        return [{"value": obj}]

    def _make_search_text(self, record: Dict[str, Any]) -> str:
        """Concatenate values into a lowercase string for simple search."""
        parts = []
        for k, v in record.items():
            if v is None:
                continue
            if isinstance(v, (str, int, float)):
                parts.append(str(v))
            elif isinstance(v, list):
                parts.extend(str(x) for x in v)
            elif isinstance(v, dict):
                parts.extend(str(x) for x in v.values())
            else:
                parts.append(str(v))
        return " ".join(parts).lower()

    def get_sources(self) -> List[str]:
        self._ensure_loaded()
        return list(self._data.keys())

    def iter_records(self) -> Iterator[Tuple[str, int, Dict[str, Any]]]:
        """Yield (source, index, record) for each record."""
        self._ensure_loaded()
        for src, recs in self._data.items():
            for i, r in enumerate(recs):
                yield src, i, r

    def get_index_text(self, source: str, idx: int) -> str:
        self._ensure_loaded()
        return self._index_texts.get((source, idx), "")

    def filter_by_source(self, sources: List[str] | None) -> Iterator[Tuple[str, int, Dict[str, Any]]]:
        self._ensure_loaded()
        if not sources:
            yield from self.iter_records()
            return
        for src in sources:
            recs = self._data.get(src, [])
            for i, r in enumerate(recs):
                yield src, i, r

    def _ensure_loaded(self) -> None:
        if not self._loaded:
            raise RuntimeError("KnowledgeRepository not loaded. Call .load() before use.")
