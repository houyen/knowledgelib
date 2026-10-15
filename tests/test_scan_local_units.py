import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

import sync_knowledgelib as sk  # noqa: E402


def _unit(path, uid):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"---\nid: {uid}\ncanonical_question: Q {uid}\naliases:\n- a\nentity_type: how_to\n"
        f"domain: x\nlast_verified: 2026-01-01\n---\n\nbody\n",
        encoding="utf-8",
    )


def test_nested_dir_named_docs_is_scanned_but_top_level_docs_is_not(tmp_path):
    _unit(tmp_path / "self-docs" / "docs" / "plan-phase-a.md", "self-docs/docs/plan-phase-a")
    _unit(tmp_path / "software" / "src" / "layout.md", "software/src/layout")
    _unit(tmp_path / "docs" / "internal.md", "docs/internal")
    _unit(tmp_path / "src" / "notes.md", "src/notes")

    ids = {u["id"] for u in sk.scan_local_units(str(tmp_path))}

    assert "self-docs/docs/plan-phase-a" in ids
    assert "software/src/layout" in ids
    assert "docs/internal" not in ids
    assert "src/notes" not in ids


def test_generated_memory_index_is_not_a_unit(tmp_path):
    _unit(tmp_path / "self-docs" / "MEMORY_INDEX.md", "self-docs/MEMORY_INDEX")
    _unit(tmp_path / "self-docs" / "real.md", "self-docs/real")
    ids = {u["id"] for u in sk.scan_local_units(str(tmp_path))}
    assert ids == {"self-docs/real"}
