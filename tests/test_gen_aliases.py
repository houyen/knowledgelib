import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import gen_aliases as g


def test_select_skips_overlay_and_vietnamese():
    units = [
        {"id": "a", "canonical_question": "What is X?"},
        {"id": "b", "canonical_question": "Cách làm X như thế nào?"},
        {"id": "c", "canonical_question": "What is Y?"},
    ]
    assert [u["id"] for u in g.select_units(units, {"c": ["x"]}, None, None, None)] == ["a"]
    assert [u["id"] for u in g.select_units(units, {"c": ["x"]}, ["c"], None, None)] == ["c"]


def test_parse_response_strips_noise():
    assert g.parse_response('ok ```json\n{"a": ["x"]}\n``` bye') == {"a": ["x"]}


def test_clean_aliases_dedupes_and_caps():
    out = g.clean_aliases(["  Foo  bar", "foo bar", "", "b", "c", "d", "e", "f", "g"])
    assert out[0] == "Foo bar" and len(out) == g.MAX_ALIASES
