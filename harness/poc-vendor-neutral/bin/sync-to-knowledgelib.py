#!/usr/bin/env python3
"""
sync-to-knowledgelib — CLI helper to manually or automatically sync
canonical self-docs/ from this repository into the centralized KnowledgeLib.
"""

import argparse
import os
import subprocess
import sys


def find_project_root():
    d = os.path.abspath(os.path.dirname(__file__))
    while d != "/":
        if os.path.exists(os.path.join(d, "policy.yaml")) or os.path.exists(os.path.join(d, ".git")):
            return d
        d = os.path.dirname(d)
    return os.getcwd()


def main():
    parser = argparse.ArgumentParser(description="Sync project self-docs to central KnowledgeLib.")
    parser.add_argument("--src", help="Source directory (defaults to <project_root>/self-docs)")
    parser.add_argument("--dest", help="Destination in KnowledgeLib (defaults to $KNOWLEDGELIB_HOME/self-docs)")
    parser.add_argument("--dry-run", action="store_true", help="Simulate extraction without writing")
    args = parser.parse_args()

    root = find_project_root()
    src_dir = args.src or os.path.join(root, "self-docs")
    if not os.path.isdir(src_dir):
        print(f"Error: self-docs directory not found at {src_dir}")
        sys.exit(1)

    kl_home = os.environ.get("KNOWLEDGELIB_HOME") or os.path.expanduser("~/Documents/Repo/knowledgelib_data")
    dest_dir = args.dest or os.path.join(kl_home, "self-docs")
    extractor = os.path.join(kl_home, "src", "extract_tech_notes.py")

    if not os.path.isfile(extractor):
        print(f"Error: KnowledgeLib extractor not found at {extractor}. Check KNOWLEDGELIB_HOME.")
        sys.exit(1)

    cmd = [sys.executable, extractor, "--src", src_dir, "--dest", dest_dir]
    if args.dry_run:
        cmd.append("--dry-run")

    print(f"Syncing {src_dir} -> {dest_dir} via KnowledgeLib extractor...")
    res = subprocess.run(cmd)
    if res.returncode != 0:
        sys.exit(res.returncode)

    if not args.dry_run:
        # Refresh memory index
        loader = os.path.join(kl_home, "src", "memory_loader.py")
        if os.path.isfile(loader):
            print("Refreshing KnowledgeLib Memory Index...")
            subprocess.run([sys.executable, loader, "--export"], cwd=kl_home)

        # Refresh vector sync
        syncer = os.path.join(kl_home, "src", "sync_knowledgelib.py")
        if not os.path.isfile(syncer):
            syncer = os.path.join(kl_home, "scripts", "sync_knowledgelib.py")
        if os.path.isfile(syncer):
            print("Syncing ChromaDB vector index...")
            subprocess.run([sys.executable, syncer], cwd=kl_home)

    print("KnowledgeLib sync complete.")


if __name__ == "__main__":
    main()
