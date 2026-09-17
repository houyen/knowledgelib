import json
import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from query_gap_report import aggregate_misses, load_misses, main


def test_aggregate_misses_counts_and_sorts():
    sample_misses = [
        {"query": "kubernetes helm chart", "source": "web_ui"},
        {"query": "  Kubernetes Helm Chart  ", "source": "mcp_search"},
        {"query": "KUBERNETES HELM CHART", "source": "query_and_get"},
        {"query": "docker compose v2", "source": "web_ui"},
        {"query": "docker compose v2", "source": "mcp_search"},
        {"query": "system design interview", "source": "web_ui"},
        {"query": "   ", "source": "web_ui"},
        {"query": None, "source": "web_ui"},
    ]

    aggregated = aggregate_misses(sample_misses)
    assert len(aggregated) == 3
    assert aggregated[0] == ("kubernetes helm chart", 3)
    assert aggregated[1] == ("docker compose v2", 2)
    assert aggregated[2] == ("system design interview", 1)


def test_load_misses_missing_file_returns_empty():
    assert load_misses("/path/khong/ton/tai.jsonl") == []


def test_load_misses_skips_malformed_lines(tmp_path):
    log_file = tmp_path / "query_misses.jsonl"
    content = (
        '{"timestamp": "2026-09-16T00:00:00Z", "query": "query 1", "source": "test"}\n'
        'invalid-json-line-here-not-json\n'
        '{"timestamp": "2026-09-16T00:01:00Z", "query": "query 2", "source": "test"}\n'
        '\n'
    )
    log_file.write_text(content, encoding="utf-8")

    misses = load_misses(str(log_file))
    assert len(misses) == 2
    assert misses[0]["query"] == "query 1"
    assert misses[1]["query"] == "query 2"


def test_main_cli_output(tmp_path, capsys):
    log_file = tmp_path / "query_misses.jsonl"
    log_file.write_text(
        '{"query": "kafka architecture", "source": "web"}\n'
        '{"query": "kafka architecture", "source": "mcp"}\n'
        '{"query": "redis clustering", "source": "agent"}\n',
        encoding="utf-8",
    )

    main(["--log-path", str(log_file), "--top", "10"])
    captured = capsys.readouterr().out
    assert "Top 2 Query Misses" in captured
    assert "kafka architecture" in captured
    assert "redis clustering" in captured


def test_main_cli_empty_file(tmp_path, capsys):
    empty_file = tmp_path / "empty.jsonl"
    main(["--log-path", str(empty_file)])
    captured = capsys.readouterr().out
    assert "Không có query miss nào" in captured
