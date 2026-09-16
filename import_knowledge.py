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

REPO_DIR = os.path.abspath(os.path.dirname(__file__))
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
    target_dir = os.path.join(REPO_DIR, domain_path)
    os.makedirs(target_dir, exist_ok=True)
    
    saved_file_infos = []
    
    for u in units:
        num = u["num"]
        title = u["title"]
        slug = re.sub(r"[^\w\s-]", "", title.lower()).strip().replace(" ", "-")
        slug = re.sub(r"-+", "-", slug) or f"unit-{num}"
        
        filename = f"unit-{num}-{slug}.md"
        file_path = os.path.join(target_dir, filename)
        
        rel_path = os.path.relpath(file_path, REPO_DIR)
        unit_id = os.path.splitext(rel_path)[0]
        
        preview = u["content"].strip()[:300].replace("\n", " ")
        
        meta = {
            "id": unit_id,
            "canonical_question": title,
            "aliases": [title, f"Unit {num}", slug],
            "entity_type": entity_type,
            "domain": domain_str,
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
            "last_verified": "2026-08-18",
            "content_preview": preview
        })
        
    return saved_file_infos

def scan_and_collect_all_markdown_units() -> list:
    """Scan entire repository for all unit .md files and build catalog entries."""
    units = []
    ignore_files = {'SKILL.md', 'AGENT_PROMPT_SNIPPET.md', 'agent.md', 'walkthrough_index.md', 'walkthrough_index_full.md', 'README.md', 'LICENSE.md'}
    
    for root, dirs, files in os.walk(REPO_DIR):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for file in files:
            if file.endswith('.md') and file not in ignore_files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, REPO_DIR)
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
                    
                    unit_entry = {
                        "id": unit_id,
                        "canonical_question": meta.get("canonical_question", os.path.basename(unit_id)),
                        "aliases": meta.get("aliases", []),
                        "entity_type": meta.get("entity_type", "reference"),
                        "domain": meta.get("domain", os.path.dirname(unit_id).replace('/', ' > ')),
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
    
    if sync_only:
        all_units = scan_and_collect_all_markdown_units()
        catalog_data = {
            "schema_version": "1.1",
            "updated_at": "2026-08-18",
            "total_units": len(all_units),
            "units": all_units
        }
    else:
        with open(CATALOG_PATH, "r", encoding="utf-8") as f:
            catalog_data = json.load(f)
            
        existing_units = catalog_data.get("units", [])
        unit_map = {u["id"]: u for u in existing_units if "id" in u}
        
        if new_unit_entries:
            for entry in new_unit_entries:
                unit_map[entry["id"]] = entry
                
        updated_list = list(unit_map.values())
        catalog_data["units"] = updated_list
        catalog_data["total_units"] = len(updated_list)
    
    with open(CATALOG_PATH, "w", encoding="utf-8") as f:
        json.dump(catalog_data, f, ensure_ascii=False, indent=2)
        
    print(f"✅ catalog.json synchronized! Total Units: {catalog_data['total_units']}")
    
    # Sync ChromaDB
    sys.path.append(REPO_DIR)
    try:
        from sync_knowledgelib import reindex_chromadb
        print("🔄 Re-indexing ChromaDB Vector Database...")
        reindex_chromadb(catalog_data, REPO_DIR)
        print("✨ ChromaDB vector sync complete!")
    except Exception as e:
        print(f"⚠️ ChromaDB sync warning: {e}")

def run_import(
    file_path: str | None,
    domain_path: str = "software/imported-books",
    domain: str = "software > imported_knowledge",
    entity_type: str = "book_chapter",
    sync_only: bool = False,
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

    units = split_text_into_units(pages, doc_name)
    new_entries = save_units_to_tree(units, domain_path, entity_type, domain)
    update_catalog_and_vector_db(new_entries)

    return {
        "status": "success",
        "mode": "import",
        "file": input_file,
        "unit_ids": [e["id"] for e in new_entries],
        "unit_count": len(new_entries),
    }


def main():
    parser = argparse.ArgumentParser(description="Import & Sync knowledge document into KnowledgeLib")
    parser.add_argument("file_path", nargs="?", help="Path to PDF, EPUB, TXT, or MD file")
    parser.add_argument("--domain-path", default="software/imported-books", help="Directory tree path inside repo (e.g. software/system-design/my-book)")
    parser.add_argument("--domain", default="software > imported_knowledge", help="Domain string for metadata")
    parser.add_argument("--type", default="book_chapter", help="Entity type (e.g. book_chapter, reference)")
    parser.add_argument("--sync-only", action="store_true", help="Re-scan repo markdown files, update catalog.json and ChromaDB without importing new file")

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
    )
    if result["status"] != "success":
        print(f"❌ {result['message']}")
        sys.exit(1)

    print(f"✅ Created {result['unit_count']} unit(s): {result['unit_ids']}")
    print("\n🎉 Import & Ingestion process successfully completed!")

if __name__ == "__main__":
    main()
