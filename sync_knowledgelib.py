#!/usr/bin/env python3
"""
KnowledgeLib Data Sync Script
Automates fetching catalog.json and syncing all unit .md files from knowledgelib.io
to a local directory structure while preserving local custom units.
"""

import os
import sys
import json
import yaml
import argparse
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

CATALOG_URL = "https://knowledgelib.io/catalog.json"
DEFAULT_TARGET_DIR = os.path.abspath(os.path.dirname(__file__))
MAX_WORKERS = 15
USER_AGENT = "KnowledgeLibSync/1.0 (Python urllib)"


def fetch_url(url: str, timeout: int = 15) -> bytes:
    """Fetch content from a URL with standard User-Agent header."""
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=timeout) as response:
        return response.read()


def download_catalog(catalog_url: str) -> dict:
    """Download catalog.json from remote URL, returning parsed JSON data."""
    print(f"📥 Downloading catalog from {catalog_url}...")
    try:
        data_bytes = fetch_url(catalog_url)
        print("✅ Remote catalog fetched successfully!")
        return json.loads(data_bytes.decode("utf-8"))
    except Exception as e:
        print(f"⚠️ Failed to download remote catalog ({e}). Using local catalog if available.", file=sys.stderr)
        return {}


def sync_unit(unit: dict, target_dir: str) -> str:
    """
    Sync a single unit .md file.
    Returns status: 'downloaded', 'skipped', or 'failed'.
    """
    unit_id = unit.get("id")
    if not unit_id:
        return "failed"

    # Construct local file path: target_dir/unit_id.md
    rel_path = f"{unit_id}.md"
    local_path = os.path.join(target_dir, rel_path)

    # Skip if file already exists and is non-empty
    if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
        return "skipped"

    # Determine remote URL
    raw_md_url = unit.get("raw_md") or f"https://knowledgelib.io/api/v1/units/{unit_id}.md"

    # Ensure parent directories exist
    os.makedirs(os.path.dirname(local_path), exist_ok=True)

    # Download file
    try:
        content = fetch_url(raw_md_url)
        with open(local_path, "wb") as f:
            f.write(content)
        return "downloaded"
    except Exception as e:
        return "failed"


def scan_local_units(target_dir: str) -> list:
    """Scan all local markdown files in repository to preserve offline imported books/units."""
    local_units = []
    ignore_files = {'SKILL.md', 'AGENT_PROMPT_SNIPPET.md', 'agent.md', 'walkthrough_index.md', 'walkthrough_index_full.md', 'README.md', 'LICENSE.md'}
    
    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for file in files:
            if file.endswith('.md') and file not in ignore_files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, target_dir)
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
                    local_units.append(unit_entry)
                except Exception as e:
                    pass
    return local_units


def reindex_chromadb(catalog_data: dict, target_dir: str):
    """
    Re-index / Upsert units in ChromaDB vector database (.chroma_db)
    to match the updated catalog.json and local markdown files.
    """
    try:
        import chromadb
    except ImportError:
        print("⚠️ chromadb library is not installed. Skipping vector re-indexing.")
        return

    db_dir = os.path.join(target_dir, ".chroma_db")
    print(f"🔄 Re-indexing vector store at: {db_dir}...")

    try:
        client = chromadb.PersistentClient(path=db_dir)
        collection = client.get_or_create_collection(name="knowledgelib_units")
    except Exception as e:
        print(f"❌ Failed to connect to ChromaDB: {e}")
        return

    units = catalog_data.get("units", [])
    if not units:
        print("⚠️ Catalog contains no units.")
        return

    existing_ids = set()
    try:
        existing_data = collection.get()
        if existing_data and "ids" in existing_data:
            existing_ids = set(existing_data["ids"])
    except Exception:
        pass

    current_catalog_ids = set()
    ids_to_upsert = []
    documents_to_upsert = []
    metadatas_to_upsert = []

    for unit in units:
        unit_id = unit.get("id")
        if not unit_id:
            continue

        current_catalog_ids.add(unit_id)
        canonical = unit.get("canonical_question", "")
        aliases = " | ".join(unit.get("aliases", []))
        domain = unit.get("domain", "")
        entity_type = unit.get("entity_type", "")
        last_verified = unit.get("last_verified", "")

        local_path = os.path.join(target_dir, f"{unit_id}.md")
        preview = unit.get("content_preview", "")
        if os.path.exists(local_path):
            try:
                with open(local_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if content.startswith("---"):
                        parts = content.split("---", 2)
                        if len(parts) >= 3:
                            content = parts[2]
                    preview = content.strip()[:300].replace("\n", " ")
            except Exception:
                pass

        doc_text = f"Question: {canonical}\nAliases: {aliases}\nDomain: {domain}\nPreview: {preview}"

        ids_to_upsert.append(unit_id)
        documents_to_upsert.append(doc_text)
        metadatas_to_upsert.append({
            "canonical_question": canonical,
            "domain": domain,
            "entity_type": entity_type,
            "last_verified": last_verified
        })

    batch_size = 250
    for i in range(0, len(ids_to_upsert), batch_size):
        collection.upsert(
            ids=ids_to_upsert[i:i+batch_size],
            documents=documents_to_upsert[i:i+batch_size],
            metadatas=metadatas_to_upsert[i:i+batch_size]
        )

    stale_ids = list(existing_ids - current_catalog_ids)
    if stale_ids:
        print(f"🧹 Removing {len(stale_ids)} stale/deleted units from vector store...")
        try:
            collection.delete(ids=stale_ids)
        except Exception as e:
            print(f"⚠️ Failed to remove stale IDs: {e}")

    print(f"✅ ChromaDB vector index synchronized! Total entries: {collection.count()}")


def main():
    parser = argparse.ArgumentParser(
        description="Sync KnowledgeLib catalog and unit markdown files."
    )
    parser.add_argument(
        "--dir",
        default=DEFAULT_TARGET_DIR,
        help=f"Target directory for synced data (default: {DEFAULT_TARGET_DIR})",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=MAX_WORKERS,
        help=f"Number of concurrent download threads (default: {MAX_WORKERS})",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-download of existing files",
    )
    parser.add_argument(
        "--skip-index",
        action="store_true",
        help="Skip re-indexing ChromaDB vector database after sync",
    )
    args = parser.parse_args()

    target_dir = os.path.abspath(args.dir)
    catalog_file_path = os.path.join(target_dir, "catalog.json")

    print(f"🚀 Starting KnowledgeLib web & local sync...")
    print(f"📂 Target Directory: {target_dir}")
    print(f"⚡ Concurrent Threads: {args.workers}")
    print("-" * 50)

    start_time = time.time()

    # 1. Download remote catalog.json
    remote_catalog = download_catalog(CATALOG_URL)
    remote_units = remote_catalog.get("units", [])
    total_remote = len(remote_units)

    print(f"📋 Found {total_remote} remote units in online catalog. Syncing markdown files...")

    if args.force:
        print("⚠️ Force mode enabled: existing files will be re-downloaded.")

    # 2. Sync unit markdown files in parallel
    downloaded_count = 0
    skipped_count = 0
    failed_count = 0

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {}
        for unit in remote_units:
            if args.force:
                unit_id = unit.get("id")
                if unit_id:
                    local_path = os.path.join(target_dir, f"{unit_id}.md")
                    if os.path.exists(local_path):
                        try:
                            os.remove(local_path)
                        except OSError:
                            pass
            future = executor.submit(sync_unit, unit, target_dir)
            futures[future] = unit

        processed = 0
        for future in as_completed(futures):
            processed += 1
            res = future.result()
            if res == "downloaded":
                downloaded_count += 1
            elif res == "skipped":
                skipped_count += 1
            else:
                failed_count += 1

            if processed % 200 == 0 or processed == total_remote:
                print(
                    f"Progress: {processed}/{total_remote} | "
                    f"Downloaded: {downloaded_count} | "
                    f"Skipped: {skipped_count} | "
                    f"Failed: {failed_count}"
                )

    # 3. Merge local units into catalog.json so offline imported books are preserved!
    print("-" * 50)
    print("🔍 Scanning and merging all local units into catalog.json...")
    all_local_units = scan_local_units(target_dir)
    
    unit_map = {u["id"]: u for u in remote_units if "id" in u}
    for lu in all_local_units:
        unit_map[lu["id"]] = lu
        
    merged_units = list(unit_map.values())
    final_catalog = {
        "schema_version": "1.1",
        "updated_at": "2026-08-18",
        "total_units": len(merged_units),
        "units": merged_units
    }
    
    with open(catalog_file_path, "w", encoding="utf-8") as f:
        json.dump(final_catalog, f, ensure_ascii=False, indent=2)
        
    print(f"✅ Merged catalog.json saved! Total Units (Remote + Local): {len(merged_units)}")

    # 4. Re-index ChromaDB unless skipped
    if not args.skip_index:
        print("-" * 50)
        reindex_chromadb(final_catalog, target_dir)

    elapsed = time.time() - start_time
    print("-" * 50)
    print("✨ KnowledgeLib Web & Local Sync completed!")
    print(f"⏱️ Time taken: {elapsed:.2f} seconds")
    print(f"📊 Summary:")
    print(f"   - Total Units (Remote + Local): {len(merged_units)}")
    print(f"   - Downloaded : {downloaded_count}")
    print(f"   - Skipped    : {skipped_count}")
    print(f"   - Failed     : {failed_count}")
    print(f"📁 Local Data: {target_dir}")


if __name__ == "__main__":
    main()
