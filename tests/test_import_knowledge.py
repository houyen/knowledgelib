import json
import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from import_knowledge import (
    compute_content_hash,
    find_duplicate_unit_id,
    run_import,
    save_units_to_tree,
    scan_and_collect_all_markdown_units,
    update_catalog_and_vector_db,
)


@pytest.fixture
def temp_repo(tmp_path, monkeypatch):
    monkeypatch.setenv("KNOWLEDGELIB_PATH", str(tmp_path))
    catalog_file = tmp_path / "catalog.json"
    catalog_file.write_text(json.dumps({"units": [], "total_units": 0}), encoding="utf-8")
    return tmp_path


def test_update_catalog_respects_knowledgelib_path(temp_repo):
    """Task 0: Ensure update_catalog_and_vector_db operates in temp repo and does not touch real catalog."""
    real_catalog_path = os.path.join(os.path.dirname(__file__), "..", "catalog.json")
    real_mtime_before = os.path.getmtime(real_catalog_path)

    unit_sample = [{
        "num": "01",
        "title": "Config Sample",
        "content": "Sample content for configuration unit."
    }]
    saved = save_units_to_tree(unit_sample, "software/test-domain", "reference", "software > test")
    update_catalog_and_vector_db(saved)

    # Temp catalog updated
    temp_catalog = json.loads((temp_repo / "catalog.json").read_text(encoding="utf-8"))
    assert temp_catalog["total_units"] == 1
    assert temp_catalog["units"][0]["id"] == saved[0]["id"]

    # Real catalog untampered
    assert os.path.getmtime(real_catalog_path) == real_mtime_before


def test_sync_only_ignores_non_knowledge_root_files(temp_repo):
    """Task 1: Non-knowledge markdown root files like AGENTS.md, PHASE5_PLAN.md are ignored."""
    (temp_repo / "AGENTS.md").write_text("# Agents Guidelines\n\nSome guidelines here.", encoding="utf-8")
    (temp_repo / "PHASE5_PLAN.md").write_text("# Phase 5 Plan\n\nPlan details.", encoding="utf-8")
    (temp_repo / "README.md").write_text("# Readme\n\nOverview.", encoding="utf-8")

    # Add one valid knowledge unit in a subdirectory
    sub_dir = temp_repo / "software" / "demo"
    sub_dir.mkdir(parents=True)
    (sub_dir / "valid-unit.md").write_text(
        "---\nid: software/demo/valid-unit\ncanonical_question: Valid Unit\n---\n# Valid Unit\n\nReal content.",
        encoding="utf-8",
    )

    units = scan_and_collect_all_markdown_units()
    unit_ids = [u["id"] for u in units]

    assert "AGENTS" not in unit_ids
    assert "PHASE5_PLAN" not in unit_ids
    assert "README" not in unit_ids
    assert "software/demo/valid-unit" in unit_ids


def test_compute_content_hash_normalizes_whitespace():
    """Task 2: Content hashing normalizes whitespace and casing."""
    t1 = "  Hello   World \n\n This is   a TEST!  "
    t2 = "hello world\nthis is a test!\n"
    assert compute_content_hash(t1) == compute_content_hash(t2)


def test_run_import_skips_exact_duplicate_on_second_call(temp_repo):
    """Task 2: Dedup check skips identical content on subsequent import."""
    doc_file = temp_repo / "sample_doc.md"
    doc_file.write_text(
        "Chapter 1: Getting Started\n\nThis is the content for chapter 1.\n\nChapter 2: Advanced Topics\n\nThis is chapter 2.",
        encoding="utf-8",
    )

    # First import
    res1 = run_import(
        str(doc_file),
        domain_path="software/guides/sample",
        domain="software > guides",
        use_llm_split=False,
    )
    assert res1["status"] == "success"
    assert res1["unit_count"] == 2
    assert len(res1["skipped_duplicates"]) == 0

    target_dir = temp_repo / "software" / "guides" / "sample"
    files_after_first = list(target_dir.glob("*.md"))
    assert len(files_after_first) == 2

    # Second import with same file
    res2 = run_import(
        str(doc_file),
        domain_path="software/guides/sample",
        domain="software > guides",
        use_llm_split=False,
    )
    assert res2["status"] == "success"
    assert res2["unit_count"] == 0
    assert len(res2["skipped_duplicates"]) == 2

    files_after_second = list(target_dir.glob("*.md"))
    assert len(files_after_second) == 2  # No new files created


def test_run_import_falls_back_to_regex_when_llm_returns_none(temp_repo, monkeypatch):
    """Task 3: When LLM splitter returns None, fallback to regex splitting."""
    import llm_splitter

    monkeypatch.setattr(llm_splitter, "split_text_with_llm", lambda *args, **kwargs: None)

    doc_file = temp_repo / "chapter_doc.md"
    doc_file.write_text(
        "Chapter 1: First Chapter\n\nContent of first chapter.\n\nChapter 2: Second Chapter\n\nContent of second chapter.",
        encoding="utf-8",
    )

    res = run_import(
        str(doc_file),
        domain_path="software/books/sample",
        domain="software > books",
        use_llm_split=True,
    )
    assert res["status"] == "success"
    assert res["split_method"] == "regex"
    assert res["unit_count"] == 2
