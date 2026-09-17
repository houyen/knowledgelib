#!/usr/bin/env python3
"""
Configurable Tech-Log Extractor & Anonymizer for KnowledgeLib.
Scans raw technical notes, runbooks, and implementation docs from ANY project repository,
sanitizes internal/PII information via configurable or automatic rules,
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

# Common public email providers that should NOT be anonymized unless explicitly requested
PUBLIC_EMAIL_DOMAINS = {
    "gmail.com", "googlemail.com", "yahoo.com", "hotmail.com", "outlook.com",
    "live.com", "icloud.com", "me.com", "aol.com", "proton.me", "protonmail.com",
    "github.com", "google.com", "microsoft.com", "apple.com", "example.com", "company.test"
}

# Generic private IP ranges (RFC 1918)
RE_PRIVATE_IP = re.compile(
    r"\b(?:192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})\b"
)

# Generic Ticket pattern for Jira / Linear / Redmine (e.g. PROJ-1234, FEAT-42)
RE_GENERIC_TICKET = re.compile(r"\b[A-Z]{2,10}-\d{1,6}\b")

# Internal chatter / meeting line patterns
RE_CHATTER_LINES = re.compile(
    r"^(?:[\s*->•]*)(?:họp|meeting|retrospective|chitchat|note riêng|sprint sync|assignee|reporter)\b.*$",
    re.IGNORECASE | re.MULTILINE,
)

# Default Software Taxonomy mapping (extensible per project)
DEFAULT_SUBDOMAIN_RULES = {
    "engine": [
        "engine", "calc", "formula", "algorithm", "rule", "salary",
        "công thức", "tính toán", "lương", "payroll", "core logic"
    ],
    "integration": [
        "api", "webhook", "adapter", "integration", "sftp", "client",
        "connector", "soap", "rest", "workday", "tích hợp", "sync"
    ],
    "security": [
        "rbac", "auth", "permission", "jwt", "token", "audit",
        "security", "compliance", "bảo mật", "phân quyền", "role"
    ],
    "database": [
        "db", "database", "schema", "migration", "table", "sql",
        "postgres", "mongodb", "atlas", "redis", "query", "prisma"
    ],
    "operations": [
        "runbook", "deploy", "attendance", "report", "export", "vận hành",
        "triển khai", "playwright", "qc", "test", "monitoring", "k8s", "docker"
    ],
}


class AnonymizeConfig:
    """Project-agnostic configuration for text anonymization and taxonomy routing."""

    def __init__(
        self,
        company_names: list[str] | None = None,
        replacement_company: str = "Enterprise",
        project_names: list[str] | None = None,
        replacement_project: str = "Core System",
        email_domains: list[str] | None = None,
        sanitize_all_corporate_emails: bool = True,
        replacement_email: str = "user@company.test",
        ticket_prefixes: list[str] | None = None,
        replacement_ticket: str = "TASK-REF",
        subdomain_rules: dict[str, list[str]] | None = None,
        custom_replacements: dict[str, str] | None = None,
    ):
        self.company_names = company_names or []
        self.replacement_company = replacement_company
        self.project_names = project_names or []
        self.replacement_project = replacement_project
        self.email_domains = [d.lower().strip() for d in (email_domains or [])]
        self.sanitize_all_corporate_emails = sanitize_all_corporate_emails
        self.replacement_email = replacement_email
        self.ticket_prefixes = ticket_prefixes or []
        self.replacement_ticket = replacement_ticket
        self.subdomain_rules = subdomain_rules or dict(DEFAULT_SUBDOMAIN_RULES)
        self.custom_replacements = custom_replacements or {}

        # Precompile company/project regexes if provided
        self._re_companies = None
        if self.company_names:
            pats = [re.escape(c) for c in sorted(self.company_names, key=len, reverse=True)]
            self._re_companies = re.compile(r"\b(?:" + "|".join(pats) + r")\b", re.IGNORECASE)

        self._re_projects = None
        if self.project_names:
            pats = [re.escape(p) for p in sorted(self.project_names, key=len, reverse=True)]
            self._re_projects = re.compile(r"\b(?:" + "|".join(pats) + r")\b", re.IGNORECASE)

        self._re_specific_emails = None
        if self.email_domains:
            doms = [re.escape(d) for d in sorted(self.email_domains, key=len, reverse=True)]
            self._re_specific_emails = re.compile(
                r"\b[A-Za-z0-9._%+-]+@(?:" + "|".join(doms) + r")\b",
                re.IGNORECASE,
            )

        self._re_specific_tickets = None
        if self.ticket_prefixes:
            pfxs = [re.escape(p) for p in sorted(self.ticket_prefixes, key=len, reverse=True)]
            self._re_specific_tickets = re.compile(r"\b(?:" + "|".join(pfxs) + r")-\d+\b", re.IGNORECASE)

    @classmethod
    def load(
        cls,
        config_path: str | None = None,
        src_dir: str | None = None,
    ) -> "AnonymizeConfig":
        """
        Load configuration from YAML file or locate it automatically.
        Search order:
        1. Explicit config_path
        2. <src_dir>/anonymize_rules.yaml or <src_dir>/.anonymize.yaml
        3. <cwd>/anonymize_rules.yaml
        4. <knowledgelib_root>/config/anonymize_rules.yaml
        5. Default built-in rules (with environment variable overrides)
        """
        data = {}
        paths_to_try = []

        if config_path:
            paths_to_try.append(config_path)

        if src_dir:
            paths_to_try.append(os.path.join(src_dir, "anonymize_rules.yaml"))
            paths_to_try.append(os.path.join(src_dir, ".anonymize.yaml"))

        cwd = os.getcwd()
        paths_to_try.append(os.path.join(cwd, "anonymize_rules.yaml"))
        paths_to_try.append(os.path.join(cwd, ".anonymize.yaml"))

        kl_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        paths_to_try.append(os.path.join(kl_root, "config", "anonymize_rules.yaml"))
        paths_to_try.append(os.path.join(kl_root, "config", "anonymize_rules.template.yaml"))

        for p in paths_to_try:
            if p and os.path.isfile(p):
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        loaded = yaml.safe_load(f)
                        if isinstance(loaded, dict):
                            data = loaded
                            break
                except Exception:
                    pass

        # Environment variable overrides
        env_companies = os.environ.get("ANONYMIZE_COMPANIES")
        if env_companies:
            data["company_names"] = [c.strip() for c in env_companies.split(",") if c.strip()]

        env_projects = os.environ.get("ANONYMIZE_PROJECT_NAMES")
        if env_projects:
            data["project_names"] = [p.strip() for p in env_projects.split(",") if p.strip()]

        env_emails = os.environ.get("ANONYMIZE_EMAIL_DOMAINS")
        if env_emails:
            data["email_domains"] = [e.strip() for e in env_emails.split(",") if e.strip()]

        return cls(
            company_names=data.get("company_names"),
            replacement_company=data.get("replacement_company", "Enterprise"),
            project_names=data.get("project_names"),
            replacement_project=data.get("replacement_project", "Core System"),
            email_domains=data.get("email_domains"),
            sanitize_all_corporate_emails=data.get("sanitize_all_corporate_emails", True),
            replacement_email=data.get("replacement_email", "user@company.test"),
            ticket_prefixes=data.get("ticket_prefixes"),
            replacement_ticket=data.get("replacement_ticket", "TASK-REF"),
            subdomain_rules=data.get("subdomains"),
            custom_replacements=data.get("custom_replacements"),
        )


def anonymize_text(text: str, config: AnonymizeConfig | None = None) -> str:
    """
    Sanitize text using AnonymizeConfig.
    Removes proprietary company names, emails, IPs, ticket codes, and meeting noise.
    """
    if not text:
        return ""

    cfg = config or AnonymizeConfig.load()
    cleaned = text

    # 1. Custom replacements dictionary
    for old_term, new_term in cfg.custom_replacements.items():
        cleaned = cleaned.replace(old_term, new_term)

    # 2. Ticket identifiers (run early to avoid fragmenting TICK-123)
    if cfg._re_specific_tickets:
        cleaned = cfg._re_specific_tickets.sub(cfg.replacement_ticket, cleaned)
    # Generic ticket pattern
    cleaned = RE_GENERIC_TICKET.sub(cfg.replacement_ticket, cleaned)

    # 3. Emails (run before company names so @company.com is not mangled before email match)
    if cfg._re_specific_emails:
        cleaned = cfg._re_specific_emails.sub(cfg.replacement_email, cleaned)

    if cfg.sanitize_all_corporate_emails:
        # Match all emails and anonymize any whose domain is not in PUBLIC_EMAIL_DOMAINS
        def _replace_corporate_email(m):
            domain = m.group(1).lower()
            if domain in PUBLIC_EMAIL_DOMAINS:
                return m.group(0)
            return cfg.replacement_email

        cleaned = re.sub(
            r"\b[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+\.[A-Za-z]{2,})\b",
            _replace_corporate_email,
            cleaned,
        )

    # 4. Specific project names
    if cfg._re_projects:
        cleaned = cfg._re_projects.sub(cfg.replacement_project, cleaned)

    # 5. Specific company names
    if cfg._re_companies:
        cleaned = cfg._re_companies.sub(cfg.replacement_company, cleaned)

    # 6. Private IP addresses
    cleaned = RE_PRIVATE_IP.sub("10.0.0.x", cleaned)


    # 7. Strip noisy meeting chatter lines
    cleaned = RE_CHATTER_LINES.sub("", cleaned)

    # 8. Clean excess blank lines
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)


    return cleaned


def compute_content_hash(text: str) -> str:
    """Compute sha256 hash of normalized text for deduplication."""
    norm_text = re.sub(r"\s+", " ", text).strip().lower()
    return hashlib.sha256(norm_text.encode("utf-8")).hexdigest()


def determine_subdomain(
    clean_title: str,
    filename: str,
    content: str,
    config: AnonymizeConfig | None = None,
    rel_subfolder: str = "",
) -> tuple[str, str]:
    """
    Determine target self-docs subfolder and domain hierarchy.
    If the file is already inside a dedicated subfolder in the source directory,
    preserve that subfolder. Otherwise, classify using config.subdomain_rules.
    """
    if rel_subfolder and rel_subfolder not in (".", ""):
        # Keep existing folder taxonomy if already organized in source repo
        clean_sub = rel_subfolder.lower().replace("_", "-").replace(" ", "-")
        return clean_sub, f"self-docs > {clean_sub}"

    cfg = config or AnonymizeConfig.load()
    combo = f"{clean_title} {filename} {content[:1000]}".lower()

    for subfolder, keywords in cfg.subdomain_rules.items():
        if any(k in combo for k in keywords):
            return subfolder, f"self-docs > {subfolder}"

    return "general", "self-docs > general"


def extract_and_anonymize_file(
    src_file: str,
    dest_base_dir: str,
    dry_run: bool = False,
    seen_hashes: set[str] | None = None,
    config: AnonymizeConfig | None = None,
    src_base_dir: str | None = None,
) -> dict:
    """
    Process a single raw documentation file:
    - Anonymize content using AnonymizeConfig
    - Generate or validate canonical frontmatter
    - Write to appropriate self-docs/<subfolder>/ directory
    """
    if seen_hashes is None:
        seen_hashes = set()

    cfg = config or AnonymizeConfig.load(src_dir=src_base_dir or os.path.dirname(src_file))

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

    # 1. Anonymize with config
    sanitized = anonymize_text(raw_content, config=cfg)

    # 2. Check deduplication hash
    content_hash = compute_content_hash(sanitized)
    if content_hash in seen_hashes:
        res["status"] = "duplicate"
        return res
    seen_hashes.add(content_hash)

    # 3. Canonical Frontmatter & Taxonomy
    base_name = os.path.basename(src_file)
    clean_base = re.sub(r"^[0-9]+-?", "", base_name)  # remove leading dates like 150926-
    clean_base = re.sub(r"\[.*?\]", "", clean_base)    # remove brackets like [DOCS] or [PLAN]
    clean_base = re.sub(r"-?[0-9]{6}\.md$", ".md", clean_base)  # remove trailing 220726.md
    slug = os.path.splitext(clean_base)[0].lower().replace("_", "-").replace(" ", "-")
    slug = re.sub(r"[^a-z0-9-]", "", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    if not slug:
        slug = "tech-note"

    rel_sub = ""
    if src_base_dir and os.path.commonpath([src_file, src_base_dir]) == src_base_dir:
        rel_dir = os.path.dirname(os.path.relpath(src_file, src_base_dir))
        if rel_dir and rel_dir != ".":
            rel_sub = rel_dir.split(os.sep)[0]

    subfolder, domain_str = determine_subdomain(slug, base_name, sanitized, config=cfg, rel_subfolder=rel_sub)
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
    config: AnonymizeConfig | None = None,
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

    cfg = config or AnonymizeConfig.load(src_dir=src_dir)
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
                    config=cfg,
                    src_base_dir=src_dir,
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
    parser = argparse.ArgumentParser(description="Configurable Tech-Log Extractor & Anonymizer for KnowledgeLib.")
    parser.add_argument("--src", required=True, help="Source directory containing raw tech notes")
    parser.add_argument("--dest", default=os.path.join(os.path.dirname(__file__), "..", "self-docs"), help="Destination self-docs directory")
    parser.add_argument("--config", help="Path to anonymize_rules.yaml config file")
    parser.add_argument("--company", help="Comma-separated company names to anonymize (e.g. 'Coteccons,CTD')")
    parser.add_argument("--project", help="Comma-separated project names to anonymize (e.g. 'Payroll')")
    parser.add_argument("--email-domain", help="Comma-separated corporate email domains (e.g. 'coteccons.vn')")
    parser.add_argument("--ticket-prefix", help="Comma-separated ticket prefixes (e.g. 'PAYROLL,JIRA')")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without writing files")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of processed files")
    args = parser.parse_args()

    # Build config from file and CLI flags
    cfg = AnonymizeConfig.load(config_path=args.config, src_dir=args.src)
    if args.company:
        cfg.company_names.extend([c.strip() for c in args.company.split(",") if c.strip()])
    if args.project:
        cfg.project_names.extend([p.strip() for p in args.project.split(",") if p.strip()])
    if args.email_domain:
        cfg.email_domains.extend([e.strip().lower() for e in args.email_domain.split(",") if e.strip()])
    if args.ticket_prefix:
        cfg.ticket_prefixes.extend([t.strip() for t in args.ticket_prefix.split(",") if t.strip()])

    print(f"Extracting notes from: {args.src}")
    print(f"Target destination:    {args.dest}")
    if cfg.company_names:
        print(f"Configured companies:  {cfg.company_names}")
    if cfg.project_names:
        print(f"Configured projects:   {cfg.project_names}")
    if cfg.email_domains:
        print(f"Configured domains:    {cfg.email_domains}")

    report = extract_directory(args.src, args.dest, dry_run=args.dry_run, max_files=args.limit, config=cfg)

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
