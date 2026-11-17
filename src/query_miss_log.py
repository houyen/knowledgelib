#!/usr/bin/env python3
"""
Module ghi nhận các truy vấn không tìm thấy kết quả (query misses)
vào file query_misses.jsonl tại thư mục gốc của kho dữ liệu.
"""

import json
import os
import sys
from datetime import datetime, timezone


DEFAULT_MAX_BYTES = 1_000_000


def _max_bytes() -> int:
    try:
        return int(os.environ.get("KNOWLEDGELIB_MISS_LOG_MAX_BYTES", DEFAULT_MAX_BYTES))
    except ValueError:
        return DEFAULT_MAX_BYTES


def _rotate_if_needed(log_file: str) -> None:
    """File vượt ngưỡng -> đổi thành <file>.1 (ghi đè bản cũ), file mới bắt đầu lại. Tối đa ~2x ngưỡng."""
    limit = _max_bytes()
    if limit > 0 and os.path.exists(log_file) and os.path.getsize(log_file) >= limit:
        os.replace(log_file, log_file + ".1")


def log_miss(query: str, source: str, repo_dir: str | None = None) -> None:
    """
    Append 1 dòng JSON vào <repo_dir>/query_misses.jsonl.
    source: định danh nơi gọi, ví dụ "query_and_get" | "mcp_search" | "web_ui".
    Không bao giờ raise ra ngoài -- lỗi ghi file chỉ print cảnh báo và return.
    repo_dir mặc định đọc từ KNOWLEDGELIB_PATH env (giống agent_client.py),
    fallback os.path.abspath(os.path.join(os.path.dirname(__file__), "..")).
    """
    try:
        if repo_dir is None:
            repo_dir = os.environ.get(
                "KNOWLEDGELIB_PATH",
                os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
            )
        log_file = os.path.join(repo_dir, "query_misses.jsonl")
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "query": query,
            "source": source,
        }
        _rotate_if_needed(log_file)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"Warning: Failed to log query miss ({e})")
