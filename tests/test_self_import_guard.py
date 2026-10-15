import json
import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

import extract_tech_notes as ext  # noqa: E402
import import_knowledge as imp  # noqa: E402


# --- extract_tech_notes: self -> self import (hook Stop R21 chạy ngay trong repo kho tri thức) ---

def _note(path, title="Workday API guide"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"# {title}\n\nTích hợp api workday adapter.\n", encoding="utf-8")


def test_extract_directory_noop_when_src_equals_dest(tmp_path):
    docs = tmp_path / "self-docs"
    _note(docs / "root_note.md")
    _note(docs / "engine" / "inner.md")
    before = sorted(str(p.relative_to(tmp_path)) for p in tmp_path.rglob("*") if p.is_file())

    report = ext.extract_directory(str(docs), str(docs))

    after = sorted(str(p.relative_to(tmp_path)) for p in tmp_path.rglob("*") if p.is_file())
    assert report["extracted"] == 0
    assert report["total_scanned"] == 0
    assert "overlap" in report["skipped_reason"]
    assert before == after, "self-import không được sinh file mới (bản trùng) hay ghi đè"


def test_extract_directory_noop_when_dest_nested_in_src(tmp_path):
    src = tmp_path / "notes"
    _note(src / "a.md")
    report = ext.extract_directory(str(src), str(src / "self-docs"))
    assert report["extracted"] == 0 and "skipped_reason" in report


def test_extract_directory_still_works_for_separate_dirs(tmp_path):
    src, dest = tmp_path / "src", tmp_path / "dest"
    _note(src / "workday_api_guide.md")
    report = ext.extract_directory(str(src), str(dest))
    assert report["extracted"] == 1
    assert "skipped_reason" not in report
    assert (dest / "integration" / "workday-api-guide.md").exists()


def test_extract_directory_skips_generated_memory_index(tmp_path):
    src, dest = tmp_path / "src", tmp_path / "dest"
    _note(src / "MEMORY_INDEX.md", title="KnowledgeLib Memory Index")
    _note(src / "real_note.md")
    report = ext.extract_directory(str(src), str(dest))
    assert report["total_scanned"] == 1
    assert not list(dest.rglob("memory-index.md"))


# --- import_knowledge: chromadb Rust panic không được làm sập ingest ---

class FakePanic(BaseException):
    """Giống pyo3_runtime.PanicException."""


def test_update_catalog_survives_chroma_panic(tmp_path, monkeypatch, capsys):
    (tmp_path / "catalog.json").write_text(
        json.dumps({"schema_version": "1.1", "total_units": 0, "units": []}), encoding="utf-8"
    )
    monkeypatch.setenv("KNOWLEDGELIB_PATH", str(tmp_path))

    import sync_knowledgelib

    def boom(*a, **k):
        raise FakePanic("range start index 10 out of range for slice of length 9")

    monkeypatch.setattr(sync_knowledgelib, "reindex_chromadb", boom)

    imp.update_catalog_and_vector_db(new_unit_entries=[{"id": "x/y", "canonical_question": "q"}])

    saved = json.loads((tmp_path / "catalog.json").read_text(encoding="utf-8"))
    assert [u["id"] for u in saved["units"]] == ["x/y"], "catalog phải được ghi dù vector sync panic"
    assert "index_health.py --fix" in capsys.readouterr().out


def test_update_catalog_does_not_swallow_keyboard_interrupt(tmp_path, monkeypatch):
    (tmp_path / "catalog.json").write_text(json.dumps({"units": []}), encoding="utf-8")
    monkeypatch.setenv("KNOWLEDGELIB_PATH", str(tmp_path))
    import sync_knowledgelib

    def interrupted(*a, **k):
        raise KeyboardInterrupt()

    monkeypatch.setattr(sync_knowledgelib, "reindex_chromadb", interrupted)
    with pytest.raises(KeyboardInterrupt):
        imp.update_catalog_and_vector_db(new_unit_entries=[])
