import os
import sys
import yaml
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from extract_tech_notes import (
    AnonymizeConfig,
    anonymize_text,
    compute_content_hash,
    determine_subdomain,
    extract_and_anonymize_file,
    extract_directory,
)
from validate_canonical import validate_unit_file


def test_anonymize_text_replaces_emails_and_company():
    raw = (
        "Liên hệ thaidt@coteccons.vn hoặc dev@vsol.vn để truy cập hệ thống Coteccons.\n"
        "Kiến trúc của Payroll CTD đang dùng microservices."
    )
    sanitized = anonymize_text(raw)
    assert "coteccons.vn" not in sanitized
    assert "Coteccons" not in sanitized
    assert "user@company.test" in sanitized


def test_anonymize_text_replaces_ips_and_tickets():
    raw = (
        "Server production đặt tại 192.168.1.50 và 10.0.1.25.\n"
        "Fix lỗi theo ticket PAYROLL-4581 và JIRA-102."
    )
    sanitized = anonymize_text(raw)
    assert "192.168.1.50" not in sanitized
    assert "10.0.1.25" not in sanitized
    assert "10.0.0.x" in sanitized
    assert "PAYROLL-4581" not in sanitized
    assert "JIRA-102" not in sanitized
    assert "TASK-REF" in sanitized


def test_anonymize_text_strips_chatter():
    raw = (
        "# RBAC Migration Guide\n\n"
        "* Họp sprint lúc 9h sáng cùng team\n"
        "* Assignee: Nguyen Van A\n"
        "Tài liệu hướng dẫn phân quyền."
    )
    sanitized = anonymize_text(raw)
    assert "Họp sprint" not in sanitized
    assert "Assignee" not in sanitized
    assert "Tài liệu hướng dẫn phân quyền" in sanitized


def test_determine_subdomain_default():
    sub, dom = determine_subdomain("Workday Adapter Sync", "workday-sync.md", "SOAP client")
    assert sub == "integration"
    assert dom == "self-docs > integration"

    sub, dom = determine_subdomain("RBAC Permission Model", "rbac.md", "User permission scoping")
    assert sub == "security"
    assert dom == "self-docs > security"

    sub, dom = determine_subdomain("Bonus Calculation Engine", "bonus.md", "Công thức tính thưởng")
    assert sub == "engine"
    assert dom == "self-docs > engine"


def test_compute_content_hash_normalized():
    h1 = compute_content_hash("Hello   World \n\n Test")
    h2 = compute_content_hash("hello world test")
    assert h1 == h2


def test_extract_and_anonymize_file(tmp_path):
    src_file = tmp_path / "150926-workday-adapter.md"
    src_file.write_text(
        "# Workday Adapter Guide\n\n"
        "Lưu ý liên hệ thaidt@coteccons.vn khi cấu hình IP 192.168.1.20.\n"
        "Theo ticket PAYROLL-992.",
        encoding="utf-8",
    )

    dest_dir = tmp_path / "dest"
    seen = set()
    res = extract_and_anonymize_file(str(src_file), str(dest_dir), seen_hashes=seen)

    assert res["status"] == "extracted"
    dest_path = res["destination"]
    assert os.path.exists(dest_path)

    # Validate canonical schema of generated file
    is_valid, errors = validate_unit_file(dest_path)
    assert is_valid is True, f"Validation errors: {errors}"

    content = open(dest_path, encoding="utf-8").read()
    assert "coteccons.vn" not in content
    assert "192.168.1.20" not in content
    assert "user@company.test" in content
    assert "TASK-REF" in content


def test_extract_directory(tmp_path):
    src_dir = tmp_path / "raw_docs"
    src_dir.mkdir()
    (src_dir / "doc1.md").write_text("# Doc 1\n\nNội dung 1 cho Coteccons.", encoding="utf-8")
    (src_dir / "doc2.md").write_text("# Doc 2\n\nNội dung 2.", encoding="utf-8")
    (src_dir / "doc3.txt").write_text("Not markdown", encoding="utf-8")

    dest_dir = tmp_path / "output_docs"
    report = extract_directory(str(src_dir), str(dest_dir))

    assert report["total_scanned"] == 2
    assert report["extracted"] == 2
    assert report["errors"] == 0


# ── Tests for Configurable Multi-Project Anonymization ─────────────────────────

def test_anonymize_different_project_arbitrary_config():
    """Verify that any project with completely different names and domains is anonymized properly."""
    custom_cfg = AnonymizeConfig(
        company_names=["AcmeBank", "AcmeCorp"],
        replacement_company="BankingCorp",
        project_names=["PaymentGateway", "PG-Core"],
        replacement_project="Transaction Engine",
        email_domains=["acmebank.com", "acmecorp.vn"],
        replacement_email="engineer@banking.test",
        ticket_prefixes=["BANK", "PAY"],
        replacement_ticket="TICKET-REF",
    )

    raw = (
        "Project PaymentGateway developed by AcmeBank team.\n"
        "Direct queries to lead@acmebank.com or admin@acmecorp.vn.\n"
        "Resolves BANK-4421 and PAY-102. Also public contact info@gmail.com stays."
    )

    sanitized = anonymize_text(raw, config=custom_cfg)
    assert "AcmeBank" not in sanitized
    assert "PaymentGateway" not in sanitized
    assert "acmebank.com" not in sanitized
    assert "acmecorp.vn" not in sanitized
    assert "BANK-4421" not in sanitized
    assert "PAY-102" not in sanitized

    assert "BankingCorp" in sanitized
    assert "Transaction Engine" in sanitized
    assert "engineer@banking.test" in sanitized
    assert "TICKET-REF" in sanitized
    # Public email provider is preserved
    assert "info@gmail.com" in sanitized


def test_anonymize_config_loaded_from_yaml_file(tmp_path):
    """Verify loading custom anonymization rules from a project YAML file."""
    cfg_file = tmp_path / "anonymize_rules.yaml"
    cfg_data = {
        "company_names": ["VinFast", "Vingroup"],
        "project_names": ["EV-Charging"],
        "email_domains": ["vinfast.vn"],
        "ticket_prefixes": ["VF", "CHARGE"],
        "subdomains": {
            "telemetry": ["canbus", "battery", "iot", "sensor"],
            "billing": ["charging-rate", "invoice", "payment"],
        },
    }
    cfg_file.write_text(yaml.safe_dump(cfg_data), encoding="utf-8")

    cfg = AnonymizeConfig.load(config_path=str(cfg_file))
    assert "VinFast" in cfg.company_names
    assert "EV-Charging" in cfg.project_names
    assert "vinfast.vn" in cfg.email_domains
    assert "telemetry" in cfg.subdomain_rules

    # Test custom subdomain routing
    sub, dom = determine_subdomain("Battery Health Monitor", "battery-health.md", "Reading canbus sensor", config=cfg)
    assert sub == "telemetry"
    assert dom == "self-docs > telemetry"


def test_anonymize_zero_config_corporate_email_detection():
    """Verify zero-config mode: any unlisted corporate domain is sanitized automatically."""
    cfg = AnonymizeConfig()
    text = "Mail to dev@random-startup-corp.xyz or support@unknown-bank.asia"
    sanitized = anonymize_text(text, config=cfg)
    assert "random-startup-corp.xyz" not in sanitized
    assert "unknown-bank.asia" not in sanitized
    assert "user@company.test" in sanitized
