#!/usr/bin/env python3
"""
CLI tổng hợp và phân tích các truy vấn bị thiếu dữ liệu (query misses).
Đọc query_misses.jsonl và thống kê tần suất các câu hỏi bị 'not found'.
"""

import argparse
from collections import Counter
import json
import os
import sys

DEFAULT_REPO_ROOT = os.environ.get(
    "KNOWLEDGELIB_PATH",
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
)
DEFAULT_LOG_PATH = os.path.join(DEFAULT_REPO_ROOT, "query_misses.jsonl")


def load_misses(log_path: str) -> list[dict]:
    """Đọc query_misses.jsonl, trả list dict. File không tồn tại -> trả []. Dòng lỗi JSON -> bỏ qua dòng đó, không crash."""
    if not os.path.exists(log_path):
        return []

    entries = []
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            for line in f:
                line_str = line.strip()
                if not line_str:
                    continue
                try:
                    data = json.loads(line_str)
                    if isinstance(data, dict):
                        entries.append(data)
                except (json.JSONDecodeError, ValueError):
                    continue
    except Exception as e:
        print(f"Warning: Failed to read log file ({e})", file=sys.stderr)
        return []

    return entries


def aggregate_misses(misses: list[dict]) -> list[tuple[str, int]]:
    """
    Group theo query đã chuẩn hoá (strip + lower), đếm số lần xuất hiện.
    Trả list (query_chuẩn_hoá, count) sắp giảm dần theo count.
    """
    counts = Counter()
    for item in misses:
        raw_query = item.get("query")
        if isinstance(raw_query, str):
            norm = raw_query.strip().lower()
            if norm:
                counts[norm] += 1

    return counts.most_common()


def main(argv: list[str] | None = None) -> None:
    """argparse: --top N (default 20), --log-path (default <repo_root>/query_misses.jsonl).
    In ra bảng đơn giản: rank, count, query. Không cần format phức tạp (không phải web UI)."""
    parser = argparse.ArgumentParser(
        description="KnowledgeLib Query Gap Report - Thống kê các câu hỏi chưa có dữ liệu"
    )
    parser.add_argument(
        "--top",
        type=int,
        default=20,
        help="Số lượng câu hỏi hàng đầu cần hiển thị (default: 20)",
    )
    parser.add_argument(
        "--log-path",
        type=str,
        default=DEFAULT_LOG_PATH,
        help=f"Đường dẫn file query_misses.jsonl (default: {DEFAULT_LOG_PATH})",
    )

    args = parser.parse_args(argv)

    misses = load_misses(args.log_path)
    if not misses:
        print(f"Không có query miss nào được ghi nhận tại: {args.log_path}")
        return

    aggregated = aggregate_misses(misses)
    top_results = aggregated[: args.top]

    print(f"\nTop {len(top_results)} Query Misses ({args.log_path}):")
    print(f"{'Rank':<6} {'Count':<8} {'Query'}")
    print("-" * 50)
    for rank, (query, count) in enumerate(top_results, 1):
        print(f"{rank:<6} {count:<8} {query}")
    print()


if __name__ == "__main__":
    main()
