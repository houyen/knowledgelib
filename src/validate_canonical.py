#!/usr/bin/env python3
"""
Canonical Validator and Auto-Fixer for KnowledgeLib units.
Enforces frontmatter schema, canonical question quality, and taxonomy standards
for self-docs/ and repository knowledge units.
"""

import argparse
from datetime import datetime, timezone
import os
import re
import sys
import yaml

ALLOWED_ENTITY_TYPES = {
    "architecture_explainer",
    "runbook",
    "gotchas",
    "troubleshooting",
    "how_to",
    "specification",
    "product_comparison",
    "reference",
    "book_chapter",
    "tech_stack",
    "compliance",
    "business_strategy",
    "finance",
}


def parse_frontmatter(content: str) -> tuple[dict | None, str]:
    """Parse YAML frontmatter and body. Returns (meta_dict, body_str) or (None, content)."""
    if not content.startswith("---"):
        return None, content

    parts = content.split("---", 2)
    if len(parts) < 3:
        return None, content

    yaml_text = parts[1]
    body = parts[2]
    try:
        data = yaml.safe_load(yaml_text)
        if isinstance(data, dict):
            return data, body
    except Exception:
        return None, content

    return None, content


def validate_unit_file(file_path: str) -> tuple[bool, list[str]]:
    """
    Validate a single markdown file against canonical KnowledgeLib schema.
    Returns (is_valid, list_of_errors).
    """
    errors = []
    if not os.path.isfile(file_path):
        return False, [f"File does not exist: {file_path}"]

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return False, [f"Failed to read file: {e}"]

    if not content.strip():
        return False, ["File is empty"]

    meta, body = parse_frontmatter(content)
    if meta is None:
        errors.append("Missing or malformed YAML frontmatter (must start and end with '---')")
        return False, errors

    # Required field: id
    unit_id = meta.get("id")
    if not unit_id or not isinstance(unit_id, str) or not unit_id.strip():
        errors.append("Field 'id' is required and must be a non-empty string")
    elif " " in unit_id:
        errors.append(f"Field 'id' must not contain spaces: '{unit_id}'")

    # Required field: canonical_question
    cq = meta.get("canonical_question")
    if not cq or not isinstance(cq, str) or not cq.strip():
        errors.append("Field 'canonical_question' is required and must be a non-empty string")
    else:
        cq_clean = cq.strip()
        # Ensure it's not just a raw filename like 'foo_bar_baz'
        if "_" in cq_clean and " " not in cq_clean and len(cq_clean.split("_")) > 2:
            errors.append(
                f"Field 'canonical_question' looks like a raw filename slug ('{cq_clean}'). Provide a human-readable question or title."
            )

    # Required field: aliases
    aliases = meta.get("aliases")
    if aliases is None or not isinstance(aliases, list):
        errors.append("Field 'aliases' is required and must be a list")
    elif len(aliases) == 0:
        errors.append("Field 'aliases' must contain at least 1 alias")
    else:
        for idx, a in enumerate(aliases):
            if not isinstance(a, str) or not a.strip():
                errors.append(f"Alias at index {idx} must be a non-empty string")

    # Required field: entity_type
    entity_type = meta.get("entity_type")
    if not entity_type or not isinstance(entity_type, str) or not entity_type.strip():
        errors.append("Field 'entity_type' is required")
    elif entity_type.strip() not in ALLOWED_ENTITY_TYPES:
        errors.append(
            f"Field 'entity_type' '{entity_type}' is invalid. Allowed: {sorted(ALLOWED_ENTITY_TYPES)}"
        )

    # Required field: domain
    domain = meta.get("domain")
    if not domain or not isinstance(domain, str) or not domain.strip():
        errors.append("Field 'domain' is required and must be a non-empty string")

    # Required field: last_verified (format YYYY-MM-DD)
    lv = meta.get("last_verified")
    if not lv:
        errors.append("Field 'last_verified' is required")
    else:
        lv_str = str(lv).strip()
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", lv_str):
            errors.append(f"Field 'last_verified' must be in format YYYY-MM-DD (got '{lv_str}')")

    # Body check
    if not body.strip():
        errors.append("Markdown content body is empty after frontmatter")

    return len(errors) == 0, errors


def validate_directory(dir_path: str, recursive: bool = True) -> dict[str, list[str]]:
    """
    Validate all .md files in directory.
    Returns mapping {file_path: [error1, error2, ...]}. Only invalid files are included.
    """
    results = {}
    ignore_files = {
        "MEMORY_INDEX.md",
        "00-START-HERE.md",
        "document-map.md",
        "README.md",
        "AGENTS.md",
        "SKILL.md",
        "LICENSE.md",
    }

    if not os.path.exists(dir_path):
        return {dir_path: [f"Directory not found: {dir_path}"]}

    for root, dirs, files in os.walk(dir_path):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]
        for file in files:
            if file.endswith(".md") and file not in ignore_files:
                fpath = os.path.join(root, file)
                is_valid, errors = validate_unit_file(fpath)
                if not is_valid:
                    results[fpath] = errors
        if not recursive:
            break

    return results


def guess_entity_type(title: str, content: str) -> str:
    """Heuristic detector for entity_type based on document title and content."""
    t_lower = title.lower()
    c_lower = content.lower()[:1500]

    if "runbook" in t_lower or "triển khai" in t_lower or "hướng dẫn vận hành" in t_lower:
        return "runbook"
    if "kiến trúc" in t_lower or "architecture" in t_lower or "engine" in t_lower or "rule flow" in t_lower:
        return "architecture_explainer"
    if "sửa lỗi" in t_lower or "fix" in t_lower or "troubleshoot" in t_lower or "lỗi" in t_lower or "bug" in t_lower:
        return "troubleshooting"
    if "cảnh báo" in t_lower or "trap" in t_lower or "bẫy" in t_lower or "sự thật kỹ thuật" in t_lower:
        return "gotchas"
    if "hướng dẫn" in t_lower or "guide" in t_lower or "how to" in t_lower or "tích hợp" in t_lower:
        return "how_to"
    if "spec" in t_lower or "đặc tả" in t_lower or "bàn giao" in t_lower:
        return "specification"
    return "how_to"


def generate_canonical_frontmatter(
    file_path: str,
    raw_content: str,
    default_domain: str = "self-docs",
) -> tuple[dict, str]:
    """
    Generate valid canonical frontmatter for an un-canonicalized markdown file.
    Returns (metadata_dict, remaining_body).
    """
    existing_meta, body = parse_frontmatter(raw_content)
    if existing_meta:
        meta = dict(existing_meta)
    else:
        meta = {}
        body = raw_content

    # Extract Title from first H1 if available
    h1_match = re.search(r"^#\s+(.+)$", body, flags=re.MULTILINE)
    raw_title = h1_match.group(1).strip() if h1_match else ""

    # Clean title
    clean_title = re.sub(r"\[.*?\]", "", raw_title)
    clean_title = re.sub(r"\(.*?\)", "", clean_title).strip()
    if not clean_title:
        base = os.path.splitext(os.path.basename(file_path))[0]
        clean_title = base.replace("_", " ").replace("-", " ").title()

    # Extract date from content if present (e.g. Cập nhật: 2026-08-05)
    date_match = re.search(r"(?:Cập nhật|Ngày|Date|Verified)[\s:]+(\d{4}-\d{2}-\d{2})", body, re.IGNORECASE)
    if date_match:
        last_verified = date_match.group(1)
    else:
        last_verified = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Generate id
    if "id" not in meta or not meta["id"]:
        rel = os.path.splitext(os.path.basename(file_path))[0]
        slug = re.sub(r"[^\w\s-]", "", rel.lower()).strip().replace(" ", "-")
        slug = re.sub(r"-+", "-", slug)
        meta["id"] = f"{default_domain}/{slug}"

    # Generate canonical_question
    if "canonical_question" not in meta or not meta["canonical_question"]:
        if clean_title.lower().startswith("hướng dẫn"):
            cq = f"How to {clean_title[10:].strip()} (Hướng dẫn {clean_title[10:].strip()})"
        elif clean_title.lower().startswith("kiến trúc") or "architecture" in clean_title.lower():
            cq = f"Architecture and technical specifications for {clean_title}"
        else:
            cq = f"Technical guide and specification: {clean_title}"
        meta["canonical_question"] = cq

    # Generate aliases
    if "aliases" not in meta or not meta["aliases"]:
        aliases = []
        if clean_title:
            aliases.append(clean_title)
        # Add filename as alias
        file_slug = os.path.splitext(os.path.basename(file_path))[0].replace("-", " ").replace("_", " ")
        if file_slug.lower() != clean_title.lower():
            aliases.append(file_slug)
        meta["aliases"] = aliases[:4]

    # Generate entity_type
    if "entity_type" not in meta or meta["entity_type"] not in ALLOWED_ENTITY_TYPES:
        meta["entity_type"] = guess_entity_type(clean_title, body)

    # Generate domain
    if "domain" not in meta or not meta["domain"]:
        meta["domain"] = default_domain

    # Generate last_verified
    if "last_verified" not in meta:
        try:
            meta["last_verified"] = datetime.strptime(last_verified, "%Y-%m-%d").date()
        except Exception:
            meta["last_verified"] = last_verified

    return meta, body


def auto_fix_file(file_path: str, default_domain: str = "self-docs", dry_run: bool = False) -> bool:
    """
    Auto-fix frontmatter in file if missing or invalid.
    Returns True if file is valid or successfully fixed.
    """
    is_valid, _ = validate_unit_file(file_path)
    if is_valid:
        return True

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return False

    meta, body = generate_canonical_frontmatter(file_path, content, default_domain=default_domain)

    # Serialize YAML frontmatter
    yaml_dump = yaml.dump(meta, allow_unicode=True, sort_keys=False).strip()
    fixed_content = f"---\n{yaml_dump}\n---\n\n{body.lstrip()}"

    if dry_run:
        return True

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(fixed_content)
        is_now_valid, _ = validate_unit_file(file_path)
        return is_now_valid
    except Exception:
        return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate and Auto-Fix Canonical Frontmatter for Knowledge Units"
    )
    parser.add_argument(
        "--dir",
        type=str,
        default="self-docs",
        help="Directory to validate (default: self-docs)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check only; return exit code 1 if invalid files exist",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Automatically inject/fix canonical frontmatter on non-compliant files",
    )
    parser.add_argument(
        "--domain",
        type=str,
        default="self-docs",
        help="Default domain prefix for auto-fix (default: self-docs)",
    )

    args = parser.parse_args(argv)

    target_dir = os.path.abspath(args.dir)
    print(f"🔍 Validating canonical units in: {target_dir}")

    invalid_map = validate_directory(target_dir)

    if not invalid_map:
        print("✅ All markdown files meet canonical standards (100% compliant).")
        return 0

    print(f"⚠️ Found {len(invalid_map)} non-compliant file(s):")
    for fpath, errs in invalid_map.items():
        print(f"\n📄 {os.path.relpath(fpath, target_dir) if target_dir in fpath else fpath}:")
        for err in errs:
            print(f"   ❌ {err}")

    if args.fix:
        print("\n🛠️ Attempting auto-fix on non-compliant files...")
        fixed_count = 0
        for fpath in invalid_map:
            ok = auto_fix_file(fpath, default_domain=args.domain)
            if ok:
                fixed_count += 1
                print(f"   ✅ Fixed: {os.path.basename(fpath)}")
            else:
                print(f"   ❌ Failed to auto-fix: {os.path.basename(fpath)}")

        print(f"\nFixed {fixed_count}/{len(invalid_map)} file(s).")
        # Re-check
        remaining = validate_directory(target_dir)
        return 0 if not remaining else 1

    if args.check:
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
