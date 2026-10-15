import json
import os
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "src"))

import retrieval_eval as re_  # noqa: E402

GOLDEN = os.path.join(ROOT, "tests", "retrieval_eval", "golden_selfdocs.json")
# Sàn hồi quy, thấp hơn đo thật (~0.74 ngày 2026-10-15) để không flaky; nâng dần khi retrieval cải thiện.
MIN_RECALL_AT_3 = 0.60


def test_first_hit_rank():
    assert re_.first_hit_rank(["a", "b", "c"], {"b"}) == 1
    assert re_.first_hit_rank(["a"], {"z"}) is None


def test_evaluate_metrics_with_fake_search():
    golden = [
        {"q": "q1", "gold": {"a"}, "note": ""},
        {"q": "q2", "gold": {"b"}, "note": ""},
        {"q": "q3", "gold": {"z"}, "note": ""},
    ]
    ranked = {"q1": ["a", "x"], "q2": ["x", "y", "b"], "q3": ["x", "y"]}
    res = re_.evaluate(lambda q, k: [{"id": i} for i in ranked[q][:k]], golden)
    assert res["n"] == 3
    assert res["recall@1"] == pytest.approx(1 / 3)
    assert res["recall@3"] == pytest.approx(2 / 3)
    assert res["mrr"] == pytest.approx((1 + 1 / 3 + 0) / 3)
    assert [m["q"] for m in res["misses"]] == ["q3"]


def test_load_golden_rejects_bad_rows(tmp_path):
    p = tmp_path / "g.json"
    p.write_text(json.dumps([{"q": "x", "gold": []}]), encoding="utf-8")
    with pytest.raises(ValueError):
        re_.load_golden(str(p))


def test_golden_ids_exist_in_catalog():
    """Golden set mục nát (đáp án trỏ unit đã đổi tên/xoá) làm số đo vô nghĩa."""
    with open(os.path.join(ROOT, "catalog.json"), encoding="utf-8") as f:
        known = {u["id"] for u in json.load(f)["units"]}
    stale = [(r["q"], g) for r in re_.load_golden(GOLDEN) for g in r["gold"] if g not in known]
    assert not stale, f"golden trỏ unit không còn trong catalog: {stale}"


def test_live_recall_floor():
    chromadb = pytest.importorskip("chromadb")  # noqa: F841
    from agent_client import KnowledgeLibClient

    try:
        client = KnowledgeLibClient(ROOT)
    except BaseException as e:  # chromadb Rust panic (BaseException) không phải lỗi của retrieval
        if isinstance(e, (KeyboardInterrupt, SystemExit)):
            raise
        pytest.skip(f"Chroma không mở được trên máy này: {type(e).__name__}: {e}")
    if client.collection is None:
        pytest.skip("Chroma chưa được index trên máy này")
    res = re_.evaluate(lambda q, k: client.search(q, top_k=k), re_.load_golden(GOLDEN))
    assert res["recall@3"] >= MIN_RECALL_AT_3, re_.print_table(res)
