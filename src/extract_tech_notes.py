#!/usr/bin/env python3
"""
Tech-Log Extractor & Anonymizer for KnowledgeLib.
Scans raw technical notes, runbooks, and implementation docs from project repositories,
sanitizes internal/PII information (company names, internal emails, IPs, ticket IDs),
structures them into valid Canonical KnowledgeLib units, and imports them into self-docs/.
"""

import argparse
import hashlib
import os
import re
import sys
import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from validate_canonical import (
    ALLOWED_ENTITY_TYPES,
    generate_canonical_frontmatter,
    parse_frontmatter,
    validate_unit_file,
)

# ── Anonymization Regexes & Rules ──────────────────────────────────────────────

# Emails: internal coteccons/vn domains -> user@company.test
RE_EMAIL_INTERNAL = re.compile(
    r"\b[A-Za-z0-9._%+-]+@(?:coteccons\.vn|[A-Za-z0-9.-]+\.vn)\b",
    re.IGNORECASE,
)

# Company & project names
RE_COMPANY = re.compile(r"\b(?:Coteccons|COTECCONS|coteccons)\b")
RE_PAYROLL_CTD = re.compile(r"\b(?:Payroll\s+CTD|CTD\s+Payroll|CTD-Payroll)\b", re.IGNORECASE)
RE_CTD_STANDALONE = re.compile(r"\bCTD\b")

# Internal IPs & hostnames
RE_PRIVATE_IP = re.compile(r"\b(?:192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3})\b")

# Ticket IDs: e.g. PAYROLL-1234, CTD-567, JIRA-890
RE_TICKETS = re.compile(r"\b(?:PAYROLL|CTD|PR|JIRA|TASK|BUG)-\d+\b")

# Internal chatter / meeting line patterns
RE_CHATTER_LINES = re.compile(
    r"^(?:[\s*->•]*)(?:họp|meeting|retrospective|chitchat|note riêng|sprint sync|assignee|reporter)\b.*$",
    re.IGNORECASE | re.MULTILINE,
)


def anonymize_text(text: str) -> str:
    """
    Sanitize text by replacing internal company names, emails, IPs,
    and Jira ticket codes with neutral enterprise terms.
    """
    if not text:
        return ""

    # Replace emails
    cleaned = RE_EMAIL_INTERNAL.sub("user@company.test", text)

    # Replace specific project / company names
    cleaned = RE_PAYROLL_CTD.sub("Enterprise Payroll", cleaned)
    cleaned = RE_COMPANY.sub("Enterprise", cleaned)
    cleaned = RE_CTD_STANDALONE.sub("Core System", cleaned)

    # Replace private IP addresses
    cleaned = RE_PRIVATE_IP.sub("10.0.0.x", cleaned)

    # Replace ticket identifiers
    cleaned = RE_TICKETS.sub("TASK-REF", cleaned)

    # Strip noisy meeting chatter lines
    cleaned = RE_CHATTER_LINES.sub("", cleaned)

    # Clean double blank lines
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)

    return cleaned


def compute_content_hash(text: str) -> str:
    """Compute sha256 hash of normalized text for deduplication."""
    norm_text = re.sub(r"\s+", " ", text).strip().lower()
    return hashlib.sha256(norm_text.encode("utf-8")).hexdigest()


def determine_subdomain(clean_title: str, filename: str, content: str) -> tuple[str, str]:
    """
    Determine target self-docs subfolder and domain hierarchy based on content.
    Returns (subfolder, domain_string).
    """
    combo = f"{clean_title} {filename} {content[:1000]}".lower()

    if any(k in combo for k in ["workday", "sftp", "adapter", "integration", "webhook", "api guide"]):
        return "integration", "self-docs > integration"
    if any(k in combo for k in ["rbac", "permission", "security", "audit", "compliance", "auth", "token"]):
        return "security", "self-docs > security"
    if any(k in combo for k in ["bonus", "salary", "formula", "engine", "chốt công", "payroll", "bảng lương"]):
        return "engine", "self-docs > engine"
    if any(k in combo for k in ["migration", "schema", "database", "mongodb", "postgres", "atlas", "table"]):
        return "database", "self-docs > database"
    if any(k in combo for k in ["attendance", "report", "export", "runbook", "vận hành", "triển khai"]):
        return "operations", "self-docs > operations"

    return "general", "self-docs > general"


def extract_and_anonymize_file(
    src_file: str,
    dest_base_dir: str,
    dry_run: bool = False,
    seen_hashes: set[str] | None = None,
) -> dict:
    """
    Process a single raw documentation file:
    - Anonymize content
    - Generate or validate canonical frontmatter
    - Write to appropriate self-docs/<subfolder>/ directory
    """
    if seen_hashes is None:
        seen_hashes = set()

    res = {
        "source": src_file,
        "status": "pending",
        "destination": None,
        "errors": [],
    }

    if not os.path.isfile(src_file) or not src_file.endswith(".md"):
        res["status"] = "skipped"
        res["errors"].append("Not a markdown file")
        return res

    try:
        with open(src_file, "r", encoding="utf-8", errors="replace") as f:
            raw_content = f.read()
    except Exception as e:
        res["status"] = "error"
        res["errors"].append(f"Cannot read file: {e}")
        return res

    if not raw_content.strip():
        res["status"] = "skipped"
        res["errors"].append("Empty file")
        return res

    # 1. Anonymize
    sanitized = anonymize_text(raw_content)

    # 2. Check deduplication hash
    content_hash = compute_content_hash(sanitized)
    if content_hash in seen_hashes:
        res["status"] = "duplicate"
        return res
    seen_hashes.add(content_hash)

    # 3. Canonical Frontmatter & Taxonomy
    base_name = os.path.basename(src_file)
    clean_base = re.sub(r"^[0-9]+-?", "", base_name)  # remove leading dates like 150926-
    clean_base = re.sub(r"-?[0-9]{6}\.md$", ".md", clean_base)  # remove trailing 220726.md
    slug = os.path.splitext(clean_base)[0].lower().replace("_", "-").replace(" ", "-")
    slug = re.sub(r"-+", "-", slug).strip("-")
    if not slug:
        slug = "tech-note"

    subfolder, domain_str = determine_subdomain(slug, base_name, sanitized)
    meta, body = generate_canonical_frontmatter(
        src_file,
        sanitized,
        default_domain=f"self-docs/{subfolder}",
    )
    meta["domain"] = domain_str
    meta["id"] = f"self-docs/{subfolder}/{slug}"

    # Format final content
    yaml_header = yaml.safe_dump(meta, sort_keys=False, allow_unicode=True).strip()
    final_content = f"---\n{yaml_header}\n---\n\n{body.lstrip()}"

    # 4. Destination path
    dest_dir = os.path.join(dest_base_dir, subfolder)
    dest_path = os.path.join(dest_dir, f"{slug}.md")
    res["destination"] = dest_path

    if not dry_run:
        os.makedirs(dest_dir, exist_ok=True)
        with open(dest_path, "w", encoding="utf-8") as f:
            f.write(final_content)

        # Validate final output
        valid, errors = validate_unit_file(dest_path)
        if not valid:
            res["status"] = "invalid"
            res["errors"] = errors
            return res

    res["status"] = "extracted"
    return res


def extract_directory(
    src_dir: str,
    dest_base_dir: str,
    dry_run: bool = False,
    max_files: int | None = None,
) -> dict:
    """
    Batch extract and anonymize markdown files from src_dir into dest_base_dir.
    Returns summary report.
    """
    summary = {
        "total_scanned": 0,
        "extracted": 0,
        "duplicates": 0,
        "skipped": 0,
        "errors": 0,
        "files": [],
    }

    if not os.path.isdir(src_dir):
        summary["errors"] = 1
        return summary

    seen_hashes = set()
    count = 0

    for root, dirs, files in os.walk(src_dir):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]
        for file in sorted(files):
            if file.endswith(".md"):
                summary["total_scanned"] += 1
                src_path = os.path.join(root, file)
                res = extract_and_anonymize_file(
                    src_path,
                    dest_base_dir,
                    dry_run=dry_run,
                    seen_hashes=seen_hashes,
                )
                summary["files"].append(res)
                if res["status"] == "extracted":
                    summary["extracted"] += 1
                elif res["status"] == "duplicate":
                    summary["duplicates"] += 1
                elif res["status"] == "skipped":
                    summary["skipped"] += 1
                else:
                    summary["errors"] += 1

                count += 1
                if max_files and count >= max_files:
                    return summary

    return summary


def main():
    parser = argparse.ArgumentParser(description="Extract & Anonymize tech notes to KnowledgeLib self-docs.")
    parser.add_argument("--src", required=True, help="Source directory containing raw tech notes")
    parser.add_argument("--dest", default=os.path.join(os.path.dirname(__file__), "..", "self-docs"), help="Destination self-docs directory")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without writing files")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of processed files")
    args = parser.parse_args()

    print(f"Extracting notes from: {args.src}")
    print(f"Target destination:    {args.dest}")
    report = extract_directory(args.src, args.dest, dry_run=args.dry_run, max_files=args.limit)

    print("\n--- Summary ---")
    print(f"Total Scanned: {report['total_scanned']}")
    print(f"Extracted:     {report['extracted']}")
    print(f"Duplicates:    {report['duplicates']}")
    print(f"Skipped:       {report['skipped']}")
    print(f"Errors:        {report['errors']}")

    if report["errors"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
