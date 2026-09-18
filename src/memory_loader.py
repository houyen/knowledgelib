#!/usr/bin/env python3
"""
Memory Loader for KnowledgeLib Agent Context.
Scans canonical self-docs and knowledge units, extracts dense technical metadata,
and compiles an ultra-compact Memory Index to load into AI agent working memory.
"""

import argparse
from datetime import datetime, timezone
import os
import sys

from validate_canonical import parse_frontmatter, validate_unit_file

DEFAULT_REPO_DIR = os.environ.get(
    "KNOWLEDGELIB_PATH",
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
)


def load_canonical_units(
    repo_dir: str | None = None,
    domain_prefix: str = "self-docs",
) -> list[dict]:
    """
    Scan repo_dir for valid canonical units matching domain_prefix.
    Returns list of dicts with parsed metadata and body snippet.
    """
    target_dir = repo_dir or DEFAULT_REPO_DIR
    search_path = os.path.join(target_dir, domain_prefix) if not os.path.isabs(domain_prefix) else domain_prefix

    if not os.path.exists(search_path):
        return []

    units = []
    ignore_files = {
        "MEMORY_INDEX.md",
        "00-START-HERE.md",
        "document-map.md",
        "README.md",
        "AGENTS.md",
        "SKILL.md",
        "LICENSE.md",
    }

    for root, dirs, files in os.walk(search_path):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]
        for f in sorted(files):
            if f.endswith(".md") and f not in ignore_files:
                fpath = os.path.join(root, f)
                is_valid, _ = validate_unit_file(fpath)
                if not is_valid:
                    continue

                try:
                    with open(fpath, "r", encoding="utf-8") as fp:
                        content = fp.read()
                    meta, body = parse_frontmatter(content)
                    if not meta:
                        continue

                    rel_path = os.path.relpath(fpath, target_dir)
                    # Extract quick first paragraph preview
                    preview_lines = []
                    for line in body.strip().splitlines()[:15]:
                        clean_line = line.strip()
                        if clean_line and not clean_line.startswith("#") and clean_line not in ("---", "***", "___"):
                            preview_lines.append(clean_line)
                        if len(preview_lines) >= 2:
                            break
                    snippet = " ".join(preview_lines)[:250]

                    units.append({
                        "id": meta.get("id", rel_path[:-3]),
                        "canonical_question": meta.get("canonical_question", ""),
                        "aliases": meta.get("aliases", []),
                        "entity_type": meta.get("entity_type", "reference"),
                        "domain": meta.get("domain", ""),
                        "last_verified": str(meta.get("last_verified", "")),
                        "constraints": meta.get("constraints", []),
                        "skip_this_unit_if": meta.get("skip_this_unit_if", []),
                        "file_rel": rel_path,
                        "snippet": snippet,
                    })
                except Exception:
                    continue

    return units


def format_compact_memory_index(units: list[dict], title: str = "Self-Docs Working Memory Index") -> str:
    """
    Format a list of canonical units into a terse, high-density markdown memory sheet.
    Optimized for LLM context injection (~25-35 tokens per unit).
    """
    if not units:
        return f"# {title}\n\n*No canonical units indexed yet.*\n"

    now_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [
        f"# {title}",
        f"> **Generated:** {now_date} | **Active Units:** {len(units)} | **Mode:** High-Density Working Memory",
        "",
        "Use this index to recall verified internal decisions, runbooks, and gotchas before querying external LLM.",
        "",
    ]

    # Group by category
    categories = {
        "Critical Gotchas & Traps": [u for u in units if u["entity_type"] in ("gotchas", "troubleshooting")],
        "Architecture & Core Rules": [u for u in units if u["entity_type"] in ("architecture_explainer", "specification")],
        "Operations & Runbooks": [u for u in units if u["entity_type"] in ("runbook", "how_to")],
        "Other References": [u for u in units if u["entity_type"] not in ("gotchas", "troubleshooting", "architecture_explainer", "specification", "runbook", "how_to")],
    }

    for cat_name, cat_units in categories.items():
        if not cat_units:
            continue
        lines.append(f"### {cat_name}")
        for u in cat_units:
            aliases_str = f" [Aliases: {', '.join(u['aliases'][:3])}]" if u["aliases"] else ""
            lines.append(f"- **`{u['id']}`** ({u['entity_type']}): {u['canonical_question']}{aliases_str}")
            if u["constraints"]:
                for c in u["constraints"][:2]:
                    lines.append(f"  - ⚠️ *Constraint:* {c}")
            if u["snippet"]:
                lines.append(f"  - 📌 *Core:* {u['snippet']}")
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def export_memory_file(
    repo_dir: str | None = None,
    domain_prefix: str = "self-docs",
    target_file: str | None = None,
) -> str:
    """Export memory index to markdown file. Returns destination path."""
    root = repo_dir or DEFAULT_REPO_DIR
    units = load_canonical_units(repo_dir=root, domain_prefix=domain_prefix)
    index_md = format_compact_memory_index(units, title=f"KnowledgeLib Memory Index ({domain_prefix})")

    if target_file is None:
        target_file = os.path.join(root, "self-docs", "MEMORY_INDEX.md")

    os.makedirs(os.path.dirname(os.path.abspath(target_file)), exist_ok=True)
    with open(target_file, "w", encoding="utf-8") as f:
        f.write(index_md)

    return target_file


def get_memory_index(repo_dir: str | None = None, domain: str = "self-docs") -> str:
    """Programmatic entry point for MCP tool or agent client."""
    root = repo_dir or DEFAULT_REPO_DIR
    units = load_canonical_units(repo_dir=root, domain_prefix=domain)
    return format_compact_memory_index(units, title=f"KnowledgeLib Memory Snapshot ({domain})")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate compact Agent Memory Index from canonical units")
    parser.add_argument("--domain", type=str, default="self-docs", help="Domain or folder to index (default: self-docs)")
    parser.add_argument("--repo-dir", type=str, default=DEFAULT_REPO_DIR, help="KnowledgeLib repository directory")
    parser.add_argument("--export", action="store_true", help="Export memory index to MEMORY_INDEX.md (default)")
    parser.add_argument("--output", type=str, default=None, help="Output file path (default: <repo_dir>/self-docs/MEMORY_INDEX.md)")
    parser.add_argument("--print", action="store_true", help="Print memory index to stdout")

    args = parser.parse_args(argv)

    if args.print:
        content = get_memory_index(repo_dir=args.repo_dir, domain=args.domain)
        print(content)
        return 0

    out_path = export_memory_file(
        repo_dir=args.repo_dir,
        domain_prefix=args.domain,
        target_file=args.output,
    )
    print(f"✅ Memory index successfully exported to: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
