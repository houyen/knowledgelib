import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from validate_canonical import validate_unit_file  # noqa: E402

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def test_coding_rule_set_entity_type_is_accepted(tmp_path):
    p = tmp_path / "rules.md"
    p.write_text(
        "---\nid: software/coding-rules/x\ncanonical_question: What rules should code follow?\n"
        "aliases:\n- x rules\nentity_type: coding_rule_set\ndomain: software > coding-rules\n"
        "last_verified: 2026-09-29\n---\n\n# Rules\n",
        encoding="utf-8",
    )
    ok, errors = validate_unit_file(str(p))
    assert ok, errors


def test_committed_coding_rules_units_are_valid():
    for name in ("go-code-rules.md", "js-ts-code-rules.md"):
        ok, errors = validate_unit_file(os.path.join(REPO, "software", "coding-rules", name))
        assert ok, (name, errors)
