import json
import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

import agent_client  # noqa: E402


class FakePanic(BaseException):
    """Giống pyo3_runtime.PanicException: kế thừa BaseException, không phải Exception."""


@pytest.fixture
def repo(tmp_path):
    (tmp_path / "catalog.json").write_text(
        json.dumps({"units": [{
            "id": "software/a", "canonical_question": "How to configure pytest",
            "aliases": ["pytest config"], "domain": "software > testing", "entity_type": "how_to",
        }]}),
        encoding="utf-8",
    )
    (tmp_path / ".chroma_db").mkdir()
    return tmp_path


def test_init_survives_chroma_panic_and_falls_back_to_keyword(repo, monkeypatch, capsys):
    class FakeChroma:
        @staticmethod
        def PersistentClient(path):
            raise FakePanic("range start index 10 out of range for slice of length 9")

    monkeypatch.setattr(agent_client, "chromadb", FakeChroma, raising=False)
    monkeypatch.setattr(agent_client, "CHROMADB_AVAILABLE", True)

    client = agent_client.KnowledgeLibClient(str(repo))

    assert client.collection is None
    assert client.chroma_client is None
    assert "Falling back" in capsys.readouterr().out
    hits = client.search("pytest config", top_k=1)
    assert hits and hits[0]["id"] == "software/a"


def test_vector_search_survives_panic_at_query_time(repo):
    client = agent_client.KnowledgeLibClient(str(repo))

    class PanickingCollection:
        def query(self, **kwargs):
            raise FakePanic("boom")

    client.collection = PanickingCollection()
    assert client.vector_search("anything") == []


def test_keyboard_interrupt_is_not_swallowed(repo, monkeypatch):
    class FakeChroma:
        @staticmethod
        def PersistentClient(path):
            raise KeyboardInterrupt()

    monkeypatch.setattr(agent_client, "chromadb", FakeChroma, raising=False)
    monkeypatch.setattr(agent_client, "CHROMADB_AVAILABLE", True)
    with pytest.raises(KeyboardInterrupt):
        agent_client.KnowledgeLibClient(str(repo))
