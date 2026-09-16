import json
import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agent_client import KnowledgeLibClient  # noqa: E402

CATALOG = {
    "units": [
        {
            "id": "software/devops/pytest-configuration",
            "canonical_question": "How to configure pytest",
            "aliases": ["pytest config", "pytest.ini"],
            "domain": "software > devops > testing",
            "entity_type": "book_chapter",
        }
    ]
}


@pytest.fixture
def client(tmp_path):
    (tmp_path / "software" / "devops").mkdir(parents=True)
    (tmp_path / "catalog.json").write_text(json.dumps(CATALOG), encoding="utf-8")
    (tmp_path / "software" / "devops" / "pytest-configuration.md").write_text(
        "# How to configure pytest\n\nBody.", encoding="utf-8"
    )
    return KnowledgeLibClient(data_path=str(tmp_path))


def test_no_chroma_db_falls_back_to_keyword_search(client):
    assert client.collection is None
    results = client.keyword_search("pytest config", top_k=3)
    assert len(results) == 1
    assert results[0]["id"] == "software/devops/pytest-configuration"
    assert results[0]["search_type"] == "keyword"


def test_search_uses_keyword_fallback_when_no_vector_collection(client):
    results = client.search("pytest config")
    assert results and results[0]["search_type"] == "keyword"


def test_query_and_get_returns_success_schema(client):
    res = client.query_and_get("pytest config")
    assert res["status"] == "success"
    assert res["unit_id"] == "software/devops/pytest-configuration"
    assert "How to configure pytest" in res["content"]
    assert res["should_fallback_to_llm"] is False


def test_query_and_get_not_found_schema(client):
    res = client.query_and_get("totally unrelated nonsense query xyz")
    assert res["status"] == "not_found"
    assert res["should_fallback_to_llm"] is True


def test_is_knowledge_query_whitelist(client):
    assert client.is_knowledge_query("best laptop 2025") is True
    assert client.is_knowledge_query("xin chào bạn khỏe không") is False
