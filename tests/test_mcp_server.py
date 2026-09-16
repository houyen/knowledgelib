import json
import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

CATALOG = {
    "units": [
        {
            "id": "software/devops/pytest-configuration",
            "canonical_question": "How to configure pytest",
            "aliases": ["pytest config", "pytest.ini"],
            "domain": "software > devops > testing",
            "entity_type": "book_chapter",
        },
        {
            "id": "software/devops/pytest-fixtures",
            "canonical_question": "How to use pytest fixtures",
            "aliases": ["pytest fixture"],
            "domain": "software > devops > testing",
            "entity_type": "book_chapter",
        },
    ]
}


@pytest.fixture
def repo(tmp_path, monkeypatch):
    (tmp_path / "software" / "devops").mkdir(parents=True)
    (tmp_path / "catalog.json").write_text(json.dumps(CATALOG), encoding="utf-8")
    (tmp_path / "software" / "devops" / "pytest-configuration.md").write_text(
        "# How to configure pytest\n\nBody.", encoding="utf-8"
    )
    (tmp_path / "software" / "devops" / "pytest-fixtures.md").write_text(
        "# How to use pytest fixtures\n\nBody.", encoding="utf-8"
    )
    monkeypatch.setenv("KNOWLEDGELIB_PATH", str(tmp_path))
    return tmp_path


def test_knowledgelib_search_returns_multiple_results(repo):
    import importlib

    import agent_client
    importlib.reload(agent_client)
    import mcp_server
    importlib.reload(mcp_server)

    results = mcp_server.knowledgelib_search("pytest", top_k=3)
    assert len(results) == 2
    assert all("score" in r or "distance" in r for r in results)


def test_knowledgelib_get_content_reads_file(repo):
    import importlib

    import agent_client
    importlib.reload(agent_client)
    import mcp_server
    importlib.reload(mcp_server)

    content = mcp_server.knowledgelib_get_content("software/devops/pytest-configuration")
    assert "How to configure pytest" in content


def test_knowledgelib_ingest_reports_missing_file(repo):
    import mcp_server

    result = mcp_server.knowledgelib_ingest(file_path="/no/such/file.pdf")
    assert result["status"] == "error"
