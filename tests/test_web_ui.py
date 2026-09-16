import json
import os
import sys
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from web_ui import app

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
        "---\nid: software/devops/pytest-configuration\ncanonical_question: How to configure pytest\ndomain: software > devops > testing\n---\n# How to configure pytest\n\nPytest body configuration.\n",
        encoding="utf-8",
    )
    (tmp_path / "software" / "devops" / "pytest-fixtures.md").write_text(
        "---\nid: software/devops/pytest-fixtures\ncanonical_question: How to use pytest fixtures\ndomain: software > devops > testing\n---\n# How to use pytest fixtures\n\nFixtures body.\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("KNOWLEDGELIB_PATH", str(tmp_path))
    return tmp_path


@pytest.fixture
def client(repo):
    return TestClient(app)


def test_index_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "KnowledgeLib" in response.text
    assert "Search" in response.text


def test_search_returns_expected_units(client):
    response = client.get("/search?q=pytest&top_k=3")
    assert response.status_code == 200
    assert "software/devops/pytest-configuration" in response.text
    assert "How to configure pytest" in response.text


def test_search_empty_query(client):
    response = client.get("/search?q=")
    assert response.status_code == 200
    assert "software/devops/pytest-configuration" not in response.text


def test_search_not_found(client):
    response = client.get("/search?q=completelyunrelatedqueryxyz")
    assert response.status_code == 200
    assert "No knowledge units found" in response.text


def test_get_unit_standalone_page(client):
    response = client.get("/unit/software/devops/pytest-configuration")
    assert response.status_code == 200
    assert "How to configure pytest" in response.text
    assert "Pytest body configuration" in response.text
    assert "Back to Search" in response.text


def test_get_unit_htmx_partial(client):
    response = client.get(
        "/unit/software/devops/pytest-configuration",
        headers={"HX-Request": "true"},
    )
    assert response.status_code == 200
    assert "How to configure pytest" in response.text
    assert "Pytest body configuration" in response.text
    # Should be partial, not full page
    assert "Back to Search" not in response.text


def test_get_unit_with_md_extension(client):
    response = client.get("/unit/software/devops/pytest-configuration.md")
    assert response.status_code == 200
    assert "How to configure pytest" in response.text


def test_get_unit_not_found(client):
    response = client.get("/unit/nonexistent/unit/path")
    assert response.status_code == 404
