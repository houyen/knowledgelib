#!/usr/bin/env python3
"""
Module ghi nhận các truy vấn không tìm thấy kết quả (query misses)
vào file query_misses.jsonl tại thư mục gốc của kho dữ liệu.
"""

import json
import os
import sys
from datetime import datetime, timezone


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
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"Warning: Failed to log query miss ({e})")
