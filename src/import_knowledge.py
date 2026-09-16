#!/usr/bin/env python3
"""
KnowledgeLib Auto-Ingestion & Sync Protocol Tool
Converts documents into KnowledgeLib tree units or syncs existing markdown files,
updates catalog.json, and re-indexes ChromaDB vector store automatically.

Supported Host Agents: Antigravity CLI, Claude Code, GitHub Copilot CLI, Amp, Cursor, Custom Agents.

Usage:
  1. Full Auto-Import Mode (PDF/EPUB/TXT/MD -> Tree -> Index):
     python3 import_knowledge.py <path_to_file> --domain-path "software/system-design/my-book" --domain "software > system-design > workbook"

  2. Agent-driven Sync Only Mode (Re-index existing .md files created by any AI Agent):
     python3 import_knowledge.py --sync-only
"""

import os
import sys
import re
import json
import yaml
import argparse
import hashlib

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def _repo_dir() -> str:
    """Return local repository base path, reading KNOWLEDGELIB_PATH dynamically if set."""
    return os.environ.get("KNOWLEDGELIB_PATH", os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

REPO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CATALOG_PATH = os.path.join(REPO_DIR, "catalog.json")
DB_DIR = os.path.join(REPO_DIR, ".chroma_db")

def parse_pdf_pages(pdf_path: str) -> list:
    """Extract pages from PDF using pypdf."""
    try:
        import pypdf
        reader = pypdf.PdfReader(pdf_path)
        pages = []
        for i, page in enumerate(reader.pages):
            txt = page.extract_text() or ""
            if txt.strip():
                pages.append((i + 1, txt))
        return pages
    except Exception as e:
        print(f"❌ Failed to parse PDF with pypdf: {e}")
        return []

def compute_content_hash(content: str) -> str:
    """Compute SHA256 hash of normalized content (lowercased, collapsed whitespace)."""
    normalized = re.sub(r"\s+", " ", content.strip().lower())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

def find_duplicate_unit_id(content_hash: str, existing_units: list[dict]) -> str | None:
    """Find the id of an existing unit that matches content_hash, or None."""
    if not content_hash:
        return None
    for u in existing_units:
        if u.get("content_hash") == content_hash:
            return u.get("id")
    return None

def split_text_into_units(pages: list, doc_name: str) -> list:
    """Split extracted document pages into logical Knowledge Units."""
    units = []
    heading_pattern = re.compile(r"^(?:chapter|day|section|part)\s+(\d{1,3})[:\.\s-]*(.*)$", re.IGNORECASE | re.MULTILINE)
    current_unit = None
    
    for page_num, text in pages:
        lines = text.splitlines()
        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue
            
            match = heading_pattern.match(line_str)
            if match:
                if current_unit and current_unit["content"].strip():
                    units.append(current_unit)
                
                num = match.group(1).zfill(2)
                raw_title = match.group(2).strip() or f"Section {num}"
                clean_title = re.sub(r"[^\w\s-]", "", raw_title).strip()
                
                current_unit = {
                    "num": num,
                    "title": clean_title if clean_title else f"Unit {num}",
                    "content": line_str + "\n\n"
                }
            else:
                if current_unit is None:
                    current_unit = {
                        "num": "01",
                        "title": f"Overview - {doc_name}",
                        "content": ""
                    }
                current_unit["content"] += line_str + "\n"
                
    if current_unit and current_unit["content"].strip():
        units.append(current_unit)
        
    if not units and pages:
        full_txt = "\n".join(p[1] for p in pages)
        units.append({
            "num": "01",
            "title": f"Summary - {doc_name}",
            "content": full_txt
        })
        
    return units

def save_units_to_tree(units: list, domain_path: str, entity_type: str, domain_str: str) -> list:
    """Save units into local Markdown tree structure with Frontmatter."""
    repo_dir = _repo_dir()
    target_dir = os.path.join(repo_dir, domain_path)
    os.makedirs(target_dir, exist_ok=True)
    
    saved_file_infos = []
    
    for u in units:
        num = u["num"]
        title = u["title"]
        slug = re.sub(r"[^\w\s-]", "", title.lower()).strip().replace(" ", "-")
        slug = re.sub(r"-+", "-", slug) or f"unit-{num}"
        
        filename = f"unit-{num}-{slug}.md"
        file_path = os.path.join(target_dir, filename)
        
        rel_path = os.path.relpath(file_path, repo_dir)
        unit_id = os.path.splitext(rel_path)[0]
        
        preview = u["content"].strip()[:300].replace("\n", " ")
        content_hash = compute_content_hash(u["content"])
        
        meta = {
            "id": unit_id,
            "canonical_question": title,
            "aliases": [title, f"Unit {num}", slug],
            "entity_type": entity_type,
            "domain": domain_str,
            "content_hash": content_hash,
            "last_verified": "2026-08-18"
        }
        
        yaml_header = yaml.dump(meta, allow_unicode=True, sort_keys=False).strip()
        md_text = f"---\n{yaml_header}\n---\n\n# {title}\n\n{u['content']}\n"
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(md_text)
            
        saved_file_infos.append({
            "id": unit_id,
            "canonical_question": title,
            "aliases": meta["aliases"],
            "entity_type": entity_type,
            "domain": domain_str,
            "content_hash": content_hash,
            "last_verified": "2026-08-18",
            "content_preview": preview
        })
        
    return saved_file_infos

def scan_and_collect_all_markdown_units() -> list:
    """Scan entire repository for all unit .md files and build catalog entries."""
    units = []
    ignore_files = {
        'SKILL.md',
        'AGENT_PROMPT_SNIPPET.md',
        'agent.md',
        'walkthrough_index.md',
        'walkthrough_index_full.md',
        'README.md',
        'LICENSE.md',
        'AGENTS.md',
        'PHASE5_PLAN.md',
    }
    repo_dir = _repo_dir()
    for root, dirs, files in os.walk(repo_dir):
        dirs[:] = [
            d for d in dirs
            if not d.startswith('.') and d not in ('games', 'docs', 'src', 'tests', 'scripts', 'templates')
        ]
        for file in files:
            if file.endswith('.md') and file not in ignore_files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, repo_dir)
                default_id = os.path.splitext(rel_path)[0]
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    meta = {}
                    preview = ""
                    if content.startswith('---'):
                        parts = content.split('---', 2)
                        if len(parts) >= 3:
                            try:
                                meta = yaml.safe_load(parts[1]) or {}
                            except Exception:
                                pass
                            preview = parts[2].strip()[:300].replace('\n', ' ')
                    
                    unit_id = meta.get("id", default_id)
                    content_hash = meta.get("content_hash")
                    
                    unit_entry = {
                        "id": unit_id,
                        "canonical_question": meta.get("canonical_question", os.path.basename(unit_id)),
                        "aliases": meta.get("aliases", []),
                        "entity_type": meta.get("entity_type", "reference"),
                        "domain": meta.get("domain", os.path.dirname(unit_id).replace('/', ' > ')),
                        "content_hash": content_hash,
                        "last_verified": str(meta.get("last_verified", "2026-08-18")),
                        "content_preview": preview
                    }
                    units.append(unit_entry)
                except Exception as e:
                    print(f"⚠️ Error reading {file_path}: {e}")
                    
    return units

def update_catalog_and_vector_db(new_unit_entries: list = None, sync_only: bool = False):
    """Update catalog.json and sync ChromaDB vector database."""
    print("🔄 Updating catalog.json...")
    repo_dir = _repo_dir()
    catalog_path = os.path.join(repo_dir, "catalog.json")

    if sync_only:
        all_units = scan_and_collect_all_markdown_units()
        catalog_data = {
            "schema_version": "1.1",
            "updated_at": "2026-08-18",
            "total_units": len(all_units),
            "units": all_units
        }
    else:
        with open(catalog_path, "r", encoding="utf-8") as f:
            catalog_data = json.load(f)
            
        existing_units = catalog_data.get("units", [])
        unit_map = {u["id"]: u for u in existing_units if "id" in u}
        
        if new_unit_entries:
            for entry in new_unit_entries:
                unit_map[entry["id"]] = entry
                
        updated_list = list(unit_map.values())
        catalog_data["units"] = updated_list
        catalog_data["total_units"] = len(updated_list)
    
    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump(catalog_data, f, ensure_ascii=False, indent=2)
        
    print(f"✅ catalog.json synchronized! Total Units: {catalog_data['total_units']}")
    
    # Sync ChromaDB
    sys.path.append(repo_dir)
    try:
        from sync_knowledgelib import reindex_chromadb
        print("🔄 Re-indexing ChromaDB Vector Database...")
        reindex_chromadb(catalog_data, repo_dir)
        print("✨ ChromaDB vector sync complete!")
    except Exception as e:
        print(f"⚠️ ChromaDB sync warning: {e}")

def run_import(
    file_path: str | None,
    domain_path: str = "software/imported-books",
    domain: str = "software > imported_knowledge",
    entity_type: str = "book_chapter",
    sync_only: bool = False,
    use_llm_split: bool = True,
) -> dict:
    """
    Callable core of the ingestion pipeline (no argparse, no sys.exit).
    Used by both the CLI (`main()`) and the MCP `knowledgelib_ingest` tool.
    Returns a status dict instead of printing-and-exiting on error.
    """
    if sync_only:
        update_catalog_and_vector_db(sync_only=True)
        return {"status": "success", "mode": "sync_only"}

    if not file_path:
        return {"status": "error", "message": "file_path is required unless sync_only=True"}

    input_file = os.path.abspath(file_path)
    if not os.path.exists(input_file):
        return {"status": "error", "message": f"Input file not found at {input_file}"}

    doc_name = os.path.splitext(os.path.basename(input_file))[0]

    if input_file.lower().endswith(".pdf"):
        pages = parse_pdf_pages(input_file)
    elif input_file.lower().endswith((".md", ".txt")):
        with open(input_file, "r", encoding="utf-8") as f:
            pages = [(1, f.read())]
    else:
        try:
            with open(input_file, "r", encoding="utf-8", errors="ignore") as f:
                pages = [(1, f.read())]
        except Exception as e:
            return {"status": "error", "message": f"Failed to read file: {e}"}

    units = None
    if use_llm_split:
        try:
            from llm_splitter import split_text_with_llm
            units = split_text_with_llm(pages, doc_name)
        except Exception:
            units = None

    split_method = "llm" if units else "regex"
    if not units:
        units = split_text_into_units(pages, doc_name)

    # Load existing catalog units for deduplication check
    repo_dir = _repo_dir()
    catalog_path = os.path.join(repo_dir, "catalog.json")
    existing_units = []
    if os.path.exists(catalog_path):
        try:
            with open(catalog_path, "r", encoding="utf-8") as f:
                c_data = json.load(f)
                existing_units = c_data.get("units", [])
        except Exception:
            existing_units = []

    skipped_duplicates = []
    units_to_save = []
    for u in units:
        c_hash = compute_content_hash(u.get("content", ""))
        dup_id = find_duplicate_unit_id(c_hash, existing_units)
        if dup_id:
            skipped_duplicates.append({"content_hash": c_hash, "existing_unit_id": dup_id})
        else:
            units_to_save.append(u)

    new_entries = []
    if units_to_save:
        new_entries = save_units_to_tree(units_to_save, domain_path, entity_type, domain)
        update_catalog_and_vector_db(new_entries)

    return {
        "status": "success",
        "mode": "import",
        "file": input_file,
        "unit_ids": [e["id"] for e in new_entries],
        "unit_count": len(new_entries),
        "skipped_duplicates": skipped_duplicates,
        "split_method": split_method,
    }


def main():
    parser = argparse.ArgumentParser(description="Import & Sync knowledge document into KnowledgeLib")
    parser.add_argument("file_path", nargs="?", help="Path to PDF, EPUB, TXT, or MD file")
    parser.add_argument("--domain-path", default="software/imported-books", help="Directory tree path inside repo (e.g. software/system-design/my-book)")
    parser.add_argument("--domain", default="software > imported_knowledge", help="Domain string for metadata")
    parser.add_argument("--type", default="book_chapter", help="Entity type (e.g. book_chapter, reference)")
    parser.add_argument("--sync-only", action="store_true", help="Re-scan repo markdown files, update catalog.json and ChromaDB without importing new file")
    parser.add_argument("--no-llm-split", action="store_true", help="Disable LLM splitting and use regex heading splitter directly")

    args = parser.parse_args()

    if args.sync_only:
        print("🚀 Starting Repository Sync-Only Mode...")
        result = run_import(None, sync_only=True)
        if result["status"] != "success":
            print(f"❌ {result['message']}")
            sys.exit(1)
        print("\n🎉 Repository catalog & vector database sync completed!")
        return

    if not args.file_path:
        parser.print_help()
        sys.exit(1)

    print(f"🚀 Starting Ingestion for: {os.path.abspath(args.file_path)}")
    result = run_import(
        args.file_path,
        domain_path=args.domain_path,
        domain=args.domain,
        entity_type=args.type,
        use_llm_split=not args.no_llm_split,
    )
    if result["status"] != "success":
        print(f"❌ {result['message']}")
        sys.exit(1)

    print(f"✅ Created {result['unit_count']} unit(s): {result['unit_ids']}")
    if result.get("skipped_duplicates"):
        print(f"ℹ️ Skipped {len(result['skipped_duplicates'])} duplicate unit(s)")
    print(f"🔀 Split Method: {result.get('split_method', 'regex')}")
    print("\n🎉 Import & Ingestion process successfully completed!")

if __name__ == "__main__":
    main()
