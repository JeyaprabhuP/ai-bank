import os
import tempfile
import json
from knowledge_loader import KnowledgeRepository
from knowledge_search import KnowledgeSearch

def test_loader_and_search(tmp_path):
    # create mock_data dir with a sample file
    d = tmp_path / "mock_data"
    d.mkdir()
    data = [
        {"id": "p1", "title": "International Transfer Fees", "content": "Flat $15 plus 0.5%"},
        {"id": "p2", "title": "Domestic Transfer Fees", "content": "$1 per transfer"}
    ]
    fp = d / "policies.json"
    fp.write_text(json.dumps(data))
    repo = KnowledgeRepository(d)
    repo.load()
    assert "policies" in repo.get_sources()
    ks = KnowledgeSearch(repo)
    results = ks.search("international transfer fee", top_n=2)
    assert len(results) >= 1
    assert results[0]["source"] == "policies"
    assert "International" in str(results[0]["record"]["title"])
