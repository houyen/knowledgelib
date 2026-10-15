import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

import index_health as ih  # noqa: E402


def _write(root, unit_id, body, frontmatter="id: x\n"):
    path = root / f"{unit_id}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{frontmatter}---\n\n{body}\n", encoding="utf-8")


def test_read_body_strips_frontmatter_and_handles_missing(tmp_path):
    _write(tmp_path, "a/one", "hello body")
    assert ih.read_body("a/one", str(tmp_path)) == "hello body"
    assert ih.read_body("a/none", str(tmp_path)) is None


def test_check_drift_reports_missing_stale_and_file(tmp_path):
    _write(tmp_path, "a/one", "x")
    _write(tmp_path, "a/two", "y")
    units = [{"id": "a/one"}, {"id": "a/two"}, {"id": "a/ghost"}]
    d = ih.check_drift(units, ["a/one", "a/old"], str(tmp_path))
    assert d["missing_in_vector"] == ["a/ghost", "a/two"]
    assert d["stale_in_vector"] == ["a/old"]
    assert d["missing_file"] == ["a/ghost"]
    assert d["vector_available"] is True


def test_check_drift_vector_unavailable_is_not_reported_as_missing(tmp_path):
    _write(tmp_path, "a/one", "x")
    d = ih.check_drift([{"id": "a/one"}], None, str(tmp_path))
    assert d["vector_available"] is False
    assert d["missing_in_vector"] == []


def test_find_identical_bodies_groups_only_real_duplicates(tmp_path):
    _write(tmp_path, "d/v1", "same text", frontmatter="id: d/v1\n")
    _write(tmp_path, "d/v2", "same text", frontmatter="id: d/v2\n")
    _write(tmp_path, "d/other", "different")
    _write(tmp_path, "d/empty1", "")
    _write(tmp_path, "d/empty2", "")
    units = [{"id": i} for i in ("d/v1", "d/v2", "d/other", "d/empty1", "d/empty2")]
    assert ih.find_identical_bodies(units, str(tmp_path)) == [["d/v1", "d/v2"]]


def test_find_near_duplicates_threshold_and_order():
    pytest.importorskip("numpy")
    ids = ["a", "b", "c"]
    vecs = [[1.0, 0.0], [0.999, 0.01], [0.0, 1.0]]
    pairs = ih.find_near_duplicates(ids, vecs, threshold=0.95)
    assert len(pairs) == 1
    assert pairs[0][1:] == ("a", "b")
    assert ih.find_near_duplicates(ids, vecs, threshold=0.9999999) == []
    assert ih.find_near_duplicates(["a"], [[1.0, 0.0]]) == []


def test_has_problems_ignores_near_dup_only():
    clean = {"drift": {"missing_in_vector": [], "stale_in_vector": [], "missing_file": []},
             "identical_body": [], "near_dup": [(0.99, "a", "b")]}
    assert ih.has_problems(clean) is False
    clean["identical_body"] = [["a", "b"]]
    assert ih.has_problems(clean) is True


def test_main_strict_exit_codes(tmp_path, capsys):
    import json

    _write(tmp_path, "a/one", "same")
    _write(tmp_path, "a/two", "same")
    (tmp_path / "catalog.json").write_text(
        json.dumps({"units": [{"id": "a/one"}, {"id": "a/two"}]}), encoding="utf-8"
    )
    assert ih.main(["--dir", str(tmp_path)]) == 0
    assert ih.main(["--dir", str(tmp_path), "--strict"]) == 1
    assert ih.main(["--dir", str(tmp_path / "missing")]) == 2
