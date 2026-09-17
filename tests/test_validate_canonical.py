import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from validate_canonical import (
    validate_unit_file,
    validate_directory,
    auto_fix_file,
    generate_canonical_frontmatter,
)


def test_validate_valid_unit(tmp_path):
    content = """---
id: self-docs/sample-guide
canonical_question: "How to configure sample guide"
aliases:
  - "sample guide"
  - "config sample"
entity_type: how_to
domain: self-docs > testing
last_verified: 2026-09-17
---

# Sample Guide

This is the body content.
"""
    f = tmp_path / "sample.md"
    f.write_text(content, encoding="utf-8")

    is_valid, errors = validate_unit_file(str(f))
    assert is_valid is True
    assert errors == []


def test_validate_missing_frontmatter(tmp_path):
    f = tmp_path / "raw.md"
    f.write_text("# Just a raw heading\n\nNo frontmatter.", encoding="utf-8")

    is_valid, errors = validate_unit_file(str(f))
    assert is_valid is False
    assert any("frontmatter" in e.lower() for e in errors)


def test_validate_missing_required_fields(tmp_path):
    content = """---
id: self-docs/incomplete
canonical_question: "Incomplete"
---

# Incomplete Body
"""
    f = tmp_path / "incomplete.md"
    f.write_text(content, encoding="utf-8")

    is_valid, errors = validate_unit_file(str(f))
    assert is_valid is False
    err_text = " ".join(errors)
    assert "aliases" in err_text
    assert "entity_type" in err_text
    assert "domain" in err_text
    assert "last_verified" in err_text


def test_auto_fix_file_converts_raw_doc(tmp_path):
    # Simulates a doc like Payroll CTD without frontmatter
    raw_content = """# Runbook Triển Khai Dọn Dẹp DB

**Cập nhật: 2026-08-18**

## 1. Sự thật nền — ĐỌC TRƯỚC KHI LÀM
Deploy code trước, apply migration sau.
"""
    f = tmp_path / "DB-Cleanup-Deploy-Runbook-180826.md"
    f.write_text(raw_content, encoding="utf-8")

    # Before fix: should be invalid
    is_valid_before, _ = validate_unit_file(str(f))
    assert is_valid_before is False

    # Auto fix
    ok = auto_fix_file(str(f), default_domain="self-docs/database")
    assert ok is True

    # After fix: should be 100% valid
    is_valid_after, errors = validate_unit_file(str(f))
    assert is_valid_after is True, f"Errors: {errors}"

    # Verify extracted properties
    fixed_text = f.read_text(encoding="utf-8")
    assert "entity_type: runbook" in fixed_text
    assert "last_verified: 2026-08-18" in fixed_text
    assert "aliases:" in fixed_text


def test_validate_directory(tmp_path):
    (tmp_path / "valid.md").write_text("""---
id: self-docs/valid
canonical_question: "Valid Question"
aliases: ["valid"]
entity_type: how_to
domain: self-docs
last_verified: 2026-09-17
---
# Valid
Content.
""", encoding="utf-8")

    (tmp_path / "invalid.md").write_text("# Invalid doc", encoding="utf-8")

    errors_map = validate_directory(str(tmp_path))
    assert len(errors_map) == 1
    assert str(tmp_path / "invalid.md") in errors_map
