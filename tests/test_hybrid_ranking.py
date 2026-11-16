import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

import agent_client  # noqa: E402
from agent_client import KnowledgeLibClient, _tokens  # noqa: E402


def _client(tmp_path, units):
    (tmp_path / "catalog.json").write_text(json.dumps({"units": units}), encoding="utf-8")
    return KnowledgeLibClient(data_path=str(tmp_path))


def _unit(uid, question, aliases=(), domain="software > x", preview=""):
    return {"id": uid, "canonical_question": question, "aliases": list(aliases), "domain": domain,
            "entity_type": "reference", "content_preview": preview}


def test_tokens_include_bigrams():
    assert _tokens("Thiết kế giải pháp") == ["thiết", "kế", "giải", "pháp", "thiết_kế", "kế_giải", "giải_pháp"]


def test_keyword_search_matches_whole_tokens_not_substrings(tmp_path):
    # Old substring scorer matched "art" inside "start"/"party". BM25 works on tokens.
    c = _client(tmp_path, [
        _unit("a/start", "How to start a party"),
        _unit("a/art", "History of art"),
    ])
    hits = c.keyword_search("art", top_k=5)
    assert [h["id"] for h in hits] == ["a/art"]


def test_rare_keyword_beats_common_vietnamese_words(tmp_path):
    # Mostly-English library with a few Vietnamese units: common Vietnamese words must not get a
    # high IDF just because they are rare corpus-wide.
    units = [_unit(f"en/{i}", f"English topic number {i}") for i in range(30)]
    units.append(_unit("en/pestle", "How do I conduct a PESTLE analysis?", ["PESTLE analysis"]))
    units += [_unit(f"vi/{i}", f"Phân tích cấu trúc bảng lương kỳ {i}", ["phân tích lương"]) for i in range(6)]
    c = _client(tmp_path, units)
    hits = c.keyword_search("phân tích PESTLE", top_k=3)
    assert hits[0]["id"] == "en/pestle"


def test_search_without_vector_uses_keyword_scores_only(tmp_path):
    c = _client(tmp_path, [_unit("a/one", "Configure pytest fixtures"), _unit("a/two", "Bake bread")])
    results = c.search("pytest fixtures", top_k=2)
    assert [r["id"] for r in results] == ["a/one"]
    assert results[0]["search_type"] == "keyword"
    assert results[0]["fused_score"] == results[0]["rrf_score"] > 0


def test_fusion_keeps_unit_found_by_only_one_source(tmp_path):
    # A unit that only the vector side finds must still be returned and can win when the keyword
    # side has nothing better (rank-based RRF used to bury such units).
    c = _client(tmp_path, [
        _unit("a/kw", "alpha beta gamma"),
        _unit("a/vec", "completely different wording"),
    ])
    c.vector_search = lambda q, top_k=3: [
        {"id": "a/vec", "canonical_question": "completely different wording", "domain": "software > x",
         "entity_type": "reference", "distance": 0.05, "search_type": "vector"},
        {"id": "a/kw", "canonical_question": "alpha beta gamma", "domain": "software > x",
         "entity_type": "reference", "distance": 0.40, "search_type": "vector"},
    ]
    results = c.search("zzz unmatched", top_k=2)
    assert results[0]["id"] == "a/vec"
    assert results[0]["search_type"] == "vector"


def test_self_docs_boost_is_only_a_tie_breaker(tmp_path):
    assert 1.0 < agent_client.SELF_DOCS_BOOST <= 1.1
    c = _client(tmp_path, [
        _unit("self-docs/weak", "notes about lunch", domain="self-docs > general"),
        _unit("software/strong", "kubernetes rollback procedure", ["kubernetes rollback"]),
    ])
    assert c.search("kubernetes rollback", top_k=1)[0]["id"] == "software/strong"


def test_embedder_disabled_by_env(monkeypatch):
    import embedding

    monkeypatch.setenv("KNOWLEDGELIB_EMBED_DISABLE", "1")
    monkeypatch.setattr(embedding, "_EMBEDDER", None)
    monkeypatch.setattr(embedding, "_LOAD_FAILED", False)
    assert embedding.load_embedder() is None


def test_alias_overlay_makes_english_unit_findable_in_vietnamese(tmp_path):
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "aliases_vi.json").write_text(
        json.dumps({"baby/bottles": ["bình sữa chống đầy hơi", "bình sữa cho bé bị đầy bụng"]}, ensure_ascii=False),
        encoding="utf-8",
    )
    c = _client(tmp_path, [
        _unit("baby/bottles", "What are the best anti-colic baby bottles?", ["anti-colic bottles"]),
        _unit("vi/skill", "Cách thiết kế skill cho bé làm quen máy tính", ["thiết kế skill"]),
    ])
    assert c.keyword_search("bình sữa chống đầy hơi cho bé", top_k=1)[0]["id"] == "baby/bottles"


def test_alias_overlay_missing_or_broken_file_is_ignored(tmp_path):
    from alias_overlay import load_extra_aliases, merged_aliases

    assert load_extra_aliases(str(tmp_path)) == {}
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "aliases_vi.json").write_text("{not json", encoding="utf-8")
    assert load_extra_aliases(str(tmp_path)) == {}
    unit = {"id": "a", "aliases": ["One", "two"]}
    assert merged_aliases(unit, {"a": ["ONE", "ba"]}) == ["One", "two", "ba"]
