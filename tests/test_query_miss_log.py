import json
import os
import sys
from unittest.mock import patch

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from query_miss_log import log_miss


def test_log_miss_appends_jsonl_line(tmp_path):
    log_miss("abc", "test_source", repo_dir=str(tmp_path))

    log_file = tmp_path / "query_misses.jsonl"
    assert log_file.exists()

    lines = log_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1

    entry = json.loads(lines[0])
    assert entry["query"] == "abc"
    assert entry["source"] == "test_source"
    assert "timestamp" in entry


def test_log_miss_appends_multiple_calls(tmp_path):
    log_miss("query 1", "source_a", repo_dir=str(tmp_path))
    log_miss("query 2", "source_b", repo_dir=str(tmp_path))

    log_file = tmp_path / "query_misses.jsonl"
    lines = log_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2

    e1 = json.loads(lines[0])
    e2 = json.loads(lines[1])
    assert e1["query"] == "query 1"
    assert e1["source"] == "source_a"
    assert e2["query"] == "query 2"
    assert e2["source"] == "source_b"


def test_log_miss_never_raises_on_unwritable_path(tmp_path, monkeypatch):
    # Path where writing fails (e.g. repo_dir points inside a regular file)
    dummy_file = tmp_path / "not_a_dir"
    dummy_file.write_text("hello", encoding="utf-8")
    invalid_repo_dir = str(dummy_file / "subfolder")

    # Should not raise any exception
    log_miss("test query", "source_err", repo_dir=invalid_repo_dir)

    # Also test when open raises OSError via monkeypatch
    with patch("builtins.open", side_effect=OSError("Permission denied")):
        log_miss("another test query", "source_err", repo_dir=str(tmp_path))
