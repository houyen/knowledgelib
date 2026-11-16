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
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

CATALOG_URL = "https://knowledgelib.io/catalog.json"
DEFAULT_TARGET_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
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
    # MEMORY_INDEX.md là artefact sinh tự động từ chính catalog (memory_loader), không phải unit tri thức:
    # đưa vào catalog làm nó tự trỏ vào chính nó và sinh bản trùng khi bị chép sang self-docs/<domain>/.
    ignore_files = {'SKILL.md', 'AGENT_PROMPT_SNIPPET.md', 'agent.md', 'walkthrough_index.md', 'walkthrough_index_full.md', 'README.md', 'LICENSE.md', 'MEMORY_INDEX.md',
                    'AGENTS.md', 'CLAUDE.md', 'GEMINI.md'}
    ignore_dirs = {'harness', 'docs', 'config', 'scripts', 'tests', 'src', 'llmwiki', 'node_modules', 'templates', 'dist', 'build', 'skills', 'addons'}
    
    for root, dirs, files in os.walk(target_dir):
        # ignore_dirs chỉ áp cho thư mục cấp gốc repo (docs/, src/, tests/...). Áp ở mọi độ sâu làm rơi
        # các unit hợp lệ nằm trong thư mục lồng tên trùng, vd self-docs/docs/plan-phase-a.md.
        at_top = os.path.abspath(root) == os.path.abspath(target_dir)
        dirs[:] = [d for d in dirs if not d.startswith('.') and not (at_top and d in ignore_dirs)]
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


def _unit_doc_text(unit: dict, target_dir: str) -> tuple:
    """Văn bản đem embed cho một unit + metadata lưu kèm."""
    from alias_overlay import load_extra_aliases, merged_aliases

    unit_id = unit.get("id")
    canonical = unit.get("canonical_question", "")
    aliases = " | ".join(merged_aliases(unit, load_extra_aliases(target_dir)))
    domain = unit.get("domain", "")

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
    metadata = {
        "canonical_question": canonical,
        "domain": domain,
        "entity_type": unit.get("entity_type", ""),
        "last_verified": unit.get("last_verified", ""),
    }
    return doc_text, metadata


def _existing_ids(collection) -> set:
    try:
        data = collection.get(include=[])
        return set(data.get("ids", [])) if data else set()
    except Exception:
        return set()


def _reindex_multilingual(client, embedder, rows: list) -> int:
    """
    Index vào collection đa ngữ (e5). Chỉ embed lại unit có văn bản thay đổi (so `doc_hash` trong
    metadata), vì embed toàn kho mất cả phút còn sync chạy sau mỗi phiên làm việc.
    """
    import hashlib
    from embedding import ML_COLLECTION

    collection = client.get_or_create_collection(name=ML_COLLECTION, metadata={"hnsw:space": "cosine"})
    stored = {}
    try:
        data = collection.get(include=["metadatas"])
        for uid, meta in zip(data.get("ids", []), data.get("metadatas", []) or []):
            stored[uid] = (meta or {}).get("doc_hash")
    except Exception:
        stored = {}

    todo = []
    for unit_id, doc_text, metadata in rows:
        doc_hash = hashlib.md5(doc_text.encode("utf-8")).hexdigest()
        if stored.get(unit_id) != doc_hash:
            todo.append((unit_id, doc_text, {**metadata, "doc_hash": doc_hash}))

    if todo:
        print(f"🧠 Embedding {len(todo)} new/changed units ({ML_COLLECTION})...")
    batch_size = 128
    for i in range(0, len(todo), batch_size):
        chunk = todo[i:i + batch_size]
        collection.upsert(
            ids=[c[0] for c in chunk],
            documents=[c[1] for c in chunk],
            metadatas=[c[2] for c in chunk],
            embeddings=embedder.embed_passages([c[1] for c in chunk]),
        )

    stale = list(set(stored) - {r[0] for r in rows})
    if stale:
        print(f"🧹 Removing {len(stale)} stale/deleted units from multilingual vector store...")
        try:
            collection.delete(ids=stale)
        except Exception as e:
            print(f"⚠️ Failed to remove stale IDs: {e}")
    return collection.count()


def reindex_chromadb(catalog_data: dict, target_dir: str):
    """
    Re-index / Upsert units in ChromaDB vector database (.chroma_db)
    to match the updated catalog.json and local markdown files.

    Hai collection:
      - knowledgelib_units_<model>: embedding đa ngữ (ưu tiên khi nạp được model, xem src/embedding.py).
      - knowledgelib_units   : embedding mặc định của Chroma, giữ làm fallback khi không có model.
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

    rows = []
    for unit in units:
        if not unit.get("id"):
            continue
        doc_text, metadata = _unit_doc_text(unit, target_dir)
        rows.append((unit["id"], doc_text, metadata))
    current_catalog_ids = {r[0] for r in rows}

    # 1. Collection đa ngữ (nếu nạp được model)
    ml_done = False
    try:
        from embedding import load_embedder
        embedder = load_embedder()
        if embedder is not None:
            total = _reindex_multilingual(client, embedder, rows)
            print(f"✅ Multilingual vector index synchronized! Total entries: {total}")
            ml_done = True
    except (KeyboardInterrupt, SystemExit):
        raise
    except BaseException as e:
        print(f"⚠️ Multilingual index skipped ({e}). Legacy index still updated.")

    # 2. Collection legacy (fallback) — cũng chỉ embed lại unit có văn bản thay đổi.
    import hashlib
    legacy_hash = {}
    try:
        data = collection.get(include=["metadatas"])
        for uid, meta in zip(data.get("ids", []), data.get("metadatas", []) or []):
            legacy_hash[uid] = (meta or {}).get("doc_hash")
    except Exception:
        legacy_hash = {}
    existing_ids = set(legacy_hash) or _existing_ids(collection)
    todo = []
    for unit_id, doc_text, metadata in rows:
        doc_hash = hashlib.md5(doc_text.encode("utf-8")).hexdigest()
        if legacy_hash.get(unit_id) != doc_hash:
            todo.append((unit_id, doc_text, {**metadata, "doc_hash": doc_hash}))
    batch_size = 250
    for i in range(0, len(todo), batch_size):
        chunk = todo[i:i + batch_size]
        collection.upsert(
            ids=[c[0] for c in chunk],
            documents=[c[1] for c in chunk],
            metadatas=[c[2] for c in chunk],
        )

    stale_ids = list(existing_ids - current_catalog_ids)
    if stale_ids:
        print(f"🧹 Removing {len(stale_ids)} stale/deleted units from vector store...")
        try:
            collection.delete(ids=stale_ids)
        except Exception as e:
            print(f"⚠️ Failed to remove stale IDs: {e}")

    print(f"✅ ChromaDB vector index synchronized! Total entries: {collection.count()}"
          + ("" if ml_done else " (legacy embedder only)"))


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
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
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

        # 4b. Cảnh báo drift / trùng lặp (chỉ in, không làm hỏng sync)
        try:
            import index_health
            index_health.print_report(index_health.run_checks(target_dir, merged_units))
        except (KeyboardInterrupt, SystemExit):
            raise
        except BaseException as e:  # gồm cả pyo3 PanicException của chromadb
            print(f"⚠️ Index health check skipped ({e})")

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
