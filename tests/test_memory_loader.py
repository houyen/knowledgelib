import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from memory_loader import (
    load_canonical_units,
    format_compact_memory_index,
    export_memory_file,
    get_memory_index,
)


@pytest.fixture
def memory_repo(tmp_path):
    self_docs = tmp_path / "self-docs"
    self_docs.mkdir()

    # Unit 1: Gotchas
    (self_docs / "db-trap.md").write_text("""---
id: self-docs/db-migration-trap
canonical_question: "How to avoid table deletion during Atlas and Go migration boot"
aliases:
  - "Atlas migration trap"
  - "Auto migrate deletion"
entity_type: gotchas
domain: self-docs > database
last_verified: 2026-09-17
constraints:
  - "Deploy code before running manual Atlas migrations"
---

# DB Migration Trap

RunMigrations executes before file migrations. Always deploy code first.
""", encoding="utf-8")

    # Unit 2: Runbook
    (self_docs / "sftp-runbook.md").write_text("""---
id: self-docs/sftp-payslip-runbook
canonical_question: "How to configure SFTP export for payslips"
aliases:
  - "SFTP export"
entity_type: runbook
domain: self-docs > integration
last_verified: 2026-09-17
---

# SFTP Runbook

Ensure SSH keys are configured in environment variables.
""", encoding="utf-8")

    return tmp_path


def test_load_canonical_units(memory_repo):
    units = load_canonical_units(repo_dir=str(memory_repo), domain_prefix="self-docs")
    assert len(units) == 2
    ids = {u["id"] for u in units}
    assert ids == {"self-docs/db-migration-trap", "self-docs/sftp-payslip-runbook"}


def test_format_compact_memory_index(memory_repo):
    units = load_canonical_units(repo_dir=str(memory_repo), domain_prefix="self-docs")
    index_md = format_compact_memory_index(units)

    assert "Critical Gotchas & Traps" in index_md
    assert "Operations & Runbooks" in index_md
    assert "self-docs/db-migration-trap" in index_md
    assert "Deploy code before running manual Atlas migrations" in index_md
    assert "self-docs/sftp-payslip-runbook" in index_md


def test_export_memory_file(memory_repo):
    out_file = memory_repo / "self-docs" / "MEMORY_INDEX.md"
    res_path = export_memory_file(
        repo_dir=str(memory_repo),
        domain_prefix="self-docs",
        target_file=str(out_file),
    )
    assert os.path.exists(res_path)
    content = out_file.read_text(encoding="utf-8")
    assert "KnowledgeLib Memory Index (self-docs)" in content
    assert "self-docs/db-migration-trap" in content


def test_get_memory_index_empty(tmp_path):
    content = get_memory_index(repo_dir=str(tmp_path), domain="non-existent")
    assert "No canonical units indexed yet" in content
